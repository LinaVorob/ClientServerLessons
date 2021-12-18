#  Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый
#  тип на кириллице.

import subprocess

args = ['ping', 'yandex.ru']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    line = line.decode('cp866').encode('utf-8')
    print(line.decode('utf-8'))

# Вывод:
#Обмен пакетами с yandex.ru [5.255.255.55] с 32 байтами данных:
#
# Ответ от 5.255.255.55: число байт=32 время=13мс TTL=249
# Ответ от 5.255.255.55: число байт=32 время=13мс TTL=249
# Ответ от 5.255.255.55: число байт=32 время=13мс TTL=249
# Ответ от 5.255.255.55: число байт=32 время=13мс TTL=249
#
# Статистика Ping для 5.255.255.55:
#     Пакетов: отправлено = 4, получено = 4, потеряно = 0
#     (0% потерь)
# Приблизительное время приема-передачи в мс:
#     Минимальное = 13мсек, Максимальное = 13 мсек, Среднее = 13 мсек
#
# Process finished with exit code 0

args = ['ping', 'youtube.com']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    line = line.decode('cp866').encode('utf-8')
    print(line.decode('utf-8'))

# Вывод:
# Обмен пакетами с youtube.com [173.194.73.136] с 32 байтами данных:
#
# Ответ от 173.194.73.136: число байт=32 время=6мс TTL=108
# Ответ от 173.194.73.136: число байт=32 время=6мс TTL=109
# Ответ от 173.194.73.136: число байт=32 время=6мс TTL=108
# Ответ от 173.194.73.136: число байт=32 время=6мс TTL=109
#
# Статистика Ping для 173.194.73.136:
#     Пакетов: отправлено = 4, получено = 4, потеряно = 0
#     (0% потерь)
# Приблизительное время приема-передачи в мс:
#     Минимальное = 6мсек, Максимальное = 6 мсек, Среднее = 6 мсек
#
# Process finished with exit code 0

# без изначального преобразования байтов в кириллицу с помощью decode('cp866') появлялась ошибка
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8e in position 0: invalid start byte
