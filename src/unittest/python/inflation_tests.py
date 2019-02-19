import unittest
import pandas as pd
import numpy as np
from serum import inject
import itertools

from yapo.common.enums import Currency

from yapo._portfolio.currency import PortfolioCurrencyFactory


@inject
class InflationTest(unittest.TestCase):
    portfolio_currency_factory: PortfolioCurrencyFactory

    @classmethod
    def setUpClass(cls):
        cls.end_period = pd.Period('2018-12', freq='M')
        cls.places = 4

    def test__exists_for_all_currencies(self):
        infl_kinds = ['values', 'accumulated', 'a_mean', 'g_mean']

        for cur, infl_kind in itertools.product(Currency, infl_kinds):
            pc = self.portfolio_currency_factory.create(currency=cur)
            infl = pc.inflation(kind=infl_kind, end_period=self.end_period, years_ago=4)
            self.assertIsNotNone(infl)

    def test__should_not_handle_both_start_date_and_years_ago(self):
        pc = self.portfolio_currency_factory.create(currency=Currency.USD)
        with self.assertRaisesRegexp(ValueError, 'either `start_period` or `years_ago` should be provided'):
            pc.inflation(kind='values',
                         start_period=pd.Period('2011-1', freq='M'),
                         end_period=self.end_period,
                         years_ago=4)

    def test__inflation_values(self):
        pc = self.portfolio_currency_factory.create(currency=Currency.USD)

        self.assertAlmostEqual(pc.inflation(kind='accumulated', end_period=self.end_period, years_ago=5).value,
                               .0780, places=self.places)
        self.assertAlmostEqual(pc.inflation(kind='a_mean', end_period=self.end_period, years_ago=5).value,
                               .0013, places=self.places)
        self.assertAlmostEqual(pc.inflation(kind='g_mean', end_period=self.end_period, years_ago=5).value,
                               .0151, places=self.places)

        infl_yoy = pc.inflation(kind='yoy', end_period=self.end_period, years_ago=5)
        self.assertEqual(infl_yoy.start_period, pd.Period('2014-1'))
        self.assertEqual(infl_yoy.end_period, pd.Period('2018-1'))
        np.testing.assert_almost_equal(infl_yoy.values, [.0076, .0073, .0207, .0211, .0191], decimal=self.places)
