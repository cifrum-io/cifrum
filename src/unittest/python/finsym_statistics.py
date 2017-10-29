import unittest

import yapo


class FinancialSymbolStatisticsTest(unittest.TestCase):

    def test_accumulated_rate_of_return(self):
        sym = yapo.information(ids='quandl/BND')
        dt = sym.get_table(start_period='2011-1', end_period='2017-2', currency='USD')
        self.assertTrue(1.20 < dt.accumulated_rate_of_return() < 1.21)
