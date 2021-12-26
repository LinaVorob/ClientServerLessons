import json
import time
from socket import AF_INET, socket, SOCK_STREAM
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', type=str, help="server's ip-address")
parser.add_argument('-p', '--port', type=int, help='Port')
args = parser.parse_args()

s = socket(AF_INET, SOCK_STREAM)
ip_addr = args.addr if args.addr else ''
port = args.port if args.port else 7777
s.bind((ip_addr, port))
s.listen(5)
while True:
    client, addr = s.accept()
    data = client.recv(1000000)
    data_json = json.loads(data.decode())
    print(f'Статус клиента: {data_json["user"]["status"]}\n'
          f'Ответ был отправлен клиентом в {data_json["time"]} с ip-адреса {addr[0]}:{addr[1]}.')
    msg = {
        "response": 202,
        "time": time.ctime(time.time()),
        "alert": "Подтверждено"
    }
    msg_json = json.dumps(msg)
    client.send(msg_json.encode('utf-8'))
    client.close()
