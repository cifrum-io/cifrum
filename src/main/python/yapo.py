from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer
from model.Portfolio import Portfolio, PortfolioAsset
from model.Enums import Currency, SecurityType
from model.FinancialSymbol import FinancialSymbol
from model.FinancialSymbolId import FinancialSymbolId
from contracts import contract
from typing import List, Dict, Union
import pandas as pd
import numpy as np


class Yapo:
    def __init__(self, fin_syms_registry):
        self.fin_syms_registry = fin_syms_registry

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
                        start_period: str, end_period: str,
                        currency: str,
                        **kwargs) -> Union[PortfolioAsset, List[PortfolioAsset]]:
        if 'name' in kwargs:
            start_period = pd.Period(start_period, freq='M')
            end_period = pd.Period(end_period, freq='M')
            currency = Currency.__dict__[currency.upper()]

            name = kwargs['name']
            finsym_info = self.information(name=name)

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
                  start_period: str, end_period: str, currency) -> Portfolio:
        """
        :param assets: list of RostSber IDs. Supported security types: stock/ETF, MUT, Currency
        :param start_period: preferred period to start
        :param end_period: preferred period to end
        :param currency: common currency for all assets
        :return: returns instance of portfolio
        """
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


yapo_instance = Yapo(fin_syms_registry=FinancialSymbolsSourceContainer.financial_symbols_registry())
information = yapo_instance.information
portfolio = yapo_instance.portfolio
portfolio_asset = yapo_instance.portfolio_asset
