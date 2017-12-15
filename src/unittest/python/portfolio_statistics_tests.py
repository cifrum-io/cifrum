import unittest
import yapo
import numpy as np


class PortfolioStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.portfolio = yapo.portfolio(assets={'quandl/BND': .4, 'quandl/VTI': .4, 'quandl/VXUS': .2},
                                       start_period='2011-1', end_period='2017-2', currency='USD')

    def test_rate_of_return(self):
        rate_of_return_naive = \
            sum(asset.rate_of_return() * weight for asset, weight in self.portfolio.assets_weighted())
        self.assertTrue(np.all(np.abs(self.portfolio.rate_of_return() - rate_of_return_naive) < 1e-3))

    def test_accumulated_rate_of_return(self):
        arors = self.portfolio.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((-.065 < arors) & (arors < .51)))

    def test_compound_annual_growth_rate(self):
        cagr_default = self.portfolio.compound_annual_growth_rate()
        self.assertTrue(abs(cagr_default - .182) < 1e-3)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20)
        self.assertTrue(abs(cagr_default - cagr_long_time) < 1e-3)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1)
        self.assertTrue(abs(cagr_one_year - .475) < 1e-3)

        cagr_array = self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        cagr_diff = np.abs(cagr_array - [cagr_default, cagr_long_time, cagr_one_year]) < 1e-3
        self.assertTrue(np.all(cagr_diff))

    def test_risk(self):
        self.assertTrue(abs(self.portfolio.risk() - .084) < 1e-3)
