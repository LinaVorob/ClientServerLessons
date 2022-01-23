import json
import logging
import log.client_log_config
import sys
import time
import threading
from socket import socket, AF_INET, SOCK_STREAM

from decor_log import log
from util import CONFIG, parser_argument, sending_msg

logger = logging.getLogger('client')


@log
def handle_response(data, encoding):
    data = json.loads(data.decode(encoding))
    if "response" in data:
        message = f'Сообщение: {data["alert"]}' if data['response'] == 200 else f'Ошибка: {data["error"]}'
        return message
    logger.critical('Некорректный формат данных')
    raise ValueError


def main():
    s = socket(AF_INET, SOCK_STREAM)
    try:
        connect_param = parser_argument(server=False)
        s.connect((connect_param['addr'], connect_param['port']))

        while True:
            if connect_param['mode'] == 'write':
                user_msg = input("Введите сообщение (q - выход): ")
                if user_msg == 'q':
                    break
                msg = {
                    "action": "msg",
                    "time": time.ctime(time.time()),
                    "user": {
                        "account_name": CONFIG['ACCOUNT_NAME'],
                        "msg": user_msg
                    }
                }
                sending_msg(s, msg, CONFIG["ENCODING"])
            elif connect_param['mode'] == 'listen':
                data = s.recv(int(CONFIG["MAX_PACKAGE_LENGTH"]))
                if data:
                    msg = handle_response(data, CONFIG["ENCODING"])
                    print(msg)
            else:
                logger.error('Неверный параметр ввода')
                break
        s.close()
    except AttributeError:
        logger.error('Необходимо указать IP сервера')
        sys.exit()
    except ValueError:
        logger.critical('Значение порта должно быть от 1024 до 65535')
        sys.exit()


if __name__ == '__main__':
    print('Started!!!')
    main()
