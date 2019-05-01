from typing import List, Dict, Union

import numpy as np
import pandas as pd
from contracts import contract
from serum import inject, singleton, Context

from ._sources.registries import FinancialSymbolsRegistry
from ._sources.all_sources import AllSymbolSources
from .common.enums import Currency, SecurityType
from .common.financial_symbol import FinancialSymbol
from .common.financial_symbol_id import FinancialSymbolId
from ._portfolio.portfolio import Portfolio, PortfolioAsset
from ._portfolio.currency import PortfolioCurrencyFactory
from ._search import _Search


@singleton
class Yapo:

    @inject
    def __init__(self,
                 fin_syms_registry: FinancialSymbolsRegistry,
                 portfolio_currency_factory: PortfolioCurrencyFactory):
        self.__search = _Search()
        self.fin_syms_registry = fin_syms_registry
        self.portfolio_currency_factory = portfolio_currency_factory
        self.__period_lowest = '1900-1'
        self.__period_highest = lambda: str(pd.Period.now(freq='M'))

    def information(self, **kwargs) -> Union[FinancialSymbol, List[FinancialSymbol]]:
        """
        Fetches financial symbol information based on internal ID.
        The information includes ISIN, short and long
        names, exchange, currency, etc.

        :param kwargs:
            either `name` or `names` should be defined

            name (str): name of a financial symbol

            names (List[str]): names of financial symbols

        :returns: financial symbol information
        """
        if 'name' in kwargs:
            name = kwargs['name']
            financial_symbol_id = FinancialSymbolId.parse(name)
            finsym_info = self.fin_syms_registry.get(financial_symbol_id)
            return finsym_info
        elif 'names' in kwargs:
            names = kwargs['names']
            finsym_infos = [self.information(name=name) for name in names]
            return finsym_infos
        else:
            raise Exception('Unexpected state of kwargs')

    def portfolio_asset(self,
                        currency: str=None,
                        start_period: str=None, end_period: str=None,
                        **kwargs) -> Union[PortfolioAsset, List[PortfolioAsset], None]:
        if start_period is None:
            start_period = self.__period_lowest
        if end_period is None:
            end_period = self.__period_highest()

        if 'name' in kwargs:
            start_period = pd.Period(start_period, freq='M')
            end_period = pd.Period(end_period, freq='M')

            name = kwargs['name']
            finsym_info = self.information(name=name)

            if finsym_info is None:
                return None

            currency = finsym_info.currency if currency is None else Currency.__dict__[currency.upper()]

            allowed_security_types = {SecurityType.STOCK_ETF, SecurityType.MUT,
                                      SecurityType.CURRENCY, SecurityType.INDEX}
            assert finsym_info.security_type in allowed_security_types
            a = PortfolioAsset(symbol=finsym_info,
                               start_period=start_period, end_period=end_period, currency=currency)
            return a
        elif 'names' in kwargs:
            names = kwargs['names']
            assets = [self.portfolio_asset(name=name,
                                           start_period=start_period, end_period=end_period,
                                           currency=currency) for name in names]
            assets = list(filter(None.__ne__, assets))
            return assets
        else:
            raise Exception('Unexpected state of kwargs')
        pass

    @contract(
        assets='dict[N](str: float|int,>0), N>0',
    )
    def portfolio(self,
                  assets: Dict[str, float],
                  currency: str,
                  start_period: str=None, end_period: str=None) -> Portfolio:
        """
        :param assets: list of RostSber IDs. Supported security types: stock/ETF, MUT, Currency
        :param start_period: preferred period to start
        :param end_period: preferred period to end
        :param currency: common currency for all assets
        :return: returns instance of portfolio
        """
        if start_period is None:
            start_period = self.__period_lowest
        if end_period is None:
            end_period = self.__period_highest()

        names = list(assets.keys())
        assets_resolved = self.portfolio_asset(names=names,
                                               start_period=str(pd.Period(start_period, freq='M') - 1),
                                               end_period=end_period,
                                               currency=currency)
        assets = {a: assets[a.symbol.identifier.format()] for a in assets_resolved}
        weights_sum = np.abs(np.fromiter(assets.values(), dtype=float, count=len(assets)).sum())
        if np.abs(weights_sum - 1.) > 1e-3:
            assets = {a: (w / weights_sum) for a, w in assets.items()}

        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        currency = Currency.__dict__[currency.upper()]

        portfolio_instance = Portfolio(assets=list(assets.keys()),
                                       weights=list(assets.values()),
                                       start_period=start_period, end_period=end_period,
                                       currency=currency)
        return portfolio_instance

    def available_names(self, **kwargs):
        """
        Returns the list of registered financial symbols names

        :param kwargs:
            either `namespace`, or `namespaces`, or nothing should be provided

            namespace (str): namespace of financial symbols

            namespaces (List[str]): a list of namespaces of financial symbols

            DEFAULT: returns the list of all registered namespaces

        :returns: (List[str]) list of financial symbols full names
        """
        if 'namespace' in kwargs:
            namespace = kwargs['namespace']
            return self.fin_syms_registry.get_all_infos(namespace)
        elif 'namespaces' in kwargs:
            namespaces = kwargs['namespaces']
            assert isinstance(namespaces, list)
            return [name
                    for namespace in namespaces
                    for name in self.available_names(namespace=namespace)]
        else:
            return self.fin_syms_registry.namespaces()

    def search(self, query, top=10):
        return self.__search.perform(query, top)

    def inflation(self, currency: str, kind: str,
                  end_period: str = None,
                  start_period: str = None, years_ago: int = None):
        currency = Currency.__dict__[currency.upper()]
        pc = self.portfolio_currency_factory.create(currency=currency)
        if start_period:
            start_period = pd.Period(start_period, freq='M')
        elif years_ago is None:
            start_period = pc.period_min
        end_period = pd.Period(end_period, freq='M') if end_period else pc.period_max
        inflation_ts = pc.inflation(kind=kind,
                                    start_period=start_period, end_period=end_period,
                                    years_ago=years_ago)
        return inflation_ts


with Context(AllSymbolSources):
    yapo_instance = Yapo()
information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
available_names = yapo_instance.available_names
search = yapo_instance.search
inflation = yapo_instance.inflation
