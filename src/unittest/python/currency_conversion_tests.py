import unittest

import yapo
from model.Enums import Currency
import numpy as np
import itertools


class CurrencyConversionTest(unittest.TestCase):

    def test_currency_should_not_be_converted_to_itself(self):
        info = yapo.information(ids='cbr/USD')
        dt = info.get_table(start_period='2015-1', end_period='2017-1', currency='USD')
        vs = dt.values['close'].as_matrix()
        self.assertTrue(np.all(np.abs(vs - 1.) < 1e-3))

    def test_currency_should_be_converted_other_currency(self):
        info = yapo.information(ids='cbr/EUR')
        dt = info.get_table(start_period='2015-1', end_period='2017-1', currency='USD')
        vs = dt.values['close'].as_matrix()
        self.assertTrue(np.all(vs > 1.05))

    def test_support_all_types_of_currency_conversions(self):
        for currency_from, currency_to in itertools.product(Currency, Currency):
            info = yapo.information(ids='cbr/' + currency_from.name)
            dt = info.get_table(start_period='2015-1', end_period='2016-12', currency=currency_to.name)
            vs = dt.values['close'].as_matrix()
            self.assertEqual(vs.size, 2 * 12)
            self.assertTrue(np.all(vs > 0.))

    def test_currency_conversion_should_be_inversive(self):
        for currency1, currency2 in itertools.product(Currency, Currency):
            info1 = yapo.information(ids='cbr/' + currency1.name)
            dt1 = info1.get_table(start_period='2015-1', end_period='2016-12', currency=currency2.name)
            vs1 = dt1.values['close'].as_matrix()

            info2 = yapo.information(ids='cbr/' + currency2.name)
            dt2 = info2.get_table(start_period='2015-1', end_period='2016-12', currency=currency1.name)
            vs2 = dt2.values['close'].as_matrix()

            self.assertTrue(np.all(np.abs(vs1 * vs2 - 1.) < 1e-3))

    def test_asset_should_be_converted_correctly(self):
        info = yapo.information(ids='nlu/630')
        dt_eur = info.get_table(start_period='2011-1', end_period='2017-2', currency='EUR')
        vs_eur = dt_eur.values['close'].as_matrix()

        dt_usd = info.get_table(start_period='2011-1', end_period='2017-2', currency='USD')
        vs_usd = dt_usd.values['close'].as_matrix()

        info_curr = yapo.information(ids='cbr/USD')
        dt_curr = info_curr.get_table(start_period='2011-1', end_period='2017-2', currency='EUR')
        vs_curr = dt_curr.values['close'].as_matrix()

        self.assertTrue(np.all(np.abs(vs_eur / vs_usd - vs_curr) < 1e-3))
