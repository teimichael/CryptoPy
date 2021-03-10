import logging
from datetime import datetime

from core import trade_lib as tl
from strategy.example.indicator.VTCompLongIndicator import Indicator, IndicatorCheck


# Vegas Tunnel Compound Strategy (long)
class VTCompLong(object):
    # Pair
    __symbol = 'BTC/USDT'

    # Time frame
    __time_frame = '15m'

    # Dynamic settings
    __setting = {
        'amount': 0.01,
        'long_weight': 1.5,
        'max_open_order': 10
    }

    # Amount per order (BTC)
    __amount = __setting['amount']

    # Long-term weight
    __long_weight = __setting['long_weight']

    # Record limit per fetch (Binance max: 1500)
    __record_limit = 1000

    # Indicator length limit (Reserve last __indicator_limit elements)
    __indicator_length_limit = 10

    # Max number of open orders (included)
    __max_open_order = __setting['max_open_order']

    # Current number of open orders
    __current_open_order = 0

    def __init__(self, bot):
        self.__bot = bot
        # Create strategy setting
        bot.create_setting(self.__setting)

    __LONG_TERM_1 = "long_term_1_order"
    __LONG_TERM_2 = "long_term_2_order"
    __MID_TERM_1 = "mid_term_1_order"
    __SHORT_TERM_1 = "short_term_1_order"

    # Long-term 1
    def __long_term_1(self, i: Indicator, setting, orders):
        if self.__crossed_below(i.ema144, i.ema36) and i.macd_dif > 0:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open long-term long strategy 1: reached max number of open orders.")
                return

            logging.info("Open long-term long strategy 1.")
            order = self.__buy(setting['amount'] * setting['long_weight'])
            if order is not None:
                self.__create_order_record(self.__LONG_TERM_1, order)
        elif len(orders) > 0:
            if self.__crossed_below(i.ema144, i.ema576):
                logging.info("Close long-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__LONG_TERM_1)

    # Long-term 2
    def __long_term_2(self, i: Indicator, setting, orders):
        if self.__crossed_below(i.low, i.ema576) and i.macd_dif > 0 and i.ema169[-1] > i.ema576[-1]:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open long-term long strategy 2: reached max number of open orders.")
                return

            logging.info("Open long-term long strategy 2.")
            order = self.__buy(setting['amount'] * setting['long_weight'])
            if order is not None:
                self.__create_order_record(self.__LONG_TERM_2, order)
        elif len(orders) > 0:
            if i.macd_dif < 0 or i.ema169[-1] < i.ema676[-1]:
                logging.info("Close long-term long strategy 2.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__LONG_TERM_2)
            elif self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Close long-term long strategy 2.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__LONG_TERM_2)

    # Mid-term 1
    def __mid_term_1(self, i: Indicator, setting, orders):
        if self.__crossed_above(i.low, i.ema144) and i.macd_dif > 0 and i.ema144[-1] > i.ema676[-1]:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open mid-term long strategy 1: reached max number of open orders.")
                return

            logging.info("Open mid-term long strategy 1.")
            order = self.__buy(setting['amount'])
            if order is not None:
                self.__create_order_record(self.__MID_TERM_1, order)
        elif len(orders) > 0:
            if i.macd_dif < 0 or i.ema144[-1] < i.ema676[-1]:
                logging.info("Close mid-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__MID_TERM_1)

    # Short-term 1
    def __short_term_1(self, i: Indicator, setting, orders):
        if self.__crossed_below(i.low, i.ema36) and i.macd_dif > 0 and i.ema36[-1] > i.ema169[-1]:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open short-term long strategy 1: reached max number of open orders.")
                return

            # Limit max number of short-term open orders to avoid short-term fluctuation
            if len(orders) >= 5:
                logging.info("Cannot open short-term long strategy 1: reached max number of short-term open orders.")
                return

            logging.info("Open short-term long strategy 1.")
            order = self.__buy(setting['amount'])
            if order is not None:
                self.__create_order_record(self.__SHORT_TERM_1, order)
        elif len(orders) > 0:
            if i.macd_dif < 0 or i.ema36[-1] < i.ema169[-1]:
                logging.info("Close short-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__SHORT_TERM_1)
            elif self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Close short-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__SHORT_TERM_1)

    # Execute strategy
    def run(self, current_time: datetime = None):
        # TODO Check connection

        log_time = (str(current_time) + ' ') if not (current_time is None) else ''
        logging.info(log_time + "Executing Vegas Tunnel Compound Long Strategy.")

        # Cancel unfilled orders
        self.__bot.cancel_unfilled_orders(self.__symbol, self.__max_open_order)

        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # Suspend running if the number of records is below the requirement
        if len(rec) < self.__record_limit:
            logging.info("Suspending.")
            return

        # Load settings
        setting = self.__bot.get_setting()

        # Load current open orders
        long_term_1_orders = self.__get_orders(self.__LONG_TERM_1)
        long_term_2_orders = self.__get_orders(self.__LONG_TERM_2)
        mid_term_1_orders = self.__get_orders(self.__MID_TERM_1)
        short_term_1_orders = self.__get_orders(self.__SHORT_TERM_1)
        self.__current_open_order = len(long_term_1_orders) + len(long_term_2_orders) + len(mid_term_1_orders) + len(
            short_term_1_orders)

        # Calculate indicators
        indicator = Indicator(rec, self.__indicator_length_limit)

        # Long-term long strategy 1
        self.__long_term_1(indicator, setting, long_term_1_orders)

        # Long-term long strategy 2
        self.__long_term_2(indicator, setting, long_term_2_orders)

        # Mid-term long strategy 1
        self.__mid_term_1(indicator, setting, mid_term_1_orders)

        # Short-term long strategy 1
        self.__short_term_1(indicator, setting, short_term_1_orders)

    # Strategy trigger (running in a high frequency)
    def run_trigger(self):
        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # Suspend running if the number of records is below the requirement
        if len(rec) < self.__record_limit:
            logging.info("Suspending.")
            return

            # Calculate indicators
        i = IndicatorCheck(rec, self.__indicator_length_limit)

        # Long-term 1 trigger (close)
        orders = self.__get_orders(self.__LONG_TERM_1)
        if len(orders) > 0:
            if self.__crossed_below(i.ema144, i.ema576):
                logging.info("Trigger: Close long-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__LONG_TERM_1)

        # Long-term 2 trigger (close)
        orders = self.__get_orders(self.__LONG_TERM_2)
        if len(orders) > 0:
            if self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Trigger: Close long-term long strategy 2.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__LONG_TERM_2)

        # Short-term trigger (close)
        orders = self.__get_orders(self.__SHORT_TERM_1)
        if len(orders) > 0:
            if self.__crossed_below(i.close, i.bbUpper * 0.999):
                logging.info("Trigger: Close short-term long strategy 1.")

                for o in orders:
                    order = self.__sell(o['amount'])
                self.__clear_order_record(self.__SHORT_TERM_1)

    # Buy order
    # TODO make a suitable order
    def __buy(self, amount: float = __amount):
        order = self.__bot.buy_market(self.__symbol, amount)
        return order

    # Sell order
    # TODO make a suitable order
    def __sell(self, amount: float = __amount):
        order = self.__bot.sell_market(self.__symbol, amount)
        return order

    # Reached max number of open orders
    def __reached_max_open_order(self):
        return self.__current_open_order >= self.__max_open_order

    def __create_order_record(self, name: str, order):
        self.__bot.create_order_record(name, order)

    def __get_orders(self, name: str):
        return self.__bot.get_orders(name)

    def __clear_order_record(self, name: str):
        self.__bot.clear_order_record(name)

    @staticmethod
    def __crossed_above(s1, s2) -> bool:
        r = tl.crossed_above(s1, s2)
        return r.iloc[-1]

    @staticmethod
    def __crossed_below(s1, s2) -> bool:
        r = tl.crossed_below(s1, s2)
        return r.iloc[-1]
