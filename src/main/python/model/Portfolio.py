from .FinancialSymbol import FinancialSymbol
from .Enums import Currency, Period
import pandas as pd
import numpy as np
import datetime
from .Settings import change_column_name
from contracts import contract


class PortfolioAsset:

    def __init__(self, symbol: FinancialSymbol, weight: float, start_period, portfolio):
        self.symbol = symbol
        self.weight = weight
        self.values = self.__transform_values(start_period, pd.Period.now(freq='M'))
        self.period_min = self.values['period'].min()
        self.period_max = self.values['period'].max()
        self.portfolio = portfolio

    def __transform_values(self, start_period, end_period):
        vals = self.symbol.values(start_period, end_period)

        if self.symbol.period == Period.DAY:
            vals['period'] = vals['date'].dt.to_period('M')
            if vals['date'].max() < datetime.datetime.now() - datetime.timedelta(days=30):
                vals = vals[vals['period'] < vals['period'].max()]
            vals_not_current_period = vals['period'] != pd.Period.now(freq='M')
            vals_lastdate_indices = vals.groupby(['period'])['date'].transform(max) == vals['date']
            vals = vals[vals_not_current_period & vals_lastdate_indices]
            del vals['date']
        elif self.symbol.period == Period.MONTH:
            vals['period'] = vals['date'].dt.to_period('M')
            del vals['date']
        elif self.symbol.period == Period.DECADE:
            vals = vals[vals['period'].str[-1] == '3']
            vals['period'] = vals['period'].apply(lambda p: pd.Period(p[:-2], freq='M'))
        else:
            raise Exception('Unexpected type of `period`')

        vals.sort_values(by='period', ascending=True, inplace=True)
        vals.index = vals['period']
        return vals

    def convert_currency(self, currency_to: Currency):
        from .FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer as Fssc

        currency_from = self.symbol.currency
        if currency_from == currency_to:
            return

        currency_rate = Fssc.currency_symbols_registry().convert(currency_from, currency_to)
        self.values = self.values.merge(currency_rate, on='period', how='left', suffixes=('', '_currency_rate'))
        self.values['close'] = self.values['close'] * self.values['close_currency_rate']
        self.values.index = self.values['period']
        self.values.sort_values(by='period', ascending=True, inplace=True)
        del self.values['close_currency_rate']

    def close(self):
        return self.values['close'].values

    def close_change(self):
        return self.values[change_column_name].values

    def period(self):
        return self.values['period'].values

    def accumulated_rate_of_return(self):
        return (self.close_change() + 1.).cumprod() - 1.

    @contract(
        years_ago='int,>0|None|list[int,>0]',
    )
    def compound_annual_growth_rate(self, years_ago=None):
        months_in_year = 12
        if years_ago is None:
            years_total = (self.portfolio.period_max - self.portfolio.period_min) / months_in_year
            close_changes = self.values[change_column_name].values
            cagr = (close_changes + 1.).prod() ** (1 / years_total) - 1.
            return cagr
        elif isinstance(years_ago, list):
            return np.array([self.compound_annual_growth_rate(years_ago=y) for y in years_ago])
        else:
            months_count = years_ago * months_in_year
            if self.portfolio.period_min > self.portfolio.period_max - months_count:
                return self.compound_annual_growth_rate(years_ago=None)
            period_start = self.portfolio.period_max - months_count
            close_changes = self.values[self.values['period'] > period_start][change_column_name].values
            cagr = (close_changes + 1.).prod() ** (1 / years_ago) - 1.
            return cagr


class Portfolio:
    def __init__(self, symbols,
                 weights: np.array,
                 start_period: pd.Period,
                 end_period: pd.Period,
                 currency: Currency):
        self.weights = weights
        self.assets = []
        self.period_min = start_period
        self.period_max = end_period
        for symbol, weight in zip(symbols, weights):
            asset = PortfolioAsset(symbol, weight, start_period, self)
            self.period_min = max(self.period_min, asset.period_min)
            self.period_max = min(self.period_max, asset.period_max)
            self.assets.append(asset)

        for asset in self.assets:
            asset.values = asset.values[(asset.values['period'] >= self.period_min) &
                                        (asset.values['period'] <= self.period_max)]
            asset.convert_currency(currency_to=currency)
            asset.values[change_column_name] = asset.values['close'].pct_change().fillna(value=0.)

    def accumulated_rate_of_return(self):
        return sum(asset.accumulated_rate_of_return() * asset.weight
                   for asset in self.assets)

    @contract(
        years_ago='int,>0|None|list[int,>0]',
    )
    def compound_annual_growth_rate(self, years_ago=None):
        cagrs = np.array([asset.compound_annual_growth_rate(years_ago) for asset in self.assets])
        return np.sum(cagrs * self.weights, axis=0)
