import json
import logging
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from core.model import Order
from core.performance import get_performance
from core.util import str_to_timestamp


# Backtesting Bot
# TODO considering balance
class BackTestBot(object):
    def __init__(self, config):
        # History cache
        self.__history = {}

        # Data directory
        self.__data_dir = config["data_dir"]

        # Result directory
        self.__result_dir = config["result_dir"]

        # Interval
        self.__interval = config["interval"]

        # Record current time
        self.__current_time = str_to_timestamp('2019-09-10 00:00:00')

        # Current balance
        self.__balance = config['balance']

        # Pair for comparison
        self.__pair = config['pair']

        # Fee
        self.__taker_rate = config['taker_fee']
        self.__maker_rate = config['maker_fee']

        # Order ID Issuer
        self.__order_id = 0

        # Order history
        self.__order_history = []

        # Order record storage
        self.__order_record = {}

        # Setting
        self.__setting = {}

    def next(self, next_time: datetime):
        for o in self.__order_history:
            if o['type'] == "market" and o['status'] == "unfilled":
                # Fill all unfilled market orders
                o['status'] = "filled"
            elif o['type'] == "limit" and o['status'] == "unfilled":
                h, i = self.__load_history(o['symbol'], self.__interval)
                price = h.iloc[i]
                if price['Low'] <= o['price'] <= price['High']:
                    # Fill all limit orders of which price is between low and high of the last record
                    o['status'] = "filled"

        # Update current time
        self.__current_time = int(next_time.timestamp() * 1000)

    # Return limited history before current time with duplicated latest time
    # Real bot will return limited history before and including current time
    # TODO symbol and timeframe
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> dict:
        # Load history
        h, i = self.__load_history(symbol, timeframe)

        # From dataframe to list
        h = h.iloc[i - limit: i].values.tolist()

        # Duplicate last record (due to the unfinished k-line data in real)
        h.append(h[-1])
        h = h[1:]

        # Integer timestamp
        for r in h:
            r[0] = int(r[0])
        return h

    def get_ticker(self, symbol: str) -> dict:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)
        return dict(
            symbol=symbol,
            last=h.iloc[i]['Open'],
            timestamp=self.__current_time
        )

    def buy_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'buy', amount, price, self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def buy_market(self, symbol: str, amount: float) -> Order:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)

        # Assume market price is close to the open price of the next record
        # TODO Check whether balance is enough to buy
        o = Order(self.__order_id, symbol, 'market', 'buy', amount, h.iloc[i]['Open'],
                  self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def sell_limit(self, symbol: str, amount: float, price: float) -> Order:
        o = Order(self.__order_id, symbol, 'limit', 'sell', amount, price, self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def sell_market(self, symbol: str, amount: float) -> Order:
        # Load history
        h, i = self.__load_history(symbol, self.__interval)
        # TODO Check whether amount is enough to sell
        o = Order(self.__order_id, symbol, 'market', 'sell', amount, h.iloc[i]['Open'],
                  self.__current_time)
        self.__order_history.append(o)
        self.__order_id += 1
        return o

    def get_order(self, o_id: int, symbol: str) -> dict:
        order = None
        for o in self.__order_history:
            if o['id'] == o_id:
                order = o
                break
        return order

    def cancel_order(self, o_id: int, symbol: str):
        for o in self.__order_history:
            if o['id'] == o_id:
                o['status'] = "cancel"
                break

    def cancel_unfilled_orders(self, symbol: str, limit: int = None):
        canceled_ids = []
        for o in self.__order_history:
            if o['status'] == "unfilled":
                o['status'] = "cancel"
                canceled_ids.append(o['id'])
        return canceled_ids

    def output_order_history(self, path: str, status: str = None):
        logging.info('Order history')
        orders = []
        if status is None:
            # Output all orders
            for o in self.__order_history:
                logging.info(o)
                orders.append([o['timestamp'], o['side'], o['amount']])
        else:
            # Output orders with specific status
            for o in self.__order_history:
                if o['status'] == status:
                    logging.info(
                        f"{datetime.fromtimestamp(o['timestamp'] / 1000)} {o['side']} ({o['amount']}) at {o['price']}")
                    orders.append([o['timestamp'], o['side'], o['amount']])

        with open(f'{path}order_history.json', 'w') as outfile:
            json.dump(orders, outfile)

    def output_performance(self, path: str):
        # path = f'{self.__result_dir}{datetime.now().timestamp()}/'
        # os.mkdir(path)

        logging.info(f'Output performance to {path}')

        # Calculate performance model
        perf = get_performance(self.__order_history)

        # Plot PnL figures
        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle('PnL Figures')
        # Plot PnL history
        ax1.plot(pd.to_datetime(perf.timestamps, unit='ms'), perf.pnl_history)
        ax1.set_title("PnL")
        ax1.set_xlabel("Time")
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylabel("PnL")
        # Plot cumulative PnL history
        ax2.plot(pd.to_datetime(perf.timestamps, unit='ms'), perf.cum_pnl_history)
        ax2.set_title("Cummulative PnL")
        ax2.set_xlabel("Time")
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylabel("Cum PnL")

        plt.tight_layout()
        plt.savefig(f'{path}pnl_history.svg')

        delattr(perf, 'pnl_history')
        delattr(perf, 'cum_pnl_history')
        delattr(perf, 'timestamps')

        # Print performance information
        perf = json.dumps(perf.__dict__)
        with open(f'{path}perf.json', 'w') as outfile:
            json.dump(perf, outfile)
        logging.info(perf)

    def output_buy_hold(self, start_time: datetime, end_time: datetime):
        logging.info('Buy & Hold')
        h, i = self.__load_history(self.__pair, self.__interval, start_time)
        start_price = h.iloc[i]['Open']
        h, i = self.__load_history(self.__pair, self.__interval, end_time)
        end_price = h.iloc[i]['Open']
        buy_hold = {
            "pnl": self.__balance / start_price * end_price - self.__balance
        }
        logging.info(buy_hold)

    # Return <History, Index of the current time | Index of the assigned timestamp>
    def __load_history(self, symbol: str, timeframe: str, time: datetime = None):
        key = symbol + timeframe
        if key not in self.__history.keys():
            self.__history[key] = pd.read_csv(f'{self.__data_dir}{symbol.replace("/", "")}_{timeframe}.csv')

        h = self.__history[key]
        assert len(h) > 0, 'Lack backtesting data.'

        timestamp = self.__current_time if time is None else int(time.timestamp() * 1000)
        i = h.index[h['Timestamp'] <= timestamp].tolist()
        assert len(i) >= 1, 'Backtesting data corrupted.'
        return h, i[-1]

    def create_order_record(self, name: str, order):
        if name in self.__order_record.keys():
            self.__order_record[name].append(order)
        else:
            self.__order_record[name] = [order]

    def get_order_record_length(self, name: str):
        if name in self.__order_record.keys():
            return len(self.__order_record[name])
        else:
            return 0

    def get_orders(self, name: str) -> list:
        if name in self.__order_record.keys():
            return self.__order_record[name]
        else:
            return []

    def clear_order_record(self, name: str):
        if name in self.__order_record.keys():
            self.__order_record[name] = []

    def create_setting(self, setting):
        self.__setting = setting

    def get_setting(self):
        return self.__setting
