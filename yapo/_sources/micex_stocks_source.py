from functools import lru_cache

from serum import singleton
import pandas as pd

from .base_classes import FinancialSymbolsSource
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol
from .._settings import rostsber_url


@singleton
class MicexStocksSource(FinancialSymbolsSource):
    def __init__(self):
        super().__init__(namespace='micex')
        self.url_base = rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t',
                                 index_col='name', parse_dates=['date_start', 'date_end'])
        self.index['date_start'] = self.index['date_start'].dt.to_period(freq='D')
        self.index['date_end'] = self.index['date_end'].dt.to_period(freq='D')

    @lru_cache(maxsize=512)
    def __extract_values(self, secid, start_period, end_period):
        df = pd.read_csv(self.url_base + secid + '.csv', sep='\t')
        df['date'] = pd.to_datetime(df['date'])
        df['period'] = df['date'].dt.to_period('M')
        df_new = df[(start_period <= df['period']) & (df['period'] <= end_period)].copy()
        df_new['legal_close'].fillna(df_new['close'], inplace=True)
        del df_new['close']
        df_new.rename(columns={'legal_close': 'close'}, inplace=True)
        df_new.dropna(inplace=True)
        return df_new

    def fetch_financial_symbol(self, name: str):
        if name not in self.index.index:
            return None
        row = self.index.loc[name]
        symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                 values=lambda start_period, end_period:
                                 self.__extract_values(name, start_period, end_period),
                                 exchange='MICEX',
                                 start_period=row['date_start'],
                                 end_period=row['date_end'],
                                 short_name=row['short_name'],
                                 long_name=row['long_name'],
                                 isin=row['isin'],
                                 currency=Currency.RUB,
                                 security_type=SecurityType.STOCK_ETF,
                                 period=Period.DAY,
                                 adjusted_close=True)
        return symbol

    def get_all_infos(self):
        infos = []
        for idx, row in self.index.iterrows():
            fin_sym_info = FinancialSymbolInfo(
                fin_sym_id=FinancialSymbolId(self.namespace, idx),
                short_name=row['short_name']
            )
            infos.append(fin_sym_info)
        return infos
