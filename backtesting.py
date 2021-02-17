import json
import logging
from datetime import timedelta

from bot.backtest_bot import BackTestBot
from core.util import str_to_date, parse_timeframe
from strategy.VTComp import VegasTunnelCompound

if __name__ == "__main__":
    # Set logging
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Load trading bot
    bot = BackTestBot(config)

    # Load strategy
    strategy = VegasTunnelCompound(bot)

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
    bot.output_order_history("filled")

    # Output performance
    bot.output_performance()

    # Buy & hold
    balance = config['balance']
    h, i = bot.load_history(config['pair'], config['interval'], start)
    start_price = h.iloc[i]['Open']
    h, i = bot.load_history(config['pair'], config['interval'], end)
    end_price = h.iloc[i]['Open']
    buy_hold = {
        "pnl": balance / start_price * end_price - balance
    }
    logging.info(buy_hold)
