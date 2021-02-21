import json


def create(name: str, order):
    with open('orders.json') as orders_file:
        orders = json.load(orders_file)
        if name in orders.keys():
            orders[name].append(Order(order))
        else:
            orders[name] = []
            orders[name].append(Order(order))
        with open('orders.json', 'w') as outfile:
            json.dump(orders, outfile)


def remove(name: str, o_id: int):
    with open('orders.json') as orders_file:
        orders = json.load(orders_file)
        if name in orders.keys():
            orders[name] = [o for o in orders[name] if o['id'] != o_id]
            with open('orders.json', 'w') as outfile:
                json.dump(orders, outfile)


def remove_last(name: str):
    with open('orders.json') as orders_file:
        orders = json.load(orders_file)
        if name in orders.keys():
            orders[name] = orders[name][:-1]
            with open('orders.json', 'w') as outfile:
                json.dump(orders, outfile)


def clear(name: str):
    with open('orders.json') as orders_file:
        orders = json.load(orders_file)
        if name in orders.keys():
            orders[name] = []
            with open('orders.json', 'w') as outfile:
                json.dump(orders, outfile)


def get_length(name: str) -> int:
    length = 0
    with open('orders.json') as orders_file:
        orders = json.load(orders_file)
        if name in orders.keys():
            length = len(orders[name])

    return length


def Order(order):
    return {
        'id': order['id'],
        'clientOrderId': order['clientOrderId'],
        'timestamp': order['timestamp'],
        'symbol': order['symbol'],
        'side': order['side'],
        'amount': order['amount'],
        'price': order['price'],
        'type': order['type']
    }
