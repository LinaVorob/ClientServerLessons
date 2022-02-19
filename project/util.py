import argparse
import dis
import json
import socket

from dotenv import dotenv_values

CONFIG = dotenv_values()


class ClientVerify(type):

    def __init__(self, clsname, bases, clsdict):

        if any(isinstance(getattr(self, obj), socket.socket) for obj in self.__dict__):
            raise ConnectionError

        for key, value in clsdict.items():
            method_dict = dis.Bytecode(value)

            if not all('accept' not in x.argrepr for x in method_dict) or not all(
                    'listen' not in x.argrepr for x in method_dict):
                raise AttributeError
            if not all('SOCK_DGRAM' not in x.argrepr for x in method_dict):
                raise ConnectionRefusedError


class ServerVerify(type):
    def __init__(self, clsname, bases, clsdict):

        for key, value in clsdict.items():
            method_dict = dis.Bytecode(value)
            if any(x.argrepr == 'connect' for x in method_dict):
                raise AttributeError
            if not all('SOCK_DGRAM' not in x.argrepr for x in method_dict):
                print(f'SOCK_DGRAM in {method_dict}')
                raise ConnectionRefusedError


class ClientTyped(metaclass=ClientVerify):
    pass


class ServerTyped(metaclass=ServerVerify):
    pass


class ServerPort:
    def __set__(self, instance, value):
        if value not in range(1024, 65535):
            print(f'plus dir')
            raise ValueError("Значение вне разрешенного диапазона")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


def sending_msg(sct, msg):
    json_message = json.dumps(msg)
    coding_msg = json_message.encode(CONFIG['ENCODING'])
    sct.send(coding_msg)


def parser_argument(server=True):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', type=str, help="server's ip-address",
                        default=CONFIG["DEFAULT_IP_SERVER"] if server else None)
    parser.add_argument('-p', '--port', type=int, help='Port', default=CONFIG['DEFAULT_PORT'])
    args = vars(parser.parse_args())
    if not args['addr'] and not server:
        raise AttributeError
    # if not 65535 >= args['port'] >= 1024:
    #     raise ValueError
    return args
