import json
import logging
from datetime import datetime

from core.model import Order
from core.performance import get_performance
from core.util import str_to_timestamp


# Backtesting Bot
# TODO considering balance
class BackTestBot(object):
    def __init__(self, history, balance: float = 1.0,
                 max_leverage: float = 100, trade_leverage: float = 1, taker_fee: float = 0.04,
                 maker_fee: float = 0.02):
        # Historical records
        self.__history = history

        # Record current time
        self.__current_time = str_to_timestamp('2019-09-10 00:00:00')

        # Current balance
        self.__balance = balance

        # Fee
        self.__taker_rate = taker_fee
        self.__maker_rate = maker_fee

        # Trade leverage
        self.__max_leverage = max_leverage
        self.__trade_leverage = trade_leverage

        # Order history
        self.__order_history = []

    def set_current_time(self, current_time: datetime):
        self.__current_time = int(current_time.timestamp() * 1000)

    # Return limited history before current time with duplicated latest time
    # Real bot will return limited history before and including current time
    # TODO symbol and timeframe
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> dict:
        h = self.__history
        i = h.index[h['Timestamp'] == self.__current_time].tolist()
        assert len(i) == 1, 'Lack backtesting data.'
        # From dataframe to list
        h = h.iloc[i[0] - limit: i[0]].values.tolist()

        # Duplicate last record
        h.append(h[-1])
        h = h[1:]

        # Integer timestamp
        for r in h:
            r[0] = int(r[0])
        return h

    def get_ticker(self, symbol: str) -> dict:
        i = self.__history.index[self.__history['Timestamp'] == self.__current_time].tolist()
        assert len(i) == 1
        return dict(
            symbol=symbol,
            last=self.__history.iloc[i[0]]['Open'],
            timestamp=self.__current_time
        )

    def buy_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(symbol, 'limit', 'buy', amount, price, self.__current_time)
        self.__order_history.append(o)
        return o

    def buy_market(self, symbol: str, amount: float) -> Order:
        i = self.__history.index[self.__history['Timestamp'] == self.__current_time].tolist()
        assert len(i) == 1

        # Assume market price is close to the open price of the next record
        # TODO Check whether balance is enough to buy
        o = Order(symbol, 'market', 'buy', amount, self.__history.iloc[i[0]]['Open'], self.__current_time)
        self.__order_history.append(o)
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(symbol, 'limit', 'sell', amount, price, self.__current_time)
        self.__order_history.append(o)
        return o

    def sell_market(self, symbol: str, amount: float) -> Order:
        i = self.__history.index[self.__history['Timestamp'] == self.__current_time].tolist()
        assert len(i) == 1
        # TODO Check whether amount is enough to sell
        o = Order(symbol, 'market', 'sell', amount, self.__history.iloc[i[0]]['Open'], self.__current_time)
        self.__order_history.append(o)
        return o

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        # Do nothing in backtesting
        return

    def output_order_history(self):
        logging.info('Order history')
        for o in self.__order_history:
            logging.info(
                str(datetime.fromtimestamp(o['timestamp'] / 1000)) + ' ' + o['side'] + ' (' + str(
                    o['amount']) + ') at (' + str(o['price']) + ')')

    def output_performance(self):
        perf = get_performance(self.__order_history)
        perf = json.dumps(perf.__dict__)
        logging.info(perf)
