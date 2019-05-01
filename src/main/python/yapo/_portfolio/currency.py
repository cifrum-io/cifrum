import pandas as pd
from contracts import contract
from serum import inject, singleton

from .._sources.single_financial_symbol_source import CbrCurrenciesSource
from .._sources.inflation_source import InflationSource
from .._settings import _MONTHS_PER_YEAR
from ..common.enums import Currency
from ..common.time_series import TimeSeries, TimeSeriesKind


@inject
class PortfolioCurrency:
    __inflation_source: InflationSource
    __cbr_currencies_source: CbrCurrenciesSource

    def __init__(self, currency: Currency):
        self._currency = currency
        self._inflation_symbol = \
            self.__inflation_source.fetch_financial_symbol(currency.name)
        self._currency_symbol = \
            self.__cbr_currencies_source.fetch_financial_symbol(currency.name)
        self._period_min = max(
            self.inflation_start_period - 1,
            self._currency_symbol.start_period.asfreq(freq='M'),
        )
        self._period_max = min(
            self.inflation_end_period,
            self._currency_symbol.end_period.asfreq(freq='M'),
        )

    @property
    def period_min(self):
        return self._period_min

    @property
    def period_max(self):
        return self._period_max

    @property
    def inflation_start_period(self):
        return self._inflation_symbol.start_period.asfreq(freq='M')

    @property
    def inflation_end_period(self):
        return self._inflation_symbol.end_period.asfreq(freq='M')

    @property
    def value(self):
        return self._currency

    @contract(
        kind='str',
        years_ago='int,>0|None',
    )
    def inflation(self, kind,
                  end_period: pd.Period,
                  start_period: pd.Period = None,
                  years_ago: int = None):
        """
        Computes the properly reduced inflation for the currency

        :param start_period:
            the period from which the inflation is calculated
        :param end_period:
            the period to which the inflation is calculated
            is computed automatically if `years_ago` is provided
        :param years_ago:
            years back from `period_max` to calculate inflation

        :param kind:
            accumulated - accumulated inflation

            a_mean - arithmetic mean of inflation

            g_mean - geometric mean of inflation

            yoy - Year on Year inflation

            values - raw values of inflation
        :return:
        """
        if (years_ago is None) == (start_period is None):
            raise ValueError('either `start_period` or `years_ago` should be provided')

        if years_ago is not None:
            start_period = end_period - years_ago * _MONTHS_PER_YEAR + 1

        inflation_values = self._inflation_symbol.values(start_period=start_period,
                                                         end_period=end_period)

        inflation_ts = TimeSeries(values=inflation_values.value.values,
                                  start_period=inflation_values.period.min(),
                                  end_period=inflation_values.period.max(),
                                  kind=TimeSeriesKind.DIFF)

        def __accumulated():
            return (inflation_ts + 1.).prod() - 1.

        if kind == 'accumulated':
            return __accumulated()
        elif kind == 'yoy':
            return inflation_ts.ytd()
        elif kind == 'accumulated_series':
            return (inflation_ts + 1.).cumprod() - 1.
        elif kind == 'a_mean':
            inflation_amean = inflation_ts.mean()
            return inflation_amean
        elif kind == 'g_mean':
            years_total = (end_period - start_period + 1) / _MONTHS_PER_YEAR
            inflation_gmean = (__accumulated() + 1.) ** (1 / years_total) - 1.
            return inflation_gmean
        elif kind == 'values':
            return inflation_ts
        else:
            raise ValueError('inflation kind is not supported: {}'.format(kind))


@singleton
class PortfolioCurrencyFactory:

    @staticmethod
    def create(currency: Currency):
        return PortfolioCurrency(currency=currency)
