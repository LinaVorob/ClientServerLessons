import inspect
import os
from datetime import datetime


def log(func):
    def callf(*args, **kwargs):
        log_data = f'{datetime.today().replace(microsecond=0)} ' \
                   f'Функция {func.__name__}() вызвана из функции {inspect.stack()[1][3]}()\n'
        mode = 'a' if 'client_func_log.log' in os.listdir() else 'w'

        with open('client_func_log.log', mode, encoding='utf-8') as func_log:
            func_log.write(log_data)
        res = func(*args, *kwargs)
        return res

    return callf


class Log:

    def __init__(self):
        pass

    def __call__(self, func):
        def callf(*args, **kwargs):
            log_data = f'{datetime.today().replace(microsecond=0)} ' \
                       f'Функция {func.__name__}() вызвана из функции {inspect.stack()[1][3]}()\n'

            mode = 'a' if 'server_func_log.log' in os.listdir() else 'w'
            with open('server_func_log.log', mode, encoding='utf-8') as func_log:
                func_log.write(log_data)
            res = func(*args, *kwargs)
            return res

        return callf
