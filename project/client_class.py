import json
import logging
import sys
import threading

from PyQt5 import QtWidgets
from sqlalchemy.orm import sessionmaker

import client_ui
import db_client
import log.client_log_config
import time
from collections import Counter
from socket import socket, AF_INET, SOCK_STREAM

from decor_log import log
from util import CONFIG, parser_argument, sending_msg, ClientTyped

logger = logging.getLogger('client')
engine = db_client.engine
Session = sessionmaker(bind=engine)
session = Session()
#
# class Client_Win(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)
#         self.ui = client_ui.Ui_MainWindow()
#         self.ui.setupUi(self)


class Client(ClientTyped):
    def __init__(self, name, logger):
        try:
            connect_param = parser_argument(server=False)
        except AttributeError:
            logger.error('Необходимо указать IP сервера')
            sys.exit()
        except ValueError:
            logger.critical('Значение порта должно быть от 1024 до 65535')
            sys.exit()
        self.addr = connect_param['addr']
        self.port = connect_param['port']
        self.name = name if name else 'Guest'
        self.logger = logger

    def client_connect(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((self.addr, self.port))
        self.logger.info('Установленно соединение с сервером')
        sending_msg(self.s, self.presence_message())

    @log
    def presence_message(self):
        message = {
            "action": CONFIG['PRESENCE'],
            "time": time.time(),
            "user": {
                "account_name": self.name,
                'message': CONFIG['STATUS']
            }
        }
        logger.info('Сообщение о появлении на сервере.')
        return message

    @log
    def handle_response(self, data):
        self.data = json.loads(data.decode(CONFIG['ENCODING']))
        if "response" in self.data.keys():
            return self.data
        logger.critical('Некорректный формат данных')
        raise ValueError

    def message_from_server(self):
        while True:
            # try:
                server_msg = self.s.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
                print(f'получено с сервера ---> {server_msg}')
                message = self.handle_response(server_msg)
                dir_key = {'presence_keys': ["response", "time", "alert"],
                           'msg_keys': ["action", "time", "from", 'to', 'message'],
                           'query_list': ["response", "alert"],
                           'error': ["response", "error"],
                           'add_del': ['response']}
                print(f'message = {message}')

                if Counter(dir_key['msg_keys']) == Counter(message.keys()):
                    if message['action'] == 'msg' and message['to'] == self.name:
                        logger.info(f'Получено сообщение от пользователя {message["from"]}:'
                                    f'\n{message["message"]}')
                elif Counter(dir_key['presence_keys']) == Counter(message.keys()) and message["response"] == 200:
                    logger.info(f'Установлено соединение с сервером. Ответ сервера: {message["alert"]}')
                elif Counter(dir_key['query_list']) == Counter(message.keys()) and message["response"] == 202:
                    logger.info(f'Список пользователей\n{message["alert"]}:')
                elif Counter(dir_key['error']) == Counter(message.keys()) and message['response'] == 400:
                    logger.error(f'Ошибка: {message["error"]}')
                elif Counter(dir_key['add_del']) == Counter(message.keys()):
                    if message['response'] == 400:
                        logger.error(f'Ошибка! Операция не выполнена')
                    else:
                        logger.info(f'Операция выполнена')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            # except (OSError, ConnectionError, ConnectionAbortedError,
            #         ConnectionResetError, json.JSONDecodeError, AttributeError):
            #     logger.critical(f'Потеряно соединение с сервером.')
            #     break

    def user_interactive(self):
        print(f'Поддерживаемые команды:\n'
              f'message - отправить сообщение. Кому и текст будут запрошены отдельно.\n'
              f'list - получить список контактов;\n'
              f'add - добавить контакт в БД;\n'
              f'del - удалить контакт из БД\n'
              f'exit - выход из программы\n')
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'exit':
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            elif command == 'list':
                self.list_of_client()
            elif command == 'add' or 'del':
                login_contact = input('Введите логин контакта: ')
                contact_name = input('Введите имя контакта: ')
                self.change_db(command, login_contact, contact_name)
            else:
                print('Команда не распознана, попробойте снова.')

    def create_message(self):
        to_user = input('Введите получателя сообщения: ')
        self.add_contact(to_user)
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            "action": 'msg',
            'from': self.name,
            'to': to_user,
            'time': time.time(),
            'message': message
        }
        logger.info(f'Сформирован словарь сообщения: {message_dict}')
        # try:
        sending_msg(self.s, message_dict)
        logger.info(f'Отправлено сообщение для пользователя {to_user}')
        new_msg = db_client.ChatHistory(to_user, message_dict['message'])
        session.add(new_msg)
        session.commit()
        # except:
        #     logger.critical('Потеряно соединение с сервером.')
        #     sys.exit(1)

    def list_of_client(self):
        message = {
            "action": "get_contacts",
            "time": time.time(),
            "user_login": self.name
        }
        logger.info('Запрос списка клиентов.')
        sending_msg(self.s, message)
        return message

    def change_db(self, command, login_contact, name):
        message = {
            "action": f'{command}_contact',
            "user_id": name,
            "time": time.ctime(time.time()),
            "user_login": login_contact
        }
        logger.info(f'Запрос на {"удаление" if command == "del" else "добавление"} контакта')
        sending_msg(self.s, message)
        return message

    def add_contact(self, to_user):
        q_user = session.query(db_client.Contacts).filter_by(name=to_user)
        if q_user is None:
            new_contact = db_client.Contacts(to_user, 'info')
            session.add(new_contact)
            session.commit()


def main():
    client_name = input('Логин: ')
    client = Client(client_name, logger)
    client.client_connect()

    receiver = threading.Thread(target=client.message_from_server)
    receiver.daemon = True
    receiver.start()

    user_interface = threading.Thread(target=client.user_interactive)
    user_interface.daemon = True
    user_interface.start()
    logger.info('Запущены процессы')
    receiver.join()
    user_interface.join()


if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # window = Client_Win()
    # window.show()
    # sys.exit(app.exec())
    threading.Thread(target=main(), args=()).start()
    main()
