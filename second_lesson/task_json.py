import json


def write_to_json(item, quantity, price, buyer, date):
    json_data = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    with open('orders.json', 'r') as json_file:
        json_orders = json.load(json_file)
        json_orders['orders'].append(json_data)
    with open('orders.json', 'w') as json_file:
        json.dump(json_orders, json_file, indent=4)


write_to_json('bag', '1', '2589', 'Tolr', '21.01.23')
