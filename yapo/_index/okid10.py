from typing import Optional

from ..common.time_series import TimeSeries, TimeSeriesKind
from .._settings import _MONTHS_PER_YEAR

import numpy as np
import pandas as pd


def compute(cbr_top10_rates: pd.DataFrame) -> TimeSeries:
    index_total: Optional[TimeSeries] = None
    start_period: pd.Period = cbr_top10_rates['period'].min()
    end_period: pd.Period = cbr_top10_rates['period'].max()
    for month_idx in range(_MONTHS_PER_YEAR):
        rates_yearly = cbr_top10_rates['rate'].values[month_idx::_MONTHS_PER_YEAR]
        index_part = TimeSeries(values=np.repeat(rates_yearly, _MONTHS_PER_YEAR)[:len(cbr_top10_rates) - month_idx],
                                start_period=start_period + month_idx + 1,
                                end_period=end_period + 1,
                                kind=TimeSeriesKind.VALUES)
        index_part = (1 + index_part / _MONTHS_PER_YEAR).cumprod()
        index_total = index_part if index_total is None else index_total[1:] + index_part

    if index_total is None:
        raise Exception('`index_total` should not be `None`')
    result: TimeSeries = index_total
    result = (result.pct_change() + 1.).cumprod() - 1.
    result = [0] + result
    result = (result + 1) * 100
    return result
