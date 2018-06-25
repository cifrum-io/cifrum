import dependency_injector.containers as containers
import dependency_injector.providers as providers
from .FinancialSymbolsSource import *
from .Settings import change_column_name


def _load_inflation_values(inflation_country):
    df = pd.read_csv('{}inflation_{}/data.csv'.format(Settings.rostsber_url, inflation_country), sep='\t')
    df['period'] = pd.to_datetime(df['date']).dt.to_period('M')
    df.sort_values(by='period', inplace=True)
    df.rename(columns={'close': change_column_name}, inplace=True)
    return df


def _load_inflation_index(inflation_country):
    dt = pd.read_csv('{}inflation_{}/__index.csv'.format(Settings.rostsber_url, inflation_country), sep='\t')
    return dt


def _load_inflation_date(inflation_country, kind):
    index = _load_inflation_index(inflation_country)
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


def _load_toprates():
    dt = pd.read_csv('{}cbr_deposit_rate/data.csv'.format(Settings.rostsber_url), sep='\t')
    dt.sort_values(by='decade', inplace=True)
    dt.rename(columns={'close': change_column_name, 'decade': 'date'},
              inplace=True)
    return dt


def _load_cbr_deposit_rate_date(kind):
    index = pd.read_csv('{}cbr_deposit_rate/__index.csv'.format(Settings.rostsber_url), sep='\t')
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


def _load_micex_mcftr_date(kind):
    index = pd.read_csv(Settings.rostsber_url + 'moex/mcftr/__index.csv', sep='\t')
    period_str = index[kind][0]
    return pd.Period(period_str, freq='M')


class FinancialSymbolsSourceContainer(containers.DeclarativeContainer):
    cbr_currencies_symbols_source = providers.Singleton(CbrCurrencyFinancialSymbolsSource)

    inflation_ru_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        name=Currency.RUB.name,
        values_fetcher=lambda: _load_inflation_values('ru'),
        start_period=_load_inflation_date('ru', 'date_start'),
        end_period=_load_inflation_date('ru', 'date_end'),
        short_name='Инфляция РФ',
        currency=Currency.RUB,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    inflation_eu_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        name=Currency.EUR.name,
        values_fetcher=lambda: _load_inflation_values('eu'),
        start_period=_load_inflation_date('eu', 'date_start'),
        end_period=_load_inflation_date('eu', 'date_start'),
        short_name='Инфляция ЕС',
        currency=Currency.EUR,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    inflation_us_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='infl',
        name=Currency.USD.name,
        values_fetcher=lambda: _load_inflation_values('us'),
        start_period=_load_inflation_date('us', 'date_start'),
        end_period=_load_inflation_date('us', 'date_start'),
        short_name='Инфляция США',
        currency=Currency.USD,
        security_type=SecurityType.INFLATION,
        period=Period.MONTH,
        adjusted_close=False,
    )

    cbr_top_rates_source = providers.Singleton(
        SingleFinancialSymbolSource,
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

    micex_mcftr_source = providers.Singleton(
        SingleFinancialSymbolSource,
        namespace='micex',
        name='MCFTR',
        values_fetcher=lambda: pd.read_csv(Settings.rostsber_url + 'moex/mcftr/data.csv', sep='\t'),
        start_period=_load_micex_mcftr_date('date_start'),
        end_period=_load_micex_mcftr_date('date_end'),
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
