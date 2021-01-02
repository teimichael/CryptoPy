import json
import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from bot.emulate_bot import EmulateBot
from strategy.VegasTunnel import VegasTunnel


# Schedule strategy
def schedule_strategy(strategy):
    scheduler = BlockingScheduler()

    # Per hour (offset 10 seconds)
    # scheduler.add_job(job, 'cron', hour='*/1', second='10')

    # Per 15 minutes (offset 3 seconds)
    # scheduler.add_job(strategy.run, 'cron', minute='*/15', second='3')

    # Every 3 seconds for test
    scheduler.add_job(strategy.run, 'interval', seconds=3)

    scheduler.start()


def set_logging():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


if __name__ == "__main__":
    # Set logging
    set_logging()

    # Load configuration file
    with open('./config.json') as f:
        config = json.load(f)

    # Load trading bot
    bot = EmulateBot(config)

    # Load strategy
    strategy = VegasTunnel(bot)

    # Schedule strategy
    schedule_strategy(strategy)
