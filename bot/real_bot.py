import json
import logging

import ccxt


# Real-Trading Bot
class RealBot(object):

    def __init__(self, config):
        logging.info("Creating REAL bot...")

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

        logging.info("REAL Bot created.")

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

    def get_ticker(self, symbol: str) -> dict:
        return self.exchange.fetch_ticker(symbol)

    def buy_limit(self, symbol: str, amount: float, price: float) -> dict:
        o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price)
        logging.info(json.dumps(o))
        return o

    def buy_market(self, symbol: str, amount: float) -> dict:
        o = self.exchange.create_order(symbol, 'market', 'buy', amount)
        logging.info(json.dumps(o))
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> dict:
        o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price)
        logging.info(json.dumps(o))
        return o

    def sell_market(self, symbol: str, amount: float) -> dict:
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

    def get_open_orders(self, symbol: str):
        if self.exchange.has['fetchOpenOrders']:
            return self.exchange.fetchOpenOrders(symbol)
        else:
            return None

    def cancel_open_orders(self, symbol: str):
        open_orders = self.get_open_orders(symbol)
        if open_orders is None:
            return
        for o in open_orders:
            self.exchange.cancel_order(o['id'], symbol)
            logging.info('Canceled unfilled order ' + o['id'])

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
        logging.info(json.dumps(b))
