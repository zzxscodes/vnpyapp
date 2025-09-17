import os
from datetime import datetime

from vnpy_examples.high_freq.idea_001.backtest_template import template
from vnpy_examples.high_freq.idea_001.strategy_001.strategy import Strategy001
from vnpy_app.utility.functions import *

def get_backtest_params(symbol):
    commission=get_commission(symbol)
    is_rate = True if commission > 1 else False
    pricetick = get_price_tick(symbol)
    size = get_multiplier(symbol)
    params = {
        "size": size,
        "pricetick": pricetick,
        "slippage": pricetick,
        "is_rate": is_rate,
        "commission": commission,
    }
    return params


class Backtest:
    def __init__(self):
        start = datetime(2022, 7, 21)
        end = datetime(2022, 7, 30)
        strategy = Strategy001
        pwd = os.path.dirname(os.path.abspath(__file__))
        self.strategy_params = {
            'start': start,
            'end': end,
            'strategy': strategy,
            'pwd': pwd,
        }
        # ['AG', 'AL', 'AU', 'BU', 'CU', 'HC', 'NI', 'PB', 'RB', 'RU', 'SN', 'ZN']

    def ag(self):
        symbol = 'AG'
        params = get_backtest_params(symbol)
        setting = {
            'model_path': '../modeling/ag/model.txt',
            'mean_train_path': '../modeling/ag/mean_train.pkl',
            'std_train_path': '../modeling/ag/std_train.pkl',
        }
        all_params = {**self.strategy_params, **params, 'setting': setting, 'symbol': symbol}
        template(**all_params)

    def al(self):
        symbol = 'AL'
        params = get_backtest_params(symbol)
        setting = {
            'model_path': '../modeling/ag/model.txt',
            'mean_train_path': '../modeling/ag/mean_train.pkl',
            'std_train_path': '../modeling/ag/std_train.pkl',
        }
        all_params = {**self.strategy_params, **params, 'setting': setting, 'symbol': symbol}
        template(**all_params)

bt = Backtest()
bt.ag()