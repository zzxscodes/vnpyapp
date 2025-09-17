import pandas as pd


class FactorCollection:
    def __init__(self, df):
        # ask->sell, bid->buy
        self.df = df
        self.rolling_windows = [10, 15, 50]
        self.functions = ['mean', 'std', 'max', 'min', 'skew', 'kurt', 'sum', 'median']

    def _calc_wap1(self, i):
        df = self.df
        wap = (df[f'bid_price_{i}'] * df[f'ask_volume_{i}'] + df[f'ask_price_{i}'] * df[f'bid_volume_{i}']) / (
                df[f'bid_volume_{i}'] + df[f'ask_volume_{i}'])
        return wap

    def _calc_wap2(self, i):
        df = self.df
        wap = (df[f'bid_price_{i}'] * df[f'bid_volume_{i}'] + df[f'ask_price_{i}'] * df[f'ask_volume_{i}']) / (
                df[f'bid_volume_{i}'] + df[f'ask_volume_{i}'])
        return wap

    def _volume_ratio(self, i):
        df = self.df
        return df[f'bid_volume_{i}'] / df[f'ask_volume_{i}']

    def _volume_dist(self, function):
        df = self.df
        upper = df[[f'bid_volume_{i + 1}' for i in range(5)]].apply(lambda x: getattr(x, function)())
        lower = df[[f'ask_volume_{i + 1}' for i in range(5)]].apply(lambda x: getattr(x, function)())
        return upper / lower

    def calc_wap1(self, i, win, function):
        return getattr(self._calc_wap1(i).rolling(win), function)()

    def calc_wap2(self, i, win, function):
        return getattr(self._calc_wap2(i).rolling(win), function)()

    def volume_ratio(self, i, win, function):
        return getattr(self._volume_ratio(i).rolling(win), function)()

    def p_rolling_stat(self, win, func) -> pd.Series:
        df = self.df
        return getattr(df['last_price'].rolling(win), func)()

    def rtn_rolling_stat(self, win, func) -> pd.Series:
        df = self.df
        return getattr(df['last_price'].pct_change().rolling(win), func)()

    def rv_rolling_corr(self, win) -> pd.Series:
        df = self.df
        rtn = df['last_price'].pct_change()
        vol = df['volume'].diff()
        return rtn.rolling(win).corr(vol)

    def label(self):
        df = self.df
        return df['last_price'].pct_change(periods=10).shift(-10)
