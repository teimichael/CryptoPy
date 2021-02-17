import json
import logging
from datetime import timedelta

from bot.backtest_bot import BackTestBot
from core.util import str_to_date, parse_timeframe
from strategy.example.VTCompLong import VegasTunnelCompoundLong

if __name__ == "__main__":
    # Set logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Load trading bot
    bot = BackTestBot(config)

    # Load strategy
    strategy = VegasTunnelCompoundLong(bot)

    # Calculate strategy execution times
    start = str_to_date(config['start_time'])
    end = str_to_date(config['end_time'])

    # Execute strategy
    timeframe_in_seconds = parse_timeframe(config['interval'])
    current = start
    i = 0
    while current <= end:
        current = start + timedelta(seconds=i * timeframe_in_seconds)
        bot.next(current)
        strategy.run(current)
        i += 1

    # Output order history
    bot.output_order_history("filled")

    # Output performance
    bot.output_performance()

    # Buy & hold
