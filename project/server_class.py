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

class Server_Win(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = admin_server.Ui_Server_int()
        self.ui.setupUi(self)


class Server(threading.Thread, metaclass=ServerTyped):

    port = ServerPort()

    def __init__(self, logger, db, port, ip):
        try:
            self.db = db
            # connect_param = parser_argument()
            self.addr = ip #connect_param['addr']
            self.port = port #connect_param['port']
            print(f'addr = {self.addr}, port = {self.port}')
        except ValueError:
            logger.error('Значение порта должно быть от 1024 до 65535')
            sys.exit()
        except AttributeError:
            logger.error('Значение должно быть положительным целым числом')
            sys.exit()
        self.logger = logger
        self.clients = []

    def server_connect(self) -> None:
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
                # try:
                resp = requests[s]
                print(f'resp ===>> {resp}')
                sending_msg(s, resp)
                # except:
                #     s.close()
                #     self.clients.remove(s)

def main(port, ip):
    db = ServerDB()
    server_s = Server(logger, db, port, ip)
    server_s.daemon = True
    server_s.start()

    server_app = QApplication(sys.argv)
    main_window = ServerInterface()
    main_window.statusBar().showMessage('Server is active')
    main_window.active_clients_table.setModel(gui_create_model(db))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(db))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
        with conflag_lock:
            new_connection = False

    # Функция создающяя окно со статистикой клиентов
    # def show_statistics():
    #     global stat_window
    #     stat_window = HistoryWindow()
    #     stat_window.history_table.setModel(create_stat_model(database))
    #     stat_window.history_table.resizeColumnsToContents()
    #     stat_window.history_table.resizeRowsToContents()
    #     stat_window.show()

    # Функция создающяя окно с настройками сервера.
    # def server_config():
    #     global config_window
    #     # Создаём окно и заносим в него текущие параметры
    #     config_window = ConfigWindow()
    #     config_window.db_path.insert(config['SETTINGS']['Database_path'])
    #     config_window.db_file.insert(config['SETTINGS']['Database_file'])
    #     config_window.port.insert(config['SETTINGS']['Default_port'])
    #     config_window.ip.insert(config['SETTINGS']['Listen_Address'])
    #     config_window.save_btn.clicked.connect(save_server_config)

    # Функция сохранения настроек
    # def save_server_config():
    #     global config_window
    #     message = QMessageBox()
    #     config['SETTINGS']['Database_path'] = config_window.db_path.text()
    #     config['SETTINGS']['Database_file'] = config_window.db_file.text()
    #     try:
    #         port = int(config_window.port.text())
    #     except ValueError:
    #         message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
    #     else:
    #         config['SETTINGS']['Listen_Address'] = config_window.ip.text()
    #         if 1023 < port < 65536:
    #             config['SETTINGS']['Default_port'] = str(port)
    #             print(port)
    #             with open('server.ini', 'w') as conf:
    #                 config.write(conf)
    #                 message.information(
    #                     config_window, 'OK', 'Настройки успешно сохранены!')
    #         else:
    #             message.warning(
    #                 config_window,
    #                 'Ошибка',
    #                 'Порт должен быть от 1024 до 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh_button.triggered.connect(list_update)
    # main_window.show_history_button.triggered.connect(show_statistics)
    # main_window.config_btn.triggered.connect(server_config)

    # Запускаем GUI
    server_app.exec_()

if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # window = Server_Win()
    # window.show()
    # sys.exit(app.exec())
    main()