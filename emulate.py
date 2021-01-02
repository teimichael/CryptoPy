import json
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from bot.emulate_bot import EmulateBot
from strategy.VegasTunnel import VegasTunnel


# Calculate performance
def schedule_perf_calculation():
    # Schedule recording performance
    scheduler = BackgroundScheduler()
    scheduler.add_job(bot.output_performance, 'cron', minute='*/15', second='30')
    scheduler.start()


def schedule_strategy(strategy):
    scheduler = BlockingScheduler()

    # Per hour (offset 10 seconds)
    # scheduler.add_job(job, 'cron', hour='*/1', second='10')

    # Per minute (offset 10 seconds)
    # scheduler.add_job(strategy.run, 'cron', minute='*/1', second='10')

    # Per 15 minutes (offset 3 seconds)
    scheduler.add_job(strategy.run, 'cron', minute='*/15', second='3')

    # Every 3 seconds for test
    # scheduler.add_job(strategy.run, 'interval', seconds=3)

    scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    with open('./config.json') as f:
        config = json.load(f)

    bot = EmulateBot(config)
    strategy = VegasTunnel(bot)

    schedule_perf_calculation()
    schedule_strategy(strategy)
