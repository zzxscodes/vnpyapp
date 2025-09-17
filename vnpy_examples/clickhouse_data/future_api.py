import os

from diskcache import Cache

from vnpy_app.utility.log import get_module_logger
from vnpy_examples.clickhouse_data.common import query

logger = get_module_logger('system.clickhouse')
local_folder = os.path.dirname(os.path.abspath(__file__))
logger.logger.disabled = True

def disk_cache():
    def decorator(func):
        def wrapper(**kwargs):
            # 生成唯一的缓存键
            key_parts = [func.__name__]
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            date = kwargs.get('date')
            key = ":".join(key_parts)
            folder = os.path.join(local_folder, '.future_database', date)
            cache = Cache(str(folder), size_limit=8 * 1024 * 1024 * 1024)
            # 检查缓存是否存在
            if key not in cache:
                logger.info(f'{key}: {date} is loading.')
                result = func(**kwargs)
                if result.empty:
                    logger.warning(f'{key}: {date} is empty.')
                else:
                    cache.set(key, result)
            else:
                logger.info(f'{key}: {date} is loaded.')
                result = cache.get(key)
            return result

        return wrapper

    return decorator


@disk_cache()
def get_future_daily_bars(date):
    table = 'ricequant_ods.future_daily_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where date = '{date}' 
order by order_book_id, date;
    """
    df = query(sql)
    return df


@disk_cache()
def get_future_minute_bars(date):
    table = 'ricequant_ods.future_minute_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where trading_date = '{date}' 
order by order_book_id, datetime;
    """
    df = query(sql)
    return df


@disk_cache()
def get_dominant_future_daily_bars(date):
    """
    return quote with no adjustment, 88 contract
    """
    table = 'ricequant_ods.future_dominant_daily_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where date = '{date}' 
order by underlying_symbol, date;
    """
    df = query(sql)
    return df


@disk_cache()
def get_dominant_future_minute_bars(date):
    """
    return quote with no adjustment, 88 contract
    """
    table = 'ricequant_ods.future_dominant_minute_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where trading_date = '{date}' 
order by underlying_symbol, datetime;
    """
    df = query(sql)
    return df


@disk_cache()
def get_symbol_dominant_future_daily_bars(date, underlying_symbol):
    table = 'ricequant_ods.future_dominant_daily_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where date = '{date}' 
and underlying_symbol = '{underlying_symbol}' 
order by underlying_symbol, date;
    """
    df = query(sql)
    return df


@disk_cache()
def get_symbol_dominant_future_minute_bars(date, underlying_symbol):
    table = 'ricequant_ods.future_dominant_minute_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where trading_date = '{date}' 
and underlying_symbol = '{underlying_symbol}' 
order by underlying_symbol, datetime;
    """
    df = query(sql)
    return df


@disk_cache()
def get_symbol_future_daily_bars(date, symbol):
    table = 'ricequant_ods.future_daily_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where date = '{date}' 
and order_book_id = '{symbol}' 
order by order_book_id, date;
    """
    df = query(sql)
    return df


@disk_cache()
def get_symbol_future_minute_bars(date, symbol):
    table = 'ricequant_ods.future_minute_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where trading_date = '{date}' 
and order_book_id = '{symbol}' 
order by order_book_id, datetime;
    """
    df = query(sql)
    return df


def get_future_ex_factor():
    table = 'ricequant_ods.future_ex_factor_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
    select * from {table} 
    order by underlying_symbol, ex_date, adjust_method;
    """
    df = query(sql)
    return df


def get_future_instrument():
    table = 'ricequant_ods.future_instruments_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
    select * from {table} 
    order by order_book_id, listed_date;
    """
    df = query(sql)
    return df


def get_future_daily_bars_with_time_range(beg_date, end_date, order_book_id):
    table = 'ricequant_ods.future_daily_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where date >= '{beg_date}'
and date <= '{end_date}'
and order_book_id = '{order_book_id}' 
order by order_book_id, date;
    """
    df = query(sql)
    return df


def get_future_minute_bars_with_time_range(beg_date, end_date, order_book_id):
    table = 'ricequant_ods.future_minute_all'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
select * from {table} 
where trading_date >= '{beg_date}'
and trading_date <= '{end_date}'
and order_book_id = '{order_book_id}' 
order by order_book_id, datetime;
    """
    df = query(sql)
    return df


__all__ = [
    'get_future_daily_bars',
    'get_future_minute_bars',
    'get_dominant_future_daily_bars',
    'get_dominant_future_minute_bars',
    'get_symbol_dominant_future_daily_bars',
    'get_symbol_dominant_future_minute_bars',
    'get_symbol_future_daily_bars',
    'get_symbol_future_minute_bars',
    'get_future_ex_factor',
    'get_future_instrument',
    'get_future_daily_bars_with_time_range',
    'get_future_minute_bars_with_time_range',
]
