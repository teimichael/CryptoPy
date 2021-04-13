import json
import time
from datetime import datetime

import ccxt
import pandas as pd

from core.util import str_to_timestamp

if __name__ == '__main__':
    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Load data config
    config = config['data']

    # Generate symbol
    symbol = config['quote'] + '/' + config['base']
    futures = ['future', 'delivery']
    if config['exchange_type'] in futures and config['quarterly'] != "":
        symbol = config['quote'] + config['base'] + "_" + config['quarterly']

    # symbol="ETH-USD-210625"
    # Initialize exchange
    exchange_param = {
        'enableRateLimit': True,
        'options': {
            'defaultType': config['exchange_type'],
        },
    }
    if config['exchange_market'] == 'okex':
        exchange = ccxt.okex(exchange_param)
    else:
        exchange = ccxt.binance(exchange_param)

    # Load markets
    markets = exchange.load_markets()

    start_time = str_to_timestamp(config['start_time'])
    end_time = min(str_to_timestamp(config['end_time']), int(time.time() * 1000))

    if config['exchange_type'] != 'delivery':
        current_time = start_time

        history = pd.DataFrame([], columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        while current_time < end_time:
            print(datetime.fromtimestamp(current_time / 1000))
            rec = pd.DataFrame(exchange.fetch_ohlcv(symbol, config['interval'],
                                                    limit=1000,
                                                    params={'startTime': current_time, 'endTime': end_time}),
                               columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

            # Whether data set exists
            if len(rec) == 0:
                raise Exception("No data available.")

            history = pd.concat([history, rec], ignore_index=True)
            current_time = int(rec.iloc[-1]['Timestamp'])

    else:
        # COIN-M data
        current_time = end_time
        last_time = start_time

        history = pd.DataFrame([], columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        while start_time < current_time and last_time != current_time:
            print(datetime.fromtimestamp(current_time / 1000))
            rec = pd.DataFrame(exchange.fetch_ohlcv(symbol, config['interval'],
                                                    limit=1000,
                                                    params={'startTime': start_time, 'endTime': current_time}),
                               columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

            # Whether data set exists
            if len(rec) == 0:
                raise Exception("No data available.")

            history = pd.concat([history, rec], ignore_index=True).sort_values('Timestamp')
            last_time = current_time
            current_time = int(rec.iloc[0]['Timestamp'])

    history.drop_duplicates(inplace=True, ignore_index=True)
    history.to_csv(f'{config["output_dir"]}{symbol.replace("/", "")}_{config["interval"]}.csv', index=False)
