import pinject

import cifrum._index
import cifrum._portfolio
import cifrum._portfolio.currency
import cifrum._portfolio.portfolio
import cifrum._search
import cifrum._sources.all_sources
import cifrum._sources.base_classes
import cifrum._sources.inflation_source
import cifrum._sources.micex_stocks_source
import cifrum._sources.moex_indexes_source
import cifrum._sources.mutru_funds_source
import cifrum._sources.okama_source
import cifrum._sources.registries
import cifrum._sources.single_financial_symbol_source
import cifrum._sources.us_data_source
import cifrum._sources.yahoo_indexes_source
import cifrum.common
from ._instance import Cifrum
from ._sources.all_sources import AllSymbolSources


class BindingSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind('symbol_sources', to_class=AllSymbolSources)


obj_graph = pinject.new_object_graph(binding_specs=[BindingSpec()],
                                     modules=[cifrum.common, cifrum._index, cifrum._portfolio,
                                              cifrum._sources.registries,
                                              cifrum._sources.all_sources,
                                              cifrum._sources.base_classes,
                                              cifrum._sources.inflation_source,
                                              cifrum._sources.micex_stocks_source,
                                              cifrum._sources.moex_indexes_source,
                                              cifrum._sources.mutru_funds_source,
                                              cifrum._sources.okama_source,
                                              cifrum._sources.single_financial_symbol_source,
                                              cifrum._sources.us_data_source,
                                              cifrum._sources.yahoo_indexes_source,
                                              cifrum._portfolio.currency,
                                              cifrum._portfolio.portfolio,
                                              cifrum._search,
                                              ])
cifrum_instance = obj_graph.provide(Cifrum)

information = cifrum_instance.information
portfolio = cifrum_instance.portfolio
portfolio_asset = cifrum_instance.portfolio_asset
available_names = cifrum_instance.available_names
search = cifrum_instance.search
inflation = cifrum_instance.inflation
currency = cifrum_instance.currency
