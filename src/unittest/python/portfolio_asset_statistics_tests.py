import unittest
import yapo
import numpy as np


class PortfolioAssetStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_name = 'quandl/BND'
        cls.asset = yapo.portfolio_asset(name=cls.asset_name,
                                         start_period='2011-1', end_period='2017-2', currency='USD')
        cls.epsilon = 1e-3

    def test_accumulated_rate_of_return(self):
        arors = self.asset.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((.0014 < arors) & (arors < .24)))

    def test_compound_annual_growth_rate(self):
        cagr_default = self.asset.compound_annual_growth_rate()
        self.assertTrue(abs(cagr_default - 0.027) < self.epsilon)

        cagr_long_time = self.asset.compound_annual_growth_rate(years_ago=20)
        self.assertTrue(abs(cagr_default - cagr_long_time) < self.epsilon)

        cagr_one_year = self.asset.compound_annual_growth_rate(years_ago=1)
        self.assertTrue(abs(cagr_one_year - .011) < self.epsilon)

        cagr_array = self.asset.compound_annual_growth_rate(years_ago=[None, 20, 1])
        cagr_diff = np.abs(cagr_array - [cagr_default, cagr_long_time, cagr_one_year]) < self.epsilon
        self.assertTrue(np.all(cagr_diff))

    def test_risk(self):
        short_asset = \
            yapo.portfolio_asset(name=self.asset_name,
                                 start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_asset.risk, period='year')
        self.assertTrue(abs(self.asset.risk() - .0311) < self.epsilon)
        self.assertTrue(abs(self.asset.risk(period='year') - .0311) < self.epsilon)
        self.assertTrue(abs(self.asset.risk(period='month') - .0087) < self.epsilon)

    def test_inflation(self):
        self.assertRaises(Exception, self.asset.inflation, kind='abracadabra')

        self.assertEqual(self.asset.inflation(kind='values').size,
                         self.asset.close().size)
        self.assertTrue(abs(self.asset.inflation(kind='accumulated') - .1102) < self.epsilon)
        self.assertTrue(abs(self.asset.inflation(kind='mean') - .0173) < self.epsilon)
