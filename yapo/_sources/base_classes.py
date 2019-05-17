from pprint import pformat
import pandas as pd

from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol


class FinancialSymbolsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def fetch_financial_symbol(self, name: str):
        raise Exception('should not be called')

    def __repr__(self):
        return pformat(vars(self))

    def get_all_infos(self):
        raise Exception('should not be called')


class SingleFinancialSymbolSource(FinancialSymbolsSource):
    def __extract_values(self, start_period, end_period):
        df = self.__values_fetcher()
        df['date'] = pd.to_datetime(df['date'])
        return df[(df['date'].dt.to_period('M') >= start_period) &
                  (df['date'].dt.to_period('M') <= end_period)].copy()

    def __init__(self, values_fetcher, namespace, name, start_period, end_period,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        super().__init__(namespace)
        self.name = name
        self.__values_fetcher = values_fetcher
        self.financial_symbol = \
            FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=self.name),
                            values=self.__extract_values,
                            isin=isin,
                            short_name=short_name,
                            long_name=long_name,
                            start_period=start_period,
                            end_period=end_period,
                            exchange=exchange,
                            currency=currency,
                            security_type=security_type,
                            period=period,
                            adjusted_close=adjusted_close)

    def fetch_financial_symbol(self, name: str):
        return self.financial_symbol if name == self.name else None

    def get_all_infos(self):
        fin_sym_info = FinancialSymbolInfo(
            fin_sym_id=self.financial_symbol.identifier,
            short_name=self.financial_symbol.short_name
        )
        return [fin_sym_info]
