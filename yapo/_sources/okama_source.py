from serum import singleton, inject
import pandas as pd

from .base_classes import FinancialSymbolsSource
from .single_financial_symbol_source import CbrTopRatesSource
from ..common.financial_symbol_info import FinancialSymbolInfo
from ..common.enums import Currency, SecurityType, Period
from ..common.financial_symbol_id import FinancialSymbolId
from ..common.financial_symbol import FinancialSymbol
from .._index.okid10 import compute as compute_top10


@singleton
@inject
class OkamaSource(FinancialSymbolsSource):
    cbr_top_rates_source: CbrTopRatesSource

    def __init__(self):
        super().__init__(namespace='index')

        self.cbr_top10_sym = self.cbr_top_rates_source.fetch_financial_symbol('TOP_rates')
        self.okid10 = 'OKID10'

    def fetch_financial_symbol(self, name: str):
        if name == self.okid10:
            def fetch_values(start_period, end_period):
                vals = self.cbr_top10_sym.values(
                    start_period=self.cbr_top10_sym.start_period,
                    end_period=end_period,
                )
                index_vals = compute_top10(vals)
                drop_first = max(0, start_period - index_vals.start_period)
                index_vals = index_vals[drop_first:]
                df = pd.DataFrame({'date': pd.date_range(index_vals.start_period.to_timestamp(),
                                                         (index_vals.end_period + 1).to_timestamp(),
                                                         freq='M'),
                                   'period': pd.period_range(index_vals.start_period,
                                                             index_vals.end_period,
                                                             freq='M'),
                                   'close': index_vals.values})
                return df
            sym = FinancialSymbol(identifier=FinancialSymbolId(namespace=self.namespace, name=name),
                                  values=fetch_values,
                                  short_name='Okama TOP10 Index',
                                  long_name='Okama TOP10 Index',
                                  start_period=self.cbr_top10_sym.start_period,
                                  end_period=self.cbr_top10_sym.end_period,
                                  currency=Currency.RUB,
                                  security_type=SecurityType.INDEX,
                                  period=Period.MONTH,
                                  adjusted_close=True)
            return sym

    def get_all_infos(self):
        fsi = FinancialSymbolInfo(
            fin_sym_id=FinancialSymbolId(self.namespace, self.okid10),
            short_name=self.okid10,
        )
        infos = [fsi]
        return infos
