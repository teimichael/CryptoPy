import json
import logging
import os

import ccxt
from tenacity import *

from core.order_manager import OrderManager


# Real-Trading Bot
class RealBot(object):

    def __init__(self, config):
        if config["exchange_market"] == "okex":
            logging.info("Creating OKEx REAL bot...")

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
            logging.info("Creating Binance REAL bot...")

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

        # Create runtime directory
        if not os.path.isdir(config['runtime_dir']):
            os.mkdir(config['runtime_dir'])

        # Runtime information path
        self.__info_path = f'{config["runtime_dir"]}info.json'

        # Runtime open order path
        self.__orders_path = f'{config["runtime_dir"]}orders.json'

        # Runtime setting path
        self.__setting_path = f'{config["runtime_dir"]}setting.json'

        if not os.path.exists(self.__info_path):
            # Create info file
            with open(self.__info_path, 'w') as outfile:
                info = {}
                json.dump(info, outfile)

        if not os.path.exists(self.__orders_path):
            # Create order record file
            with open(self.__orders_path, 'w') as outfile:
                order = {}
                json.dump(order, outfile)

        # Order manager
        self.om = OrderManager(self.__orders_path)

        logging.info("REAL Bot created.")

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None, duplicate=None) -> dict:
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
    def get_order_book(self, symbol: str, limit: int = None):
        if limit is None:
            return self.exchange.fetch_order_book(symbol=symbol)
        else:
            return self.exchange.fetch_order_book(symbol=symbol, limit=limit)

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

    # Buy (Good till crossing / Post only)
    def buy_gtx(self, symbol: str, amount: float, price: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price, params={'timeInForce': 'GTX'})
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price, params={'timeInForce': 'GTX'})
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

    # Sell (Good till crossing / Post only)
    def sell_gtx(self, symbol: str, amount: float, price: float) -> dict:
        try:
            o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price, params={'timeInForce': 'GTX'})
        except ccxt.NetworkError as e:
            logging.info('Network error: ', str(e))
            o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price, params={'timeInForce': 'GTX'})
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
    def get_order(self, o_id, symbol: str) -> dict:
        o = self.exchange.fetch_order(id=o_id, symbol=symbol)
        return o

    # TODO still needs test
    # @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
    #        after=after_log(logging.getLogger(__name__), logging.ERROR))
    # def get_orders(self, symbol: str, limit: int = None) -> dict:
    #     orders = self.exchange.fetch_orders(symbol=symbol)
    #     return orders

    def get_open_orders(self, symbol: str, limit: int = None):
        orders = self.__fetch_open_orders(symbol, limit)
        return orders

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2),
           after=after_log(logging.getLogger(__name__), logging.ERROR))
    def cancel_order(self, o_id, symbol):
        self.exchange.cancel_order(o_id, symbol)

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        canceled_ids = []
        open_orders = self.get_open_orders(symbol, limit)
        if open_orders is None or len(open_orders) == 0:
            return canceled_ids
        for o in open_orders:
            self.cancel_order(o['id'], symbol)
            logging.info('Canceled unfilled order ' + o['id'])
            canceled_ids.append(o['id'])
        return canceled_ids

    def output_balance(self):
        balance = self.get_balance()
        if balance is not None:
            with open(self.__info_path) as info_file:
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
                with open(self.__info_path, 'w') as outfile:
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

    def create_order_record(self, name: str, order):
        self.om.create(name, order)

    def get_order_record_length(self, name: str):
        return self.om.get_length(name)

    def get_orders(self, name: str):
        return self.om.get_orders(name)

    def get_all_orders(self):
        return self.om.get_all()

    def replace_order(self, name: str, o_id, new_order):
        self.om.replace(name, o_id, new_order)

    def clear_order_record(self, name: str):
        self.om.clear(name)

    def create_setting(self, setting):
        if not os.path.exists(self.__setting_path):
            # Create setting file
            with open(self.__setting_path, 'w') as outfile:
                json.dump(setting, outfile)

    def get_setting(self):
        with open(self.__setting_path) as setting_file:
            setting = json.load(setting_file)
        return setting
