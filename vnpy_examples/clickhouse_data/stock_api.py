import os

import tushare as ts
from diskcache import Cache

from vnpy_app.utility.database.sqlite.setting import backtest_setting
from vnpy_app.utility.log import get_module_logger
from vnpy_examples.clickhouse_data.common import query

setting = backtest_setting()
ts_pro = ts.pro_api(setting['datafeed.password'])
logger = get_module_logger('system.clickhouse')
local_folder = os.path.dirname(os.path.abspath(__file__))


def disk_cache():
    def decorator(func):
        def wrapper(**kwargs):
            # 生成唯一的缓存键
            key_parts = [func.__name__]
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            date = kwargs.get('date')
            key = ":".join(key_parts)
            folder = os.path.join(local_folder, '.stock_database', date)
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
def get_stock_ticks(date, order_book_id):
    table = 'cquote.stock_tick_distributed'
    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    sql = f"""
SELECT * FROM {table}
where EventDate = '{date}'
and order_book_id = '{order_book_id}'
order by order_book_id, datetime;
    """
    df = query(sql)
    return df

__all__ = ['get_stock_ticks']