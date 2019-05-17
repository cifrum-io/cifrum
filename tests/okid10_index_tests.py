import unittest

import pandas as pd
import numpy as np

import yapo
from yapo._settings import _MONTHS_PER_YEAR


class Okid10IndexTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asset_name = 'index/OKID10'
        cls.places = 4

    def test__present_in_available_names(self):
        sym_ids = {x.fin_sym_id.format() for x in yapo.available_names(namespace='index')}
        self.assertTrue(self.asset_name in sym_ids)

    def test__have_valid_max_period_range(self):
        okid10 = yapo.portfolio_asset(name=self.asset_name)
        cbr_top10 = yapo.information(name='cbr/TOP_rates')

        self.assertEqual(okid10.close().start_period,
                         cbr_top10.start_period + _MONTHS_PER_YEAR)
        self.assertTrue(cbr_top10.end_period - okid10.close().end_period < 2)

    def test__have_valid_selected_period_range(self):
        start_period = pd.Period('2013-1', freq='M')
        end_period = pd.Period('2015-3', freq='M')

        okid10 = yapo.portfolio_asset(name=self.asset_name, start_period=str(start_period), end_period=str(end_period))
        self.assertEqual(okid10.close().start_period, start_period)
        self.assertEqual(okid10.close().end_period, end_period)

    def test__have_correct_values(self):
        okid10 = yapo.portfolio_asset(name=self.asset_name, end_period='2018-12')
        np.testing.assert_almost_equal(okid10.close()[:5].values,
                                       [100., 100.9854, 101.9356, 102.8515, 103.7328], decimal=self.places)
        np.testing.assert_almost_equal(okid10.close()[-5:].values,
                                       [212.0694, 213.2737, 214.4767, 215.6832, 216.8961], decimal=self.places)

    def test__compute_correctly_in_other_currencies(self):
        okid10_usd = yapo.portfolio_asset(name=self.asset_name, end_period='2018-12', currency='usd')
        okid10_rub = yapo.portfolio_asset(name=self.asset_name, end_period='2018-12', currency='rub')

        okid10_currency_rate = okid10_usd.close() / okid10_rub.close()

        vs_rub = yapo.portfolio_asset(name='cbr/RUB',
                                      start_period=okid10_currency_rate.start_period,
                                      end_period=okid10_currency_rate.end_period,
                                      currency='usd').close()

        np.testing.assert_almost_equal(okid10_currency_rate.values, vs_rub.values, decimal=self.places)
