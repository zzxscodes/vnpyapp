from datetime import datetime
from typing import List

import pandas as pd

from vnpy.trader.constant import Exchange
from vnpy.trader.constant import Interval
from vnpy.trader.database import get_database
from vnpy.trader.object import BarData
from vnpy.trader.object import TickData
from vnpy_app.utility.converter import convert_ticks, convert_bars
from vnpy_app.utility.database.mysql.setting import backtest_setting

date_format = '%Y-%m-%d'


def load_ticks(symbol: str, exchange: Exchange, start: str, end: str) -> pd.DataFrame:
    backtest_setting()
    database = get_database()
    result = database.load_tick_data(
        symbol=symbol,
        exchange=exchange,
        start=datetime.strptime(start, date_format),
        end=datetime.strptime(end, date_format),
    )
    df = convert_ticks(result)
    return df


def load_bars(symbol: str, exchange: Exchange, start: str, end: str, interval: Interval) -> pd.DataFrame:
    backtest_setting()
    database = get_database()
    result = database.load_bar_data(
        symbol=symbol,
        exchange=exchange,
        start=datetime.strptime(start, date_format),
        end=datetime.strptime(end, date_format),
        interval=interval
    )
    df = convert_bars(result)
    return df


def upload_ticks(ticks: List[TickData]):
    backtest_setting()
    database = get_database()
    result = database.save_tick_data(ticks)
    print(result)


def upload_bars(bars: List[BarData]):
    backtest_setting()
    database = get_database()
    result = database.save_bar_data(bars)
    print(result)


def delete_ticks(symbol: str, exchange: Exchange):
    backtest_setting()
    database = get_database()
    count = database.delete_tick_data(symbol, exchange)
    print(f'tick count: {count}')


def delete_bars(symbol: str, exchange: Exchange, interval: Interval):
    backtest_setting()
    database = get_database()
    count = database.delete_bar_data(symbol, exchange, interval)
    print(f'bar count: {count}')
