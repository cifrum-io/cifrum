import pandas as pd
import dependency_injector.containers as containers
import dependency_injector.providers as providers
import os
import quandl
from yapo.Enums import Currency, SecurityType, Period
from yapo import Settings


class FinancialSymbol:
    def __init__(self, namespace, ticker, values,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        self.namespace = namespace
        self.ticker = ticker
        self.values = values
        self.isin = isin
        self.short_name = short_name
        self.long_name = long_name
        self.exchange = exchange
        self.currency = currency
        self.security_type = security_type
        self.period = period
        self.adjusted_close = adjusted_close

    def values(self):
        return self.values()


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
            symbol = FinancialSymbol(namespace=self.namespace,
                                     ticker=str(row['id']),
                                     values=lambda: pd.read_csv(url, sep='\t'))
            symbols.append(symbol)
        return symbols


class FinancialSymbolsRegistry(object):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self, symbol_sources):
        self.symbols = []
        for symbol_source in symbol_sources:
            self.symbols += symbol_source.get_financial_symbols()

    def get(self, namespace, ticker):
        if namespace == 'quandl':
            def extract_values():
                df = quandl.get('EOD/{}'.format(ticker), collapse='monthly')
                df_res = pd.DataFrame()
                df_res['close'] = df['Adj_Close']
                df_res['date'] = df_res.index
                return df_res

            symbol = FinancialSymbol(namespace=namespace, ticker=ticker, values=extract_values)
            return symbol
        else:
            result = list(filter(
                lambda ast: ast.namespace == namespace and ast.ticker == ticker,
                self.symbols
            ))
            if len(result) != 1:
                raise Exception('ticker {}/{} is not found'.format(namespace, ticker))

            return result[0]


class FinancialSymbolsSourceContainer(containers.DeclarativeContainer):
    currency_usd_rub_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='cbr',
        ticker='USD',
        path='currency/USD-RUB.csv',
        short_name='Доллар США',
        currency=Currency.USD,
        security_type=SecurityType.CURRENCY,
        period=Period.DAY,
        adjusted_close=True
    )

    inflation_ru_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='RU',
        path='inflation_ru/data.csv',
        short_name='Инфляция РФ',
        currency=Currency.RUB,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False
    )

    inflation_eu_source = providers.Singleton(SingleFinancialSymbolSource,
                                              path='inflation_eu/data.csv',
                                              namespace='infl',
                                              ticker='EU')

    micex_mcftr_source = providers.Singleton(SingleFinancialSymbolSource,
                                             path='moex/mcftr/data.csv',
                                             namespace='micex',
                                             ticker='MCFTR')

    micex_stocks_source = providers.Singleton(MicexStocksFinancialSymbolsSource)

    nlu_muts_source = providers.Singleton(NluFinancialSymbolsSource)

    financial_symbols_registry = providers.Singleton(FinancialSymbolsRegistry,
                                                     symbol_sources=[
                                                         currency_usd_rub_source(),
                                                         inflation_ru_source(),
                                                         inflation_eu_source(),
                                                         micex_mcftr_source(),
                                                         micex_stocks_source(),
                                                         nlu_muts_source(),
                                                     ])


def info(ids: str):
    """
    Fetches ticker info based on internal ID. The info includes ISIN, short and long names,
    exchange, currency, etc.

    :param ids: a string that contains list of RostSber IDs separated by comma
    :returns: - list of tickers info if 2 or more IDs are provided
              - ticker info if single ID is provided
    """
    ids_arr = [s.strip() for s in ids.split(',')]
    tickers_info = []
    for id_str in ids_arr:
        ticker_namespace, ticker = id_str.split('/')
        registry = FinancialSymbolsSourceContainer.financial_symbols_registry()
        ticker_info = registry.get(ticker_namespace, ticker)
        tickers_info.append(ticker_info)
    tickers_info = tickers_info[0] if len(tickers_info) == 1 else tickers_info
    return tickers_info
