# Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
# (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

words = [b'class', b'function', b'method']

for word in words:
    print(f'Содержимое: {word}\nТип: {type(word)}\nДлина: {len(word)}\n____________')

#байты представлены как сама последовательность символов.
