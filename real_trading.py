import json
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from bot.real_bot import RealBot
from bot.emulate_bot import EmulateBot
from strategy.VTCompLong import VegasTunnelCompoundLong


# Schedule balance log
def schedule_balance_log(bot):
    scheduler = BackgroundScheduler()
    scheduler.add_job(bot.output_balance, 'cron', minute='*/15', second='30')
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

    # Per 15 minutes (offset 3 seconds)
    scheduler.add_job(strategy.run, 'cron', minute='*/15', second='3')

    # Every 3 seconds for test
    # scheduler.add_job(strategy.run, 'interval', seconds=3)

    scheduler.start()


def set_logging():
    log_name = 'log_' + str(datetime.now().date()) + '.log'
    logging.basicConfig(filename=log_name,
                        filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)


# Real-trading entry
if __name__ == "__main__":
    # Set logging
    set_logging()

    # Load configuration file
    with open('./config.json') as f:
        config = json.load(f)

    # Load trading bot
    # bot = RealBot(config)  # Uncomment this to run real bot for trading when everything is ready.
    bot = EmulateBot(config)

    # Load strategy
    strategy = VegasTunnelCompoundLong(bot)

    # Schedule balance log
    schedule_balance_log(bot)

    # Schedule strategy trigger
    schedule_strategy_trigger(strategy)

    # Schedule strategy
    schedule_strategy(strategy)
