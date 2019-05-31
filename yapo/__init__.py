from serum import Context

from ._instance import Yapo
from ._sources.all_sources import AllSymbolSources

with Context(AllSymbolSources):
    yapo_instance = Yapo()
information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
available_names = yapo_instance.available_names
search = yapo_instance.search
inflation = yapo_instance.inflation
