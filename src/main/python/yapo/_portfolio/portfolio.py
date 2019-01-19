from typing import List
import dateutil.relativedelta
from serum import inject
import numpy as np
import pandas as pd
from contracts import contract
import datetime as dtm
from textwrap import dedent


from .inflation import PortfolioInflation
from .._sources.registries import CurrencySymbolsRegistry
from .._common.enums import Currency, Period
from .._common.financial_symbol import FinancialSymbol
from .._common.time_series import TimeSeries, TimeSeriesKind
from .._settings import _MONTHS_PER_YEAR


@inject
class PortfolioAsset(PortfolioInflation):

    currency_symbols_registry: CurrencySymbolsRegistry

    def __init__(self, symbol: FinancialSymbol,
                 start_period: pd.Period, end_period: pd.Period, currency: Currency):
        if end_period - start_period < 2:
            raise ValueError('period range should be at least 2 months')

        self.symbol = symbol
        self.currency = currency

        datetime_now = dtm.datetime.now()
        if (datetime_now + dtm.timedelta(days=1)).month == datetime_now.month:
            datetime_now -= dateutil.relativedelta.relativedelta(months=1)
        period_now = pd.Period(datetime_now, freq='M')
        self.period_min = max(
            pd.Period(self.symbol.start_period, freq='M'),
            self.currency.period_min,
            self.currency.inflation().start_period,
            start_period,
        )
        self.period_max = min(
            pd.Period(self.symbol.end_period, freq='M'),
            period_now,
            self.currency.period_max,
            self.currency.inflation().end_period,
            end_period,
        )
        self.values = self.__transform_values_according_to_period()

        self.currency = currency
        self.__convert_currency(currency_to=currency)

        super().__init__(self.currency, self.period_min, self.period_max)

    def __transform_values_according_to_period(self):
        vals = self.symbol.values(start_period=self.period_min, end_period=self.period_max)
        if len(vals['period']) > 0:
            self.period_min = max(self.period_min, min(vals['period']))
            self.period_max = min(self.period_max, max(vals['period']))
        # TODO: okama_dev-98
        if self.symbol.period == Period.DECADE:
            ts = TimeSeries(values=vals['rate'].values,
                            start_period=self.period_min, end_period=self.period_max,
                            kind=TimeSeriesKind.DIFF)
        else:
            ts = TimeSeries(values=vals['close'].values,
                            start_period=self.period_min, end_period=self.period_max,
                            kind=TimeSeriesKind.VALUES)
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
                                   kind=TimeSeriesKind.CURRENCY_RATE)
        self.values = self.values * currency_rate

    def close(self):
        return self.values

    def rate_of_return(self, kind='values', real=False):
        if kind not in ['values', 'accumulated', 'ytd']:
            raise ValueError('`kind` is not in expected values')

        if kind == 'ytd':
            ror = self.rate_of_return(kind='values', real=real)

            drop_first_count = None if ror.start_period.month == 1 else _MONTHS_PER_YEAR - ror.start_period.month + 1
            drop_last_count = None if ror.end_period.month == _MONTHS_PER_YEAR else -ror.end_period.month
            ror_full_yearly = ror[drop_first_count:drop_last_count]
            ror_full_yearly_splits = \
                np.split(ror_full_yearly.values,
                         ror_full_yearly.end_period.year - ror_full_yearly.start_period.year + 1)
            ror_ytd_ts = [((splt + 1.).prod() - 1.) for splt in ror_full_yearly_splits]
            ror_ytd = TimeSeries(values=np.array(ror_ytd_ts),
                                 start_period=ror_full_yearly.start_period,
                                 end_period=ror_full_yearly.end_period,
                                 kind=TimeSeriesKind.YTD)
            return ror_ytd

        ror = self.values.pct_change()

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.) - 1.

        if kind == 'accumulated':
            ror = (ror + 1.).cumprod() - 1.

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
        if end_period - start_period < 2:
            raise ValueError('period range should be at least 2 months')

        self.weights = weights
        self.currency = currency
        self.period_min = max(
            start_period,
            self.currency.period_min,
            self.currency.inflation().start_period,
            *[a.period_min for a in assets],
        )
        self.period_max = min(
            end_period,
            self.currency.period_max,
            self.currency.inflation().end_period,
            *[a.period_max for a in assets]
        )

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
            return ((risk_monthly ** 2 + mean ** 2) ** 12 - mean ** 24).sqrt()
        else:
            raise Exception('unexpected value of `period` {}'.format(period))

    @contract(
        years_ago='int,>0|None|list[int,>0]',
        real='bool',
    )
    def compound_annual_growth_rate(self, years_ago=None, real=False):
        if years_ago is None:
            years_total = (self.period_max - self.period_min) / _MONTHS_PER_YEAR
            cagr = (self.rate_of_return() + 1.).prod() ** (1 / years_total) - 1.
            if real:
                cagr = (cagr + 1.) / (self.inflation(kind='accumulated') + 1.) ** (1 / years_total) - 1.
            return cagr
        elif isinstance(years_ago, list):
            return np.array([self.compound_annual_growth_rate(years_ago=y, real=real)
                             for y in years_ago])
        elif isinstance(years_ago, int):
            months_count = years_ago * _MONTHS_PER_YEAR
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

        if kind == 'ytd':
            ror_assets = np.array([a.rate_of_return(kind='ytd', real=real) for a in self.assets])
            ror = (ror_assets * self.weights).sum()
            return ror

        ror_assets = np.array([a.rate_of_return() for a in self.assets])
        ror = (ror_assets * self.weights).sum()

        if real:
            inflation = self.inflation(kind='values')
            ror = (ror + 1.) / (inflation + 1.) - 1.

        if kind == 'accumulated':
            ror = (ror + 1.).cumprod() - 1.

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
