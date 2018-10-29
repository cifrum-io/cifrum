import unittest
import yapo
import numpy as np


class PortfolioStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_names = {'nlu/922': .4, 'micex/FXRU': .4, 'micex/FXMM': .2}
        cls.portfolio = yapo.portfolio(assets=cls.asset_names,
                                       start_period='2015-3', end_period='2017-5', currency='USD')
        cls.places = 4

    def test_rate_of_return(self):
        rate_of_return_definition = \
            sum(asset.rate_of_return() * weight for asset, weight in self.portfolio.assets_weighted())
        np.testing.assert_almost_equal(self.portfolio.rate_of_return().values,
                                       rate_of_return_definition.values)

    def test_accumulated_rate_of_return(self):
        arors = self.portfolio.rate_of_return(kind='accumulated').values
        self.assertAlmostEqual(arors.min(), -.0294, places=self.places)
        self.assertAlmostEqual(arors.max(), .3024, places=self.places)

        arors_real = self.portfolio.rate_of_return(kind='accumulated', real=True).values
        self.assertAlmostEqual(arors_real.min(), -.0326, places=self.places)
        self.assertAlmostEqual(arors_real.max(), .2577, places=self.places)


    def test_handle_related_inflation(self):
        self.assertRaises(Exception, self.portfolio.inflation, kind='abracadabra')

        self.assertAlmostEqual(self.portfolio.inflation(kind='accumulated').value, .0365, places=self.places)
        self.assertAlmostEqual(self.portfolio.inflation(kind='a_mean').value, .0014, places=self.places)
        self.assertAlmostEqual(self.portfolio.inflation(kind='g_mean').value, .0167, places=self.places)
        self.assertEqual(self.portfolio.inflation(kind='values').size,
                         self.portfolio.rate_of_return().size)

    def test_compound_annual_growth_rate(self):
        cagr_default = self.portfolio.compound_annual_growth_rate()
        self.assertAlmostEqual(cagr_default.value, .1261, places=self.places)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20)
        self.assertAlmostEqual((cagr_default - cagr_long_time).value, 0., places=self.places)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1)
        self.assertAlmostEqual(cagr_one_year.value, .1709, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        self.assertAlmostEqual((cagr_default1 - cagr_default).value, 0., places=self.places)
        self.assertAlmostEqual((cagr_long_time1 - cagr_long_time).value, 0., places=self.places)
        self.assertAlmostEqual((cagr_one_year1 - cagr_one_year).value, 0., places=self.places)

    def test_compound_annual_growth_rate_real(self):
        cagr_default = self.portfolio.compound_annual_growth_rate(real=True)
        self.assertAlmostEqual(cagr_default.value, .1076, places=self.places)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20, real=True)
        self.assertAlmostEqual(cagr_default.value, cagr_long_time.value, places=self.places)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1, real=True)
        self.assertAlmostEqual(cagr_one_year.value, .1494, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
        self.assertAlmostEqual(cagr_default1.value, cagr_default.value, places=self.places)
        self.assertAlmostEqual(cagr_long_time1.value, cagr_long_time.value, places=self.places)
        self.assertAlmostEqual(cagr_one_year1.value, cagr_one_year.value, places=self.places)

    def test_risk(self):
        short_portfolio = yapo.portfolio(assets=self.asset_names,
                                         start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_portfolio, period='year')
        self.assertAlmostEqual(self.portfolio.risk(period='year').value, .1592, places=self.places)
        self.assertAlmostEqual(self.portfolio.risk(period='month').value, .0407, places=self.places)
        self.assertAlmostEqual(self.portfolio.risk().value, .1592, places=self.places)
