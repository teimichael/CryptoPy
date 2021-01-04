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

        # Load markets
        markets = self.exchange.load_markets()

        self.__order_history = []
        logging.info("Emulate bot created.")

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> dict:
        if limit is None:
            return self.exchange.fetch_ohlcv(symbol, timeframe)
        else:
            return self.exchange.fetch_ohlcv(symbol, timeframe, params={'limit': limit})

    def get_ohlcv_range(self, symbol: str, timeframe: str, start: int, end: int) -> dict:
        return self.exchange.fetch_ohlcv(symbol, timeframe, params={'startTime': start, 'endTime': end})

    def get_balance(self) -> dict:
        return self.exchange.fetch_balance()['info']

    def get_positions(self) -> list:
        balance = self.exchange.fetch_balance()
        return balance['info']['positions']

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

    def cancel_open_orders(self, symbol: str):
        # Do nothing in emulation
        return

    def output_performance(self):
        perf = get_performance(self.__order_history)
        perf = json.dumps(perf.__dict__)
        logging.info(perf)

    def output_balance(self):
        balance = self.get_balance()
        b = {
            'totalWalletBalance': balance['totalWalletBalance'],
            'totalUnrealizedProfit': balance['totalUnrealizedProfit'],
            'totalMarginBalance': balance['totalMarginBalance'],
            'totalInitialMargin': balance['totalInitialMargin'],
            'totalMaintMargin': balance['totalMaintMargin'],
            'totalPositionInitialMargin': balance['totalPositionInitialMargin'],
            'totalOpenOrderInitialMargin': balance['totalOpenOrderInitialMargin'],
            'totalCrossWalletBalance': balance['totalCrossWalletBalance'],
            'totalCrossUnPnl': balance['totalCrossUnPnl'],
            'availableBalance': balance['availableBalance']
        }
        b = json.dumps(b)
        logging.info(b)
