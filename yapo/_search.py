from typing import List, Optional

from serum import inject
import re

from .common.financial_symbol_id import FinancialSymbolId
from .common.financial_symbol import FinancialSymbol
from ._sources.registries import FinancialSymbolsRegistry
from ._sources.all_sources import AllSymbolSources


@inject
class _Search:
    sources: AllSymbolSources
    fin_syms_registry: FinancialSymbolsRegistry

    def __init__(self):
        self.id2sym = {}

        def handle_quandl_info(x, src):
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            line = '{} {} {}'.format(fin_sym.name, fin_sym.exchange, fin_sym.short_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        def handle_micex_stocks(x, src):
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            line = '{} {} {} {}'.format(fin_sym.name, fin_sym.exchange, fin_sym.isin, fin_sym.long_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        def handle_mutru(x, src):
            fin_sym = src.fetch_financial_symbol(x.fin_sym_id.name)

            line = '{} {}'.format(fin_sym.name, fin_sym.short_name)
            line = re.sub(r'\s+', ' ', line.lower())

            self.id2sym.update({line: fin_sym})

            return line

        quandl_lines = [handle_quandl_info(x, self.sources.quandl_source)
                        for x in self.sources.quandl_source.get_all_infos()]
        micex_stocks_lines = [handle_micex_stocks(x, self.sources.micex_stocks_source)
                              for x in self.sources.micex_stocks_source.get_all_infos()]
        mutru_lines = [handle_mutru(x, self.sources.mut_ru_source)
                       for x in self.sources.mut_ru_source.get_all_infos()]

        self.lines = quandl_lines + micex_stocks_lines + mutru_lines

    def _check_finsym_access(self, query: str) -> Optional[FinancialSymbol]:
        namespaces = self.fin_syms_registry.namespaces()

        starts_with_namespace = False
        for ns in namespaces:
            if query.startswith(ns + '/'):
                starts_with_namespace = True
                break
        if not starts_with_namespace:
            return None

        fsid = FinancialSymbolId.parse(query)
        return self.fin_syms_registry.get(fsid)

    @inject
    def perform(self, query: str, top: int) -> List[FinancialSymbol]:
        try:
            fs = self._check_finsym_access(query=query)
        except Exception:
            fs = None

        if fs:
            return [fs]
        else:
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

            r = [(l.find(query), l) for l in self.lines]
            r = filter(lambda x: x[0] != -1, r)
            r = sorted(r, key=lambda x: '{:4d} {}'.format(x[0], x[1]))
            r = r[:top]
            r = [self.id2sym[x[1]] for x in r]
            return list(r)[:top]
