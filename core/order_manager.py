import os

import pandas as pd


def create(name: str, order):
    rec = pd.DataFrame({'timestamp': [order['timestamp']], 'id': [order['id']], 'amount': [order['amount']]})
    if os.path.exists(name):
        store = pd.read_csv(name)
        store = store.append(rec, ignore_index=True)
        store.to_csv(name, index=False)
    else:
        rec.to_csv(name, index=False)


def remove(name: str, o_id: int):
    if os.path.exists(name):
        store = pd.read_csv(name)
        store = store[~store['id'].isin([o_id])]
        store.to_csv(name, index=False)


def remove_last(name: str):
    if os.path.exists(name):
        store = pd.read_csv(name)
        store = store[:-1]
        store.to_csv(name, index=False)


def clear(name: str):
    if os.path.exists(name):
        os.remove(name)


def get_length(name: str):
    if os.path.exists(name):
        store = pd.read_csv(name)
        return len(store.index)
    else:
        return 0
