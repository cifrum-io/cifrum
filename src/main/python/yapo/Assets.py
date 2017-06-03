import pandas as pd
import dependency_injector.containers as containers
import dependency_injector.providers as providers
import os
import quandl
from yapo import Settings


class Asset:
    def __init__(self, namespace, ticker, values):
        self.namespace = namespace
        self.ticker = ticker
        self.values = values

    def values(self):
        return self.values()


class AssetsSource:
    def __init__(self, namespace):
        self.namespace = namespace

    def get_assets(self):
        raise Exception('should not be called')


class SingleItemAssetsSource(AssetsSource):
    def __init__(self, path, namespace, ticker):
        super().__init__(namespace)
        self.path = path
        self.ticker = ticker

    def get_assets(self):
        url = Settings.rostsber_url + self.path
        return [Asset(namespace=self.namespace,
                      ticker=self.ticker,
                      values=lambda: pd.read_csv(url, sep='\t'))
                ]


class MicexStocksAssetsSource(AssetsSource):
    def __init__(self):
        super().__init__('micex')
        self.url_base = Settings.rostsber_url + 'moex/stock_etf/'
        self.index = pd.read_csv(self.url_base + 'stocks_list.csv', sep='\t')

    def get_assets(self):
        assets = []
        for (idx, row) in self.index.iterrows():
            secid = row['SECID']
            asset = Asset(namespace=self.namespace,
                          ticker=secid,
                          values=lambda: pd.read_csv(self.url_base + secid + '.csv', sep='\t'))
            assets.append(asset)
        return assets


class NluAssetsSource(AssetsSource):
    def __init__(self):
        super().__init__('nlu')
        self.url_base = Settings.rostsber_url + 'mut_rus/'
        self.index = pd.read_csv(self.url_base + 'mut_rus.csv', sep='\t')

    def get_assets(self):
        assets = []
        for (idx, row) in self.index.iterrows():
            url = '{}/{}'.format(self.url_base, row['id'])
            asset = Asset(namespace=self.namespace,
                          ticker=str(row['id']),
                          values=lambda: pd.read_csv(url, sep='\t'))
            assets.append(asset)
        return assets


class AssetsRegistry(object):
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def __init__(self, asset_sources):
        self.assets = []
        for asset_source in asset_sources:
            self.assets += asset_source.get_assets()

    def get(self, namespace, ticker):
        if namespace == 'quandl':
            def extract_values():
                df = quandl.get('EOD/{}'.format(ticker), collapse='monthly')
                df_res = pd.DataFrame()
                df_res['close'] = df['Adj_Close']
                df_res['date'] = df_res.index
                return df_res

            asset = Asset(namespace=namespace, ticker=ticker, values=extract_values)
            return asset
        else:
            result = list(filter(
                lambda ast: ast.namespace == namespace and ast.ticker == ticker,
                self.assets
            ))
            if len(result) != 1:
                raise Exception('ticker {}/{} is not found'.format(namespace, ticker))

            return result[0]


class AssetSourceContainer(containers.DeclarativeContainer):
    currency_usd_rub_source = providers.Singleton(SingleItemAssetsSource,
                                                  path='currency/USD-RUB.csv',
                                                  namespace='cbr',
                                                  ticker='USD')

    inflation_ru_source = providers.Singleton(SingleItemAssetsSource,
                                              path='inflation_ru/data.csv',
                                              namespace='infl',
                                              ticker='RU')

    inflation_eu_source = providers.Singleton(SingleItemAssetsSource,
                                              path='inflation_eu/data.csv',
                                              namespace='infl',
                                              ticker='EU')

    micex_mcftr_source = providers.Singleton(SingleItemAssetsSource,
                                             path='moex/mcftr/data.csv',
                                             namespace='micex',
                                             ticker='MCFTR')

    micex_stocks_source = providers.Singleton(MicexStocksAssetsSource)

    nlu_muts_source = providers.Singleton(NluAssetsSource)

    assets_registry = providers.Singleton(AssetsRegistry,
                                          asset_sources=[
                                              currency_usd_rub_source(),
                                              inflation_ru_source(),
                                              inflation_eu_source(),
                                              micex_mcftr_source(),
                                              micex_stocks_source(),
                                              nlu_muts_source(),
                                          ])


def info(ids: str):
    """
    Fetches ticker info based on internal ID. The info includes ISIN, short and long names,
    exchange, currency, etc.

    :param ids: a string that contains list of RostSber IDs separated by comma
    :returns: list of tickers info
    """
    ids_arr = [s.strip() for s in ids.split(',')]
    tickers_info = []
    for id_str in ids_arr:
        ticker_namespace, ticker = id_str.split('/')
        asset = AssetSourceContainer.assets_registry().get(ticker_namespace, ticker)
        tickers_info.append(asset)
    return tickers_info
