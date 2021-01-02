import logging
from datetime import datetime

from core import trade_lib as tl
from strategy.Indicator import Indicator


# Vegas Tunnel Strategy
class VegasTunnel(object):
    # Pair
    __symbol = 'BTC/USDT'

    # Time frame
    __time_frame = '1h'

    # Max order
    __max_order = 10

    # Amount per order
    __amount = 0.001

    # Record limit per fetch (Binance max: 1500)
    __record_limit = 1000

    # Indicator length limit (Reserve last __indicator_limit elements)
    __indicator_length_limit = 10

    def __init__(self, bot):
        self.__bot = bot

    __long_term_1_order = []
    __long_term_2_order = []
    __mid_term_1_order = []
    __short_term_1_order = []

    # Long-term 1
    def __long_term_1(self, i: Indicator):
        if self.__crossed_below(i.ema144, i.ema36) and i.macd_dif > 0:
            # TODO make a suitable order
            logging.info("Open long-term long strategy 1.")
            order = self.__bot.buy_market(self.__symbol, self.__amount)
            self.__long_term_1_order.append(order)
        elif len(self.__long_term_1_order) > 0:
            if self.__crossed_below(i.ema144, i.ema576):
                logging.info("Close long-term long strategy 1.")

                # TODO make a suitable order
                for o in self.__long_term_1_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__long_term_1_order = []

    # Long-term 2
    def __long_term_2(self, i: Indicator):
        if self.__crossed_below(i.low, i.ema576) and i.macd_dif > 0 and i.ema169[-1] > i.ema576[-1]:
            # TODO make a suitable order
            logging.info("Open long-term long strategy 2.")
            order = self.__bot.buy_market(self.__symbol, self.__amount)
            self.__long_term_2_order.append(order)
        elif len(self.__long_term_2_order) > 0:
            if i.macd_dif < 0 or i.ema169[-1] < i.ema676[-1]:
                logging.info("Close long-term long strategy 2.")
                # TODO make a suitable order
                for o in self.__long_term_2_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__long_term_2_order = []
            elif self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Close long-term long strategy 2.")

                # TODO make a suitable order
                for o in self.__long_term_2_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__long_term_2_order = []

    # Mid-term 1
    def __mid_term_1(self, i: Indicator):
        if self.__crossed_above(i.low, i.ema144) and i.macd_dif > 0 and i.ema144[-1] > i.ema676[-1]:
            # TODO make a suitable order
            logging.info("Open mid-term long strategy 1.")
            order = self.__bot.buy_market(self.__symbol, self.__amount)
            self.__mid_term_1_order.append(order)
        elif len(self.__mid_term_1_order) > 0:
            if i.macd_dif < 0 or i.ema144[-1] < i.ema676[-1]:
                logging.info("Close mid-term long strategy 1.")
                # TODO make a suitable order
                for o in self.__mid_term_1_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__mid_term_1_order = []
            elif self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Close mid-term long strategy 1.")

                # TODO make a suitable order
                for o in self.__mid_term_1_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__mid_term_1_order = []

    # Short-term 1
    def __short_term_1(self, i: Indicator):
        if self.__crossed_below(i.low, i.ema36) and i.macd_dif > 0 and i.ema36[-1] > i.ema169[-1]:
            # TODO make a suitable order
            logging.info("Open short-term long strategy 1.")
            order = self.__bot.buy_market(self.__symbol, self.__amount)
            self.__short_term_1_order.append(order)
        elif len(self.__short_term_1_order) > 0:
            if i.macd_dif < 0 or i.ema36[-1] < i.ema169[-1]:
                logging.info("Close short-term long strategy 1.")

                # TODO make a suitable order
                for o in self.__short_term_1_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__short_term_1_order = []
            elif self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Close short-term long strategy 1.")

                # TODO make a suitable order
                for o in self.__short_term_1_order:
                    order = self.__bot.sell_market(self.__symbol, self.__amount)
                self.__short_term_1_order = []

    def run(self, current_time: datetime = None):
        # TODO Check connection

        log_time = (str(current_time) + ' ') if not (current_time is None) else ''
        logging.info(log_time + "Executing Vegas Tunnel Strategy.")

        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # TODO Ensure the latest record (rec[-1]) is after the exact time point to execute the strategy

        # Calculate indicators
        indicator = Indicator(rec, self.__indicator_length_limit)

        # Long-term long strategy 1
        self.__long_term_1(indicator)

        # Long-term long strategy 2
        self.__long_term_2(indicator)

        # Mid-term long strategy 1
        self.__mid_term_1(indicator)

        # Short-term long strategy 1
        self.__short_term_1(indicator)

    @staticmethod
    def __crossed_above(s1, s2) -> bool:
        r = tl.crossed_above(s1, s2)
        return r.iloc[-1]

    @staticmethod
    def __crossed_below(s1, s2) -> bool:
        r = tl.crossed_below(s1, s2)
        return r.iloc[-1]