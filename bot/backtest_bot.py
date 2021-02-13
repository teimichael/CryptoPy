import json
import logging
from datetime import datetime

import pandas as pd

from core.model import Order
from core.performance import get_performance
from core.util import str_to_timestamp


# Backtesting Bot
# TODO considering balance
class BackTestBot(object):
    def __init__(self, config):
        # History cache
        self.__history = {}

        # Data directory
        self.__data_dir = config["data_dir"]

        # Interval
        self.__interval = config["interval"]

        # Record current time
        self.__current_time = str_to_timestamp('2019-09-10 00:00:00')

        # Current balance
        self.__balance = config['balance']

        # Fee
        self.__taker_rate = config['taker_fee']
        self.__maker_rate = config['maker_fee']

        # Trade leverage
        self.__max_leverage = config['max_leverage']
        self.__trade_leverage = config['trade_leverage']

        # Order ID Issuer
        self.__order_id = 0

        # Order history
        self.__order_history = []

    def next(self, next_time: datetime):
        for o in self.__order_history:
            if o['type'] == "market" and o['status'] == "unfilled":
                # Fill all unfilled market orders
                o['status'] = "filled"
            elif o['type'] == "limit" and o['status'] == "unfilled":
                h, i = self.__load_history(o['symbol'], self.__interval)
                price = h.iloc[i]
                if price['Low'] <= o['price'] <= price['High']:
                    # Fill all limit orders of which price is between low and high of the last record
                    o['status'] = "filled"

        # Update current time
        self.__current_time = int(next_time.timestamp() * 1000)

    # Return limited history before current time with duplicated latest time
    # Real bot will return limited history before and including current time
    # TODO symbol and timeframe
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> dict:
        # Load history
        h, i = self.__load_history(symbol, timeframe)

        # From dataframe to list
        h = h.iloc[i - limit: i].values.tolist()

        # Duplicate last record (due to the unfinished k-line data in real)
        h.append(h[-1])
        h = h[1:]

        # Integer timestamp
        for r in h:
            r[0] = int(r[0])
        return h

    def get_ticker(self, symbol: str) -> dict:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)
        return dict(
            symbol=symbol,
            last=h.iloc[i]['Open'],
            timestamp=self.__current_time
        )

    def buy_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'buy', amount, price, self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def buy_market(self, symbol: str, amount: float) -> Order:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)

        # Assume market price is close to the open price of the next record
        # TODO Check whether balance is enough to buy
        o = Order(self.__order_id, symbol, 'market', 'buy', amount, h.iloc[i]['Open'],
                  self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'sell', amount, price, self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def sell_market(self, symbol: str, amount: float) -> Order:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)
        # TODO Check whether amount is enough to sell
        o = Order(self.__order_id, symbol, 'market', 'sell', amount, h.iloc[i]['Open'],
                  self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def get_order(self, o_id: int, symbol: str) -> dict:
        order = None
        for o in self.__order_history:
            if o['id'] == o_id:
                order = o
                break
        return order

    def cancel_order(self, o_id: int, symbol: str):
        for o in self.__order_history:
            if o['id'] == o_id:
                o['status'] = "cancel"
                break

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        canceled_ids = []
        for o in self.__order_history:
            if o['status'] == "unfilled":
                o['status'] = "cancel"
                canceled_ids.append(o['id'])
        return canceled_ids

    def output_order_history(self, status=None):
        logging.info('Order history')
        if status is None:
            for o in self.__order_history:
                logging.info(o)
        elif status == "filled":
            for o in self.__order_history:
                if o['status'] == "filled":
                    logging.info(str(datetime.fromtimestamp(o['timestamp'] / 1000)) + ' ' + o['side'] + ' (' + str(
                        o['amount']) + ') at (' + str(o['price']) + ')')

    def output_performance(self):
        perf = get_performance(self.__order_history)
        perf = json.dumps(perf.__dict__)
        logging.info(perf)

    # Return <History, Index of the current time>
    def __load_history(self, symbol: str, timeframe: str):
        key = symbol + timeframe
        if key not in self.__history.keys():
            self.__history[key] = pd.read_csv(f'{self.__data_dir}{symbol.replace("/", "")}_{timeframe}.csv')

        h = self.__history[key]
        assert len(h) > 0, 'Lack backtesting data.'

        i = h.index[h['Timestamp'] == self.__current_time].tolist()
        assert len(i) == 1, 'Backtesting data corrupted.'
        return h, i[0]
