import unittest
import yapo
import numpy as np


class PortfolioStatisticsTest(unittest.TestCase):

    def test_accumulated_rate_of_return(self):
        p = yapo.portfolio(assets=[('quandl/BND', 1.)],
                           start_period='2011-1', end_period='2017-2',
                           currency='USD')
        arors = p.accumulated_rate_of_return()[1:]
        self.assertTrue(np.all((.0014 < arors) & (arors < .24)))
