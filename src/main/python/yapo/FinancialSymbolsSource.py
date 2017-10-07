import pandas as pd
import os
import quandl
from yapo.Enums import Currency, SecurityType, Period
from yapo import Settings, FinancialSymbol as FSim


class FinancialSymbolsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def get_financial_symbols(self):
        raise Exception('should not be called')


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
        self.financial_symbol = FSim.FinancialSymbol(namespace=self.namespace,
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

    def get_financial_symbols(self):
        return [self.financial_symbol]


class MicexStocksFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__('micex')
        self.url_base = Settings.rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + 'stocks_list.csv', sep='\t')

    def get_financial_symbols(self):
        symbols = []
        for (idx, row) in self.index.iterrows():
            secid = row['SECID']
            symbol = FSim.FinancialSymbol(namespace=self.namespace,
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
            symbols.append(symbol)
        return symbols


class NluFinancialSymbolsSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__('nlu')
        self.url_base = Settings.rostsber_url + 'mut_rus/'
        self.index = pd.read_csv(self.url_base + 'mut_rus.csv', sep='\t')

    def get_financial_symbols(self):
        symbols = []
        for (idx, row) in self.index.iterrows():
            url = '{}/{}'.format(self.url_base, row['id'])
            symbol = FSim.FinancialSymbol(namespace=self.namespace,
                                          ticker=str(row['id']),
                                          values=lambda: pd.read_csv(url, sep='\t'),
                                          short_name=row['ПИФ'],
                                          currency=Currency.RUB,
                                          security_type=SecurityType.MUT,
                                          period=Period.DAY,
                                          adjusted_close=True)
            symbols.append(symbol)
        return symbols


class FinancialSymbolsRegistry(object):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self, symbol_sources):
        self.symbols = []
        for symbol_source in symbol_sources:
            self.symbols += symbol_source.get_financial_symbols()

    @staticmethod
    def _handle_quandl(namespace, ticker):
        def extract_values():
            df = quandl.get('EOD/{}'.format(ticker), collapse='monthly')
            df_res = pd.DataFrame()
            df_res['close'] = df['Adj_Close']
            df_res['date'] = df_res.index
            return df_res

        symbol = FSim.FinancialSymbol(namespace=namespace,
                                      ticker=ticker,
                                      values=extract_values,
                                      exchange='NASDAQ',
                                      currency=Currency.USD,
                                      security_type=SecurityType.STOCK_ETF,
                                      period=Period.DAY,
                                      adjusted_close=True)
        return symbol

    def get(self, namespace, ticker):
        if namespace == 'quandl':
            return self._handle_quandl(namespace=namespace, ticker=ticker)
        else:
            result = [
                ast for ast in self.symbols if ast.namespace == namespace and ast.ticker == ticker
            ]
            result_count = len(result)
            if result_count == 1:
                return result[0]
            elif len(result) == 0:
                return None
            else:
                raise Exception('Something went wrong. Two or more tickers are found for {}/{}. '
                                'Please, submit the issue'.format(namespace, ticker))
