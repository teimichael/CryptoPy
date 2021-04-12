import json


class OrderManager(object):

    def __init__(self, orders_path: str):
        self.__orders_path = orders_path

    def create(self, name: str, order):
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                orders[name].append(self.sim_order(order))
            else:
                orders[name] = []
                orders[name].append(self.sim_order(order))
            with open(self.__orders_path, 'w') as outfile:
                json.dump(orders, outfile)

    def remove(self, name: str, o_id: int):
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                orders[name] = [o for o in orders[name] if o['id'] != o_id]
                with open(self.__orders_path, 'w') as outfile:
                    json.dump(orders, outfile)

    def remove_last(self, name: str):
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                orders[name] = orders[name][:-1]
                with open(self.__orders_path, 'w') as outfile:
                    json.dump(orders, outfile)

    def clear(self, name: str):
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                orders[name] = []
                with open(self.__orders_path, 'w') as outfile:
                    json.dump(orders, outfile)

    def get_length(self, name: str) -> int:
        length = 0
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                length = len(orders[name])

        return length

    # Get all orders with name
    def get_orders(self, name: str) -> list:
        r = []
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
            if name in orders.keys():
                r = orders[name]

        return r

    # get all orders
    def get_all(self) -> dict:
        with open(self.__orders_path) as orders_file:
            orders = json.load(orders_file)
        return orders

    @staticmethod
    def sim_order(order):
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
