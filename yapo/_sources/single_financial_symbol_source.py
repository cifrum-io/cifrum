import datetime as dtm
from functools import lru_cache
from typing import Optional, Callable

import pandas as pd
from serum import singleton

from .base_classes import SingleFinancialSymbolSource, FinancialSymbolsSource
from .._settings import data_url, change_column_name
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol import FinancialSymbol
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol_info import FinancialSymbolInfo


@singleton
class CbrTopRatesSource(SingleFinancialSymbolSource):
    def _load_rates(self):
        df = pd.read_csv('{}cbr_deposit_rate/data.csv'.format(data_url), sep='\t')
        df.sort_values(by='decade', inplace=True)
        df.rename(columns={'close': change_column_name, 'decade': 'date'},
                  inplace=True)
        return df

    def _load_dates(self, kind):
        index = pd.read_csv('{}cbr_deposit_rate/__index.csv'.format(data_url), sep='\t')
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
        self.url_base = data_url + 'currency/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name')
        self.__short_names = {
            Currency.RUB: 'Рубль РФ',
            Currency.USD: 'Доллар США',
            Currency.EUR: 'Евро',
        }
        self._currency_min_date = {
            Currency.RUB.name: pd.Period('1990', freq='D'),
            Currency.USD.name: pd.Period('1913', freq='D'),
            Currency.EUR.name: pd.Period('1996', freq='D'),
        }

    @lru_cache(maxsize=512)
    def __currency_values(self, name: str) -> Callable[[pd.Period, pd.Period], pd.DataFrame]:
        def func(start_period: pd.Period, end_period: pd.Period) -> pd.DataFrame:
            start_period = max(start_period,
                               pd.Period(self._currency_min_date[name], freq='M'))
            end_period = min(end_period, pd.Period.now(freq='M'))
            date_range = pd.date_range(start=start_period.to_timestamp(),
                                       end=(end_period + 1).to_timestamp(),
                                       freq='D')
            df = pd.DataFrame({'date': date_range, 'close': 1.0})

            df['period'] = df['date'].dt.to_period('M')
            df_new = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
            return df_new

        return func

    def fetch_financial_symbol(self, name: str) -> Optional[FinancialSymbol]:
        name = name.upper()
        currency = Currency.__dict__.get(name)  # type: ignore

        if currency is None:
            return None

        fs = FinancialSymbol(
            identifier=FinancialSymbolId(namespace='cbr', name=name),
            values=self.__currency_values(name),
            short_name=self.__short_names[currency],
            start_period=self._currency_min_date[currency.name],
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
