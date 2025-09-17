from vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy_app.utility.log import get_module_logger
from vnpy_app.utility.manager import MarketDataManager
from vnpy_app.expression.parser import calculate_field

from vnpy_app.vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
)


class DoubleMaStrategy(CtaTemplate):
    author = "用Python的交易员"

    fast_window = 10
    slow_window = 20

    parameters = ["fast_window", "slow_window"]
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        bar_size = 25
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(bar_size)
        self.em = MarketDataManager(bar_size)
        self.logger = get_module_logger(__name__)

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
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        am = self.am
        am.update_bar(bar)
        em = self.em
        em.update_bar(bar)
        if not am.inited:
            return
        df = em.market_data
        df['fast'] = calculate_field(df, f'Mean($close, {self.fast_window})')
        df['slow'] = calculate_field(df, f'Mean($close, {self.slow_window})')

        cross_over = (df['fast'].iloc[-1] > df['slow'].iloc[-1]
                      and df['fast'].iloc[-2] < df['slow'].iloc[-2])
        cross_below = (df['fast'].iloc[-1] < df['slow'].iloc[-1]
                       and df['fast'].iloc[-2] > df['slow'].iloc[-2])

        if cross_over:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)

        elif cross_below:
            if self.pos == 0:
                self.short(bar.close_price, 1)
            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

        self.put_event()

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

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
