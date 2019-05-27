from ..common.time_series import TimeSeries, TimeSeriesKind
from .._settings import _MONTHS_PER_YEAR

import numpy as np


def compute(cbr_top10_rates):
    index_total = None
    start_period = min(cbr_top10_rates['period'])
    end_period = max(cbr_top10_rates['period'])
    for month_idx in range(_MONTHS_PER_YEAR):
        rates_yearly = cbr_top10_rates['rate'].values[month_idx::_MONTHS_PER_YEAR]
        index_part = TimeSeries(values=np.repeat(rates_yearly, _MONTHS_PER_YEAR)[:len(cbr_top10_rates) - month_idx],
                                start_period=start_period + month_idx + 1,
                                end_period=end_period + 1,
                                kind=TimeSeriesKind.VALUES)
        index_part = (1 + index_part / _MONTHS_PER_YEAR).cumprod()
        index_total = index_part if index_total is None else index_total[1:] + index_part

    index_total = (index_total.pct_change() + 1.).cumprod() - 1.
    index_total = [0] + index_total
    index_total = (index_total + 1) * 100
    return index_total
