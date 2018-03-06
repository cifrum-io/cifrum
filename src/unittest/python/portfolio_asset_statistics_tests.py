import unittest
import yapo
import numpy as np


class PortfolioAssetStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset = yapo.portfolio_asset(name='quandl/BND',
                                         start_period='2011-1', end_period='2017-2', currency='USD')

    def test_accumulated_rate_of_return(self):
        arors = self.asset.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((.0014 < arors) & (arors < .24)))

    def test_compound_annual_growth_rate(self):
        cagr_default = self.asset.compound_annual_growth_rate()
        self.assertTrue(abs(cagr_default - 0.03) < 1e-3)

        cagr_long_time = self.asset.compound_annual_growth_rate(years_ago=20)
        self.assertTrue(abs(cagr_default - cagr_long_time) < 1e-3)

        cagr_one_year = self.asset.compound_annual_growth_rate(years_ago=1)
        self.assertTrue(abs(cagr_one_year - .012) < 1e-3)

        cagr_array = self.asset.compound_annual_growth_rate(years_ago=[None, 20, 1])
        cagr_diff = np.abs(cagr_array - [cagr_default, cagr_long_time, cagr_one_year]) < 1e-3
        self.assertTrue(np.all(cagr_diff))

    def test_risk(self):
        self.assertTrue(abs(self.asset.risk() - .0311) < 1e-3)
