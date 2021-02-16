import logging
from datetime import datetime

from core import trade_lib as tl

from strategy.indicator.BBCompIndicator import Indicator


# Bollinger Bands Compound strategy (Long-term Best: 15m)
class BollingerBands(object):
    # Pair
    __symbol = 'BTC/USDT'

    # Time frame
    __time_frame = '5m'

    # Amount per order
    __amount = 0.01

    # Record limit per fetch (Binance max: 1500)
    __record_limit = 1000

    # Indicator length limit (Reserve last __indicator_limit elements)
    __indicator_length_limit = 500

    # Max number of open orders (included)
    __max_open_order = 1

    # Slippage rate allowed while buying
    __slippage_buy = 1 + 0.00008

    def __init__(self, bot):
        self.__bot = bot

    def __long(self, i: Indicator):
        if len(self.__long_order) < self.__max_open_order:
            if self.__crossed_above(i.fastMA, i.bbBasis) and i.close[-1] > i.bbBasis[-1] and abs(i.osc) == 1:
                # Break up
                logging.info("Open long.")
                order = self.__buy()
                if order is not None:
                    self.__long_order.append(order)
        elif len(self.__long_order) > 0:
            if self.__crossed_below(i.fastMA, i.bbBasis) and i.close[-1] < i.bbBasis[-1] and abs(i.osc) == 2:
                # Break down
                logging.info("Close long.")
                order = self.__bot.sell_market(self.__symbol, self.__amount)
                if order is not None:
                    self.__long_order = []
                else:
                    logging.error("Failed to close order.")

    __long_order = []

    # Execute strategy
    def run(self, current_time: datetime = None):
        # TODO Check connection

        log_time = (str(current_time) + ' ') if not (current_time is None) else ''
        logging.info(log_time + "Executing BB Compound Strategy.")

        # Cancel unfilled orders
        self.__bot.cancel_unfilled_orders(self.__symbol, self.__max_open_order)

        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # Suspend running if the number of records is below the requirement
        if len(rec) < self.__record_limit:
            logging.info("Suspending.")
            return

        # Calculate indicators
        indicator = Indicator(rec, self.__indicator_length_limit)

        # Run long strategy
        self.__long(indicator)

    def __buy(self, weight: float = 1):
        ticker = self.__bot.get_ticker(self.__symbol)
        if ticker is None:
            order = self.__bot.buy_market(self.__symbol, self.__amount * weight)
        else:
            order = self.__bot.buy_limit(self.__symbol, self.__amount * weight, ticker['last'] * self.__slippage_buy)
        return order

    @staticmethod
    def __crossed_above(s1, s2) -> bool:
        r = tl.crossed_above(s1, s2)
        return r.iloc[-1]

    @staticmethod
    def __crossed_below(s1, s2) -> bool:
        r = tl.crossed_below(s1, s2)
        return r.iloc[-1]
