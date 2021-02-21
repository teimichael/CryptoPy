import json
import logging

import ccxt
from tenacity import *

from core import order_manager as om
from core.model import Order
from core.performance import get_performance


# Real-time Emulator
class EmulateBot(object):

    def __init__(self, config):
        if config["exchange_market"] == "okex":
            logging.info("Creating OKEx emulate bot...")

            self.exchange = ccxt.okex({
                'apiKey': config["api_access"]["api_key"],
                'secret': config["api_access"]["secret"],
                'password': config["api_access"]["password"],
                'enableRateLimit': True,
                'options': {
                    'defaultType': config["exchange_type"],
                },
            })
        else:
            logging.info("Creating Binance emulate bot...")

            self.exchange = ccxt.binance({
                'apiKey': config["api_access"]["api_key"],
                'secret': config["api_access"]["secret"],
                'enableRateLimit': True,
                'options': {
                    'defaultType': config["exchange_type"],
                },
            })

        # Load markets
        markets = self.exchange.load_markets()

        # Track complete order history
        self.__order_history = []

        # Order ID Issuer
        self.__order_id = 0

        # Create info file
        with open('info.json', 'w') as outfile:
            info = {}
            json.dump(info, outfile)

        # Create order record file
        with open('orders.json', 'w') as outfile:
            order = {}
            json.dump(order, outfile)

        logging.info("Emulate bot created.")

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> dict:
        rec = self.__fetch_ohlcv(symbol, timeframe, limit)
        return rec

    # TODO No use
    def get_ohlcv_range(self, symbol: str, timeframe: str, start: int, end: int) -> dict:
        return self.exchange.fetch_ohlcv(symbol, timeframe, params={'startTime': start, 'endTime': end})

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_balance(self) -> dict:
        balance = self.exchange.fetch_balance()
        return balance['info'] if balance is not None else None

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_positions(self) -> list:
        balance = self.exchange.fetch_balance()
        return balance['info']['positions'] if balance is not None else None

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_ticker(self, symbol: str) -> dict:
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_order(self, o_id: int, symbol: str) -> dict:
        o = self.exchange.fetch_order(id=o_id, symbol=symbol)
        return o

    # TODO still needs test
    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_orders(self, symbol: str, limit: int = None) -> dict:
        orders = self.exchange.fetch_orders(symbol=symbol)
        return orders

    def buy_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'buy', amount, price)
        self.__order_history.append(o)
        self.__order_id += 1
        logging.info('buy (' + str(amount) + ') at (' + str(price) + ')')
        return o

    def buy_market(self, symbol: str, amount: float) -> Order:
        ticker = self.exchange.fetch_ticker(symbol)
        o = Order(self.__order_id, symbol, 'market', 'buy', amount, ticker['last'])
        self.__order_history.append(o)
        self.__order_id += 1
        logging.info('buy (' + str(amount) + ') at (' + str(ticker['last']) + ')')
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'sell', amount, price)
        self.__order_history.append(o)
        self.__order_id += 1
        logging.info('sell (' + str(amount) + ') at (' + str(price) + ')')
        return o

    def sell_market(self, symbol: str, amount: float) -> Order:
        ticker = self.exchange.fetch_ticker(symbol)
        o = Order(self.__order_id, symbol, 'market', 'sell', amount, ticker['last'])
        self.__order_history.append(o)
        self.__order_id += 1
        logging.info('sell (' + str(amount) + ') at (' + str(ticker['last']) + ')')
        return o

    def get_open_orders(self, symbol: str, limit: int = None):
        orders = self.__fetch_open_orders(symbol, limit)
        return orders

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        open_orders = self.get_open_orders(symbol, limit)
        if open_orders is None or len(open_orders) == 0:
            return
        # Do nothing in emulation
        return

    def output_performance(self):
        perf = get_performance(self.__order_history)
        perf = json.dumps(perf.__dict__)
        logging.info(perf)

    def output_balance(self):
        balance = self.get_balance()
        if balance is not None:
            with open('info.json') as info_file:
                info = json.load(info_file)
                info['balance'] = {
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
                with open('info.json', 'w') as outfile:
                    json.dump(info, outfile)
        else:
            logging.info('Cannot fetch balance due to exceptions.')

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def __fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = None):
        if limit is None:
            return self.exchange.fetch_ohlcv(symbol, timeframe)
        else:
            return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def __fetch_open_orders(self, symbol: str, limit: int = None):
        if self.exchange.has['fetchOpenOrders']:
            if limit is None:
                return self.exchange.fetchOpenOrders(symbol=symbol)
            else:
                return self.exchange.fetchOpenOrders(symbol=symbol, limit=limit)

    @staticmethod
    def create_order_record(name: str, order):
        om.create(name, order)

    @staticmethod
    def get_order_record_length(name: str):
        return om.get_length(name)

    @staticmethod
    def clear_order_record(name: str):
        om.clear(name)
