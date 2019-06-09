import pinject

from ._instance import Yapo
from ._sources.all_sources import AllSymbolSources


class BindingSpec(pinject.BindingSpec):
    def configure(self, bind):
        bind('symbol_sources', to_class=AllSymbolSources)


obj_graph = pinject.new_object_graph(binding_specs=[BindingSpec()])
yapo_instance = obj_graph.provide(Yapo)

information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
available_names = yapo_instance.available_names
search = yapo_instance.search
inflation = yapo_instance.inflation
