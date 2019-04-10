from functools import lru_cache

from serum import singleton
import pandas as pd
import quandl

from .base_classes import FinancialSymbolsSource
from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol
from .._settings import *


@singleton
class QuandlSource(FinancialSymbolsSource):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self):
        super().__init__(namespace='ny')
        self.url_base = rostsber_url + 'quandl/'
        self.index = pd.read_csv(self.url_base + '__index.csv', sep='\t', index_col='name',
                                 parse_dates=['date_start', 'date_end'])
        self.index['date_start'] = self.index['date_start'].dt.to_period(freq='D')
        self.index['date_end'] = self.index['date_end'].dt.to_period(freq='D')

    @lru_cache(maxsize=512)
    def __extract_values(self, name, start_period, end_period):
        df = quandl.get('EOD/{}.11'.format(name),
                        start_date=start_period.to_timestamp().strftime('%Y-%m-%d'),
                        end_date=end_period.to_timestamp('M').strftime('%Y-%m-%d'),
                        collapse='monthly')
        df_res = pd.DataFrame()
        df_res['close'] = df['Adj_Close']
        df_res['date'] = df_res.index
        return df_res

    def fetch_financial_symbol(self, name: str):
        if name in self.index.index:
            row = self.index.loc[name]
            symbol = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                     values=lambda start_period, end_period:
                                         self.__extract_values(name, start_period, end_period),
                                     exchange=row['exchange'],
                                     short_name=row['short_name'],
                                     start_period=row['date_start'],
                                     end_period=row['date_end'],
                                     currency=Currency.USD,
                                     security_type=SecurityType.STOCK_ETF,
                                     period=Period.DAY,
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
