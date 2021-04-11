import csv
import json
import os
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

        # Raw data subdirectory
        self.__raw_subdir = "raw/"

        # Script subdirectory
        self.__script_subdir = "script/"

        # Interval
        self.__interval = config["interval"]

        # Record current time
        self.__current_time = str_to_timestamp('2019-09-10 00:00:00')

        # Current balance
        self.__balance = config['balance']

        # Pair for comparison
        self.__pair = config['pair']

        # Fee
        self.__taker_fee = config['taker_fee']
        self.__maker_fee = config['maker_fee']

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
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 500, duplicate=True) -> dict:
        # Load history
        h, i = self.__load_history(symbol, timeframe)

        # From dataframe to list
        h = h.iloc[i - limit: i].values.tolist()

        # Duplicate last record (due to the unfinished k-line data in real)
        if duplicate:
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

    # Buy (Good till crossing / Post only) same with buy limit for backtesting
    def buy_gtx(self, symbol: str, amount: float, price: float) -> Order:
        return self.buy_limit(symbol, amount, price)

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

    # Buy (Good till crossing / Post only) same with sell limit for backtesting
    def sell_gtx(self, symbol: str, amount: float, price: float) -> Order:
        return self.sell_limit(symbol, amount, price)

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

    def output_order_history(self, result_dir: str, status: str = None):
        print('Order history')
        orders = []
        if status is None:
            for o in self.__order_history:
                # logging.info(o)
                orders.append([o['timestamp'], o['side'], o['amount'], o['symbol']])
        else:
            # Output orders with specific status
            for o in self.__order_history:
                if o['status'] == status:
                    # logging.info(
                    #     f"{datetime.fromtimestamp(o['timestamp'] / 1000)} {o['side']} ({o['amount']}) at {o['price']}")
                    orders.append([o['timestamp'], o['side'], o['amount'], o['symbol']])

        path = result_dir + self.__raw_subdir
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(f'{path}order_history.json', 'w') as outfile:
            json.dump(orders, outfile)

    def output_performance(self, result_dir: str, start_time: datetime, end_time: datetime):
        print(f'Output performance to {result_dir}')

        # Calculate performance model
        perf = get_performance(self.__order_history, self.__taker_fee, self.__maker_fee)

        # Plot PnL figures
        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle('PnL Figures')
        # Plot PnL history
        pnl_timestamps = [r[0] for r in perf.pnl_history]
        pnl_history = [r[1] for r in perf.pnl_history]
        ax1.plot(pd.to_datetime(pnl_timestamps, unit='ms'), pnl_history)
        ax1.set_title("PnL")
        ax1.set_xlabel("Time")
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylabel("PnL")
        # Plot cumulative PnL history
        cum_pnl_timestamps = [r[0] for r in perf.cum_pnl_history]
        cum_pnl_history = [r[1] for r in perf.cum_pnl_history]
        ax2.plot(pd.to_datetime(cum_pnl_timestamps, unit='ms'), cum_pnl_history)
        ax2.set_title("Cummulative PnL")
        ax2.set_xlabel("Time")
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylabel("Cum PnL")

        plt.tight_layout()
        plt.savefig(f'{result_dir}pnl_history.svg')

        # Output PnL information
        path = result_dir + self.__raw_subdir
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(f'{path}pnl.json', 'w') as outfile:
            json.dump(perf.pnl_history, outfile)

        with open(f'{path}cum_pnl.json', 'w') as outfile:
            json.dump(perf.cum_pnl_history, outfile)

        delattr(perf, 'pnl_history')
        delattr(perf, 'cum_pnl_history')

        # Output performance information
        h, i = self.__load_history(self.__pair, self.__interval, start_time)
        start_price = h.iloc[i]['Open']
        h, i = self.__load_history(self.__pair, self.__interval, end_time)
        end_price = h.iloc[i]['Open']

        perf.buy_hold = self.__balance / start_price * end_price - self.__balance

        print(perf.__dict__)

        # Store performance information
        with open(f'{result_dir}performance.json', 'w') as outfile:
            json.dump(perf.__dict__, outfile, indent=4)

    def output_view(self, result_dir: str, global_dir: str, plot):
        data_name = self.__pair.replace("/", "") + "_" + self.__interval

        k_line = []
        with open(f'{self.__data_dir}{data_name}.csv') as k_data_file:
            csv_reader = csv.reader(k_data_file)
            header = next(csv_reader)
            if header is not None:
                for row in csv_reader:
                    k_line.append(row)

        k_line = "const K_LINE_DATA = " + json.dumps(k_line)
        with open(f'{global_dir}{data_name}.js', 'w') as k_line_file:
            k_line_file.write(k_line)

        raw_path = result_dir + self.__raw_subdir
        script_path = result_dir + self.__script_subdir
        if not os.path.isdir(script_path):
            os.mkdir(script_path)

        # Create scripts
        with open(f'{raw_path}order_history.json') as orders_file:
            order_history = json.load(orders_file)
            with open(f'{script_path}order_history.js', 'w') as orders_script:
                order_history = "const ORDER_HISTORY = " + json.dumps(order_history)
                orders_script.write(order_history)

        with open(f'{raw_path}pnl.json') as pnl_file:
            pnl_history = json.load(pnl_file)
            with open(f'{script_path}pnl.js', 'w') as pnl_script:
                pnl_history = "const PNL = " + json.dumps(pnl_history)
                pnl_script.write(pnl_history)

        with open(f'{raw_path}cum_pnl.json') as cum_pnl_file:
            cum_pnl_history = json.load(cum_pnl_file)
            with open(f'{script_path}cum_pnl.js', 'w') as cum_pnl_script:
                cum_pnl_history = "const CUM_PNL = " + json.dumps(cum_pnl_history)
                cum_pnl_script.write(cum_pnl_history)

        with open(f'{script_path}plot.js', 'w') as plot_script:
            indicator = "const INDICATOR = " + json.dumps(plot)
            plot_script.write(indicator)

        # Create HTML
        with open('view/index.html') as template:
            t = template.read()
            t = t.replace("{!k_line!}", f'../global/{data_name}.js') \
                .replace("{!order_history!}", f'{self.__script_subdir}order_history.js') \
                .replace("{!pnl!}", f'{self.__script_subdir}pnl.js') \
                .replace("{!cum_pnl!}", f'{self.__script_subdir}cum_pnl.js') \
                .replace("{!plot!}", f'{self.__script_subdir}plot.js')
            with open(f'{result_dir}index.html', 'w') as index_html:
                index_html.write(t)

    def output_config(self, result_dir: str, config):
        c = {
            'strategy': config['strategy'],
            'setting': self.__setting,
            'start_time': config['start_time'],
            'end_time': config['end_time'],
            'interval': config['interval'],
            'balance': config['balance'],
            'pair': config['pair'],
            'taker_fee': config['taker_fee'],
            'maker_fee': config['maker_fee']
        }

        with open(f'{result_dir}config.json', 'w') as config_file:
            json.dump(c, config_file, indent=4)
