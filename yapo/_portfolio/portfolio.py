import copy
import datetime as dtm
from textwrap import dedent
from typing import List, Dict

import dateutil.relativedelta
import numpy as np
import pandas as pd
from contracts import contract
from serum import inject

from .currency import PortfolioCurrencyFactory
from .._settings import _MONTHS_PER_YEAR
from .._sources.registries import CurrencySymbolsRegistry
from ..common.enums import Currency, Period
from ..common.financial_symbol import FinancialSymbol
from ..common.time_series import TimeSeries, TimeSeriesKind


@inject
class PortfolioAsset:
    currency_symbols_registry: CurrencySymbolsRegistry
    portfolio_currency_factory: PortfolioCurrencyFactory

    def __init__(self, symbol: FinancialSymbol,
                 start_period: pd.Period, end_period: pd.Period, currency: Currency,
                 portfolio: 'Portfolio' = None,
                 weight: int = None):
        if (end_period - start_period).n < 2:
            raise ValueError('period range should be at least 2 months')

        self.symbol = symbol
        self.currency = self.portfolio_currency_factory.create(currency=currency)
        self._portfolio = portfolio
        self._weight = weight

        datetime_now = dtm.datetime.now()
        if (datetime_now + dtm.timedelta(days=1)).month == datetime_now.month:
            datetime_now -= dateutil.relativedelta.relativedelta(months=1)
        period_now = pd.Period(datetime_now, freq='M')
        self._period_min = max(
            pd.Period(self.symbol.start_period, freq='M'),
            self.currency.period_min,
            start_period,
        )
        self._period_max = min(
            pd.Period(self.symbol.end_period, freq='M'),
            period_now,
            self.currency.period_max,
            end_period,
        )
        if self._period_min >= self._period_max:
            raise ValueError('`self._period_min` must not be >= `self._period_max`')

        currency_conversion_rate = self.__currency_conversion_rate(currency_to=self.currency.value)
        self._period_min = max(self._period_min, currency_conversion_rate.start_period)
        self._period_max = min(self._period_max, currency_conversion_rate.end_period)

        self.__values = self.__transform_values_according_to_period()

    @property
    def portfolio(self):
        return self._portfolio

    @property
    def weight(self):
        return self._weight

    def __transform_values_according_to_period(self):
        vals = self.symbol.values(start_period=self._period_min, end_period=self._period_max)
        if len(vals['period']) > 0:
            self._period_min = max(self._period_min, vals['period'].min())
            self._period_max = min(self._period_max, vals['period'].max())
        # TODO: okama_dev-98
        if self.symbol.period == Period.DECADE:
            ts = TimeSeries(values=vals['rate'].values,
                            start_period=self._period_min, end_period=self._period_max,
                            kind=TimeSeriesKind.DIFF)
        else:
            ts = TimeSeries(values=vals['close'].values,
                            start_period=self._period_min, end_period=self._period_max,
                            kind=TimeSeriesKind.VALUES)
        currency_conversion_rate = self.__currency_conversion_rate(currency_to=self.currency.value)
        ts = ts * currency_conversion_rate
        return ts

    def __currency_conversion_rate(self, currency_to: Currency):
        currency_from = self.symbol.currency
        currency_rate = self.currency_symbols_registry \
            .convert(currency_from=currency_from,
                     currency_to=currency_to,
                     start_period=self._period_min,
                     end_period=self._period_max)
        currency_rate = TimeSeries(values=currency_rate['close'].values,
                                   start_period=currency_rate['period'].min(),
                                   end_period=currency_rate['period'].max(),
                                   kind=TimeSeriesKind.CURRENCY_RATE)
        return currency_rate

    def close(self):
        return copy.deepcopy(self.__values)

    def get_return(self, kind='values', real=False):
        if kind not in ['values', 'cumulative', 'ytd']:
            raise ValueError('`kind` is not in expected values')

        if kind == 'ytd':
            ror = self.get_return(kind='values', real=real)
            ror_ytd = ror.ytd()
            return ror_ytd

        ror = self.close().pct_change()

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.) - 1.

        if kind == 'cumulative':
            ror = (ror + 1.).cumprod() - 1.

        return ror

    def risk(self, period='year'):
        """
        Returns risk of the asset

        :param period:
            month - returns monthly risk

            year - returns risk approximated to yearly value
        """
        p = Portfolio(assets=[self], weights=np.array([1.0]),
                      start_period=self._period_min,
                      end_period=self._period_max,
                      currency=self.currency.value)
        return p.risk(period=period)

    @contract(
        years_ago='int,>0|None|list[int,>0]',
        real='bool',
    )
    def get_cagr(self, years_ago=None, real=False):
        p = Portfolio(assets=[self], weights=np.array([1.0]),
                      start_period=self._period_min,
                      end_period=self._period_max,
                      currency=self.currency.value)
        return p.get_cagr(years_ago=years_ago, real=real)

    def inflation(self, kind: str, years_ago: int = None):
        ror = self.get_return()
        start_period = None if years_ago else ror.start_period
        return self.currency.inflation(kind=kind,
                                       start_period=start_period, end_period=ror.end_period,
                                       years_ago=years_ago)

    def __repr__(self):
        asset_repr = """\
            PortfolioAsset(
                 symbol: {},
                 currency: {},
                 period_min: {},
                 period_max: {}
            )""".format(self.symbol.identifier, self.currency,
                        self._period_min, self._period_max)
        return dedent(asset_repr)


@inject
class Portfolio:
    portfolio_currency_factory: PortfolioCurrencyFactory

    def __init__(self,
                 assets: List[PortfolioAsset],
                 weights: np.array,
                 start_period: pd.Period, end_period: pd.Period,
                 currency: Currency):
        self.weights = weights
        self.currency = self.portfolio_currency_factory.create(currency=currency)

        self._assets = [PortfolioAsset(symbol=a.symbol,
                                       start_period=start_period,
                                       end_period=end_period,
                                       currency=currency,
                                       portfolio=self,
                                       weight=w) for a, w in zip(assets, weights)]

    @property
    def assets(self) -> Dict[str, PortfolioAsset]:
        assets_dict = {a.symbol.identifier_str: a for a in self._assets}
        return assets_dict

    def risk(self, period='year'):
        """
        Returns risk of the asset

        :param period:
            month - returns monthly risk

            year - returns risk approximated to yearly value
        """
        if period == 'month':
            ror = self.get_return()
            return ror.std()
        elif period == 'year':
            ror = self.get_return()
            if ror.period_size < 12:
                raise Exception('year risk is requested for less than 12 months')

            mean = (1. + ror).mean()
            risk_monthly = self.risk(period='month')
            risk_yearly = ((risk_monthly ** 2 + mean ** 2) ** 12 - mean ** 24).sqrt()
            return risk_yearly
        else:
            raise Exception('unexpected value of `period` {}'.format(period))

    @contract(
        years_ago='int,>0|None|list[int,>0]',
        real='bool',
    )
    def get_cagr(self, years_ago=None, real=False):
        if years_ago is None:
            ror = self.get_return()
            years_total = ror.period_size / _MONTHS_PER_YEAR
            ror_c = (ror + 1.).prod()
            cagr = ror_c ** (1 / years_total) - 1.
            if real:
                inflation_cumulative = self.inflation(kind='cumulative')
                cagr = (cagr + 1.) / (inflation_cumulative + 1.) ** (1 / years_total) - 1.
            return cagr
        elif isinstance(years_ago, list):
            return np.array([self.get_cagr(years_ago=y, real=real)
                             for y in years_ago])
        elif isinstance(years_ago, int):
            ror = self.get_return()
            months_count = years_ago * _MONTHS_PER_YEAR
            if ror.period_size < months_count:
                return self.get_cagr(years_ago=None, real=real)

            ror_slice = self.get_return()[-months_count:]
            ror_slice_c = (ror_slice + 1.).prod()
            cagr = ror_slice_c ** (1 / years_ago) - 1.
            if real:
                inflation_cumulative = self.inflation(kind='cumulative',
                                                      years_ago=years_ago)
                cagr = (cagr + 1.) / (inflation_cumulative + 1.) ** (1 / years_ago) - 1.
            return cagr
        else:
            raise Exception('unexpected type of `years_ago`: {}'.format(years_ago))

    def get_return(self, kind='values', real=False) -> TimeSeries:
        if kind not in ['values', 'cumulative', 'ytd']:
            raise ValueError('`kind` is not in expected values')

        if kind == 'ytd':
            ror_assets = np.array([a.get_return(kind=kind, real=real) for a in self._assets])
            ror = (ror_assets * self.weights).sum()
            return ror

        ror_assets = np.array([a.get_return() for a in self._assets])
        ror = (ror_assets * self.weights).sum()

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.) - 1.

        if kind == 'cumulative':
            ror = (ror + 1.).cumprod() - 1.

        return ror

    def inflation(self, kind: str, years_ago: int = None):
        ror = self.get_return()
        start_period = None if years_ago else ror.start_period
        return self.currency.inflation(kind=kind,
                                       start_period=start_period,
                                       end_period=ror.end_period,
                                       years_ago=years_ago)

    def __repr__(self):
        assets_repr = ', '.join(asset.symbol.identifier.__repr__() for asset in self._assets)
        portfolio_repr = """\
            Portfolio(
                 assets: {},
                 currency: {},
            )""".format(assets_repr, self.currency)
        return dedent(portfolio_repr)
