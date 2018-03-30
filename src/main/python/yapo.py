from typing import List, Dict, Union

import numpy as np
import pandas as pd
from contracts import contract

from model.Enums import Currency, SecurityType
from model.FinancialSymbol import FinancialSymbol
from model.FinancialSymbolId import FinancialSymbolId
from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer
from model.Portfolio import Portfolio, PortfolioAsset


class Yapo:
    def __init__(self, fin_syms_registry):
        self.fin_syms_registry = fin_syms_registry
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
                        **kwargs) -> Union[PortfolioAsset, List[PortfolioAsset]]:
        if start_period is None:
            start_period = self.__period_lowest
        if end_period is None:
            end_period = self.__period_highest()

        if 'name' in kwargs:
            start_period = pd.Period(start_period, freq='M')
            end_period = pd.Period(end_period, freq='M')

            name = kwargs['name']
            finsym_info = self.information(name=name)
            currency = finsym_info.currency if currency is None else Currency.__dict__[currency.upper()]

            allowed_security_types = {SecurityType.STOCK_ETF, SecurityType.MUT, SecurityType.CURRENCY}
            assert finsym_info.security_type in allowed_security_types
            return PortfolioAsset(finsym_info,
                                  start_period=start_period, end_period=end_period, currency=currency)
        elif 'names' in kwargs:
            names = kwargs['names']
            asset = [self.portfolio_asset(name=name,
                                          start_period=start_period, end_period=end_period,
                                          currency=currency) for name in names]
            return asset
        else:
            raise Exception('Unexpected state of kwargs')
        pass

    @contract(
        assets='dict[N](str: float,>0), N>0',
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
        weights = np.fromiter(assets.values(), dtype=float, count=len(names))
        if np.abs(weights.sum() - 1.) > 1e-3:
            weights /= np.abs(weights.sum())

        assets = self.portfolio_asset(names=names,
                                      start_period=start_period, end_period=end_period,
                                      currency=currency)

        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        currency = Currency.__dict__[currency.upper()]

        portfolio_instance = Portfolio(assets=assets, weights=weights,
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


yapo_instance = Yapo(fin_syms_registry=FinancialSymbolsSourceContainer.financial_symbols_registry())
information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
available_names = yapo_instance.available_names
