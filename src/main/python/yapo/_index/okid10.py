from ..common.time_series import TimeSeries, TimeSeriesKind
from .._settings import _MONTHS_PER_YEAR

import numpy as np


def compute(cbr_top10_rates):
    index_total = None
    for month_idx in range(_MONTHS_PER_YEAR):
        rates_yearly = cbr_top10_rates['rate'].values[month_idx::_MONTHS_PER_YEAR]
        index_part = TimeSeries(values=np.repeat(rates_yearly, _MONTHS_PER_YEAR)[:len(cbr_top10_rates) - month_idx],
                                start_period=min(cbr_top10_rates['period']) + month_idx + 1,
                                end_period=max(cbr_top10_rates['period']) + 1,
                                kind=TimeSeriesKind.DIFF)
        index_part = (1 + index_part / _MONTHS_PER_YEAR).cumprod()
        index_total = index_part if index_total is None else index_total[1:] + index_part

    index_total *= 100
    return index_total
