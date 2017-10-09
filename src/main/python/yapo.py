from model.FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer as Container


def information(ids: str):
    """
    Fetches ticker information based on internal ID. The information includes ISIN, short and long
    names, exchange, currency, etc.

    :param ids: a string that contains list of RostSber IDs separated by comma
    :returns: - list of tickers information if 2 or more IDs are provided
              - ticker information if single ID is provided
    """
    ids_arr = [s.strip() for s in ids.split(',')]
    tickers_info = []
    for id_str in ids_arr:
        ticker_namespace, ticker = id_str.split('/')
        registry = Container.financial_symbols_registry()
        ticker_info = registry.get(ticker_namespace, ticker)
        tickers_info.append(ticker_info)
    tickers_info = tickers_info[0] if len(tickers_info) == 1 else tickers_info
    return tickers_info
