import json
import logging

import ccxt

from core.model import Order
from core.performance import get_performance


# Real-time Emulator
class EmulateBot(object):

    def __init__(self, config):
        logging.info("Creating emulate bot...")

        self.exchange = ccxt.binance({
            'apiKey': config["api_access"]["api_key"],
            'secret': config["api_access"]["secret"],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            },
        })

        self.__order_history = []
        logging.info("Emulate bot created.")

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> dict:
        if limit is None:
            return self.exchange.fetch_ohlcv(symbol, timeframe)
        else:
            return self.exchange.fetch_ohlcv(symbol, timeframe, params={'limit': limit})

    def get_ohlcv_range(self, symbol: str, timeframe: str, start: int, end: int) -> dict:
        return self.exchange.fetch_ohlcv(symbol, timeframe, params={'startTime': start, 'endTime': end})

    def get_balance(self):
        return self.exchange.fetch_balance()

    def get_ticker(self, symbol: str):
        return self.exchange.fetch_ticker(symbol)

    def buy_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(symbol, 'limit', 'buy', amount, price)
        self.__order_history.append(o)
        logging.info('buy (' + str(amount) + ') at (' + str(price) + ')')
        return o

    def buy_market(self, symbol: str, amount: float) -> Order:
        ticker = self.exchange.fetch_ticker(symbol)
        o = Order(symbol, 'market', 'buy', amount, ticker['last'])
        self.__order_history.append(o)
        logging.info('buy (' + str(amount) + ') at (' + str(ticker['last']) + ')')
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(symbol, 'limit', 'sell', amount, price)
        self.__order_history.append(o)
        logging.info('sell (' + str(amount) + ') at (' + str(price) + ')')
        return o

    def sell_market(self, symbol: str, amount: float) -> Order:
        ticker = self.exchange.fetch_ticker(symbol)
        o = Order(symbol, 'market', 'sell', amount, ticker['last'])
        self.__order_history.append(o)
        logging.info('sell (' + str(amount) + ') at (' + str(ticker['last']) + ')')
        return o

    def output_performance(self):
        perf = get_performance(self.__order_history)
        perf = json.dumps(perf.__dict__)
        logging.info(perf)
