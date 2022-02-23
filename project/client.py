import json
import logging
import log.client_log_config
import sys
import threading
import time
from collections import Counter
from socket import socket, AF_INET, SOCK_STREAM

from decor_log import log
from util import CONFIG, parser_argument, sending_msg

logger = logging.getLogger('client')


@log
def handle_response(data, encoding):
    data = json.loads(data.decode(encoding))
    if "response" in data.keys():
        return data
    logger.critical('Некорректный формат данных')
    raise ValueError


@log
def presence_message(CONFIGS, account_name='Guest'):
    message = {
        "action": CONFIGS['PRESENCE'],
        "time": time.time(),
        "user": {
            "account_name": account_name,
            'message': CONFIGS['STATUS']
        }
    }
    logger.info('Сообщение о появлении на сервере.')
    return message


def message_from_server(sock, my_username):
    while True:
        try:
            server_msg = sock.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
            message = handle_response(server_msg, CONFIG['ENCODING'])
            needed_keys = ["action", "time", "from", 'to', 'message']

            if Counter(needed_keys) == Counter(message.keys()):
                if message['action'] == 'msg' and message['from'] == \
                        my_username:
                    logger.info(f'Получено сообщение от пользователя '
                                f'{message["from"]}:\n{message["message"]}')
                else:
                    logger.error(f'Получено некорректное'
                                 f'сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            logger.critical(f'Потеряно соединение с сервером.')
            break


def user_interactive(sock, username):
    print(f'Поддерживаемые команды:\n'
          f'message - отправить сообщение.'
          f'Кому и текст будет запрошены отдельно.\n'
          f'exit - выход из программы\n')
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'exit':
            logger.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова.')


def create_message(sock, account_name='Guest'):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        "action": 'msg',
        'from': account_name,
        'to': to_user,
        'time': time.time(),
        'message': message
    }
    logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        sending_msg(sock, message_dict, CONFIG['ENCODING'])
        logger.info(f'Отправлено сообщение для пользователя {to_user}')
    except:

        logger.critical('Потеряно соединение с сервером.')
        sys.exit(1)


def main():
    s = socket(AF_INET, SOCK_STREAM)
    try:
        connect_param = parser_argument(server=False)
        s.connect((connect_param['addr'], connect_param['port']))
        sending_msg(s, presence_message(CONFIG), CONFIG['ENCODING'])
        response = s.recv(int(CONFIG['MAX_PACKAGE_LENGTH']))
        answer = handle_response(response, CONFIG['ENCODING'])
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer["alert"]}')
    except AttributeError:
        logger.error('Необходимо указать IP сервера')
        sys.exit()
    except ValueError:
        logger.critical('Значение порта должно быть от 1024 до 65535')
        sys.exit()
    client_name = ''
    receiver = threading.Thread(target=message_from_server, args=(s, client_name))
    receiver.daemon = True
    receiver.start()

    user_interface = threading.Thread(target=user_interactive, args=(s, client_name))
    user_interface.daemon = True
    user_interface.start()
    logger.info('Запущены процессы')
    receiver.join()
    user_interface.join()
    ##########################


if __name__ == '__main__':
    threading.Thread(target=main(), args=()).start()
    main()
