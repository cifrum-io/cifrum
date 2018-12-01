import datetime as dtm
from textwrap import dedent
from typing import List

import dateutil.relativedelta
import numpy as np
import pandas as pd
from contracts import contract
from serum import inject

from .FinancialSymbolsSource import CurrencySymbolsRegistry
from .Enums import Currency, Period
from .FinancialSymbol import FinancialSymbol
from .TimeSeries import TimeSeries


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
        months_in_year = 12
        inflation = self.currency.inflation()
        inflation_values = inflation.values(start_period=self.period_min + 1, end_period=self.period_max)

        inflation = TimeSeries(values=inflation_values.value.values,
                               start_period=inflation_values.period.min(),
                               end_period=inflation_values.period.max(),
                               derivative=1)
        if isinstance(years_ago, int):
            inflation = inflation[-years_ago * months_in_year:]

        if kind == 'accumulated':
            return (inflation + 1.).prod() - 1.
        elif kind == 'a_mean':
            inflation_amean = inflation.mean()
            return inflation_amean
        elif kind == 'g_mean':
            years_total = (self.period_max - self.period_min) / months_in_year
            inflation_gmean = (self.inflation(kind='accumulated') + 1.) ** (1 / years_total) - 1.
            return inflation_gmean
        elif kind == 'values':
            return inflation
        else:
            raise Exception('inflation kind is not supported: {}'.format(kind))


@inject
class PortfolioAsset(PortfolioInflation):

    currency_symbols_registry: CurrencySymbolsRegistry

    def __init__(self, symbol: FinancialSymbol,
                 start_period: pd.Period, end_period: pd.Period, currency: Currency):
        self.symbol = symbol

        datetime_now = dtm.datetime.now()
        if (datetime_now + dtm.timedelta(days=1)).month == datetime_now.month:
            datetime_now -= dateutil.relativedelta.relativedelta(months=1)
        period_end = pd.Period(datetime_now, freq='M')  # can't use Period.now because `now` is mocked in tests
        self.period_min = max(
            pd.Period(self.symbol.start_period, freq='M'),
            start_period,
        )
        self.period_max = min(
            pd.Period(self.symbol.end_period, freq='M'),
            period_end,
            end_period,
        )
        self.values = self.__transform_values_according_to_period()

        self.currency = currency
        self.__convert_currency(currency_to=currency)

        super().__init__(self.currency, self.period_min, self.period_max)

    def __transform_values_according_to_period(self):
        vals = self.symbol.values(self.period_min, self.period_max)

        if self.symbol.period == Period.DAY:
            # we are interested in day-time data as follows
            # - if there is no data for month or more (ticker is dead, probably), we drop all data for
            #   the last available period
            # - we drop data for the period of the current month
            # - for every period we take the value that is last in each month

            if 'period' not in vals.columns:
                vals['period'] = vals['date'].dt.to_period('M')
            if self.symbol.end_period < dtm.datetime.now() - dateutil.relativedelta.relativedelta(months=1):
                vals = vals[vals['period'] < pd.Period(self.symbol.end_period, freq='M')]
            indicator__not_current_period = vals['period'] != pd.Period.now(freq='M')
            indicator__lastdate_indices = vals['period'] != vals['period'].shift(1)
            vals = vals[indicator__lastdate_indices & indicator__not_current_period].copy()
            del vals['date']

            self.period_max = min(self.period_max, vals['period'].max())
        elif self.symbol.period == Period.MONTH:
            del vals['date']
        elif self.symbol.period == Period.DECADE:
            vals = vals[vals['period'].str[-1] == '3']
            vals['period'] = vals['period'].apply(lambda p: pd.Period(p[:-2], freq='M'))
        else:
            raise Exception('Unexpected type of `period`')

        vals.sort_values(by='period', ascending=True, inplace=True)
        ts = TimeSeries(values=vals['close'].values,
                        start_period=self.period_min, end_period=self.period_max,
                        derivative=0)
        return ts

    def __convert_currency(self, currency_to: Currency):
        currency_from = self.symbol.currency
        if currency_from == currency_to:
            return

        currency_rate = self.currency_symbols_registry \
                            .convert(currency_from, currency_to, self.period_min, self.period_max)
        currency_rate = TimeSeries(values=currency_rate['close'].values,
                                   start_period=currency_rate['period'].min(),
                                   end_period=currency_rate['period'].max(),
                                   derivative=0)
        self.values = self.values * currency_rate

    def close(self):
        return self.values

    def rate_of_return(self, kind='values', real=False):
        if kind not in ['values', 'accumulated', 'ytd']:
            raise ValueError('`kind` is not in expected values')

        ror = self.values.pct_change()

        if kind == 'ytd':
            ror_ytd = ror[-self.period_max.month:]
            if real:
                inflation = self.inflation(kind='values')[-self.period_max.month:]
                ror_ytd = (ror_ytd + 1.) / (inflation + 1).cumprod() - 1.
            return (ror_ytd + 1.).cumprod() - 1.

        if kind == 'accumulated':
            ror = (ror + 1.).cumprod() - 1.

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.).cumprod() - 1.

        return ror

    def period(self):
        return pd.period_range(self.period_min, self.period_max, freq='M')

    def risk(self, period='year'):
        """
        Returns risk of the asset

        :param period:
            month - returns monthly risk

            year - returns risk approximated to yearly value
        """
        p = Portfolio(assets=[self], weights=np.array([1.0]),
                      start_period=self.period_min, end_period=self.period_max,
                      currency=self.currency)
        return p.risk(period=period)

    @contract(
        years_ago='int,>0|None|list[int,>0]',
        real='bool',
    )
    def compound_annual_growth_rate(self, years_ago=None, real=False):
        p = Portfolio(assets=[self], weights=np.array([1.0]),
                      start_period=self.period_min, end_period=self.period_max,
                      currency=self.currency)
        return p.compound_annual_growth_rate(years_ago=years_ago, real=real)

    def __repr__(self):
        asset_repr = """\
            PortfolioAsset(
                 symbol: {},
                 currency: {},
                 period_min: {},
                 period_max: {}
            )""".format(self.symbol.identifier, self.currency,
                        self.period_min, self.period_max)
        return dedent(asset_repr)


class Portfolio(PortfolioInflation):
    def __init__(self,
                 assets: List[PortfolioAsset],
                 weights: np.array,
                 start_period: pd.Period, end_period: pd.Period,
                 currency: Currency):
        self.weights = weights
        self.period_min = max(start_period, *[a.period_min for a in assets])
        self.period_max = min(end_period, *[a.period_max for a in assets])
        self.currency = currency

        super().__init__(self.currency, self.period_min, self.period_max)

        self.assets = [PortfolioAsset(symbol=a.symbol,
                                      start_period=self.period_min,
                                      end_period=self.period_max,
                                      currency=currency) for a in assets]

    def assets_weighted(self):
        return list(zip(self.assets, self.weights))

    def period(self):
        return pd.period_range(self.period_min, self.period_max, freq='M')

    def risk(self, period='year'):
        """
        Returns risk of the asset

        :param period:
            month - returns monthly risk

            year - returns risk approximated to yearly value
        """
        if period == 'month':
            ror = self.rate_of_return()
            return ror.std()
        elif period == 'year':
            if self.period_max - self.period_min < 12:
                raise Exception('year risk is request for less than 12 months')

            mean = (1. + self.rate_of_return()).mean()
            risk_monthly = self.risk(period='month')
            return np.sqrt((risk_monthly ** 2 + mean ** 2) ** 12 - mean ** 24)
        else:
            raise Exception('unexpected value of `period` {}'.format(period))

    @contract(
        years_ago='int,>0|None|list[int,>0]',
        real='bool',
    )
    def compound_annual_growth_rate(self, years_ago=None, real=False):
        months_in_year = 12
        if years_ago is None:
            years_total = (self.period_max - self.period_min) / months_in_year
            cagr = (self.rate_of_return() + 1.).prod() ** (1 / years_total) - 1.
            if real:
                cagr = (cagr + 1.) / (self.inflation(kind='accumulated') + 1.) ** (1 / years_total) - 1.
            return cagr
        elif isinstance(years_ago, list):
            return np.array([self.compound_annual_growth_rate(years_ago=y, real=real)
                             for y in years_ago])
        elif isinstance(years_ago, int):
            months_count = years_ago * months_in_year
            if self.period_min > self.period_max - months_count:
                return self.compound_annual_growth_rate(years_ago=None, real=real)

            ror_series = self.rate_of_return()[-months_count:]
            cagr = (ror_series + 1.).prod() ** (1 / years_ago) - 1.
            if real:
                inflation = self.inflation(kind='accumulated', years_ago=years_ago)
                cagr = (cagr + 1.) / (inflation + 1.) ** (1 / years_ago) - 1.
            return cagr
        else:
            raise Exception('unexpected type of `years_ago`: {}'.format(years_ago))

    def rate_of_return(self, kind='values', real=False):
        if kind not in ['values', 'accumulated', 'ytd']:
            raise ValueError('`kind` is not in expected values')

        ror_assets = np.array([a.rate_of_return() for a in self.assets])
        ror = (ror_assets * self.weights).sum()

        if kind == 'ytd':
            ror_ytd = ror[-self.period_max.month:]
            if real:
                inflation = self.inflation(kind='values')[-self.period_max.month:]
                ror_ytd = (ror_ytd + 1.) / (inflation + 1).cumprod() - 1.
            return (ror_ytd + 1.).cumprod() - 1.

        if kind == 'accumulated':
            ror = (ror + 1.).cumprod() - 1.

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.).cumprod() - 1.

        return ror

    def __repr__(self):
        assets_repr = ', '.join(asset.symbol.identifier.__repr__() for asset in self.assets)
        portfolio_repr = """\
            Portfolio(
                 assets: {},
                 currency: {},
                 start_period: {},
                 end_period: {}
            )""".format(assets_repr, self.currency,
                        self.period_min, self.period_max)
        return dedent(portfolio_repr)
