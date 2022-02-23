import json
import logging
import log.server_log_config
import select
import sys
import time
from collections import Counter
from socket import AF_INET, socket, SOCK_STREAM

from decor_log import Log
from util import CONFIG, parser_argument, sending_msg, ServerPort, ServerTyped
from sqlalchemy.orm import sessionmaker
from db_server import ServerDB
# from PyQt5 import uic, QtWidgets
# import admin_server

logger = logging.getLogger('server')


# class Server_Win(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)
#         self.ui = admin_server.Ui_Server_int()
#         self.ui.setupUi(self)


class Server(ServerTyped):

    port = ServerPort()

    def __init__(self, logger, db):
        try:
            self.db = db
            connect_param = parser_argument()
            self.addr = connect_param['addr']
            self.port = connect_param['port']
            print(f'addr = {self.addr}, port = {self.port}')
        except ValueError:
            logger.error('Значение порта должно быть от 1024 до 65535')
            sys.exit()
        except AttributeError:
            logger.error('Значение должно быть положительным целым числом')
            sys.exit()
        self.logger = logger
        self.clients = []

    def server_connect(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.bind((self.addr, self.port))
        self.s.listen(int(CONFIG["MAX_CONNECTIONS"]))
        self.s.settimeout(1)
        logger.info(f'Сервер запущен на порту: {self.port}, по адресу: {self.addr}.')

    @Log()
    def new_connection(self):
        client, addr = self.s.accept()
        self.clients.append(client)
        logger.debug(f'Клиент {addr} добавлен')

    @Log()
    def handle_response(self, data):
        data = json.loads(data.decode(CONFIG['ENCODING']))
        if not isinstance(data, dict):
            logger.critical('Некорректный формат данных')
            raise ValueError
        return data

    @Log()
    def forming_msg(self, data, addr):
        dir_key = {'presence_keys': ["action", "time", "user"],
                   'msg_keys': ["action", "time", "from", 'to', 'message'],
                   'query': ["action", "time", "user_login"]}
        if Counter(dir_key['presence_keys']) == Counter(data.keys()):
            msg = {
                "response": 200,
                "time": time.ctime(time.time()),
                "alert": 'Alright'
            }
            print(type(data['user']['account_name']), type(addr[0]), type(addr[1]))
            self.db.login(data['user']['account_name'], addr[0], addr[1])
            logger.info(f'От клиента полученно сообщение: {data["user"]["message"]} в {data["time"]}')
        elif Counter(dir_key['msg_keys']) == Counter(data.keys()):
            msg = {
                "action": 'msg',
                "time": time.ctime(time.time()),
                "from": data["from"],
                'to': data["to"],
                "message": data['message']
            }
            logger.info(f'От клиента {data["from"]} полученно сообщение: {data["message"]} в {data["time"]}')
        elif Counter(dir_key['query']) == Counter(data.keys()):
            if data['action'] == "get_contacts":
                return self.db.users_list()
            else:
                logger.info(f'Принято сообщение об удалении/добавлении контакта')
                # try:
                print(f'data---->{data}')
                self.db.change_db(data['action'][:3], data['user_login'])
                msg = {'response': 200}
                # except AttributeError:
                #     msg = {'response': 400}
        else:
            msg = {
                "response": 400,
                "error": 'Bad Request'
            }
            logger.warning(f'Bad Request')
        return msg

    def read_requests(self, resp):
        requests = {}
        for s in resp:
            try:
                data = s.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
                requests[s] = self.forming_msg(self.handle_response(data), s.getsockname())
            except:
                self.clients.remove(s)
        return requests

    @Log()
    def write_response(self, requests, w):
        for s in w:
            if s in requests:
                # try:
                resp = requests[s]
                print(f'resp ===>> {resp}')
                sending_msg(s, resp)
                # except:
                #     s.close()
                #     self.clients.remove(s)



def main():
    db = ServerDB()
    server_s = Server(logger, db)
    server_s.server_connect()
    while True:
        try:
            server_s.new_connection()
        except OSError:
            pass
        finally:
            wait = 10
            w = []
            r = []
            try:
                r, w, e = select.select(server_s.clients, server_s.clients, [], wait)
            except:
                pass

            clients_msg = server_s.read_requests(r)
            if clients_msg:
                server_s.write_response(clients_msg, w)


if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # window = Server_Win()
    # window.show()
    # sys.exit(app.exec())
    main()