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
        self.assertTrue(np.all(np.abs((self.portfolio.rate_of_return() - rate_of_return_naive).values) < self.epsilon))

    def test_accumulated_rate_of_return(self):
        arors = self.portfolio.rate_of_return(kind='accumulated').values
        self.assertTrue(np.all((-.063 < arors) & (arors < .4796)))

        arors_real = self.portfolio.rate_of_return(kind='accumulated', real=True).values
        self.assertTrue(np.all((-.0951 < arors_real) & (arors_real < .3394)))

    def test_handle_related_inflation(self):
        self.assertRaises(Exception, self.portfolio.inflation, kind='abracadabra')

        self.assertAlmostEqual(self.portfolio.inflation(kind='accumulated').value, .1062, delta=self.epsilon)
        self.assertAlmostEqual(self.portfolio.inflation(kind='a_mean').value, .0014, delta=self.epsilon)
        self.assertAlmostEqual(self.portfolio.inflation(kind='g_mean').value, .0173, delta=self.epsilon)
        self.assertEqual(self.portfolio.inflation(kind='values').size,
                         self.portfolio.rate_of_return().size)

    def test_compound_annual_growth_rate(self):
        cagr_default = self.portfolio.compound_annual_growth_rate()
        self.assertAlmostEqual(cagr_default.value, .0665, delta=self.epsilon)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20)
        self.assertAlmostEqual((cagr_default - cagr_long_time).value, 0., delta=self.epsilon)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1)
        self.assertAlmostEqual(cagr_one_year.value, .1455, delta=self.epsilon)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        self.assertAlmostEqual((cagr_default1 - cagr_default).value, 0., delta=self.epsilon)
        self.assertAlmostEqual((cagr_long_time1 - cagr_long_time).value, 0., delta=self.epsilon)
        self.assertAlmostEqual((cagr_one_year1 - cagr_one_year).value, 0., delta=self.epsilon)

    def test_compound_annual_growth_rate_real(self):
        cagr_default = self.portfolio.compound_annual_growth_rate(real=True)
        self.assertAlmostEqual(cagr_default.value, .0490, delta=self.epsilon)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20, real=True)
        self.assertAlmostEqual((cagr_default - cagr_long_time).value, 0., delta=self.epsilon)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1, real=True)
        self.assertAlmostEqual(cagr_one_year.value, .1150, delta=self.epsilon)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
        self.assertAlmostEqual((cagr_default1 - cagr_default).value, 0., delta=self.epsilon)
        self.assertAlmostEqual((cagr_long_time1 - cagr_long_time).value, 0., delta=self.epsilon)
        self.assertAlmostEqual((cagr_one_year1 - cagr_one_year).value, 0., delta=self.epsilon)

    def test_risk(self):
        short_portfolio = yapo.portfolio(assets=self.asset_names,
                                         start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_portfolio, period='year')
        self.assertAlmostEqual(self.portfolio.risk(period='year').value, .078, delta=self.epsilon)
        self.assertAlmostEqual(self.portfolio.risk(period='month').value, .021, delta=self.epsilon)
        self.assertAlmostEqual(self.portfolio.risk().value, .078, delta=self.epsilon)
