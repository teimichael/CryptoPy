import json
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from bot.emulate_bot import EmulateBot
from strategy.example.VTCompLong import VTCompLong


# Calculate performance
def schedule_perf_calculation(bot):
    # Schedule recording performance
    scheduler = BackgroundScheduler()
    # Per 15 minutes (offset 30 seconds)
    scheduler.add_job(bot.output_performance, 'cron', minute='*/5', second='30')
    scheduler.start()


# Schedule strategy trigger
def schedule_strategy_trigger(strategy):
    # Schedule strategy trigger (trigger special events between two strategy executions)
    scheduler = BackgroundScheduler()
    # Per 1 minute (offset 15 seconds)
    scheduler.add_job(strategy.run_trigger, 'cron', minute='*/1', second='15')

    scheduler.start()


# Schedule execution of strategy
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


def set_logging(config):
    # Set logging
    dir = config['logs_dir']
    if not os.path.isdir(dir):
        os.mkdir(dir)
    log_name = f'{dir}/log_{datetime.now().date()}.log'
    logging.basicConfig(filename=log_name,
                        filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)


# Emulate entry point
if __name__ == "__main__":
    # Load configuration file
    with open('./config.json') as f:
        config = json.load(f)

    # Set logging
    set_logging(config)

    # Load trading bot
    bot = EmulateBot(config)

    # Load strategy
    strategy = VTCompLong(bot)

    # Schedule performance calculation
    schedule_perf_calculation(bot)

    # Schedule strategy trigger
    schedule_strategy_trigger(strategy)

    # Schedule strategy
    schedule_strategy(strategy)
