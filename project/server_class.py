import json
import logging
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

import log.server_log_config
import select
import sys
import time
from collections import Counter
from socket import AF_INET, socket, SOCK_STREAM

from UI_Server import ServerInterface, gui_create_model
from decor_log import Log
from util import CONFIG, parser_argument, sending_msg, ServerPort, ServerTyped
from sqlalchemy.orm import sessionmaker
from db_server import ServerDB
from PyQt5 import uic, QtWidgets
import admin_server

logger = logging.getLogger('server')
new_connection = False
conflag_lock = threading.Lock()


class Server(threading.Thread):
    __metaclass__ = ServerTyped
    port = ServerPort()

    def __init__(self, logger, db, param):
        super(Server, self).__init__()
        try:
            self.db = db
            # connect_param = #parser_argument()
            self.addr = param[1] #connect_param['addr']
            self.port = int(param[0]) #connect_param['port']
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

    def run(self) -> None:
        self.server_connect()
        while True:
            try:
                self.new_connection()
            except OSError:
                pass
            finally:
                wait = 10
                w = []
                r = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass

                clients_msg = self.read_requests(r)
                if clients_msg:
                    self.write_response(clients_msg, w)

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
        global new_connection
        dir_key = {'presence_keys': ["action", "time", "user"],
                   'msg_keys': ["action", "time", "from", 'to', 'message'],
                   'query': ["action", "time", "user_login"]}
        if Counter(dir_key['presence_keys']) == Counter(data.keys()):
            msg = {
                "response": 200,
                "time": time.ctime(time.time()),
                "alert": 'Alright'
            }
            # Запускается, когда новый клиент пытается подключиться к серверу
            self.db.login(data['user']['account_name'], addr[0], addr[1])
            with conflag_lock:
                new_connection = True
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
                query_list = self.db.users_list()
                list_users = [user[0] for user in query_list]
                msg = {
                    "response": 202,
                    "alert": list_users
                }
                return msg
            else:
                logger.info(f'Принято сообщение об удалении/добавлении контакта')
                try:
                    print(f'data---->{data}')
                    self.db.change_db(data['action'][:3], data['user_login'])
                    msg = {'response': 200}
                except AttributeError:
                    msg = {'response': 400}
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
                try:
                    resp = requests[s]
                    print(f'resp ===>> {resp}')
                    sending_msg(s, resp)
                except:
                    s.close()
                    self.clients.remove(s)

def main():
    db = ServerDB()

    server_app = QApplication(sys.argv)
    main_window = ServerInterface()

    # По нажатию кнопки "Подключить" запускает сервер
    def start_server():
        param = main_window.get_connect_param()
        print(param)
        server_s = Server(logger, db, param)
        server_s.daemon = True
        server_s.start()

    main_window.statusBar().showMessage('Server is active')
    main_window.active_clients_table.setModel(gui_create_model(db))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()
    main_window.connect_btn.clicked.connect(start_server)

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(db))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
        with conflag_lock:
            new_connection = False


    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh.triggered.connect(list_update)
    # main_window.show_history_button.triggered.connect(show_statistics)
    # main_window.config_btn.triggered.connect(server_config)

    # Запускаем GUI
    server_app.exec_()


if __name__ == '__main__':
    main()