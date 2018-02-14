import os
from itertools import groupby
from pprint import pformat

import pandas as pd
import quandl

from . import Settings
from .Enums import Currency, SecurityType, Period
from .FinancialSymbol import FinancialSymbol
from .FinancialSymbolId import FinancialSymbolId


class FinancialSymbolsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def fetch_financial_symbol(self, ticker: str):
        raise Exception('should not be called')

    def __repr__(self):
        return pformat(vars(self))


class SingleFinancialSymbolSource(FinancialSymbolsSource):
    @staticmethod
    def __extract_values(values_fetcher, start_period, end_period):
        df = values_fetcher()
        df['date'] = pd.to_datetime(df['date'])
        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def __init__(self, values_fetcher, namespace, ticker,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        super().__init__(namespace)
        self.ticker = ticker
        self.financial_symbol = \
            FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=self.ticker),
                            values=lambda start_period, end_period:
                                self.__extract_values(values_fetcher, start_period, end_period),
                            isin=isin,
                            short_name=short_name,
                            long_name=long_name,
                            exchange=exchange,
                            currency=currency,
                            security_type=security_type,
                            period=period,
                            adjusted_close=adjusted_close)

    def fetch_financial_symbol(self, ticker: str):
        return self.financial_symbol if ticker == self.ticker else None


class CbrCurrencyFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='cbr')
        self.short_names = {
            Currency.RUB: 'Рубль РФ',
            Currency.USD: 'Доллар США',
            Currency.EUR: 'Евро',
        }

    @staticmethod
    def __currency_values(ticker, start_period, end_period):
        currency_min_date = {
            Currency.RUB.name: pd.Period('1990', freq='M'),
            Currency.USD.name: pd.Period('1900', freq='M'),
            Currency.EUR.name: pd.Period('1999', freq='M'),
        }
        start_period = max(start_period, currency_min_date[ticker])
        end_period = min(end_period, pd.Period.now(freq='M'))
        date_range = pd.date_range(start=start_period.to_timestamp(),
                                   end=(end_period + 1).to_timestamp(),
                                   freq='D')
        df = pd.DataFrame({'date': date_range, 'close': 1.0})

        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def fetch_financial_symbol(self, ticker: str):
        currency = Currency.__dict__.get(ticker)
        if currency is None:
            return None
        else:
            fs = FinancialSymbol(
                identifier=FinancialSymbolId(namespace='cbr', name=ticker),
                values=lambda start_period, end_period: self.__currency_values(ticker, start_period, end_period),
                short_name=self.short_names[currency],
                currency=currency,
                security_type=SecurityType.CURRENCY,
                period=Period.DAY,
                adjusted_close=True
            )
            return fs


class MicexStocksFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='micex')
        self.url_base = Settings.rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + 'stocks_list.csv', sep='\t')

    def __extract_values(self, secid, start_period, end_period):
        df = pd.read_csv(self.url_base + secid + '.csv', sep='\t')
        df['date'] = pd.to_datetime(df['date'])
        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def fetch_financial_symbol(self, ticker: str):
        for _, row in self.index.iterrows():
            secid = row['SECID']
            if secid == ticker:
                symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=secid),
                                         values=lambda start_period, end_period:
                                             self.__extract_values(secid, start_period, end_period),
                                         exchange='MICEX',
                                         short_name=row['SHORTNAME'],
                                         long_name=row['NAME'],
                                         isin=row['ISIN'],
                                         currency=Currency.RUB,
                                         security_type=SecurityType.STOCK_ETF,
                                         period=Period.DAY,
                                         adjusted_close=True)
                return symbol
        return None


class NluFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='nlu')
        self.url_base = Settings.rostsber_url + 'mut_rus/'
        self.index = pd.read_csv(self.url_base + 'mut_rus.csv', sep='\t')

    def __extract_values(self, row_id, start_period, end_period):
        url = '{}{}.csv'.format(self.url_base, row_id)
        df = pd.read_csv(url, sep='\t')
        df['date'] = pd.to_datetime(df['date'])
        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def fetch_financial_symbol(self, ticker: str):
        for _, row in self.index.iterrows():
            row_id = str(row['id'])
            if row_id == ticker:
                symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=row_id),
                                         values=lambda start_period, end_period:
                                             self.__extract_values(row_id, start_period, end_period),
                                         short_name=row['ПИФ'],
                                         currency=Currency.RUB,
                                         security_type=SecurityType.MUT,
                                         period=Period.DAY,
                                         adjusted_close=True)
                return symbol
        return None


class QuandlFinancialSymbolsSource(FinancialSymbolsSource):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self):
        super().__init__(namespace='quandl')
        ticker_list_url = 'http://static.quandl.com/end_of_day_us_stocks/ticker_list.csv'
        self.ticker_list = pd.read_csv(filepath_or_buffer=ticker_list_url, index_col=0)

    @staticmethod
    def __extract_values(ticker, start_period, end_period):
        df = quandl.get('EOD/{}.11'.format(ticker),
                        start_date=start_period.to_timestamp().strftime('%Y-%m-%d'),
                        end_date=end_period.to_timestamp('M').strftime('%Y-%m-%d'),
                        collapse='monthly')
        df_res = pd.DataFrame()
        df_res['close'] = df['Adj_Close']
        df_res['date'] = df_res.index
        return df_res

    def fetch_financial_symbol(self, ticker: str):
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=ticker),
                                 values=lambda start_period, end_period:
                                     self.__extract_values(ticker, start_period, end_period),
                                 exchange=self.ticker_list.loc[ticker, 'Exchange'],
                                 short_name=self.ticker_list.loc[ticker, 'Name'],
                                 currency=Currency.USD,
                                 security_type=SecurityType.STOCK_ETF,
                                 period=Period.DAY,
                                 adjusted_close=True)
        return symbol


class FinancialSymbolsRegistry(object):
    def __init__(self, symbol_sources):
        def symbol_source_key(x): return x.namespace

        symbol_sources = sorted(symbol_sources, key=symbol_source_key)
        self.symbol_sources = {}
        for k, v in groupby(symbol_sources, key=symbol_source_key):
            self.symbol_sources.update({k: list(v)})

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
                raise Exception('Something went wrong. {} tickers are found for {}. '
                                'Please, submit the issue'
                                .format(result_count, financial_symbol_id.format()))
        else:
            return None


class CurrencySymbolsRegistry(object):
    def __init__(self):
        self.url_base = Settings.rostsber_url + 'currency/'

    def convert(self, currency_from: Currency, currency_to: Currency):
        if currency_to == currency_from:
            url = '{}{}-{}.csv'.format(self.url_base, 'USD', 'RUB')
            df = pd.read_csv(url, sep='\t', parse_dates=['date'])
            df['close'] = 1.0
            df['period'] = df['date'].dt.to_period('M')
            vals_lastdate_indices = df.groupby(['period'])['date'].transform(max) == df['date']
            df = df[vals_lastdate_indices]
            del df['date'], df['nominal']
            return df
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
            return df
        elif currency_from == Currency.RUB:
            df = self.convert(currency_to, currency_from)
            df['close'] = 1.0 / df['close']
            return df
        else:
            df = self.convert(currency_from, Currency.RUB)
            df_to = self.convert(Currency.RUB, currency_to)
            df = df.merge(df_to, on='period', suffixes=('', '_to'))
            df['close'] = df['close'] * df['close_to']
            del df['close_to']
            return df
