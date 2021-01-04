import logging

import ccxt


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
        logging.info("REAL Bot created.")

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = None) -> dict:
        if limit is None:
            return self.exchange.fetch_ohlcv(symbol, timeframe)
        else:
            return self.exchange.fetch_ohlcv(symbol, timeframe, params={'limit': limit})

    def get_ohlcv_range(self, symbol: str, timeframe: str, start: int, end: int) -> dict:
        return self.exchange.fetch_ohlcv(symbol, timeframe, params={'startTime': start, 'endTime': end})

    def get_ticker(self, symbol: str) -> dict:
        return self.exchange.fetch_ticker(symbol)

    def buy_limit(self, symbol: str, amount: float, price: float) -> dict:
        o = self.exchange.create_order(symbol, 'limit', 'buy', amount, price)
        logging.info(o)
        return o

    def buy_market(self, symbol: str, amount: float) -> dict:
        o = self.exchange.create_order(symbol, 'market', 'buy', amount)
        logging.info(o)
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> dict:
        o = self.exchange.create_order(symbol, 'limit', 'sell', amount, price)
        logging.info(o)
        return o

    def sell_market(self, symbol: str, amount: float) -> dict:
        o = self.exchange.create_order(symbol, 'market', 'sell', amount)
        logging.info(o)
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
