import os

import numpy as np
import pandas as pd

from vnpy_app.utility.database.mysql.loader import load_ticks
from vnpy_app.utility.functions import *
from vnpy_app.utility.log import TimeInspector
from vnpy_examples.high_freq.idea_001.modeling.template import *


def get_dataset():
    beg = '2022-07-01'
    end = '2022-10-01'
    # end = '2023-07-01'
    exchange = get_exchange('SHFE')
    symbol = 'AG'
    if os.path.exists('tick_data.parquet'):
        with TimeInspector.logt('load_ticks_with_cache'):
            df = pd.read_parquet('tick_data.parquet')
    else:
        with TimeInspector.logt('load_ticks_without_cache'):
            df = load_ticks(symbol + '88', exchange, beg, end)
            df.drop(columns=['exchange'], inplace=True)
            df.to_parquet('tick_data.parquet')
    df_factors = get_factors(df)
    df_factors['label'] = df_factors['label'].mask(df_factors['label'].abs() >= 0.005, np.nan)
    df_factors['datetime'] = pd.to_datetime(df_factors['datetime'])
    df_factors.set_index(['datetime', 'instrument'], inplace=True)
    df_factors.to_parquet('dataset.parquet')


def main():
    get_dataset()
    train_regress_model()
    regress_model()
    """
             predictions    labels
predictions     1.000000  0.405845
labels          0.405845  1.000000
             predictions    labels
predictions     1.000000  0.455736
labels          0.455736  1.000000
[2656818:MainThread](2025-07-30 10:50:44,836) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:153] - predictions normal
[2656818:MainThread](2025-07-30 10:50:44,855) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:154] - 0.00012396483961273926
[2656818:MainThread](2025-07-30 10:50:44,874) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:155] - -0.00011912446727514657
[2656818:MainThread](2025-07-30 10:50:44,893) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:156] - 0.5306247722084748
[2656818:MainThread](2025-07-30 10:50:44,913) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:157] - 0.5186728516392798
[2656818:MainThread](2025-07-30 10:50:44,931) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:158] - 52131
[2656818:MainThread](2025-07-30 10:50:44,950) INFO - system.user.vnpy_examples.high_freq.idea_001.modeling.template - [template.py:159] - 63595
    """


if __name__ == '__main__':
    main()
