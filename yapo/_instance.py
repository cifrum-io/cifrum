from typing import List, Dict, Union, Optional

import numpy as np
import pandas as pd
from contracts import contract

from ._portfolio.currency import PortfolioCurrencyFactory
from ._portfolio.portfolio import Portfolio, PortfolioAsset, PortfolioItemsFactory
from ._search import _Search
from ._sources.registries import FinancialSymbolsRegistry
from .common.enums import Currency, SecurityType
from .common.financial_symbol import FinancialSymbol
from .common.financial_symbol_id import FinancialSymbolId


class Yapo:

    def __init__(self,
                 financial_symbols_registry: FinancialSymbolsRegistry,
                 portfolio_currency_factory: PortfolioCurrencyFactory,
                 portfolio_items_factory: PortfolioItemsFactory,
                 search: _Search):
        self.portfolio_currency_factory = portfolio_currency_factory
        self.portfolio_items_factory = portfolio_items_factory
        self.financial_symbols_registry = financial_symbols_registry
        self.__search = search
        self.__period_lowest = '1900-1'
        self.__period_highest = lambda: str(pd.Period.now(freq='M'))

    def information(self, **kwargs) -> Union[Optional[FinancialSymbol], List[Optional[FinancialSymbol]]]:
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
            finsym_info = self.financial_symbols_registry.get(financial_symbol_id)
            return finsym_info
        elif 'names' in kwargs:
            names = kwargs['names']
            finsym_infos: List[Optional[FinancialSymbol]] = []
            for name in names:
                finsym_info1 = self.information(name=name)
                if not (finsym_info1 is None or isinstance(finsym_info1, FinancialSymbol)):
                    raise ValueError('Unexpected type of financial symbol information')
                finsym_infos.append(finsym_info1)
            return finsym_infos
        else:
            raise Exception('Unexpected state of kwargs')

    def portfolio_asset(self,
                        currency: str = None,
                        start_period: str = None, end_period: str = None,
                        **kwargs) -> Union[PortfolioAsset, List[PortfolioAsset], None]:
        if start_period is None:
            start_period = self.__period_lowest
        if end_period is None:
            end_period = self.__period_highest()

        if 'name' in kwargs:
            start_period = pd.Period(start_period, freq='M')
            end_period = pd.Period(end_period, freq='M')

            name: str = kwargs['name']
            finsym_info = self.information(name=name)

            if finsym_info is None:
                return None
            if not isinstance(finsym_info, FinancialSymbol):
                raise ValueError('Unexpected type of financial symbol information')

            if currency is None:
                currency_enum: Currency = finsym_info.currency
            else:
                currency_enum = Currency.__dict__[currency.upper()]  # type: ignore

            allowed_security_types = {SecurityType.STOCK_ETF, SecurityType.MUT,
                                      SecurityType.CURRENCY, SecurityType.INDEX}
            assert finsym_info.security_type in allowed_security_types
            a = self.portfolio_items_factory.new_asset(symbol=finsym_info,
                                                       start_period=start_period, end_period=end_period,
                                                       currency=currency_enum)
            return a
        elif 'names' in kwargs:
            names: List[str] = kwargs['names']
            assets: List[PortfolioAsset] = []
            for name in names:
                pa = self.portfolio_asset(name=name,
                                          start_period=start_period, end_period=end_period,
                                          currency=currency)
                if pa is None:
                    continue
                if not isinstance(pa, PortfolioAsset):
                    raise ValueError('Unexpected type of portfolio asset')
                assets.append(pa)
            return assets
        else:
            raise ValueError('Unexpected state of `kwargs`. Either `name`, or `names` should be given')
        pass

    @contract(
        assets='dict[N](str: float|int,>0), N>0',
    )
    def portfolio(self,
                  assets: Dict[str, float],
                  currency: str,
                  start_period: str = None, end_period: str = None) -> Portfolio:
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
        assets_resolved = \
            self.portfolio_asset(names=names,
                                 start_period=str(pd.Period(start_period, freq='M') - 1),
                                 end_period=end_period,
                                 currency=currency)
        if not isinstance(assets_resolved, list):
            raise ValueError('`assets_resolved` should be list')
        asset2weight_dict: Dict[PortfolioAsset, float] = \
            {a: assets[a.symbol.identifier.format()] for a in assets_resolved}
        weights_sum: float = \
            np.abs(np.fromiter(asset2weight_dict.values(), dtype=float, count=len(asset2weight_dict)).sum())

        if np.abs(weights_sum - 1.) > 1e-3:
            asset2weight_dict = {a: (w / weights_sum) for a, w in asset2weight_dict.items()}

        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        currency_enum: Currency = Currency.__dict__[currency.upper()]  # type: ignore

        portfolio_instance = \
            self.portfolio_items_factory.new_portfolio(assets_to_weight=asset2weight_dict,
                                                       start_period=start_period, end_period=end_period,
                                                       currency=currency_enum)
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
            return self.financial_symbols_registry.get_all_infos(namespace)
        elif 'namespaces' in kwargs:
            namespaces = kwargs['namespaces']
            assert isinstance(namespaces, list)
            return [name
                    for namespace in namespaces
                    for name in self.available_names(namespace=namespace)]
        else:
            return self.financial_symbols_registry.namespaces()

    def search(self, query: str, top=10):
        return self.__search.perform(query, top)

    def inflation(self, currency: str, kind: str,
                  end_period: str = None,
                  start_period: str = None, years_ago: int = None):
        currency_enum: Currency = Currency.__dict__[currency.upper()]  # type: ignore
        pc = self.portfolio_currency_factory.new(currency=currency_enum)
        if start_period:
            start_period = pd.Period(start_period, freq='M')
        elif years_ago is None:
            start_period = pc.period_min
        end_period = pd.Period(end_period, freq='M') if end_period else pc.period_max
        inflation_ts = pc.inflation(kind=kind,
                                    start_period=start_period, end_period=end_period,
                                    years_ago=years_ago)
        return inflation_ts
