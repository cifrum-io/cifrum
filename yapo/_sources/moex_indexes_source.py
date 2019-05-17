from functools import lru_cache

from serum import singleton
import pandas as pd

from .base_classes import FinancialSymbolsSource
from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol
from .._settings import rostsber_url


@singleton
class MoexIndexesSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='index')
        self.url_base = rostsber_url + 'index/moex/'

        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name',
                                 parse_dates=['date_start', 'date_end'])
        self.index['date_start'] = self.index['date_start'].dt.to_period(freq='D')
        self.index['date_end'] = self.index['date_end'].dt.to_period(freq='D')

    @lru_cache(maxsize=512)
    def __extract_values(self, row_id, start_period, end_period):
        url = '{}{}.csv'.format(self.url_base, row_id)
        df = pd.read_csv(url, sep='\t', parse_dates=['date'])
        df['period'] = df['date'].dt.to_period('M')
        df_new = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
        return df_new

    def fetch_financial_symbol(self, name: str):
        if name not in self.index.index:
            return None
        row = self.index.loc[name]
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                 values=lambda start_period, end_period:
                                 self.__extract_values(name, start_period, end_period),
                                 short_name=row['short_name'],
                                 start_period=row['date_start'],
                                 end_period=row['date_end'],
                                 currency=Currency.RUB,
                                 security_type=SecurityType.INDEX,
                                 period=Period.DAY,
                                 adjusted_close=True)
        return symbol

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fin_sym_info = FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, str(idx)),
                short_name=row['short_name'],
            )
            infos.append(fin_sym_info)
        return infos
