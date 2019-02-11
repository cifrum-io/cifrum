import unittest
import yapo
import numpy as np
import pandas as pd
import itertools as it

from yapo.common.time_series import TimeSeriesKind


class PortfolioStatisticsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.portfolio_period_start = pd.Period('2015-3', freq='M')
        cls.portfolio_period_end = pd.Period('2017-5', freq='M')
        cls.asset_names = {'mut_ru/0890-94127385': 4, 'micex/FXRU': 3, 'micex/FXMM': 2}
        cls.portfolio = yapo.portfolio(assets=cls.asset_names,
                                       start_period=str(cls.portfolio_period_start),
                                       end_period=str(cls.portfolio_period_end),
                                       currency='USD')
        cls.places = 4

    def test__compute_statistics_for_partially_incomplete_portfolio(self):
        asset_names = {'nlu/92': 1, 'micex/FXRU': 2, 'micex/FXMM': 3}
        portfolio = yapo.portfolio(assets=asset_names,
                                   start_period=str(self.portfolio_period_start),
                                   end_period=str(self.portfolio_period_end),
                                   currency='USD')

        for kind, real in it.product(['values', 'accumulated', 'ytd'],
                                     [True, False]):
            self.assertIsNotNone(portfolio.rate_of_return(kind=kind, real=real))

        for years_ago, real in it.product([None, 1, 5, 20, 50], [True, False]):
            self.assertIsNotNone(portfolio.compound_annual_growth_rate(years_ago=years_ago, real=real))

        for period in ['year', 'month']:
            self.assertIsNotNone(portfolio.risk(period=period))

    def test__normalize_weights(self):
        self.assertAlmostEqual(np.sum(self.portfolio.weights), 1., places=self.places)

        portfolio_assets = {
            k.symbol.identifier.format(): v for k, v in self.portfolio.assets_weighted()
        }
        self.assertAlmostEqual(portfolio_assets['mut_ru/0890-94127385'], .4444, places=self.places)
        self.assertAlmostEqual(portfolio_assets['micex/FXRU'], .3333, places=self.places)
        self.assertAlmostEqual(portfolio_assets['micex/FXMM'], .2222, places=self.places)

        asset_names = {'mut_ru/xxxx-xxxxxxxx': 1, 'micex/FXRU': 2, 'micex/FXMM': 3}
        portfolio_misprint = yapo.portfolio(assets=asset_names,
                                            start_period=str(self.portfolio_period_start),
                                            end_period=str(self.portfolio_period_end),
                                            currency='USD')
        self.assertAlmostEqual(np.sum(portfolio_misprint.weights), 1., places=self.places)
        portfolio_assets = {
            k.symbol.identifier.format(): v for k, v in portfolio_misprint.assets_weighted()
        }
        self.assertAlmostEqual(portfolio_assets['micex/FXRU'], .4, places=self.places)
        self.assertAlmostEqual(portfolio_assets['micex/FXMM'], .6, places=self.places)

    def test__rate_of_return(self):
        rate_of_return_definition = \
            sum(asset.rate_of_return() * weight for asset, weight in self.portfolio.assets_weighted())
        np.testing.assert_almost_equal(self.portfolio.rate_of_return().values,
                                       rate_of_return_definition.values)

    def test__accumulated_rate_of_return(self):
        arors = self.portfolio.rate_of_return(kind='accumulated').values
        self.assertAlmostEqual(arors.min(), -.0492, places=self.places)
        self.assertAlmostEqual(arors.max(), .3015, places=self.places)

        arors_real = self.portfolio.rate_of_return(kind='accumulated', real=True).values
        self.assertAlmostEqual(arors_real.min(), -.0524, places=self.places)
        self.assertAlmostEqual(arors_real.max(), .2568, places=self.places)

    def test__ytd_rate_of_return(self):
        ror_ytd = self.portfolio.rate_of_return(kind='ytd')
        self.assertEqual(ror_ytd.start_period, pd.Period('2016-1', freq='M'))
        self.assertEqual(ror_ytd.end_period, pd.Period('2016-1', freq='M'))
        np.testing.assert_almost_equal(ror_ytd.values, [.3480], decimal=self.places)

        ror_ytd_real = self.portfolio.rate_of_return(kind='ytd', real=True)
        self.assertEqual(ror_ytd_real.start_period, pd.Period('2016-1', freq='M'))
        self.assertEqual(ror_ytd_real.end_period, pd.Period('2016-1', freq='M'))
        np.testing.assert_almost_equal(ror_ytd_real.values, [.3206], decimal=self.places)

    def test__handle_related_inflation(self):
        self.assertRaises(Exception, self.portfolio.inflation, kind='abracadabra')

        self.assertAlmostEqual(self.portfolio.inflation(kind='accumulated').value, .0365, places=self.places)
        self.assertAlmostEqual(self.portfolio.inflation(kind='a_mean').value, .0014, places=self.places)
        self.assertAlmostEqual(self.portfolio.inflation(kind='g_mean').value, .0167, places=self.places)

        infl_yoy = self.portfolio.inflation(kind='yoy')
        self.assertEqual(infl_yoy.start_period, pd.Period('2016-1'))
        self.assertEqual(infl_yoy.end_period, pd.Period('2016-1'))
        np.testing.assert_almost_equal(infl_yoy.values, [.0207], decimal=self.places)

        self.assertEqual(self.portfolio.inflation(kind='values').size,
                         self.portfolio.rate_of_return().size)

    def test__compound_annual_growth_rate(self):
        cagr_default = self.portfolio.compound_annual_growth_rate()
        self.assertAlmostEqual(cagr_default.value, .1241, places=self.places)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20)
        self.assertAlmostEqual((cagr_default - cagr_long_time).value, 0., places=self.places)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1)
        self.assertAlmostEqual(cagr_one_year.value, .1814, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
        self.assertAlmostEqual((cagr_default1 - cagr_default).value, 0., places=self.places)
        self.assertAlmostEqual((cagr_long_time1 - cagr_long_time).value, 0., places=self.places)
        self.assertAlmostEqual((cagr_one_year1 - cagr_one_year).value, 0., places=self.places)

    def test__compound_annual_growth_rate_real(self):
        cagr_default = self.portfolio.compound_annual_growth_rate(real=True)
        self.assertAlmostEqual(cagr_default.value, .1056, places=self.places)

        cagr_long_time = self.portfolio.compound_annual_growth_rate(years_ago=20, real=True)
        self.assertAlmostEqual(cagr_default.value, cagr_long_time.value, places=self.places)

        cagr_one_year = self.portfolio.compound_annual_growth_rate(years_ago=1, real=True)
        self.assertAlmostEqual(cagr_one_year.value, .1597, places=self.places)

        cagr_default1, cagr_long_time1, cagr_one_year1 = \
            self.portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
        self.assertAlmostEqual(cagr_default1.value, cagr_default.value, places=self.places)
        self.assertAlmostEqual(cagr_long_time1.value, cagr_long_time.value, places=self.places)
        self.assertAlmostEqual(cagr_one_year1.value, cagr_one_year.value, places=self.places)

    def test__risk(self):
        short_portfolio = yapo.portfolio(assets=self.asset_names,
                                         start_period='2016-8', end_period='2016-12', currency='USD')

        self.assertRaises(Exception, short_portfolio, period='year')

        self.assertEqual(self.portfolio.risk().kind, TimeSeriesKind.REDUCED_VALUE)
        self.assertEqual(self.portfolio.risk(period='year').kind, TimeSeriesKind.REDUCED_VALUE)
        self.assertEqual(self.portfolio.risk(period='month').kind, TimeSeriesKind.REDUCED_VALUE)

        self.assertAlmostEqual(self.portfolio.risk(period='year').value, .1689, places=self.places)
        self.assertAlmostEqual(self.portfolio.risk(period='month').value, .0432, places=self.places)
        self.assertAlmostEqual(self.portfolio.risk().value, .1689, places=self.places)
