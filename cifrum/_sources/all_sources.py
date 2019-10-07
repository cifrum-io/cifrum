from abc import ABCMeta, abstractmethod
from typing import List

from .._sources.base_classes import FinancialSymbolsSource
from .._sources.inflation_source import InflationSource
from .._sources.micex_stocks_source import MicexStocksSource
from .._sources.moex_indexes_source import MoexIndexesSource
from .._sources.mutru_funds_source import MutualFundsRuSource
from .._sources.okama_source import OkamaSource
from .._sources.us_data_source import UsDataSource
from .._sources.single_financial_symbol_source import CbrCurrenciesSource, CbrTopRatesSource
from .._sources.yahoo_indexes_source import YahooIndexesSource


class SymbolSources(metaclass=ABCMeta):
    @property
    @abstractmethod
    def sources(self) -> List[FinancialSymbolsSource]:
        raise NotImplementedError()


class AllSymbolSources(SymbolSources):

    def __init__(self,
                 cbr_currencies_source: CbrCurrenciesSource,
                 cbr_top_rates_source: CbrTopRatesSource,
                 inflation_source: InflationSource,
                 micex_stocks_source: MicexStocksSource,
                 moex_indexes_source: MoexIndexesSource,
                 mutual_funds_ru_source: MutualFundsRuSource,
                 us_data_source: UsDataSource,
                 okama_source: OkamaSource,
                 yahoo_indexes_source: YahooIndexesSource):
        self.cbr_currencies_source = cbr_currencies_source
        self.cbr_top_rates_source = cbr_top_rates_source
        self.inflation_source = inflation_source
        self.micex_stocks_source = micex_stocks_source
        self.moex_indexes_source = moex_indexes_source
        self.mutual_funds_ru_source = mutual_funds_ru_source
        self.us_data_source = us_data_source
        self.okama_source = okama_source
        self.yahoo_indexes_source = yahoo_indexes_source

    @property
    def sources(self):
        return [
            self.cbr_currencies_source,
            self.cbr_top_rates_source,
            self.inflation_source,
            self.micex_stocks_source,
            self.moex_indexes_source,
            self.mutual_funds_ru_source,
            self.us_data_source,
            self.okama_source,
            self.yahoo_indexes_source,
        ]
