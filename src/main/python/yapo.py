from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer as Container
from model.FinancialSymbol import FinancialSymbol
from typing import List


def information(name: str) -> FinancialSymbol:
    """
    Fetches ticker information based on internal ID. The information includes ISIN, short and long
    names, exchange, currency, etc.

    :param name: string that contains list of RostSber IDs separated by comma
    :returns: financial symbol information
    """
    if isinstance(name, str):
        registry = Container.financial_symbols_registry()
        ticker_namespace, ticker = name.split('/')
        finsym_info = registry.get(ticker_namespace, ticker)
        return finsym_info
    else:
        raise Exception('Unexpected type of `name`')


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
