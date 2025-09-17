from datetime import datetime

from vnpy.trader.constant import Exchange
from vnpy.trader.constant import Interval
from vnpy.trader.database import get_database
from vnpy_app.utility.converter import convert_ticks, convert_bars
from vnpy_app.utility.database.sqlite.setting import backtest_setting

date_format = '%Y-%m-%d'


def load_ticks(symbol: str, exchange: Exchange, start: str, end: str):
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


def load_bars(symbol: str, exchange: Exchange, start: str, end: str, interval: Interval):
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


def upload_ticks(ticks):
    backtest_setting()
    database = get_database()
    result = database.save_tick_data(ticks)
    print(result)


def upload_bars(bars):
    backtest_setting()
    database = get_database()
    result = database.save_bar_data(bars)
    print(result)
