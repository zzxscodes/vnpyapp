import os

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine, text

from vnpy_app.utility.database.mysql.setting import backtest_setting
from vnpy_app.utility.log import get_module_logger

setting = backtest_setting()
ts_pro = ts.pro_api(setting['datafeed.password'])
logger = get_module_logger('system.clickhouse')
local_folder = os.path.dirname(os.path.abspath(__file__))


def query(sql):
    host = '192.168.0.231'
    port = 18123
    user = 'ro_yangcheng'
    password = 'vJxCNbvG95i5'

    engine_params = 'clickhouse://'
    engine_params += user + ':'
    engine_params += password + '@'
    engine_params += host + ':'
    engine_params += str(port)
    engine = create_engine(engine_params)

    with engine.connect() as connection:
        result = connection.execute(text(sql))
    df = pd.DataFrame(result)
    return df


def get_trade_date(beg, end):
    df = ts_pro.trade_cal('DCE')
    df['TRADE_DATE'] = df['CAL_DATE'].map(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:])
    df.sort_values('TRADE_DATE', inplace=True)
    dates = df.query(f"TRADE_DATE > '{beg}' and TRADE_DATE < '{end}'").query('IS_OPEN == 1')['TRADE_DATE'].tolist()
    return dates


def get_fut_basic():
    exchanges = ['CFFEX', 'DCE', 'CZCE', 'SHFE', 'INE', 'GFEX']
    columns = ['name', 'multiplier', 'trade_unit', 'per_unit', 'quote_unit', 'quote_unit_desc']
    ls = list()
    for exchange in exchanges:
        df = ts_pro.fut_basic(exchange=exchange)
        df.dropna(inplace=True)
        df.drop(columns=columns, inplace=True)
        ls.append(df)
    df_all = pd.concat(ls)
    df_all.sort_values(by=['exchange', 'fut_code', 'symbol'], inplace=True)
    return df_all


def get_stock_basic():
    df = ts_pro.stock_basic()
    df.sort_values(by=['market', 'ts_code'], inplace=True)
    df.dropna(inplace=True)
    return df

def get_index_basic():
    df = ts_pro.index_basic()
    df.sort_values(by=['market', 'ts_code'], inplace=True)
    df.dropna(inplace=True)
    return df


def get_index_weight(index_code, date):
    # date must be the last
    assert index_code in ['000001.SH', '000300.SH', '000905.SH', '000852.SH', '932000.CSI']
    trade_date = date[:4] + date[5:7]  + date[8:]
    df = ts_pro.index_weight(index_code=index_code, trade_date=trade_date)
    return df


__all__ = [
    'query',
    'get_trade_date',
    'get_fut_basic',
    'get_stock_basic',
    'get_index_basic',
    'get_index_weight'
]
