from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer
from model.Portfolio import Portfolio
from model.Enums import Currency, SecurityType
from model.FinancialSymbol import FinancialSymbol
from contracts import contract
from typing import Tuple, List, Union
import pandas as pd
import numpy as np


class Yapo:
    def __init__(self, fin_syms_registry):
        self.fin_syms_registry = fin_syms_registry

    def information(self, **kwargs) -> Union[FinancialSymbol, List[FinancialSymbol]]:
        """
        Fetches ticker information based on internal ID.
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
            ticker_namespace, ticker = name.split('/')
            finsym_info = self.fin_syms_registry.get(ticker_namespace, ticker)
            return finsym_info
        elif 'names' in kwargs:
            names = kwargs['names']
            finsym_infos = [self.information(name=name) for name in names]
            return finsym_infos
        else:
            raise Exception('Unexpected state of kwargs')

    @contract(
        assets='list[N], N>0',
    )
    def portfolio(self,
                  assets: List[Tuple[str, float]],
                  start_period, end_period, currency) -> Portfolio:
        """
        :param assets: list of RostSber IDs. Supported security types: stock/ETF, MUT, Currency
        :param start_period: preferred period to start
        :param end_period: preferred period to end
        :param currency: common currency for all assets
        :return: returns instance of portfolio
        """
        [names, weights] = zip(*assets)
        weights = np.array(weights)
        assert np.all(weights > 0.)
        weights_sum = np.abs(weights.sum())
        weights = weights / weights_sum

        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        currency = Currency.__dict__[currency.upper()]

        finsym_infos = self.information(names=names)

        allowed_security_types = {SecurityType.STOCK_ETF, SecurityType.MUT, SecurityType.CURRENCY}
        for sym in finsym_infos:
            assert sym.security_type in allowed_security_types

        portfolio_instance = Portfolio(finsym_infos,
                                       weights,
                                       start_period=start_period,
                                       end_period=end_period,
                                       currency=currency)
        return portfolio_instance


yapo_instance = Yapo(fin_syms_registry=FinancialSymbolsSourceContainer.financial_symbols_registry())
information = yapo_instance.information
portfolio = yapo_instance.portfolio
