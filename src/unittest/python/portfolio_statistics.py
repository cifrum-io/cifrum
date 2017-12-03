import unittest
import yapo
import numpy as np


class PortfolioStatisticsTest(unittest.TestCase):

    def test_accumulated_rate_of_return(self):
        prtflio = yapo.portfolio(assets={'quandl/BND': .4, 'quandl/VTI': .4, 'quandl/VXUS': .2},
                                 start_period='2011-1', end_period='2017-2', currency='USD')
        arors = prtflio.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((-.06 < arors) & (arors < .55)))

    def test_portfolio__compound_annual_growth_rate(self):
        prtflio = yapo.portfolio(assets={'quandl/BND': .4, 'quandl/VTI': .4, 'quandl/VXUS': .2},
                                 start_period='2011-1', end_period='2017-2', currency='USD')
        cagr_default = prtflio.compound_annual_growth_rate()
        self.assertTrue(abs(cagr_default - 0.068) < 1e-3)

        cagr_long_time = prtflio.compound_annual_growth_rate(years_ago=20)
        self.assertTrue(abs(cagr_default - cagr_long_time) < 1e-3)

        cagr_one_year = prtflio.compound_annual_growth_rate(years_ago=1)
        self.assertTrue(abs(cagr_one_year - .15) < 1e-3)

        cagr_array = prtflio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        cagr_diff = np.abs(cagr_array - [cagr_default, cagr_long_time, cagr_one_year]) < 1e-3
        self.assertTrue(np.all(cagr_diff))
