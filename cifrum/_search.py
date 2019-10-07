import re
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple, Iterator, Dict

from typing_extensions import Protocol

from ._sources.base_classes import FinancialSymbolsSource
from ._sources.micex_stocks_source import MicexStocksSource
from ._sources.mutru_funds_source import MutualFundsRuSource
from ._sources.us_data_source import UsDataSource
from ._sources.registries import FinancialSymbolsRegistry
from .common.financial_symbol import FinancialSymbol
from .common.financial_symbol_id import FinancialSymbolId
from .common.financial_symbol_info import FinancialSymbolInfo


class SymbolSourcesSearchable(Protocol):
    us_data_source: UsDataSource
    micex_stocks_source: MicexStocksSource
    mutual_funds_ru_source: MutualFundsRuSource


class _Search:
    def __handle_us_data_info(self) -> List[str]:
        def func(x: FinancialSymbolInfo, src: FinancialSymbolsSource) -> str:
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            if fin_sym is None:
                return ''

            line = '{} {} {}'.format(fin_sym.name, fin_sym.exchange, fin_sym.short_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        lines = [func(x, self.symbol_sources.us_data_source)
                 for x in self.symbol_sources.us_data_source.get_all_infos()]
        return lines

    def __handle_micex_stocks(self) -> List[str]:
        def func(x: FinancialSymbolInfo, src: FinancialSymbolsSource) -> str:
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            if fin_sym is None:
                return ''

            line = '{} {} {} {}'.format(fin_sym.name, fin_sym.exchange, fin_sym.isin, fin_sym.long_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        lines = [func(x, self.symbol_sources.micex_stocks_source)
                 for x in self.symbol_sources.micex_stocks_source.get_all_infos()]
        return lines

    def __handle_mutru(self) -> List[str]:
        def func(x: FinancialSymbolInfo, src: FinancialSymbolsSource) -> str:
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            if fin_sym is None:
                return ''

            line = '{} {}'.format(fin_sym.name, fin_sym.short_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        lines = [func(x, self.symbol_sources.mutual_funds_ru_source)
                 for x in self.symbol_sources.mutual_funds_ru_source.get_all_infos()]
        return lines

    def __init__(self,
                 symbol_sources: SymbolSourcesSearchable,
                 financial_symbols_registry: FinancialSymbolsRegistry):
        self.symbol_sources = symbol_sources
        self.financial_symbols_registry = financial_symbols_registry

        self.id2sym: Dict[str, FinancialSymbol] = {}

        pool = ThreadPoolExecutor(3)

        us_data_source_lines_fut = pool.submit(self.__handle_us_data_info)
        micex_stocks_lines_fut = pool.submit(self.__handle_micex_stocks)
        mutru_lines_fut = pool.submit(self.__handle_mutru)

        def handle_all_lines() -> List[str]:
            result = us_data_source_lines_fut.result() + micex_stocks_lines_fut.result() + mutru_lines_fut.result()
            return result

        self.lines_future: futures.Future[List[str]] = pool.submit(handle_all_lines)

    def _check_finsym_access(self, query: str) -> Optional[FinancialSymbol]:
        namespaces = self.financial_symbols_registry.namespaces()

        starts_with_namespace = False
        for ns in namespaces:
            if query.startswith(ns + '/'):
                starts_with_namespace = True
                break
        if not starts_with_namespace:
            return None

        fsid = FinancialSymbolId.parse(query)
        return self.financial_symbols_registry.get(fsid)

    def perform(self, query: str, top: int) -> List[FinancialSymbol]:
        try:
            fs = self._check_finsym_access(query=query)
        except Exception:
            fs = None

        if fs is not None:
            return [fs]

        if not isinstance(query, str):
            raise ValueError('`query` should be string')
        if not isinstance(top, int):
            raise ValueError('`top` should be int')

        top = max(0, top)
        if not query or top == 0:
            return []

        query = re.sub(r'\s+', ' ', query.strip().lower())
        if len(query) == 0:
            return []

        lines: List[str] = self.lines_future.result()
        r: Iterator[Tuple[int, str]] = ((l.find(query), l) for l in lines)
        r = filter(lambda x: x[0] != -1, r)
        r_list = sorted(r, key=lambda x: '{:4d} {}'.format(x[0], x[1]))
        symbols: List[FinancialSymbol] = [self.id2sym[x[1]] for x in r_list[:top]]
        return symbols
