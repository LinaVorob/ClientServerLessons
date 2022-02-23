# 1. В директории проекта создать каталог log, в котором для клиентской и серверной сторон в отдельных модулях формата
# server_log_config.py и server_log_config.py создать логгеры;

# 2. В каждом модуле выполнить настройку соответствующего логгера по следующему алгоритму:
# Создание именованного логгера;
# Сообщения лога должны иметь следующий формат: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>";
# Журналирование должно производиться в лог-файл;
# На стороне сервера необходимо настроить ежедневную ротацию лог-файлов.

# 3. Реализовать применение созданных логгеров для решения двух задач:
# Журналирование обработки исключений try/except. Вместо функции print() использовать журналирование и обеспечить
# вывод служебных сообщений в лог-файл;
# Журналирование функций, исполняемых на серверной и клиентской сторонах при работе мессенджера.


import logging
from logging import handlers

_format = logging.Formatter('%(asctime)s %(levelname)-10s %(module)-15s %(message)s')

server_log = logging.getLogger('server')
server_log.setLevel(logging.INFO)

server_handler = handlers.TimedRotatingFileHandler("server.log", when='D', interval=1, backupCount=10,
                                                   encoding='utf-8')
server_handler.setFormatter(_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(_format)

server_log.addHandler(console_handler)
server_log.addHandler(server_handler)
