import numpy as np
import pandas as pd

from yapo.common.time_series import TimeSeries, TimeSeriesKind

_start_period = pd.Period('2011-1', freq='M')
_end_period = pd.Period('2011-4', freq='M')
_values = np.linspace(start=1.0, stop=10.0, num=4)
_tseries = TimeSeries(values=_values,
                      start_period=_start_period,
                      end_period=_end_period,
                      kind=TimeSeriesKind.VALUES)


def test__period_getters():
    assert _tseries.start_period == _start_period
    assert _tseries.end_period == _end_period
    assert _tseries.size == _values.size
    assert _tseries.period_size == _values.size
    assert _tseries.period_range() == list(pd.period_range(start=_start_period, end=_end_period, freq='M'))


def test__values_getter():
    np.testing.assert_equal(_tseries.values, _values)
