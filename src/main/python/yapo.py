from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer as Container
from model.Portfolio import Portfolio
from contracts import contract
from typing import Tuple, List


def information(**kwargs):
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
    registry = Container.financial_symbols_registry()
    if 'name' in kwargs:
        name = kwargs['name']
        ticker_namespace, ticker = name.split('/')
        finsym_info = registry.get(ticker_namespace, ticker)
        return finsym_info
    elif 'names' in kwargs:
        names = kwargs['names']
        finsym_infos = [information(name=name) for name in names]
        return finsym_infos
    else:
        raise Exception('Unexpected state of kwargs')


def portfolio(names: List[str]) -> List[FinancialSymbol]:
    """
    :param names: (:obj:`list` of :obj:`str`):
    :return: (:obj:`list` of :obj:`FinancialSymbol`)
    """
    if isinstance(names, list):
        finsym_infos = [information(name) for name in names]
        return finsym_infos
    else:
        raise Exception('Unexpected type of `names`')
