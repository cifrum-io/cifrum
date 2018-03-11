import unittest
import yapo
import numpy as np


class PortfolioStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_names = {'quandl/BND': .4, 'quandl/VTI': .4, 'quandl/VXUS': .2}
        cls.portfolio = yapo.portfolio(assets=cls.asset_names,
                                       start_period='2011-1', end_period='2017-2', currency='USD')
        cls.epsilon = 1e-3

    def test_rate_of_return(self):
        rate_of_return_naive = \
            sum(asset.rate_of_return() * weight for asset, weight in self.portfolio.assets_weighted())
        self.assertTrue(np.all(np.abs(self.portfolio.rate_of_return() - rate_of_return_naive) < self.epsilon))

    def test_accumulated_rate_of_return(self):
        arors = self.portfolio.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((-.065 < arors) & (arors < .51)))

    def test_compound_annual_growth_rate(self):
        cagr_default = self.portfolio.compound_annual_growth_rate()
        self.assertTrue(abs(cagr_default - .182) < self.epsilon)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20)
        self.assertTrue(abs(cagr_default - cagr_long_time) < self.epsilon)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1)
        self.assertTrue(abs(cagr_one_year - .475) < self.epsilon)

        cagr_array = self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        cagr_diff = np.abs(cagr_array - [cagr_default, cagr_long_time, cagr_one_year]) < self.epsilon
        self.assertTrue(np.all(cagr_diff))

    def test_risk(self):
        short_portfolio = \
            yapo.portfolio(assets=self.asset_names,
                           start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_portfolio, period='year')
        self.assertTrue(abs(self.portfolio.risk() - .078) < self.epsilon)
        self.assertTrue(abs(self.portfolio.risk(period='year') - .078) < self.epsilon)
        self.assertTrue(abs(self.portfolio.risk(period='month') - .021) < self.epsilon)
