import pinject

import yapo._index
import yapo._portfolio
import yapo._portfolio.currency
import yapo._portfolio.portfolio
import yapo._search
import yapo._sources.all_sources
import yapo._sources.base_classes
import yapo._sources.inflation_source
import yapo._sources.micex_stocks_source
import yapo._sources.moex_indexes_source
import yapo._sources.mutru_funds_source
import yapo._sources.okama_source
import yapo._sources.registries
import yapo._sources.single_financial_symbol_source
import yapo._sources.us_data_source
import yapo._sources.yahoo_indexes_source
import yapo.common
from ._instance import Yapo
from ._sources.all_sources import AllSymbolSources


class BindingSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind('symbol_sources', to_class=AllSymbolSources)


obj_graph = pinject.new_object_graph(binding_specs=[BindingSpec()],
                                     modules=[yapo.common, yapo._index, yapo._portfolio,
                                              yapo._sources.registries,
                                              yapo._sources.all_sources,
                                              yapo._sources.base_classes,
                                              yapo._sources.inflation_source,
                                              yapo._sources.micex_stocks_source,
                                              yapo._sources.moex_indexes_source,
                                              yapo._sources.mutru_funds_source,
                                              yapo._sources.okama_source,
                                              yapo._sources.single_financial_symbol_source,
                                              yapo._sources.us_data_source,
                                              yapo._sources.yahoo_indexes_source,
                                              yapo._portfolio.currency,
                                              yapo._portfolio.portfolio,
                                              yapo._search,
                                              ])
yapo_instance = obj_graph.provide(Yapo)

information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
available_names = yapo_instance.available_names
search = yapo_instance.search
inflation = yapo_instance.inflation
currency = yapo_instance.currency
