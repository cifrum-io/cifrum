from functools import lru_cache

from serum import singleton
import datetime as dtm
import pandas as pd

from .base_classes import SingleFinancialSymbolSource, FinancialSymbolsSource
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol
from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.enums import Currency, SecurityType, Period
from .._settings import rostsber_url, change_column_name


@singleton
class CbrTopRatesSource(SingleFinancialSymbolSource):
    def _load_rates(self):
        df = pd.read_csv('{}cbr_deposit_rate/data.csv'.format(rostsber_url), sep='\t')
        df.sort_values(by='decade', inplace=True)
        df.rename(columns={'close': change_column_name, 'decade': 'date'},
                  inplace=True)
        return df

    def _load_dates(self, kind):
        index = pd.read_csv('{}cbr_deposit_rate/__index.csv'.format(rostsber_url), sep='\t')
        period_str = index[kind][0]
        return pd.Period(period_str, freq='M')

    def __init__(self):
        super().__init__(
            namespace='cbr',
            name='TOP_rates',
            values_fetcher=lambda: self._load_rates(),
            start_period=self._load_dates(kind='date_start'),
            end_period=self._load_dates(kind='date_end'),
            long_name='Динамика максимальной процентной ставки (по вкладам в российских рублях)',
            currency=Currency.RUB,
            security_type=SecurityType.RATES,
            period=Period.DECADE,
            adjusted_close=False,
        )


@singleton
class CbrCurrenciesSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='cbr')
        self.url_base = rostsber_url + 'currency/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.__short_names = {
            Currency.RUB: 'Рубль РФ',
            Currency.USD: 'Доллар США',
            Currency.EUR: 'Евро',
        }
        self.__currency_min_date = {
            Currency.RUB.name: pd.Period('1990', freq='D'),
            Currency.USD.name: pd.Period('1900', freq='D'),
            Currency.EUR.name: pd.Period('1999', freq='D'),
        }

    @lru_cache(maxsize=512)
    def __currency_values(self, name, start_period, end_period):
        start_period = max(start_period,
                           pd.Period(self.__currency_min_date[name], freq='M'))
        end_period = min(end_period, pd.Period.now(freq='M'))
        date_range = pd.date_range(start=start_period.to_timestamp(),
                                   end=(end_period + 1).to_timestamp(),
                                   freq='D')
        df = pd.DataFrame({'date': date_range, 'close': 1.0})

        df['period'] = df['date'].dt.to_period('M')
        df_new = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
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
                end_period=pd.Period(dtm.datetime.now(), freq='D'),
                currency=currency,
                security_type=SecurityType.CURRENCY,
                period=Period.DAY,
                adjusted_close=True,
            )
            return fs

    def get_all_infos(self):
        return [
            FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, short_name.name),
                short_name=short_name,
            ) for short_name in self.__short_names.keys()
        ]
