import json
import logging
import log.server_log_config
import sys
import time
from collections import Counter
from socket import AF_INET, socket, SOCK_STREAM

from decor_log import Log
from util import CONFIG, parser_argument, sending_msg

logger = logging.getLogger('server')


@Log()
def handle_response(data, encoding):
    data = json.loads(data.decode(encoding))
    if not isinstance(data, dict):
        logger.critical('Некорректный формат данных')
        raise ValueError
    return data


@Log()
def forming_msg(data):
    needed_keys = ["action", "time", "type", "user"]

    if Counter(needed_keys) == Counter(data.keys()):
        msg = {
            "response": 200,
            "time": time.ctime(time.time()),
            "alert": "Accept"
        }
        logger.info(f'От клиента полученно сообщение: {data["user"]["status"]} в {data["time"]}')
    else:
        msg = {
            "response": 400,
            "error": 'Bad Request'
        }
        logger.warning(f'Bad Request')
    return msg


def main():
    s = socket(AF_INET, SOCK_STREAM)
    try:
        connect_param = parser_argument()
        s.bind((connect_param['addr'], connect_param['port']))
    except ValueError:
        logger.error('Значение порта должно быть от 1024 до 65535')
        sys.exit()
    s.listen(int(CONFIG["MAX_CONNECTIONS"]))

    while True:
        client, addr = s.accept()
        try:
            data = client.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
            handle_msg = handle_response(data, CONFIG['ENCODING'])
            sending_msg(client, forming_msg(handle_msg), CONFIG['ENCODING'])
        except ValueError:
            logger.critical(f'Некорректное сообщение')
        client.close()


if __name__ == '__main__':
    main()
