import unittest
from datetime import datetime

from vnpy.trader.constant import Interval
from vnpy_app.utility.database.mysql.setting import backtest_setting
from vnpy_app.vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy_app.utility.log import TimeInspector


class MyTestCase(unittest.TestCase):
    def test_something3(self):
        # takes: 30s
        from vnpy_examples.intraday_strategy.double_ma_strategy.expression_strategy.double_ma_strategy_ops import DoubleMaStrategy
        self.start = datetime(2015, 1, 1)
        self.end = datetime(2015, 4, 1)
        backtest_setting()
        engine = BacktestingEngine()
        engine.set_parameters(
            vt_symbol="IF88.CFFEX",
            interval=Interval.MINUTE,
            start=self.start,
            end=self.end,
            commission=0.3 / 10000,
            slippage=0.2,
            size=300,
            pricetick=0.2,
            capital=1000000,
        )
        engine.add_strategy(DoubleMaStrategy, {})
        engine.load_data()
        with TimeInspector().logt("backtesting"):
            engine.run_backtesting()
        df = engine.calculate_result()
        engine.calculate_statistics()
        engine.show_chart()
        print(df)


if __name__ == '__main__':
    unittest.main()
