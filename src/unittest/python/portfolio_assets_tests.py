import unittest

from pandas.core.dtypes.dtypes import PeriodDtype
from pandas.tseries.offsets import MonthEnd
import pandas as pd
import numpy as np
import datetime as dtm
from freezegun import freeze_time

import yapo
from model.Enums import Currency, Period, SecurityType
from model.FinancialSymbolsSource import SingleFinancialSymbolSource, FinancialSymbolsRegistry


class PortfolioAssetsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.portfolio = yapo.portfolio(assets={'quandl/MSFT': 1.,
                                               'micex/SBER': 1., 'micex/SBERP': 1.,
                                               'nlu/449': 1.,
                                               'cbr/USD': 1., 'cbr/EUR': 1., 'cbr/RUB': 1.},
                                       start_period='2011-3', end_period='2015-5', currency='USD')
        cls.epsilon = 1e-3

    def test_fail_if_asset_security_type_is_not_supported(self):
        unsupported_ids = ['infl/RUB', 'infl/USD', 'infl/EUR', 'cbr/TOP_rates', 'micex/MCFTR']

        for unsupported_id in unsupported_ids:
            self.assertRaises(AssertionError,
                              lambda: yapo.portfolio_asset(name=unsupported_id,
                                                           start_period='2011-3', end_period='2015-5', currency='USD'))

    def test_period_should_be_sorted(self):
        for asset in self.portfolio.assets:
            self.assertTrue(all(asset.period()[i] <= asset.period()[i + 1]
                                for i in range(len(asset.period()) - 1)))

    def test_values_should_have_correct_schema(self):
        for asset in self.portfolio.assets:
            self.assertTrue(set(asset.values.columns) >= {'period', 'close'})

    def test_default_periods(self):
        asset = yapo.portfolio_asset(name='micex/SBER')
        self.assertGreaterEqual(asset.period_min, pd.Period('1900-1', freq='M'))
        self.assertGreaterEqual(pd.Period.now(freq='M'), asset.period_max)
        self.assertEqual(asset.currency, Currency.RUB)

        portfolio = yapo.portfolio(assets={'micex/SBER': 1.}, currency='rub')
        self.assertGreaterEqual(portfolio.period_min, pd.Period('1900-1', freq='M'))
        self.assertGreaterEqual(pd.Period.now(freq='M'), portfolio.period_max)

    def test_index_should_be_numerical(self):
        for asset in self.portfolio.assets:
            self.assertTrue(set(asset.values.columns) >= {'period', 'close'})
            self.assertIsInstance(asset.values.index.dtype, PeriodDtype,
                                  msg='Incorrect index type for ' + str(asset))
            self.assertIsInstance(asset.values.index.dtype.freq, MonthEnd)

    def test_last_month_period_should_be_dropped(self):
        num_days = 60
        date_start = dtm.datetime.now() - dtm.timedelta(days=num_days)
        date_list = pd.date_range(date_start, periods=num_days, freq='D')

        np.random.seed(42)
        values = pd.DataFrame({'close': np.random.uniform(10., 100., num_days),
                               'date': date_list})

        test_source = SingleFinancialSymbolSource(
            namespace='test_ns', name='test',
            values_fetcher=lambda: values,
            security_type=SecurityType.STOCK_ETF,
            period=Period.DAY,
            currency=Currency.RUB
        )
        fin_sym_registry = FinancialSymbolsRegistry(symbol_sources=[test_source])
        yapo_instance = yapo.Yapo(fin_syms_registry=fin_sym_registry)
        end_period = pd.Period.now(freq='M')
        start_period = end_period - 2
        asset = yapo_instance.portfolio_asset(name='test_ns/test',
                                              start_period=str(start_period), end_period=str(end_period),
                                              currency='USD')
        self.assertEqual(set(asset.period()), {end_period - 1, end_period - 2})

    @freeze_time('2018-1-30 1:0:0')
    def test_quandl_values(self):
        asset = yapo.portfolio_asset(name='quandl/SPY',
                                     start_period='2017-11', end_period='2018-2', currency='usd')
        self.assertEqual(set(asset.period()), {pd.Period('2017-11'), pd.Period('2017-12')})

    def test_drop_last_month_data_if_no_activity_within_30_days(self):
        num_days = 60
        date_start = dtm.datetime.now() - dtm.timedelta(days=num_days + 30)
        date_list = pd.date_range(date_start, periods=num_days, freq='D')

        np.random.seed(42)
        values = pd.DataFrame({'close': np.random.uniform(10., 100., num_days),
                               'date': date_list})

        test_source = SingleFinancialSymbolSource(
            namespace='test_ns', name='test',
            values_fetcher=lambda: values,
            security_type=SecurityType.STOCK_ETF,
            period=Period.DAY,
            currency=Currency.RUB
        )
        fin_sym_registry = FinancialSymbolsRegistry(symbol_sources=[test_source])
        yapo_instance = yapo.Yapo(fin_syms_registry=fin_sym_registry)
        end_period = pd.Period.now(freq='M')
        start_period = end_period - 2
        asset = yapo_instance.portfolio_asset(name='test_ns/test',
                                              start_period=str(start_period), end_period=str(end_period),
                                              currency='USD')
        self.assertEqual(set(asset.period()), {end_period - 2})

    def test_compute_accumulated_rate_of_return(self):
        for asset in self.portfolio.assets:
            aror = asset.accumulated_rate_of_return()
            self.assertTrue(not np.all(np.isnan(aror)))
        self.assertTrue(not np.all(np.isnan(self.portfolio.accumulated_rate_of_return())))

    def test_close_and_its_change_should_preserve_ratio(self):
        for asset in self.portfolio.assets:
            rate_of_return_given = asset.rate_of_return()
            rate_of_return_expected = np.diff(asset.close()) / asset.close()[:-1]
            self.assertTrue(np.all(np.abs(rate_of_return_given[1:] - rate_of_return_expected) < self.epsilon))
