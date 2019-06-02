from typing import Optional, List, Dict

from serum import singleton, inject
import pandas as pd
from itertools import groupby

from .._sources.base_classes import FinancialSymbolsSource
from .._sources.single_financial_symbol_source import CbrCurrenciesSource
from .all_sources import SymbolSources
from .._settings import data_url
from ..common.financial_symbol import FinancialSymbol
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.enums import Currency


@singleton
class FinancialSymbolsRegistry:

    @inject
    def __init__(self, symbol_sources: SymbolSources):
        def symbol_source_key(x: FinancialSymbolsSource) -> str:
            return x.namespace

        symbol_sources_list: List[FinancialSymbolsSource] = \
            sorted(symbol_sources.sources, key=symbol_source_key)
        self.symbol_sources: Dict[str, List[FinancialSymbolsSource]] = {}
        for k, v in groupby(symbol_sources_list, key=symbol_source_key):
            self.symbol_sources.update({k: list(v)})

    def namespaces(self):
        return list(self.symbol_sources.keys())

    def get_all_infos(self, namespace):
        if namespace is None:
            return None
        return [name
                for sym_source in self.symbol_sources.get(namespace)
                for name in sym_source.get_all_infos()]

    def get(self, financial_symbol_id: FinancialSymbolId) -> Optional[FinancialSymbol]:
        symbol_sources_list: Optional[List[FinancialSymbolsSource]] = \
            self.symbol_sources.get(financial_symbol_id.namespace)

        if symbol_sources_list is None:
            return None

        result: List[FinancialSymbol] = []
        for symbol_source in symbol_sources_list:
            fin_symbol = symbol_source.fetch_financial_symbol(financial_symbol_id.name)
            if fin_symbol is not None:
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


@singleton
@inject
class CurrencySymbolsRegistry:
    cbr_currencies_source: CbrCurrenciesSource

    def __init__(self):
        self.url_base = data_url + 'currency/'
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
            currency_min_date = self.cbr_currencies_source._currency_min_date[currency_from.name]
            p_range = pd.period_range(start=str(currency_min_date),
                                      end=str(end_period + 1),
                                      freq='M')
            df = pd.DataFrame.from_dict({'period': p_range, 'close': 1.})
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
