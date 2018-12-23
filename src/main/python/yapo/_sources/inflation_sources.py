from serum import singleton
import pandas as pd

from .base_classes import SingleFinancialSymbolSource
from ..model.Settings import rostsber_url, change_column_name
from ..model.Enums import Currency, SecurityType, Period


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


@singleton
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


@singleton
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


@singleton
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
