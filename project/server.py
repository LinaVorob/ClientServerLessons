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
    presence_keys = ["action", "time", "user"]
    msg_keys = ["action", "time", "from", 'to', 'message']

    if Counter(presence_keys) == Counter(data.keys()):
        print('if')
        msg = {
            "response": 200,
            "time": time.ctime(time.time()),
            "alert": data['user']['message']
        }
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
    requests = []
    for s in resp:
        try:
            data = s.recv(int(CONFIG['MAX_PACKAGE_LENGTH'])).decode(CONFIG['ENCODING'])
            requests[s] = data
        except:
            clients.remove(s)
    return requests


@Log()
def write_response(requests, w, clients):
    for s in w:
        if s in requests:
            try:
                resp = requests[s].encode('utf-8')
                test = s.send(resp)
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
        except OSError:
            pass
        else:
            clients.append(client)
        finally:
            w = []
            r = []
            try:
                r, w, e = select.select(clients, clients, [])
            except OSError:
                pass
        try:
            handle_msg, data = '', ''
            if r:
                for member in r:
                    try:
                        data = member.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
                        print(data)
                        handle_msg = handle_response(data, CONFIG['ENCODING'])
                    except ValueError:
                        logger.critical(f'Некорректное сообщение')
                    except:
                        pass
            if data != '':
                for member in w:
                    print(handle_msg)
                    print(forming_msg(handle_msg))
                    sending_msg(member, forming_msg(handle_msg), CONFIG["ENCODING"])
                else:
                    data = ''
        except Exception:
            pass

        # requests = read_requests(r, clients)
        # write_response(requests, w, clients)
        # for client in w:
        #     try:
        #         sending_msg(client, 'echo', CONFIG['ENCODING'])
        #     except Exception:
        #         clients.remove(client)
        # try:
        #     print(r)
        #     data = client.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
        #     handle_msg = handle_response(data, CONFIG['ENCODING'])
        #     for msg in r:
        #         sending_msg(r, forming_msg(handle_msg), CONFIG['ENCODING'])
        # except ValueError:
        #     logger.critical(f'Некорректное сообщение')
        # except:
        #     pass
        # client.close()


if __name__ == '__main__':
    main()
