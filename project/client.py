import json
import logging
import log.client_log_config
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from decor_log import log
from util import CONFIG, parser_argument, sending_msg

logger = logging.getLogger('client')


@log
def handle_response(data, encoding):
    data = json.loads(data.decode(encoding))
    if "response" in data:
        message = f'Сообщение от сервера: {data["alert"]}' if data['response'] == 200 else f'Ошибка: {data["error"]}'
        return f'Код ответа: {data["response"]}.\n{message}'
    logger.critical('Некорректный формат данных')
    raise ValueError


def main():
    s = socket(AF_INET, SOCK_STREAM)
    try:
        connect_param = parser_argument(server=False)
        s.connect((connect_param['addr'], connect_param['port']))
        # msg = {
        #     "action": "presence",
        #     "time": time.ctime(time.time()),
        #     "type": "status",
        #     "user": {
        #         "account_name": CONFIG['ACCOUNT_NAME'],
        #         "status": CONFIG["STATUS"]
        #     }
        # }
        while True:
            msg = input("Введите сообщение: ")
            sending_msg(s, msg, CONFIG["ENCODING"])
            data = s.recv(int(CONFIG["MAX_PACKAGE_LENGTH"])).decode(CONFIG["ENCODING"])
            print(f'Ответ: {data}')
        s.close()
    except AttributeError:
        logger.error('Необходимо указать IP сервера')
        sys.exit()
    except ValueError:
        logger.critical('Значение порта должно быть от 1024 до 65535')
        sys.exit()


if __name__ == '__main__':
    main()
