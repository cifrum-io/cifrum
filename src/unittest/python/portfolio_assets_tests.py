import unittest

from freezegun import freeze_time
from serum import Context
import pandas as pd
import numpy as np
import datetime as dtm

from yapo._sources.all_sources import SymbolSources
from yapo._sources.base_classes import SingleFinancialSymbolSource
from yapo.common.enums import Currency, SecurityType, Period

import yapo


class PortfolioAssetsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.portfolio = yapo.portfolio(assets={'mut_ru/0890-94127385': 1., 'micex/FXRU': 1., 'micex/FXMM': 1.,
                                               'cbr/USD': 1., 'cbr/EUR': 1., 'cbr/RUB': 1.},
                                       start_period='2015-3', end_period='2017-5', currency='USD')

    def test__fail_if_asset_security_type_is_not_supported(self):
        unsupported_ids = ['infl/RUB', 'infl/USD', 'infl/EUR', 'cbr/TOP_rates']

        for unsupported_id in unsupported_ids:
            self.assertRaises(AssertionError,
                              lambda: yapo.portfolio_asset(name=unsupported_id,
                                                           start_period='2011-3', end_period='2015-5', currency='USD'))

    def test__period_should_be_sorted(self):
        for asset in self.portfolio.assets.values():
            period_range = asset.close().period_range()
            self.assertTrue(all(period_range[i] <= period_range[i + 1]
                                for i in range(len(period_range) - 1)))

    def test__default_periods(self):
        asset = yapo.portfolio_asset(name='micex/SBER')
        self.assertGreaterEqual(asset.close().start_period, pd.Period('1900-1', freq='M'))
        self.assertGreaterEqual(pd.Period.now(freq='M'), asset.close().end_period)
        self.assertEqual(asset.currency.value, Currency.RUB)

        portfolio = yapo.portfolio(assets={'micex/SBER': 1.}, currency='rub')
        self.assertGreaterEqual(portfolio.rate_of_return().start_period, pd.Period('1900-1', freq='M'))
        self.assertGreaterEqual(pd.Period.now(freq='M'), portfolio.rate_of_return().end_period)

    @freeze_time('2018-10-31 1:0:0')
    def test__data_for_last_month_period_should_be_dropped(self):
        class TestSymbolSources(SymbolSources):
            def __init__(self):
                num_days = 70
                date_start = dtm.datetime.now() - dtm.timedelta(days=num_days)
                date_list = pd.date_range(date_start, periods=num_days, freq='D')

                self.values = pd.DataFrame({'close': np.linspace(start=1., stop=100., num=num_days),
                                            'date': date_list})

            @property
            def sources(self):
                return [SingleFinancialSymbolSource(
                            namespace='test_ns', name='test',
                            values_fetcher=lambda: self.values,
                            security_type=SecurityType.STOCK_ETF,
                            start_period=pd.Period(self.values['date'].min(), freq='D'),
                            end_period=pd.Period(self.values['date'].max(), freq='D'),
                            period=Period.DAY,
                            currency=Currency.RUB)]

        with Context(TestSymbolSources):
            yapo_instance = yapo._instance.Yapo()
        end_period = pd.Period.now(freq='M')
        start_period = end_period - 2
        asset = yapo_instance.portfolio_asset(name='test_ns/test',
                                              start_period=str(start_period), end_period=str(end_period),
                                              currency='USD')
        self.assertEqual(set(asset.close().period_range()),
                         {end_period - 1, end_period - 2})

    @freeze_time('2018-1-30 1:0:0')
    def test__quandl_values(self):
        asset = yapo.portfolio_asset(name='ny/MSFT',
                                     start_period='2017-11', end_period='2018-2', currency='usd')
        self.assertEqual(set(asset.close().period_range()),
                         {pd.Period('2017-11'), pd.Period('2017-12')})

    @freeze_time('2018-10-31 1:0:0')
    def test__drop_last_month_data_if_no_activity_within_last_full_month(self):
        class TestSymbolSources(SymbolSources):
            def __init__(self):
                num_days = 58
                date_start = dtm.datetime.now() - dtm.timedelta(days=num_days + 32)
                date_list = pd.date_range(date_start, periods=num_days, freq='D')

                self.values = pd.DataFrame({'close': np.linspace(start=10., stop=100., num=num_days),
                                            'date': date_list})

            @property
            def sources(self):
                return [SingleFinancialSymbolSource(
                            namespace='test_ns', name='test',
                            values_fetcher=lambda: self.values,
                            security_type=SecurityType.STOCK_ETF,
                            start_period=pd.Period(self.values['date'].min(), freq='D'),
                            end_period=pd.Period(self.values['date'].max(), freq='D'),
                            period=Period.DAY,
                            currency=Currency.RUB)]

        with Context(TestSymbolSources):
            yapo_instance = yapo._instance.Yapo()
        end_period = pd.Period.now(freq='M')
        start_period = end_period - 2
        asset = yapo_instance.portfolio_asset(name='test_ns/test',
                                              start_period=str(start_period), end_period=str(end_period),
                                              currency='USD')
        self.assertEqual(set(asset.close().period_range()), {end_period - 2})

    def test__compute_accumulated_rate_of_return(self):
        for asset in self.portfolio.assets.values():
            aror = asset.rate_of_return(kind='accumulated').values
            self.assertTrue(not np.all(np.isnan(aror)))
        self.assertTrue(not np.all(np.isnan(self.portfolio.rate_of_return(kind='accumulated').values)))

    def test__close_and_its_change_should_preserve_ratio(self):
        for asset in self.portfolio.assets.values():
            rate_of_return_given = asset.rate_of_return().values
            rate_of_return_expected = np.diff(asset.close().values) / asset.close().values[:-1]
            np.testing.assert_almost_equal(rate_of_return_given, rate_of_return_expected)

    def test__fail_if_date_range_is_short(self):
        # Asset
        self.assertRaises(ValueError,
                          lambda: yapo.portfolio_asset(name='micex/FXRU', start_period='2015-3', end_period='2015-4'))

        try:
            yapo.portfolio_asset(name='micex/FXRU', start_period='2015-3', end_period='2015-4')
        except ValueError as e:
            self.assertTrue(e.args[0].startswith('period range should'))

        # Portfolio
        self.assertRaises(ValueError,
                          lambda: yapo.portfolio(assets={'micex/FXRU': 1.},
                                                 start_period='2015-3', end_period='2015-4',
                                                 currency='rub'))

        try:
            yapo.portfolio(assets={'micex/FXRU': 1.},
                           start_period='2015-3', end_period='2015-4',
                           currency='rub')
        except ValueError as e:
            self.assertTrue(e.args[0].startswith('period range should'))
