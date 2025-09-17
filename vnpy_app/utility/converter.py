from dataclasses import asdict
from typing import List

import pandas as pd

from vnpy.trader.object import TickData, BarData


def convert_ticks(tick_data: List[TickData]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(tick) for tick in tick_data])
    return df


def convert_bars(bar_data: List[BarData]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(bar) for bar in bar_data])
    return df


def revert_ticks(df: pd.DataFrame) -> List[TickData]:
    ticks = []

    for _, row in df.iterrows():
        tick_dict = row.to_dict()
        tick = TickData(**tick_dict)
        ticks.append(tick)

    return ticks


def revert_bars(df: pd.DataFrame) -> List[BarData]:
    bars = []

    for _, row in df.iterrows():
        bar_dict = row.to_dict()
        bar = BarData(**bar_dict)
        bars.append(bar)

    return bars

__all__ = [
    "convert_ticks",
    "convert_bars",
    "revert_ticks",
    "revert_bars"
]