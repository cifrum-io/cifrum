from abc import ABCMeta, abstractmethod

from serum import singleton, inject

from .micex_stocks_source import MicexStocksSource
from .mutru_funds_source import MutualFundsRuSource
from .quandl_source import QuandlSource
from .moex_indexes_source import MoexIndexesSource
from .single_financial_symbol_source import CbrCurrenciesSource, CbrTopRatesSource
from .okama_source import OkamaSource
from .inflation_source import InflationSource
from .yahoo_indexes_source import YahooIndexesSource


@singleton
class SymbolSources(metaclass=ABCMeta):
    @property
    @abstractmethod
    def sources(self):
        raise NotImplementedError()


@inject
class AllSymbolSources(SymbolSources):
    cbr_currencies_source: CbrCurrenciesSource
    cbr_top_rates_source: CbrTopRatesSource
    inflation_source: InflationSource
    moex_indexes_source: MoexIndexesSource
    micex_stocks_source: MicexStocksSource
    mut_ru_source: MutualFundsRuSource
    quandl_source: QuandlSource
    okama_source: OkamaSource
    yahoo_indexes_source: YahooIndexesSource

    @property
    def sources(self):
        return [
            self.cbr_currencies_source,
            self.cbr_top_rates_source,
            self.inflation_source,
            self.micex_stocks_source,
            self.moex_indexes_source,
            self.mut_ru_source,
            self.quandl_source,
            self.okama_source,
            self.yahoo_indexes_source,
        ]
