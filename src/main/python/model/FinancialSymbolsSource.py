import os
from itertools import groupby
from pprint import pformat

import pandas as pd
import quandl

from . import Settings
from .Enums import Currency, SecurityType, Period
from .FinancialSymbol import FinancialSymbol


class FinancialSymbolsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def fetch_financial_symbol(self, ticker: str):
        raise Exception('should not be called')

    def __repr__(self):
        return pformat(vars(self))


class SingleFinancialSymbolSource(FinancialSymbolsSource):
    def __init__(self, path, namespace, ticker,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        super().__init__(namespace)
        self.path = path
        self.ticker = ticker

        url = Settings.rostsber_url + self.path
        self.financial_symbol = FinancialSymbol(namespace=self.namespace,
                                                ticker=self.ticker,
                                                values=lambda: pd.read_csv(url, sep='\t'),
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


class MicexStocksFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='micex')
        self.url_base = Settings.rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + 'stocks_list.csv', sep='\t')

    def fetch_financial_symbol(self, ticker: str):
        for _, row in self.index.iterrows():
            secid = row['SECID']
            if secid == ticker:
                symbol = FinancialSymbol(namespace=self.namespace,
                                         ticker=secid,
                                         values=lambda: pd.read_csv(self.url_base + secid + '.csv',
                                                                    sep='\t'),
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

    def fetch_financial_symbol(self, ticker: str):
        for _, row in self.index.iterrows():
            row_id = str(row['id'])
            if row_id == ticker:
                url = '{}{}.csv'.format(self.url_base, row_id)
                symbol = FinancialSymbol(namespace=self.namespace,
                                         ticker=row_id,
                                         values=lambda: pd.read_csv(url, sep='\t'),
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

    @staticmethod
    def _extract_values(ticker):
        df = quandl.get('EOD/{}'.format(ticker), collapse='monthly')
        df_res = pd.DataFrame()
        df_res['close'] = df['Adj_Close']
        df_res['date'] = df_res.index
        return df_res

    def fetch_financial_symbol(self, ticker: str):
        symbol = FinancialSymbol(namespace=self.namespace,
                                 ticker=ticker,
                                 values=lambda: self._extract_values(ticker),
                                 exchange='NASDAQ',
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

    def get(self, namespace, ticker):
        if namespace in self.symbol_sources.keys():
            result = []
            for symbol_source in self.symbol_sources.get(namespace):
                fin_symbol = symbol_source.fetch_financial_symbol(ticker)
                if fin_symbol:
                    result.append(fin_symbol)
            result_count = len(result)
            if result_count == 1:
                return result[0]
            elif result_count == 0:
                return None
            else:
                raise Exception('Something went wrong. {} tickers are found for {}/{}. '
                                'Please, submit the issue'
                                .format(result_count, namespace, ticker))
        else:
            return None
