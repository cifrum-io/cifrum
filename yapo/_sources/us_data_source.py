from functools import lru_cache
from typing import Optional, Callable

import pandas as pd

from .base_classes import FinancialSymbolsSource
from .._settings import data_url
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol import FinancialSymbol
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol_info import FinancialSymbolInfo


class UsDataSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='ny')

        self.url_base = data_url + 'v2/us'
        self.index = pd.read_csv(self.url_base, sep=',', index_col='Code')

    @lru_cache(maxsize=512)
    def __extract_values(self, name: str) -> Callable[[pd.Period, pd.Period], pd.DataFrame]:
        def func(start_period: pd.Period, end_period: pd.Period) -> pd.DataFrame:
            nonlocal name
            df = pd.read_csv(self.url_base + '/' + name, sep='\t', parse_dates=['period'])
            df.rename(columns={'period': 'date'}, inplace=True)
            df['period'] = df['date'].dt.to_period(freq='M')
            df_new = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
            return df_new

        return func

    def fetch_financial_symbol(self, name: str) -> Optional[FinancialSymbol]:
        if name in self.index.index:
            row = self.index.loc[name]
            symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                     values=self.__extract_values(name),
                                     exchange=row['Exchange'],
                                     short_name=row['Name'],
                                     currency=Currency.__dict__.get(row['Currency']),  # type: ignore
                                     security_type=SecurityType.STOCK_ETF,
                                     period=Period.MONTH,
                                     adjusted_close=True)
            return symbol
        return None

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fsi = FinancialSymbolId(self.namespace, str(idx))
            fs_info = FinancialSymbolInfo(fin_sym_id=fsi, short_name=idx)
            infos.append(fs_info)
        return infos
