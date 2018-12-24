import pandas as pd
from contracts import contract

from .._settings import _MONTHS_PER_YEAR
from .._common.enums import Currency
from .._common.time_series import TimeSeries, TimeSeriesKind


class PortfolioInflation:
    def __init__(self, currency: Currency,
                 period_min: pd.Period, period_max: pd.Period):
        self.currency = currency
        self.period_min = period_min
        self.period_max = period_max

    @contract(
        kind='str',
        years_ago='int,>0|None',
    )
    def inflation(self, kind, years_ago=None):
        """
        Computes the properly reduced inflation for the currency

        :param years_ago:
            years back from `period_max` to calculate inflation

        :param kind:
            accumulated - accumulated inflation

            a_mean - arithmetic mean of inflation

            g_mean - geometric mean of inflation

            values - raw values of inflation
        :return:
        """
        inflation = self.currency.inflation()
        inflation_values = inflation.values(start_period=self.period_min + 1, end_period=self.period_max)

        inflation = TimeSeries(values=inflation_values.value.values,
                               start_period=inflation_values.period.min(),
                               end_period=inflation_values.period.max(),
                               kind=TimeSeriesKind.DIFF)
        if isinstance(years_ago, int):
            inflation = inflation[-years_ago * _MONTHS_PER_YEAR:]

        if kind == 'accumulated':
            return (inflation + 1.).prod() - 1.
        elif kind == 'a_mean':
            inflation_amean = inflation.mean()
            return inflation_amean
        elif kind == 'g_mean':
            years_total = (self.period_max - self.period_min) / _MONTHS_PER_YEAR
            inflation_gmean = (self.inflation(kind='accumulated') + 1.) ** (1 / years_total) - 1.
            return inflation_gmean
        elif kind == 'values':
            return inflation
        else:
            raise Exception('inflation kind is not supported: {}'.format(kind))
