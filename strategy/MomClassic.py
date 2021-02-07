import logging
from datetime import datetime

from core import trade_lib as tl
from strategy.indicator.MomClassicIndicator import Indicator


# Momentum Classic Strategy
class MomClassic(object):
    # Pair
    __symbol = 'BTC/USDT'

    # Time frame
    __time_frame = '1m'

    # Amount per order (BTC)
    __amount = 0.01

    # Record limit per fetch (Binance max: 1500)
    __record_limit = 500

    # Indicator length limit (Reserve last __indicator_limit elements)
    __indicator_length_limit = 10

    def __init__(self, bot):
        self.__bot = bot

    __unfilled_long_order_id = []
    __unfilled_short_order_id = []

    __unfilled_close_long_order_id = []
    __unfilled_close_short_order_id = []

    __long_order_id = []
    __short_order_id = []

    # Long Strategy
    def __long(self, i: Indicator):
        if i.mom0[-1] > 0 and i.mom1[-1] > 0:
            if len(self.__long_order_id) < 1 and len(self.__unfilled_long_order_id) < 1:
                logging.info("Open long strategy.")
                order = self.__buy(i.high[-1])
                if order is not None:
                    self.__unfilled_long_order_id.append(order['id'])

                if len(self.__short_order_id) > 0:
                    logging.info("Close short strategy.")
                    for o in self.__short_order_id:
                        order = self.__buy(i.high[-1])
                        if order is not None:
                            self.__unfilled_close_short_order_id.append(order['id'])
        else:
            for o_id in self.__unfilled_long_order_id:
                self.__bot.cancel_order(o_id, self.__symbol)
                self.__unfilled_long_order_id.remove(o_id)
            for o_id in self.__unfilled_close_short_order_id:
                self.__bot.cancel_order(o_id, self.__symbol)
                self.__unfilled_close_short_order_id.remove(o_id)

    # Short Strategy
    def __short(self, i: Indicator):
        if i.mom0[-1] < 0 and i.mom1[-1] < 0:
            if len(self.__short_order_id) < 1 and len(self.__unfilled_short_order_id) < 1:
                logging.info("Open short strategy.")
                order = self.__sell(i.low[-1])
                if order is not None:
                    self.__unfilled_short_order_id.append(order['id'])

                if len(self.__long_order_id) > 0:
                    logging.info("Close long strategy.")
                    for o in self.__long_order_id:
                        order = self.__sell(i.low[-1])
                        if order is not None:
                            self.__unfilled_close_long_order_id.append(order['id'])
        else:
            for o_id in self.__unfilled_short_order_id:
                self.__bot.cancel_order(o_id, self.__symbol)
                self.__unfilled_short_order_id.remove(o_id)
            for o_id in self.__unfilled_close_long_order_id:
                self.__bot.cancel_order(o_id, self.__symbol)
                self.__unfilled_close_long_order_id.remove(o_id)

    # Execute strategy
    def run(self, current_time: datetime = None):
        # TODO Check connection

        log_time = (str(current_time) + ' ') if not (current_time is None) else ''
        logging.info(log_time + "Executing Momentum Classic Strategy.")

        # Check whether orders are filled
        for o_id in self.__unfilled_long_order_id:
            o = self.__bot.get_order(o_id, self.__symbol)
            if o['status'] == "filled":
                self.__unfilled_long_order_id.remove(o['id'])
                self.__long_order_id.append(o['id'])

        for o_id in self.__unfilled_close_long_order_id:
            o = self.__bot.get_order(o_id, self.__symbol)
            if o['status'] == "filled":
                self.__unfilled_close_long_order_id.remove(o['id'])
                self.__long_order_id.pop()

        for o_id in self.__unfilled_short_order_id:
            o = self.__bot.get_order(o_id, self.__symbol)
            if o['status'] == "filled":
                self.__unfilled_short_order_id.remove(o['id'])
                self.__short_order_id.append(o['id'])

        for o_id in self.__unfilled_close_short_order_id:
            o = self.__bot.get_order(o_id, self.__symbol)
            if o['status'] == "filled":
                self.__unfilled_close_short_order_id.remove(o['id'])
                self.__short_order_id.pop()

        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # TODO Ensure the latest record (rec[-1]) is after the exact time point to execute the strategy

        # Calculate indicators
        indicator = Indicator(rec, self.__indicator_length_limit)

        # Long strategy
        self.__long(indicator)

        # Short strategy
        self.__short(indicator)

    # Buy order (stop price)
    # TODO make a suitable order
    def __buy(self, stop_price):
        order = self.__bot.buy_limit(self.__symbol, self.__amount, stop_price)
        return order

    # Sell order (stop price)
    # TODO make a suitable order
    def __sell(self, stop_price):
        order = self.__bot.sell_limit(self.__symbol, self.__amount, stop_price)
        return order

    @staticmethod
    def __crossed_above(s1, s2) -> bool:
        r = tl.crossed_above(s1, s2)
        return r.iloc[-1]

    @staticmethod
    def __crossed_below(s1, s2) -> bool:
        r = tl.crossed_below(s1, s2)
        return r.iloc[-1]
