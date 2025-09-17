import lightgbm as lgb
import pandas as pd

from vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.trader.utility import BarGenerator
from vnpy_app.utility.converter import convert_ticks
from vnpy_app.utility.log import get_module_logger
from vnpy_app.vnpy_ctastrategy import CtaTemplate
from vnpy_examples.high_freq.idea_001.modeling.template import get_factors


class Strategy001(CtaTemplate):
    author = "用Python的交易员"

    parameters = []
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.ticks = []
        self.tick_size = 60
        self.tick_cnt = 0
        self.logger = get_module_logger('user.' + __name__)
        self.model = lgb.Booster(model_file=setting['model_path'])
        self.train_mean = pd.read_pickle(setting['mean_train_path'])
        self.train_std = pd.read_pickle(setting['std_train_path'])

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.ticks.append(tick)
        if len(self.ticks) >= self.tick_size:
            self.ticks = self.ticks[-self.tick_size:]
        else:
            return
        df = convert_ticks(self.ticks)
        df_all = get_factors(df)
        df_feature = df_all.drop(columns=['datetime', 'instrument', 'label'])
        df_feature = (df_feature - self.train_mean) / self.train_std
        ds_feature = lgb.Dataset(df_feature)
        pred = self.model.predict(ds_feature.data)
        if pred[0] > 0.0001 and self.pos == 0:
            self.logger.info(f"{tick.datetime}, long, {tick.last_price}")
            self.buy(tick.last_price + 1, 1)
        if pred[0] < -0.0001 and self.pos == 0:
            self.logger.info(f"{tick.datetime}, short, {tick.last_price}")
            self.short(tick.last_price - 1, 1)
        if self.pos:
            self.tick_cnt += 1
            if self.pos > 0 and self.tick_cnt > 10:
                self.logger.info(f"{tick.datetime}, close long, {tick.last_price}")
                self.sell(tick.last_price - 1, 1, )
                self.tick_cnt = 0
            elif self.pos < 0 and self.tick_cnt > 10:
                self.logger.info(f"{tick.datetime}, close short, {tick.last_price}")
                self.cover(tick.last_price + 1, 1)
                self.tick_cnt = 0
        self.bg.update_tick(tick)
        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        if bar.datetime.minute % 10 == 0:
            self.logger.info(f"{bar.datetime}")

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()
