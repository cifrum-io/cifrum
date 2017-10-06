import dependency_injector.containers as containers
import dependency_injector.providers as providers

from yapo.FinancialSymbolsSource import *


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

    currency_eur_rub_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='cbr',
        ticker='EUR',
        path='currency/EUR-RUB.csv',
        short_name='Евро',
        currency=Currency.EUR,
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

    inflation_eu_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='EU',
        path='inflation_eu/data.csv',
        short_name='Инфляция ЕС',
        currency=Currency.EUR,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False
    )

    inflation_us_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='US',
        path='inflation_us/data.csv',
        short_name='Инфляция США',
        currency=Currency.USD,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False
    )

    cbr_top_rates_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='cbr',
        ticker='TOP_rates',
        path='cbr_deposit_rate/data.csv',
        long_name='Динамика максимальной процентной ставки (по вкладам в российских рублях) ',
        currency=Currency.RUB,
        security_type=SecurityType.RATES,
        period=Period.DECADE,
        adjusted_close=False
    )

    micex_mcftr_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='micex',
        ticker='MCFTR',
        path='moex/mcftr/data.csv',
        short_name='MICEX Total Return',
        currency=Currency.RUB,
        security_type=SecurityType.INDEX,
        period=Period.DAY,
        adjusted_close=False
    )

    micex_stocks_source = providers.Singleton(MicexStocksFinancialSymbolsSource)

    nlu_muts_source = providers.Singleton(NluFinancialSymbolsSource)

    financial_symbols_registry = providers.Singleton(FinancialSymbolsRegistry,
                                                     symbol_sources=[
                                                         currency_usd_rub_source(),
                                                         currency_eur_rub_source(),
                                                         cbr_top_rates_source(),
                                                         inflation_ru_source(),
                                                         inflation_eu_source(),
                                                         inflation_us_source(),
                                                         micex_mcftr_source(),
                                                         micex_stocks_source(),
                                                         nlu_muts_source(),
                                                     ])


def information(ids: str):
    """
    Fetches ticker information based on internal ID. The information includes ISIN, short and long
    names, exchange, currency, etc.

    :param ids: a string that contains list of RostSber IDs separated by comma
    :returns: - list of tickers information if 2 or more IDs are provided
              - ticker information if single ID is provided
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
