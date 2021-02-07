import json

from bot.emulate_bot import EmulateBot

# Load configuration file

with open('./config.json') as f:
    config = json.load(f)

# Load trading bot
bot = EmulateBot(config)

open_orders = bot.get_open_orders('BTC/USDT')
print(open_orders)

orders = bot.get_orders('BTC/USDT')
print(orders)
