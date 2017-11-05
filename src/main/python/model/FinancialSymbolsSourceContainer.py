import dependency_injector.containers as containers
import dependency_injector.providers as providers
from .FinancialSymbolsSource import *
from .Settings import change_column_name


class FinancialSymbolsSourceContainer(containers.DeclarativeContainer):
    cbr_currencies_symbols_source = providers.Singleton(CbrCurrencyFinancialSymbolsSource)

    @classmethod
    def __load_inflation(cls, inflation_country):
        dt = pd.read_csv('{}/inflation_{}/data.csv'.format(Settings.rostsber_url, inflation_country), sep='\t')
        dt.rename(columns={'close': change_column_name}, inplace=True)
        dt['close'] = (dt[change_column_name] + 1.).cumprod()
        return dt

    inflation_ru_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='RU',
        values_fetcher=lambda: FinancialSymbolsSourceContainer.__load_inflation('ru'),
        short_name='Инфляция РФ',
        currency=Currency.RUB,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    inflation_eu_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='EU',
        values_fetcher=lambda: FinancialSymbolsSourceContainer.__load_inflation('eu'),
        short_name='Инфляция ЕС',
        currency=Currency.EUR,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    inflation_us_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        ticker='US',
        values_fetcher=lambda: FinancialSymbolsSourceContainer.__load_inflation('us'),
        short_name='Инфляция США',
        currency=Currency.USD,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    cbr_top_rates_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='cbr',
        ticker='TOP_rates',
        values_fetcher=lambda: pd.read_csv(Settings.rostsber_url + 'cbr_deposit_rate/data.csv', sep='\t'),
        long_name='Динамика максимальной процентной ставки (по вкладам в российских рублях) ',
        currency=Currency.RUB,
        security_type=SecurityType.RATES,
        period=Period.DECADE,
        adjusted_close=False,
    )

    micex_mcftr_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='micex',
        ticker='MCFTR',
        values_fetcher=lambda: pd.read_csv(Settings.rostsber_url + 'moex/mcftr/data.csv', sep='\t'),
        short_name='MICEX Total Return',
        currency=Currency.RUB,
        security_type=SecurityType.INDEX,
        period=Period.DAY,
        adjusted_close=False,
    )

    micex_stocks_source = providers.Singleton(MicexStocksFinancialSymbolsSource)

    nlu_muts_source = providers.Singleton(NluFinancialSymbolsSource)

    quandl_source = providers.Singleton(QuandlFinancialSymbolsSource)

    financial_symbols_registry = providers.Singleton(
        FinancialSymbolsRegistry,
        symbol_sources=[
            cbr_currencies_symbols_source(),
            cbr_top_rates_source(),
            inflation_ru_source(),
            inflation_eu_source(),
            inflation_us_source(),
            micex_mcftr_source(),
            micex_stocks_source(),
            nlu_muts_source(),
            quandl_source(),
        ]
    )

    currency_symbols_registry = providers.Singleton(CurrencySymbolsRegistry)
