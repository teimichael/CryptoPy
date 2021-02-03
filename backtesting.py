import json
import logging
from datetime import datetime, timedelta

import pandas as pd

from bot.backtest_bot import BackTestBot
from core.util import str_to_date
from strategy.VTClassic import VegasTunnelClassic
from strategy.VTLComp import VegasTunnelCompound
from strategy.VTLCompLong import VegasTunnelCompoundLong


def test_1h(start: datetime, end: datetime):
    times = (end - start).days * 24 + 1
    for i in range(times):
        current = start + timedelta(hours=i)
        bot.set_current_time(current)
        strategy.run(current)


def test_15m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 4 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 15)
        bot.set_current_time(current)
        strategy.run(current)


def test_5m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 12 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 5)
        bot.set_current_time(current)
        strategy.run(current)


def test_3m(start: datetime, end: datetime):
    times = (end - start).days * 24 * 20 + 1
    for i in range(times):
        current = start + timedelta(minutes=i * 3)
        bot.set_current_time(current)
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
    strategy = VegasTunnelClassic(bot)
    # strategy = VegasTunnelCompound(bot)
    # strategy = VegasTunnelCompoundLong(bot)

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

    # Output order history
    bot.output_order_history()

    # Output performance
    bot.output_performance()

    # Buy & hold
