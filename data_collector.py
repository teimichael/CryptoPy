import json
import os
from datetime import datetime

import pandas as pd
from binance_data import DataClient
from dateutil.tz import tzutc


def get_raw_data(base: str, quote: str, time_frame: str, start_date: str, end_date: str, raw_data_dir: str,
                 futures: bool = True):
    if futures:
        print('Collecting futures data from Binance')
    else:
        print('Collecting spot data from Binance')
    client = DataClient(futures=futures)
    pair_list = client.get_binance_pairs(base_currencies=[base], quote_currencies=[quote])
    print(start_date)
    store_data = client.kline_data(pair_list, time_frame, start_date=start_date, end_date=end_date,
                                   storage=['csv', raw_data_dir],
                                   progress_statements=True)


def integrity_check(symbol: str, time_frame: str, raw_data_dir: str):
    for root, dirs, files in os.walk(f"{raw_data_dir}{time_frame}_data/{symbol}/individual_csvs"):
        for name in files:
            df = pd.read_csv(os.path.join(root, name))
            # 1h: 25, 15m: 96
            if time_frame == '1h' and len(df) != 25:
                print(name)
            elif time_frame == '15m' and len(df) != 96:
                print(name)


def str_to_timestamp(date: str) -> int:
    d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tzutc())
    return int(d.timestamp() * 1000)


def data_cleaning(symbol: str, time_frame: str, raw_data_dir: str, data_dir: str):
    df = pd.read_csv(f'{raw_data_dir}{time_frame}_data/{symbol}/{symbol}.csv')
    df = df.drop_duplicates()
    df['Opened'] = df['Opened'].apply(lambda t: str_to_timestamp(t))
    df = df.rename(columns={'Opened': 'Timestamp'})
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    df.to_csv(f'{data_dir}{symbol}_{time_frame}.csv', index=False)


if __name__ == '__main__':
    # Load configuration file
    with open('./backtest_config.json') as f:
        config = json.load(f)

    # Load data config
    config = config['data']

    # Trading symbol (pair)
    symbol = config['quote'] + config['base']

    # Get raw data
    get_raw_data(config['base'], config['quote'], config['time_frame'], config['start_date'], config['end_date'],
                 config['raw_data_dir'], config['futures'])

    # Check integrity
    integrity_check(symbol, config['time_frame'], config['raw_data_dir'])

    # Clean data
    data_cleaning(symbol, config['time_frame'], config['raw_data_dir'], config['clean_data_dir'])
