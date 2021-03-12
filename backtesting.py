import importlib
import json
import logging
import os
from datetime import timedelta, datetime

from bot.backtest_bot import BackTestBot
from core.util import str_to_date, parse_timeframe

if __name__ == "__main__":
    # Set logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Create result directory
    if not os.path.isdir(config['result_dir']):
        os.mkdir(config['result_dir'])

    # Load trading bot
    bot = BackTestBot(config)

    # Load strategy
    m = 'strategy.'
    m += 'example.' + config['strategy'] if config['example'] else config['strategy']
    strategy_cls = getattr(importlib.import_module(m), config['strategy'])
    strategy = strategy_cls(bot)

    # Execute strategy
    start = str_to_date(config['start_time'])
    end = str_to_date(config['end_time'])
    timeframe_in_seconds = parse_timeframe(config['interval'])
    current = start
    i = 0
    while current <= end:
        current = start + timedelta(seconds=i * timeframe_in_seconds)
        bot.next(current)
        strategy.run(current)
        i += 1

    # Create output directory
    path = f'{config["result_dir"]}{datetime.now().timestamp()}/'
    os.mkdir(path)

    # Output order history
    bot.output_order_history(path, "filled")

    # Output performance
    bot.output_performance(path)

    # Buy & hold
    bot.output_buy_hold(start, end)
