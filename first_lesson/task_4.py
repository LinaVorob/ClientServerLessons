#Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое
# и выполнить обратное преобразование (используя методы encode и decode).

words = ['разработка', 'администрирование', 'protocol', 'standard']
words_byte = []
for item in words:
    print(f'{item.encode()}')
    words_byte.append(item.encode())
else:
    print('_____________________')

for item in words_byte:
    print(f'{item.decode()}')

# Символы записанные кириллицей были заменены их числовым кодом. А латиницей не изменились, но тип так же byte.
# Обратное преобразование все вернуло в прежний вид.
# Вывод:
# b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0'
# b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'
# b'protocol'
# b'standard'
# _____________________
# разработка
# администрирование
# protocol
# standard
