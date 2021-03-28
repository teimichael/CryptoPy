import importlib
import json
import logging
import os
from datetime import timedelta, datetime

from bot.backtest_bot import BackTestBot
from core.util import str_to_date, parse_timeframe

if __name__ == "__main__":
    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Create result directory
    if not os.path.isdir(config['result_dir']):
        os.mkdir(config['result_dir'])

    # Create global directory
    global_dir = f'{config["result_dir"]}global/'
    if not os.path.isdir(global_dir):
        os.mkdir(global_dir)

    # Create output directory
    result_dir = f'{config["result_dir"]}{datetime.now().timestamp()}/'
    os.mkdir(result_dir)

    # Set logging
    logging.basicConfig(format='%(message)s', level=logging.INFO,
                        handlers=[logging.StreamHandler(), logging.FileHandler(f'{result_dir}backtest.log')])

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

    # Output order history
    bot.output_order_history(result_dir, "filled")

    # Output performance
    bot.output_performance(result_dir, start, end)

    # Output visualization of the result
    bot.output_view(result_dir, global_dir, config['plot'])

    # Output backtesting information
    bot.output_config(result_dir, config)
