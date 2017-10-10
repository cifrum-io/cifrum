from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer as Container


def information(ids):
    """
    Fetches ticker information based on internal ID. The information includes ISIN, short and long
    names, exchange, currency, etc.

    :param ids: a list of strings that contains list of RostSber IDs separated by comma
    :returns: - list of tickers information if 2 or more IDs are provided
              - ticker information if single ID is provided
    """
    if isinstance(ids, str):
        registry = Container.financial_symbols_registry()
        ticker_namespace, ticker = ids.split('/')
        ticker_info = registry.get(ticker_namespace, ticker)
        return ticker_info
    elif isinstance(ids, list):
        return [information(id_str) for id_str in ids]
    else:
        raise Exception('Unexpected type of `ids`')
