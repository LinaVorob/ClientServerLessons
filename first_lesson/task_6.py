# Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.

import locale

def_coding = locale.getpreferredencoding()
print(f'Кодировка по умолчанию: {def_coding}')

with open('test_file.txt') as f_n:
    print(f'Кодировка файла: {f_n.encoding}')
    print('Результат без принудительной кодировки:')
    for line in f_n:
        print(line)
with open('test_file.txt', encoding="utf-8") as file_uni:
    print('Результат при кодировании utf-8:')
    for line in file_uni:
        print(line)

with open('test_file.txt', encoding="ascii") as file_uni:
    print('Результат при кодировании ascii:')
    try:
        for line in file_uni:
            print(line)
    except UnicodeError as uni:
        print(uni)


#Вывод:
# Кодировка по умолчанию: cp1251
# Кодировка файла: cp1251
# Результат без принудительной кодировки:
# СЃРµС‚РµРІРѕРµ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёРµ
#
# СЃРѕРєРµС‚
#
# РґРµРєРѕСЂР°С‚РѕСЂ
# Результат при кодировании utf-8:
# сетевое программирование
#
# сокет
#
# декоратор
# Результат при кодировании ascii:
# 'ascii' codec can't decode byte 0xd1 in position 0: ordinal not in range(128)
#

# Только при принудительном указании utf-8 возможно прочитать содержимое файла. В остальных случаях либо ошибка, либо
# сбитый текст с ошибочной дешифровкой.

