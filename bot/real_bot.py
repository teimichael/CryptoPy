import json
import logging

import ccxt
from tenacity import *


# Real-Trading Bot
class RealBot(object):

    def __init__(self, config):
        logging.info("Creating REAL bot...")

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

        logging.info("REAL Bot created.")

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

    def buy_limit(self, symbol: str, amount: float, price: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price)
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price)
        logging.info(json.dumps(o))
        return o

    def buy_market(self, symbol: str, amount: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'market', 'buy', amount)
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'market', 'buy', amount)
        logging.info(json.dumps(o))
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price)
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price)
        logging.info(json.dumps(o))
        return o

    def sell_market(self, symbol: str, amount: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'market', 'sell', amount)
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'market', 'sell', amount)
        logging.info(json.dumps(o))
        return o

    def buy_stop_loss(self, symbol: str, amount: float, price: float):
        stop_loss_params = {'stopPrice': price}
        return self.exchange.create_order(symbol, 'stop_market', 'buy', amount, None, stop_loss_params)

    def sell_stop_loss(self, symbol: str, amount: float, price: float):
        stop_loss_params = {'stopPrice': price}
        return self.exchange.create_order(symbol, 'stop_market', 'sell', amount, None, stop_loss_params)

    def buy_take_profit(self, symbol: str, amount: float, price: float):
        take_profit_params = {'stopPrice': price}
        return self.exchange.create_order(symbol, 'take_profit_market', 'buy', amount, None, take_profit_params)

    def sell_take_profit(self, symbol: str, amount: float, price: float):
        take_profit_params = {'stopPrice': price}
        return self.exchange.create_order(symbol, 'take_profit_market', 'sell', amount, None, take_profit_params)

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def get_open_orders(self, symbol: str, limit: int = None):
        orders = self.__fetch_open_orders(symbol, limit)
        return orders

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        open_orders = self.get_open_orders(symbol, limit)
        if open_orders is None or len(open_orders) == 0:
            return
        for o in open_orders:
            try:
                self.exchange.cancel_order(o['id'], symbol)
            except ccxt.NetworkError as e:
                logging.info('Network error: ', str(e))
                self.exchange.cancel_order(o['id'], symbol)
            logging.info('Canceled unfilled order ' + o['id'])

    def output_balance(self):
        balance = self.get_balance()
        if balance is not None:
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
            logging.info(json.dumps(b))
        else:
            logging.info('Cannot fetch balance due to exceptions.')

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def __fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = None):
        if limit is None:
            return self.exchange.fetch_ohlcv(symbol, timeframe)
        else:
            return self.exchange.fetch_ohlcv(symbol, timeframe, params={'limit': limit})

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def __fetch_open_orders(self, symbol: str, limit: int = None):
        if self.exchange.has['fetchOpenOrders']:
            if limit is None:
                return self.exchange.fetchOpenOrders(symbol=symbol)
            else:
                return self.exchange.fetchOpenOrders(symbol=symbol, limit=limit)
