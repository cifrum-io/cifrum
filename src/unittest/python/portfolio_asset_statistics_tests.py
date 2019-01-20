import unittest
import yapo
import numpy as np
import pandas as pd
from yapo.common.time_series import TimeSeriesKind


class PortfolioAssetStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_name = 'mut_ru/0890-94127385'
        cls.portfolio_period_start = pd.Period('2011-1', freq='M')
        cls.portfolio_period_end = pd.Period('2017-2', freq='M')
        cls.asset = yapo.portfolio_asset(name=cls.asset_name,
                                         start_period=str(cls.portfolio_period_start),
                                         end_period=str(cls.portfolio_period_end),
                                         currency='USD')
        cls.places = 4

    def test__accumulated_rate_of_return(self):
        arors = self.asset.rate_of_return(kind='accumulated').values
        self.assertAlmostEqual(arors.max(), .0924, places=self.places)
        self.assertAlmostEqual(arors.min(), -.5464, places=self.places)

        arors_real = self.asset.rate_of_return(kind='accumulated', real=True).values
        self.assertAlmostEqual(arors_real.max(), .0765, places=self.places)
        self.assertAlmostEqual(arors_real.min(), -.5725, places=self.places)

    def test__ytd_rate_of_return(self):
        ror_ytd = self.asset.rate_of_return(kind='ytd')
        self.assertEqual(ror_ytd.start_period, pd.Period('2012-1', freq='M'))
        self.assertEqual(ror_ytd.end_period, pd.Period('2016-12', freq='M'))
        self.assertEqual(ror_ytd.kind, TimeSeriesKind.YTD)
        np.testing.assert_almost_equal(ror_ytd.values, [.2041, -.0344, -.4531, .0046, .5695], decimal=self.places)

        ror_ytd_real = self.asset.rate_of_return(kind='ytd', real=True)
        self.assertEqual(ror_ytd_real.start_period, pd.Period('2012-1', freq='M'))
        self.assertEqual(ror_ytd_real.end_period, pd.Period('2016-12', freq='M'))
        self.assertEqual(ror_ytd_real.kind, TimeSeriesKind.YTD)
        np.testing.assert_almost_equal(ror_ytd_real.values,
                                       [.1835, -.0486, -.4572, -.0026, .5376], decimal=self.places)

    def test__handle_related_inflation(self):
        self.assertRaises(Exception, self.asset.inflation, kind='abracadabra')

        self.assertAlmostEqual(self.asset.inflation(kind='accumulated').value, .1062, places=self.places)
        self.assertAlmostEqual(self.asset.inflation(kind='a_mean').value, 0.0014, places=self.places)
        self.assertAlmostEqual(self.asset.inflation(kind='g_mean').value, 0.0167, places=self.places)

        self.assertEqual(self.asset.inflation(kind='values').size,
                         self.asset.rate_of_return().size)

    def test__compound_annual_growth_rate(self):
        cagr_default = self.asset.compound_annual_growth_rate()
        self.assertAlmostEqual(cagr_default.value, -.0562, places=self.places)

        cagr_long_time = self.asset.compound_annual_growth_rate(years_ago=20)
        self.assertAlmostEqual(cagr_long_time.value, cagr_default.value, places=self.places)

        cagr_one_year = self.asset.compound_annual_growth_rate(years_ago=1)
        self.assertAlmostEqual(cagr_one_year.value, .4738, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.asset.compound_annual_growth_rate(years_ago=[None, 20, 1])
        self.assertAlmostEqual(cagr_default1.value, cagr_default.value, places=self.places)
        self.assertAlmostEqual(cagr_long_time1.value, cagr_long_time.value, places=self.places)
        self.assertAlmostEqual(cagr_one_year1.value, cagr_one_year.value, places=self.places)

    def test__compound_annual_growth_rate_real(self):
        cagr_default = self.asset.compound_annual_growth_rate(real=True)
        self.assertAlmostEqual(cagr_default.value, -.0717, places=self.places)

        cagr_long_time = self.asset.compound_annual_growth_rate(years_ago=20, real=True)
        self.assertAlmostEqual(cagr_default.value, cagr_long_time.value, places=self.places)

        cagr_one_year = self.asset.compound_annual_growth_rate(years_ago=1, real=True)
        self.assertAlmostEqual(cagr_one_year.value, .4345, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.asset.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
        self.assertAlmostEqual(cagr_default1.value, cagr_default.value, places=self.places)
        self.assertAlmostEqual(cagr_long_time1.value, cagr_long_time.value, places=self.places)
        self.assertAlmostEqual(cagr_one_year1.value, cagr_one_year.value, places=self.places)

    def test__risk(self):
        short_asset = yapo.portfolio_asset(name=self.asset_name,
                                           start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_asset.risk, period='year')
        self.assertEqual(self.asset.risk().kind, TimeSeriesKind.REDUCED_VALUE)
        self.assertEqual(self.asset.risk(period='year').kind, TimeSeriesKind.REDUCED_VALUE)
        self.assertEqual(self.asset.risk(period='month').kind, TimeSeriesKind.REDUCED_VALUE)

        self.assertAlmostEqual(self.asset.risk().value, .2860, places=self.places)
        self.assertAlmostEqual(self.asset.risk(period='year').value, .2860, places=self.places)
        self.assertAlmostEqual(self.asset.risk(period='month').value, .0823, places=self.places)

    def test__inflation(self):
        self.assertRaises(Exception, self.asset.inflation, kind='abracadabra')

        self.assertAlmostEqual(self.asset.inflation(kind='accumulated').value, .1062, places=self.places)
        self.assertAlmostEqual(self.asset.inflation(kind='a_mean').value, .0014, places=self.places)
        self.assertAlmostEqual(self.asset.inflation(kind='g_mean').value, .0167, places=self.places)

        self.assertEqual(self.asset.inflation(kind='values').size,
                         self.asset.rate_of_return().size)
