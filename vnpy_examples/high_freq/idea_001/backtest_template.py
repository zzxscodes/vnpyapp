import os

import pandas as pd

from vnpy.trader.constant import Interval
from vnpy_app.utility.database.mysql.setting import backtest_setting
from vnpy_app.utility.functions import *
from vnpy_app.utility.log import TimeInspector
from vnpy_app.utility.warning import suppress_warnings
from vnpy_app.vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_app.vnpy_ctastrategy.base import BacktestingMode


@suppress_warnings([DeprecationWarning])
def template(symbol, strategy, pwd, start, end, commission, slippage, size, pricetick, is_rate, setting):
    backtest_setting()
    exchange_symbol = symbol + '.' + get_symbol_exchange(symbol)
    no_adjust_symbol = exchange_symbol.replace('.', '88.')
    with TimeInspector().logt(f"{symbol} backtesting"):
        engine = BacktestingEngine()
        engine.set_parameters(
            vt_symbol=no_adjust_symbol,
            interval=Interval.TICK,
            start=start,
            end=end,
            commission=commission,
            slippage=slippage,
            size=size,
            pricetick=pricetick,
            capital=10000000,
            mode=BacktestingMode.TICK,
            is_rate=is_rate
        )
        engine.add_strategy(strategy, setting)
        engine.load_data()
        engine.run_backtesting()
    result = engine.calculate_result()
    trades = engine.get_all_trades()
    statistics = engine.calculate_statistics()
    plot = engine.show_chart(result)
    folder_path = f'{pwd}/backtest'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    result.to_csv(f'{folder_path}/{symbol}_result.csv')
    pd.DataFrame(trades).to_csv(f'{folder_path}/{symbol}_trades.csv')
    pd.Series(statistics).to_frame('stat').to_csv(f'{folder_path}/{symbol}_stat.csv')
    plot.write_image(f'{folder_path}/{symbol}_plot.png')
