import argparse
import json

from dotenv import dotenv_values

CONFIG = dotenv_values()


def sending_msg(sct, msg, encoding):
    json_message = json.dumps(msg)
    coding_msg = json_message.encode(encoding)
    sct.send(coding_msg)


def parser_argument(server=True):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', type=str, help="server's ip-address",
                        default=CONFIG["DEFAULT_IP_SERVER"] if server else None)
    parser.add_argument('-p', '--port', type=int, help='Port', default=CONFIG['DEFAULT_PORT'])
    args = vars(parser.parse_args())
    if not args['addr'] and not server:
        raise AttributeError
    if not 65535 >= args['port'] >= 1024:
        raise ValueError
    return args
