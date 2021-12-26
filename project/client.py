import json
from socket import socket, AF_INET, SOCK_STREAM
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="server's ip-address")
parser.add_argument('-p', '--port', type=int, help='Port')
args = parser.parse_args()

s = socket(AF_INET, SOCK_STREAM)
addr = args.addr
port = args.port if args.port else 7777
s.connect((addr, port))
msg = {
    "action": "presence",
    "time": time.ctime(time.time()),
    "type": "status",
    "user": {
        "account_name": "C0deMaver1ck",
        "status": "I am here!"
    }
}
msg_json = json.dumps(msg)
s.send(msg_json.encode('utf-8'))
data = s.recv(1000000)
data_json = json.loads(data.decode())
print(f'Код ответа: {data_json["response"]}.\n'
      f'Сообщение от сервера: {data_json["alert"]}')
s.close()
