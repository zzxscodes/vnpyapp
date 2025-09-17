from datetime import time

import pandas as pd

from function import plot_lob
from vnpy_app.utility.log import get_module_logger

logger = get_module_logger('user.' + __name__)
logger.info('begin reading data')
df = pd.read_parquet('../tick_data.parquet')
df['rtn'] = ((df['ask_price_1'] + df['bid_price_1']) / 2).pct_change(periods=10).shift(-10)
df['time'] = df['datetime'].dt.tz_localize(None).dt.time
logger.info('end reading data')

threshold = 2e-3
window_len = 10
df = df.iloc[window_len: window_len + 100000]
day_time = lambda x: time(9, 5, 0) < x < time(14, 55, 0)
night_time = lambda x: time(21, 5, 0) < x or x < time(2, 25, 0)
df = df[df['time'].apply(day_time) | df['time'].apply(night_time)]
idxes = df[abs(df['rtn']) > threshold].index
logger.info('start plotting')
for idx in idxes[:1]:
    idx_pos = df.index.get_loc(idx)
    beg_pos = idx_pos - window_len
    end_pos = idx_pos + window_len
    datetime = df.loc[idx, 'datetime']
    label = df.loc[idx, 'rtn']
    if beg_pos < 0:
        continue
    selected_df = df.iloc[beg_pos + 1:end_pos + 1]
    logger.info(f'plotting {datetime}')
    fig = plot_lob(selected_df, label)
    logger.info(f'plotting {datetime} done')
    fig.savefig(f'{datetime}.jpg')
