import logging
from datetime import datetime

from core import trade_lib as tl
from strategy.indicator.VTLClassicIndicator import Indicator


# Vegas Tunnel Classic Strategy
class VegasTunnel(object):
    # Pair
    __symbol = 'BTC/USDT'

    # Time frame
    __time_frame = '1h'

    # Amount per order (BTC)
    __amount = 0.001

    # Long-term weight
    __long_weight = 1.5

    # Record limit per fetch (Binance max: 1500)
    __record_limit = 1000

    # Indicator length limit (Reserve last __indicator_limit elements)
    __indicator_length_limit = 10

    # Max number of open orders (included)
    __max_open_order = 8

    # Slippage rate allowed while buying
    __slippage_buy = 1 + 0.00008

    def __init__(self, bot):
        self.__bot = bot

    __long_term_order = []
    __short_term_order = []

    # Long-term Strategy
    def __long_term(self, i: Indicator):
        if self.__crossed_above(i.close, i.ema144) and i.ema144[-1] > i.ema169[-1]:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open long-term long strategy: reached max number of open orders.")
                return

            logging.info("Open long-term long strategy.")
            order = self.__buy(self.__long_weight)
            if order is not None:
                self.__long_term_order.append(order)
        elif len(self.__long_term_order) > 0:
            if self.__crossed_below(i.close, i.ema144) and i.ema144[-1] < i.ema169[-1]:
                logging.info("Close long-term long strategy.")

                for o in self.__long_term_order:
                    order = self.__sell(self.__long_weight)
                self.__long_term_order = []

    # Short-term Strategy
    def __short_term(self, i: Indicator):
        if self.__crossed_above(i.close, i.ema21) and i.ema21[-1] > i.ema34[-1]:
            # Check whether reached max number of open orders to prevent overbuying
            if self.__reached_max_open_order():
                logging.info("Cannot open short-term long strategy: reached max number of open orders.")
                return

            # Limit max number of short-term open orders to avoid short-term fluctuation
            if len(self.__short_term_order) >= 5:
                logging.info("Cannot open short-term long strategy: reached max number of short-term open orders.")
                return

            logging.info("Open short-term long strategy.")
            order = self.__buy()
            if order is not None:
                self.__short_term_order.append(order)
        elif len(self.__short_term_order) > 0:
            if self.__crossed_below(i.close, i.ema21) and i.ema21[-1] < i.ema34[-1]:
                logging.info("Close short-term long strategy.")

                for o in self.__short_term_order:
                    order = self.__sell()
                self.__short_term_order = []

    # Execute strategy
    def run(self, current_time: datetime = None):
        # TODO Check connection

        log_time = (str(current_time) + ' ') if not (current_time is None) else ''
        logging.info(log_time + "Executing Vegas Tunnel Strategy.")

        # Cancel unfilled orders
        self.__bot.cancel_unfilled_orders(self.__symbol, self.__max_open_order)

        # Fetch records
        rec = self.__bot.get_ohlcv(self.__symbol, self.__time_frame, self.__record_limit)

        # TODO Ensure the latest record (rec[-1]) is after the exact time point to execute the strategy

        # Calculate indicators
        indicator = Indicator(rec, self.__indicator_length_limit)

        # Long-term long strategy
        self.__long_term(indicator)

        # Short-term long strategy
        self.__short_term(indicator)

    # Buy order
    # TODO make a suitable order
    def __buy(self, weight: float = 1):
        # ticker = self.__bot.get_ticker(self.__symbol)
        # if ticker is None:
        #     order = self.__bot.buy_market(self.__symbol, self.__amount * weight)
        # else:
        #     order = self.__bot.buy_limit(self.__symbol, self.__amount * weight, ticker['last'] * self.__slippage_buy)
        order = self.__bot.buy_market(self.__symbol, self.__amount * weight)
        return order

    # Sell order
    # TODO make a suitable order
    def __sell(self, weight: float = 1):
        order = self.__bot.sell_market(self.__symbol, self.__amount * weight)
        return order

    # Reached max number of open orders
    def __reached_max_open_order(self):
        return self.__count_current_open_orders() >= self.__max_open_order

    # Total number of current open orders
    def __count_current_open_orders(self):
        return len(self.__long_term_order) + len(self.__short_term_order)

    @staticmethod
    def __crossed_above(s1, s2) -> bool:
        r = tl.crossed_above(s1, s2)
        return r.iloc[-1]

    @staticmethod
    def __crossed_below(s1, s2) -> bool:
        r = tl.crossed_below(s1, s2)
        return r.iloc[-1]
