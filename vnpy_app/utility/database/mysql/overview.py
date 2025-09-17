import pandas as pd

from vnpy.trader.database import get_database
from vnpy_app.utility.database.mysql.setting import backtest_setting


def get_bar_overview():
    backtest_setting()
    database = get_database()
    bar_overviews = database.get_bar_overview()
    df = pd.DataFrame([getattr(b, '__data__') for b in bar_overviews])
    df['suffix'] = df['symbol'].apply(lambda symbol: ''.join([x for x in symbol if x.isdigit()]))
    df['interval'] = df['interval'].apply(lambda x: str(x))
    df['exchange'] = df['exchange'].apply(lambda x: str(x))
    df.sort_values(['interval', 'suffix', 'exchange', 'symbol'], inplace=True)
    return df


def get_tick_overview():
    backtest_setting()
    database = get_database()
    tick_overviews = database.get_tick_overview()
    df = pd.DataFrame([getattr(t, '__data__') for t in tick_overviews])
    df['suffix'] = df['symbol'].apply(lambda symbol: ''.join([x for x in symbol if x.isdigit()]))
    df['exchange'] = df['exchange'].apply(lambda x: str(x))
    df.sort_values(['suffix', 'exchange', 'symbol'], inplace=True)
    return df
