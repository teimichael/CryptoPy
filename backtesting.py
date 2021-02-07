import json
import logging
from datetime import datetime, timedelta

import pandas as pd

from bot.backtest_bot import BackTestBot
from core.util import str_to_date
from strategy.MomClassic import MomClassic


def test_1h(start: datetime, end: datetime):
    times = (end - start).days * 24 + 1
    for i in range(times):
        current = start + timedelta(hours=i)
        bot.next(current)
        strategy.run(current)


def test_15m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 4 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 15)
        bot.next(current)
        strategy.run(current)


def test_5m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 12 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 5)
        bot.next(current)
        strategy.run(current)


def test_3m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 20 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 3)
        bot.next(current)
        strategy.run(current)


def test_1m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 60 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 1)
        bot.next(current)
        strategy.run(current)


if __name__ == "__main__":
    # Set logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Load history records
    # TODO Raise file not found error
    history = pd.read_csv(f'{config["data_dir"]}{config["pair"]}_{config["interval"]}.csv')

    # Load trading bot
    bot = BackTestBot(history, config['balance'], config['trade_leverage'],
                      config['max_leverage'],
                      config['taker_fee'], config['maker_fee'])

    # Load strategy
    strategy = MomClassic(bot)

    # Calculate strategy execution times
    start = str_to_date(config['start_time'])
    end = str_to_date(config['end_time'])

    # Execute strategy
    if config['interval'] == '1h':
        test_1h(start, end)
    elif config['interval'] == '15m':
        test_15m(start, end)
    elif config['interval'] == '5m':
        test_5m(start, end)
    elif config['interval'] == '3m':
        test_3m(start, end)
    elif config['interval'] == '1m':
        test_1m(start, end)

    # Output order history
    bot.output_order_history("filled")

    # Output performance
    bot.output_performance()

    # Buy & hold
