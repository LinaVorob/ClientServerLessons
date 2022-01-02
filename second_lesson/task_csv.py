import csv
import os
import re


def get_data():
    files = os.listdir()
    pattern = 'info[a-zA-Z0-9_-]*.txt$'
    files = list(filter(lambda x: re.search(pattern, x), files))
    pattern_prod = 'Изготовитель ОС:[a-zA-z0-9 ]*'
    pattern_name = 'Название ОС:[a-zA-z0-9 ]*'
    pattern_code = 'Код продукта:[a-zA-z0-9 ]*'
    pattern_type = 'Тип системы:[a-zA-z0-9 ]*'
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]

    for file in files:
        with open(file, 'r', encoding='"windows-1251') as f:
            for line in f:
                print(line)
                print(re.search(pattern_prod, line))
                if re.search(pattern_prod, line):
                    os_prod_list.append(line.replace('  ', '').split(':')[1].replace('\n', ''))
                elif re.search(pattern_code, line):
                    os_code_list.append(line.replace('  ', '').split(': ')[1].replace('\n', ''))
                elif re.search(pattern_name, line):
                    os_name_list.append(line.replace('  ', '').split(':')[1].replace('\n', ''))
                elif re.search(pattern_type, line):
                    os_type_list.append(line.replace('  ', '').split(':')[1].replace('\n', ''))
    for item in range(len(main_data[0]) - 1):
        main_data.append([os_prod_list[item], os_name_list[item], os_code_list[item], os_type_list[item]])

    return main_data


def write_to_csv(file):
    info_list = get_data()
    with open(file, 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in info_list:
            f_n_writer.writerow(row)


write_to_csv('task_1.csv')
