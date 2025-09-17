import pandas as pd
import numpy as np
from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager


class ArrayManagerAppend(ArrayManager):
    def __init__(self, size=100):
        super().__init__(size)
        self.datetime_array: np.ndarray = np.empty(size, dtype='datetime64[us]')

    def update_bar(self, bar: BarData) -> None:
        super().update_bar(bar)
        self.datetime_array[:-1] = self.datetime_array[1:]
        self.datetime_array[-1] = np.datetime64(bar.datetime.replace(tzinfo=None))

    @property
    def datetime(self) -> np.ndarray:
        """
        Get open price time series.
        """
        return self.datetime_array


class MarketDataManager(ArrayManagerAppend):
    def __init__(self, size: int = 100):
        super(MarketDataManager, self).__init__(size)
        self.market_data = self._format_dataframe()

    def _format_dataframe(self):
        return pd.DataFrame({
            '$open': self.open_array,
            '$high': self.high_array,
            '$low': self.low_array,
            '$close': self.close_array,
            '$volume': self.volume_array,
            '$turnover': self.turnover_array,
            '$open_interest': self.open_interest_array,
        }, index=self.datetime_array)

    def update_bar(self, bar: BarData) -> None:
        super(MarketDataManager, self).update_bar(bar)
        self.market_data = self._format_dataframe()
