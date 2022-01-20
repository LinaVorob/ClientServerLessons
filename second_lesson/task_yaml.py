import yaml

dict_data = {
    'first': ['раз', 'два'],
    'second': 549,
    'third': {
        'Summary': '\u2211',
        'Euro': '\u20AC',
        'Tamil': '\u0BF5',
        'Latin M': '\u0270',
    }
}


with open('file.yaml', 'w', encoding='utf-8') as f_n:
    yaml.dump(dict_data, f_n, default_flow_style=False, allow_unicode=True)

with open('file.yaml', 'r', encoding='utf-8') as file:
    file_content = yaml.load(file, Loader=yaml.Loader)

print(f'исходные == считанные? {file_content == dict_data}')
