import datetime as dtm
from abc import ABCMeta, abstractmethod
from itertools import groupby
from pprint import pformat

import numpy as np
import pandas as pd
import quandl
from serum import dependency, inject

from model.Settings import *
from . import Settings
from .Enums import Currency, SecurityType, Period
from .FinancialSymbol import FinancialSymbol
from .FinancialSymbolId import FinancialSymbolId
from .FinancialSymbolInfo import FinancialSymbolInfo


def _load_inflation_values(inflation_country):
    df = pd.read_csv('{}inflation_{}/data.csv'.format(rostsber_url, inflation_country), sep='\t')
    df['period'] = pd.to_datetime(df['date']).dt.to_period('M')
    df.sort_values(by='period', inplace=True)
    df.rename(columns={'close': change_column_name}, inplace=True)
    return df


def _load_inflation_index(inflation_country):
    dt = pd.read_csv('{}inflation_{}/__index.csv'.format(rostsber_url, inflation_country), sep='\t')
    return dt


def _load_inflation_date(inflation_country, kind):
    index = _load_inflation_index(inflation_country)
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


def _load_toprates():
    dt = pd.read_csv('{}cbr_deposit_rate/data.csv'.format(rostsber_url), sep='\t')
    dt.sort_values(by='decade', inplace=True)
    dt.rename(columns={'close': change_column_name, 'decade': 'date'},
              inplace=True)
    return dt


def _load_cbr_deposit_rate_date(kind):
    index = pd.read_csv('{}cbr_deposit_rate/__index.csv'.format(rostsber_url), sep='\t')
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


def _load_micex_mcftr_date(kind):
    index = pd.read_csv(rostsber_url + 'moex/mcftr/__index.csv', sep='\t')
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


class FinancialSymbolsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def fetch_financial_symbol(self, name: str):
        raise Exception('should not be called')

    def __repr__(self):
        return pformat(vars(self))

    def get_all_infos(self):
        raise Exception('should not be called')


class SingleFinancialSymbolSource(FinancialSymbolsSource):
    def __extract_values(self, start_period, end_period):
        df = self.__values_fetcher()
        df['date'] = pd.to_datetime(df['date'])
        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def __init__(self, values_fetcher, namespace, name, start_period, end_period,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        super().__init__(namespace)
        self.name = name
        self.__values_fetcher = values_fetcher
        self.financial_symbol = \
            FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=self.name),
                            values=self.__extract_values,
                            isin=isin,
                            short_name=short_name,
                            long_name=long_name,
                            start_period=start_period,
                            end_period=end_period,
                            exchange=exchange,
                            currency=currency,
                            security_type=security_type,
                            period=period,
                            adjusted_close=adjusted_close)

    def fetch_financial_symbol(self, name: str):
        return self.financial_symbol if name == self.name else None

    def get_all_infos(self):
        fin_sym_info = FinancialSymbolInfo(
            fin_sym_id=self.financial_symbol.identifier,
            short_name=self.financial_symbol.short_name
        )
        return [fin_sym_info]


@dependency
class CbrTopRatesSource(SingleFinancialSymbolSource):
    def __init__(self):
        super().__init__(
            namespace='cbr',
            name='TOP_rates',
            values_fetcher=lambda: _load_toprates(),
            start_period=_load_cbr_deposit_rate_date('date_start'),
            end_period=_load_cbr_deposit_rate_date('date_end'),
            long_name='Динамика максимальной процентной ставки (по вкладам в российских рублях)',
            currency=Currency.RUB,
            security_type=SecurityType.RATES,
            period=Period.DECADE,
            adjusted_close=False,
        )


@dependency
class MicexMcftrSource(SingleFinancialSymbolSource):
    def __init__(self):
        super().__init__(
            namespace='micex',
            name='MCFTR',
            values_fetcher=lambda: pd.read_csv(rostsber_url + 'moex/mcftr/data.csv', sep='\t'),
            start_period=_load_micex_mcftr_date('date_start'),
            end_period=_load_micex_mcftr_date('date_end'),
            short_name='MICEX Total Return',
            currency=Currency.RUB,
            security_type=SecurityType.INDEX,
            period=Period.DAY,
            adjusted_close=False,
        )


@dependency
class InflationRuSource(SingleFinancialSymbolSource):
    def __init__(self):
        super().__init__(
            namespace='infl',
            name=Currency.RUB.name,
            values_fetcher=lambda: _load_inflation_values('ru'),
            start_period=_load_inflation_date(inflation_country='ru', kind='date_start'),
            end_period=_load_inflation_date(inflation_country='ru', kind='date_end'),
            short_name='Инфляция РФ',
            currency=Currency.RUB,
            security_type=SecurityType.INFLATION,
            period=Period.MONTH,
            adjusted_close=False,
        )


@dependency
class InflationEuSource(SingleFinancialSymbolSource):
    def __init__(self):
        super().__init__(
            namespace='infl',
            name=Currency.EUR.name,
            values_fetcher=lambda: _load_inflation_values('eu'),
            start_period=_load_inflation_date(inflation_country='eu', kind='date_start'),
            end_period=_load_inflation_date(inflation_country='eu', kind='date_end'),
            short_name='Инфляция ЕС',
            currency=Currency.EUR,
            security_type=SecurityType.INFLATION,
            period=Period.MONTH,
            adjusted_close=False,
        )


@dependency
class InflationUsSource(SingleFinancialSymbolSource):
    def __init__(self):
        super().__init__(
            namespace='infl',
            name=Currency.USD.name,
            values_fetcher=lambda: _load_inflation_values('us'),
            start_period=_load_inflation_date(inflation_country='us', kind='date_start'),
            end_period=_load_inflation_date(inflation_country='us', kind='date_end'),
            short_name='Инфляция США',
            currency=Currency.USD,
            security_type=SecurityType.INFLATION,
            period=Period.MONTH,
            adjusted_close=False,
        )


@dependency
class CbrCurrenciesSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='cbr')
        self.url_base = Settings.rostsber_url + 'currency/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.__short_names = {
            Currency.RUB: 'Рубль РФ',
            Currency.USD: 'Доллар США',
            Currency.EUR: 'Евро',
        }
        self.__currency_min_date = {
            Currency.RUB.name: pd.Period('1990', freq='M'),
            Currency.USD.name: pd.Period('1900', freq='M'),
            Currency.EUR.name: pd.Period('1999', freq='M'),
        }

    def __currency_values(self, name, start_period, end_period):
        start_period = max(start_period, self.__currency_min_date[name])
        end_period = min(end_period, pd.Period.now(freq='M'))
        date_range = pd.date_range(start=start_period.to_timestamp(),
                                   end=(end_period + 1).to_timestamp(),
                                   freq='D')
        df = pd.DataFrame({'date': date_range, 'close': 1.0})

        period = df['date'].dt.to_period('M')
        df_new = df[(start_period <= period) & (period <= end_period)].copy()
        return df_new

    def fetch_financial_symbol(self, name: str):
        currency = Currency.__dict__.get(name)
        if currency is None:
            return None
        else:
            fs = FinancialSymbol(
                identifier=FinancialSymbolId(namespace='cbr', name=name),
                values=lambda start_period, end_period: self.__currency_values(name, start_period, end_period),
                short_name=self.__short_names[currency],
                start_period=self.__currency_min_date[currency.name],
                end_period=dtm.datetime.now(),
                currency=currency,
                security_type=SecurityType.CURRENCY,
                period=Period.DAY,
                adjusted_close=True
            )
            return fs

    def get_all_infos(self):
        return [
            FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, short_name.name),
                short_name=short_name
            ) for short_name in self.__short_names.keys()
        ]


@dependency
class MicexStocksSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='micex')
        self.url_base = Settings.rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.index['date_start'] = pd.to_datetime(self.index['date_start'])
        self.index['date_end'] = pd.to_datetime(self.index['date_end'])

    def __extract_values(self, secid, start_period, end_period):
        df = pd.read_csv(self.url_base + secid + '.csv', sep='\t')
        df['date'] = pd.to_datetime(df['date'])
        period = df['date'].dt.to_period('M')
        df_new = df[(start_period <= period) & (period <= end_period)].copy()
        return df_new

    def fetch_financial_symbol(self, name: str):
        if name not in self.index.index:
            return None
        row = self.index.loc[name]
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                 values=lambda start_period, end_period:
                                 self.__extract_values(name, start_period, end_period),
                                 exchange='MICEX',
                                 start_period=row['date_start'],
                                 end_period=row['date_end'],
                                 short_name=row['short_name'],
                                 long_name=row['long_name'],
                                 isin=row['isin'],
                                 currency=Currency.RUB,
                                 security_type=SecurityType.STOCK_ETF,
                                 period=Period.DAY,
                                 adjusted_close=True)
        return symbol

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fin_sym_info = FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, idx),
                short_name=row['short_name']
            )
            infos.append(fin_sym_info)
        return infos


@dependency
class NluSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='nlu')
        self.url_base = Settings.rostsber_url + 'mut_rus/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t')

        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.index['date_start'] = pd.to_datetime(self.index['date_start'])
        self.index['date_end'] = pd.to_datetime(self.index['date_end'])
        assert self.index.index.dtype == np.int64

    def __extract_values(self, row_id, start_period, end_period):
        url = '{}{}.csv'.format(self.url_base, row_id)
        df = pd.read_csv(url, sep='\t')
        df['date'] = pd.to_datetime(df['date'])
        period = df['date'].dt.to_period('M')
        df_new = df[(start_period <= period) & (period <= end_period)].copy()
        return df_new

    def fetch_financial_symbol(self, name: str):
        try:
            name_int = int(name)
        except ValueError:
            return None
        if name_int not in self.index.index:
            return None
        row = self.index.loc[name_int]
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                 values=lambda start_period, end_period:
                                 self.__extract_values(name, start_period, end_period),
                                 short_name=row['short_name'],
                                 start_period=row['date_start'],
                                 end_period=row['date_end'],
                                 currency=Currency.RUB,
                                 security_type=SecurityType.MUT,
                                 period=Period.DAY,
                                 adjusted_close=True)
        return symbol

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fin_sym_info = FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, str(idx)),
                short_name=row['short_name']
            )
            infos.append(fin_sym_info)
        return infos


@dependency
class QuandlSource(FinancialSymbolsSource):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self):
        super().__init__(namespace='quandl')
        self.url_base = Settings.rostsber_url + 'quandl/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.index['date_start'] = pd.to_datetime(self.index['date_start'])
        self.index['date_end'] = pd.to_datetime(self.index['date_end'])

    @staticmethod
    def __extract_values(name, start_period, end_period):
        df = quandl.get('EOD/{}.11'.format(name),
                        start_date=start_period.to_timestamp().strftime('%Y-%m-%d'),
                        end_date=end_period.to_timestamp('M').strftime('%Y-%m-%d'),
                        collapse='monthly')
        df_res = pd.DataFrame()
        df_res['close'] = df['Adj_Close']
        df_res['date'] = df_res.index
        return df_res

    def fetch_financial_symbol(self, name: str):
        if name in self.index.index:
            symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                     values=lambda start_period, end_period:
                                         self.__extract_values(name, start_period, end_period),
                                     exchange=self.index.loc[name, 'exchange'],
                                     short_name=self.index.loc[name, 'short_name'],
                                     start_period=self.index.loc[name, 'date_start'],
                                     end_period=self.index.loc[name, 'date_end'],
                                     currency=Currency.USD,
                                     security_type=SecurityType.STOCK_ETF,
                                     period=Period.DAY,
                                     adjusted_close=True)
            return symbol
        return None

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fsi = FinancialSymbolId(self.namespace, str(idx)).format()
            fs_info = FinancialSymbolInfo(fin_sym_id=fsi, short_name=idx)
            infos.append(fs_info)
        return infos


@dependency
class SymbolSources(metaclass=ABCMeta):
    @property
    @abstractmethod
    def sources(self):
        raise NotImplementedError()


@inject
class AllSymbolSources(SymbolSources):
    cbr_currencies_source: CbrCurrenciesSource
    cbr_top_rates_source: CbrTopRatesSource
    inflation_ru_source: InflationRuSource
    inflation_eu_source: InflationEuSource
    inflation_us_source: InflationUsSource
    micex_mcftr_source: MicexMcftrSource
    micex_stocks_source: MicexStocksSource
    nlu_muts_source: NluSource
    quandl_source: QuandlSource

    @property
    def sources(self):
        return [
            self.cbr_currencies_source,
            self.cbr_top_rates_source,
            self.inflation_ru_source,
            self.inflation_eu_source,
            self.inflation_us_source,
            self.micex_mcftr_source,
            self.micex_stocks_source,
            self.nlu_muts_source,
            self.quandl_source,
        ]


@dependency
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


@dependency
class CurrencySymbolsRegistry:
    def __init__(self):
        self.url_base = Settings.rostsber_url + 'currency/'

    def convert(self, currency_from: Currency, currency_to: Currency,
                start_period: pd.Period, end_period: pd.Period):
        if currency_to == currency_from:
            url = '{}{}-{}.csv'.format(self.url_base, 'USD', 'RUB')
            df = pd.read_csv(url, sep='\t', parse_dates=['date'])
            df['close'] = 1.0
            df['period'] = df['date'].dt.to_period('M')
            vals_lastdate_indices = df.groupby(['period'])['date'].transform(max) == df['date']
            df = df[vals_lastdate_indices]
            del df['date'], df['nominal']
        elif currency_to == Currency.RUB:
            url = '{}{}-{}.csv'.format(self.url_base,
                                       currency_from.name,
                                       currency_to.name)
            df = pd.read_csv(url, sep='\t', parse_dates=['date'])
            df['close'] = df['close'] * df['nominal']
            df['period'] = df['date'].dt.to_period('M')
            vals_lastdate_indices = df.groupby(['period'])['date'].transform(max) == df['date']
            df = df[vals_lastdate_indices]
            del df['date'], df['nominal']
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
