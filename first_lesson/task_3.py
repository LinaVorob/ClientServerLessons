#Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
attr = b'attribute'
class_word = b'класс'
func = b'функция'
type_word = b'type'

# нельзя записать в байтовом виде слова «класс», «функция», так как кириллица не относится к ASCII. В итоге ошибки:
#  File "D:\PyCharm\ClientServerLessons\first_lesson\task_3.py", line 3
#     class_word = b'класс'
#                               ^
# SyntaxError: bytes can only contain ASCII literal characters.
#
#   File "D:\PyCharm\ClientServerLessons\first_lesson\task_3.py", line 4
#     func = b'функция'
#                             ^
# SyntaxError: bytes can only contain ASCII literal characters

