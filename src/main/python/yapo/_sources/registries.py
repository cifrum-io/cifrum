from serum import singleton, inject
import pandas as pd
from itertools import groupby

from .all_sources import SymbolSources
from .._settings import rostsber_url
from .._common.financial_symbol_id import FinancialSymbolId
from .._common.enums import Currency


@singleton
class FinancialSymbolsRegistry:

    @inject
    def __init__(self, symbol_sources: SymbolSources):
        def symbol_source_key(x): return x.namespace

        symbol_sources = sorted(symbol_sources.sources, key=symbol_source_key)
        self.symbol_sources = {}
        for k, v in groupby(symbol_sources, key=symbol_source_key):
            self.symbol_sources.update({k: list(v)})

    def namespaces(self):
        return list(self.symbol_sources.keys())

    def get_all_infos(self, namespace):
        if namespace is None:
            return None
        return [name
                for sym_source in self.symbol_sources.get(namespace)
                for name in sym_source.get_all_infos()]

    def get(self, financial_symbol_id: FinancialSymbolId):
        if financial_symbol_id.namespace in self.symbol_sources.keys():
            result = []
            for symbol_source in self.symbol_sources.get(financial_symbol_id.namespace):
                fin_symbol = symbol_source.fetch_financial_symbol(financial_symbol_id.name)
                if fin_symbol:
                    result.append(fin_symbol)
            result_count = len(result)
            if result_count == 1:
                return result[0]
            elif result_count == 0:
                return None
            else:
                raise Exception('Something went wrong. {} names are found for {}. '
                                'Please, submit the issue'
                                .format(result_count, financial_symbol_id.format()))
        else:
            return None


@singleton
class CurrencySymbolsRegistry:
    def __init__(self):
        self.url_base = rostsber_url + 'currency/'
        currency_index = pd.read_csv('{}__index.csv'.format(self.url_base),
                                     sep='\t', parse_dates=['date_start', 'date_end'])
        self.__f_currency_data = {}
        for supported_currency_pair in currency_index['name']:
            url = '{}{}.csv'.format(self.url_base, supported_currency_pair)
            df = pd.read_csv(url, sep='\t', parse_dates=['date'])
            df['period'] = df['date'].dt.to_period('M')
            vals_lastdate_indices = df.groupby(['period'])['date'].transform(max) == df['date']
            df = df[vals_lastdate_indices].copy()
            df['close'] = df['close'] * df['nominal']
            del df['date'], df['nominal']
            supported_currency_pair = tuple(str.split(supported_currency_pair, '-'))
            self.__f_currency_data.update({supported_currency_pair: df})

    def __currency_data(self, currency_pair):
        return self.__f_currency_data[currency_pair].copy()

    def convert(self, currency_from: Currency, currency_to: Currency,
                start_period: pd.Period, end_period: pd.Period):
        if currency_to == currency_from:
            df = self.__currency_data(('USD', 'RUB'))
            df['close'] = 1.0
        elif currency_to == Currency.RUB:
            df = self.__currency_data((currency_from.name, currency_to.name))
        elif currency_from == Currency.RUB:
            df = self.convert(currency_to, currency_from, start_period, end_period)
            df['close'] = 1.0 / df['close']
        else:
            df = self.convert(currency_from, Currency.RUB, start_period, end_period)
            df_to = self.convert(Currency.RUB, currency_to, start_period, end_period)
            df = df.merge(df_to, on='period', suffixes=('', '_to'))
            df['close'] = df['close'] * df['close_to']
            del df['close_to']

        df = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
        df.sort_values(by='period', ascending=True, inplace=True)
        return df
