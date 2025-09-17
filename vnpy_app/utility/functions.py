import os
from functools import lru_cache

import pandas as pd
import yaml

from vnpy.trader.constant import Interval, Exchange


def get_interval(interval: str):
    return getattr(Interval, interval)


def get_exchange(exchange: str):
    return getattr(Exchange, exchange)


@lru_cache()
def read_yaml():
    file_path = os.path.join(os.path.dirname(__file__), 'symbols.yaml')
    with open(file_path, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
    df = pd.DataFrame.from_dict(result['symbols'], orient='index')
    df.index.name = 'symbol'
    df.reset_index(inplace=True)
    return df


def get_symbol_exchange(symbol, is_value=True):
    df = read_yaml()
    exchange = df.query(f"symbol == '{symbol}'")['exchange'].values[0]
    if not is_value:
        exchange = get_exchange(exchange)
    return exchange


def get_symbol_name(symbol):
    df = read_yaml()
    return df.query(f"symbol == '{symbol}'")['name'].values[0]


def get_category(category):
    df = read_yaml()
    if category == 'all':
        return df['symbol'].tolist()
    else:
        return df.query(f"category == '{category}'")['symbol'].tolist()


def get_exchange_symbols(exchange):
    df = read_yaml()
    return df.query(f"exchange == '{exchange}'")['symbol'].tolist()


def get_locked_symbols():
    df = read_yaml()
    return df.query('is_locked == True').symbol.tolist()


def get_free_intraday_symbols():
    df = read_yaml()
    return df.query('is_free == True').symbol.tolist()


def get_rate_commission_symbols():
    df = read_yaml()
    return df.query('is_rate == True').symbol.tolist()


def get_currency_commission_symbols():
    df = read_yaml()
    return df.query('is_rate == False').symbol.tolist()


def get_commission(symbol):
    df = read_yaml()
    return df.query(f"symbol == '{symbol}'")['fee'].values[0]


def get_price_tick(symbol):
    df = read_yaml()
    return df.query(f"symbol == '{symbol}'")['price_tick'].values[0]


def get_multiplier(symbol):
    df = read_yaml()
    return df.query(f"symbol == '{symbol}'")['contract_multiplier'].values[0]


__all__ = [
    'get_symbol_exchange',
    'get_category',
    'get_symbol_name',
    'get_interval',
    'get_exchange',
    'get_exchange_symbols',
    'get_locked_symbols',
    'get_free_intraday_symbols',
    'get_rate_commission_symbols',
    'get_currency_commission_symbols',
    'get_commission',
    'get_price_tick',
    'get_multiplier',
]
