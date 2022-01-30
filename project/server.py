import json
import logging
import select

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
    print('in forming')
    print(f'data --> {type(data)}')
    print(f'counter key --> {Counter(data.keys())}')
    presence_keys = ["action", "time", "user"]
    msg_keys = ["action", "time", "from", 'to', 'message']

    if Counter(presence_keys) == Counter(data.keys()):
        print('if')
        msg = {
            "response": 200,
            "time": time.ctime(time.time()),
            "alert": data['user']['message']
        }
        print(msg)
        logger.info(f'От клиента полученно сообщение: {data["user"]["message"]} в {data["time"]}')
    elif Counter(msg_keys) == Counter(data.keys()):
        msg = {
            "response": 200,
            "time": time.ctime(time.time()),
            "alert": data['message']
        }
        logger.info(f'От клиента полученно сообщение: {data["message"]} в {data["time"]}')
    else:
        print('else')
        msg = {
            "response": 400,
            "error": 'Bad Request'
        }
        logger.warning(f'Bad Request')
    return msg


def read_requests(resp, clients):
    print(f'resp --> {resp}')
    requests = {}
    for s in resp:
        try:
            print(f's --> {s}')
            data = s.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
            print(f'---------------------------\n'
                  f'data --> {data}\n'
                  f'---------------------------')
            print(handle_response(data, CONFIG['ENCODING']))
            requests[s] = forming_msg(handle_response(data, CONFIG['ENCODING']))
            print(f'forming msg --> {requests}')
        except:
            clients.remove(s)
    return requests


@Log()
def write_response(requests, w, clients):
    print(f'in write msg')
    print(f'w --> {w}')
    print(f'requests write --> {requests}')
    for s in w:
        if s in requests:
            print('in if write')
            try:
                print(f'type resp --> {type(requests[s])}')
                resp = requests[s]
                print(type(resp))
                print(f'resp --> {resp}')
                sending_msg(s, resp, CONFIG['ENCODING'])
            except:
                s.close()
                clients.remove(s)


def main():
    s = socket(AF_INET, SOCK_STREAM)
    clients = []
    try:
        connect_param = parser_argument()
        s.bind((connect_param['addr'], connect_param['port']))
        logger.info(f'Сервер запущен на порту: {connect_param["port"]}, по адресу: {connect_param["addr"]}.')
    except ValueError:
        logger.error('Значение порта должно быть от 1024 до 65535')
        sys.exit()
    s.listen(int(CONFIG["MAX_CONNECTIONS"]))
    s.settimeout(1)
    while True:
        try:
            client, addr = s.accept()
            print(f'client, addr')
        except OSError:
            pass
        else:
            clients.append(client)
            print('client appended')
        finally:
            wait = 10
            w = []
            r = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except:
                pass
        print('try read requests')
        clients_msg = read_requests(r, clients)
        print(f'client_msg --> {clients_msg}')
        print('read')
        if clients_msg:
            print('in msg')
            write_response(clients_msg, w, clients)

        # try:
        #     handle_msg, data = '', ''
        #     if r:
        #         for member in r:
        #             try:
        #                 data = member.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
        #                 handle_msg = handle_response(data, CONFIG['ENCODING'])
        #             except Exception as e:
        #                 logger.warning(e)
        #                 clients.remove(member)
        #     if data != b'':
        #         for member in w:
        #             print(forming_msg(handle_msg))
        #             sending_msg(member, forming_msg(handle_msg), CONFIG["ENCODING"])
        #         else:
        #             data = b''
        # except Exception:
        #     pass


if __name__ == '__main__':
    main()
