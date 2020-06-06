import datetime as dtm
from functools import lru_cache
from typing import Optional, Callable

import pandas as pd

import swagger_client
from .base_classes import FinancialSymbolsSource
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol import FinancialSymbol
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol_info import FinancialSymbolInfo


class MutualFundsRuSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='mut_ru')
        self.infos_api = swagger_client.InfosApi()
        self.adjusted_values_api = swagger_client.AdjustedValuesApi()

    @lru_cache(maxsize=512)
    def __extract_values(self, row_id: str) -> Callable[[pd.Period, pd.Period], pd.DataFrame]:
        def func(start_period: pd.Period, end_period: pd.Period) -> pd.DataFrame:
            adjusted_close_values = \
                self.adjusted_values_api.adjusted_close_values(registration_number=row_id,
                                                               currency='rub',
                                                               start_date=str(start_period.asfreq(freq='D')),
                                                               end_date=str(end_period.asfreq(freq='D')),
                                                               period_frequency='month',
                                                               interpolation_type='lastValue')
            df = pd.DataFrame({
                'close': [v.value for v in adjusted_close_values.values],
                'date': [dtm.datetime.combine(v._date, dtm.time(0, 0)) for v in adjusted_close_values.values],
                'period': [pd.Period(v._date, freq='M') for v in adjusted_close_values.values],
            })
            return df

        return func

    def fetch_financial_symbol(self, name: str) -> Optional[FinancialSymbol]:
        mutru_info = self.infos_api.mutru_info(name)
        if mutru_info is None:
            return None
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                 values=self.__extract_values(name),
                                 short_name=mutru_info.name,
                                 start_period=pd.Period(mutru_info.date_start, freq='D'),
                                 end_period=pd.Period(mutru_info.date_end, freq='D'),
                                 currency=Currency.RUB,
                                 security_type=SecurityType.MUT,
                                 period=Period.DAY,
                                 adjusted_close=True,
                                 )
        return symbol

    def get_all_infos(self):
        infos = []
        for info in self.infos_api.mutru_infos():
            fin_sym_info = FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, str(info.registration_number)),
                short_name=info.name,
            )
            infos.append(fin_sym_info)
        return infos
