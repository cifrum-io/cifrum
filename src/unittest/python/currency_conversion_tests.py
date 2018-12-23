import unittest

import pandas as pd
import numpy as np
import itertools
from serum import inject

import yapo
from yapo._sources.registries import CurrencySymbolsRegistry
from yapo.model.Enums import Currency


class CurrencyConversionTest(unittest.TestCase):

    @inject
    def test__currency_should_not_be_converted_to_itself_inside_converter(self, csr: CurrencySymbolsRegistry):
        for cur in Currency:
            dt = csr.convert(currency_from=cur, currency_to=cur,
                             start_period=pd.Period('1991-1', freq='M'), end_period=pd.Period('2015-1', freq='M'))
            vs = dt['close'].values
            self.assertTrue(np.all(np.abs(vs - 1.) < 1e-3))

    def test__currency_should_not_be_converted_to_itself_inside_datatable(self):
        for cur in Currency:
            vs = yapo.portfolio_asset(name='cbr/' + cur.name,
                                      start_period='2015-1', end_period='2017-1',
                                      currency=cur.name).close()

            self.assertTrue(np.all(np.abs((vs - 1.).values) < 1e-3))

    def test__currency_should_be_converted_other_currency(self):
        vs = yapo.portfolio_asset(name='cbr/EUR',
                                  start_period='2015-1', end_period='2017-1',
                                  currency='USD').close()

        self.assertTrue(np.all(vs.values > 1.05))

    def test__support_all_types_of_currency_conversions(self):
        for currency_from, currency_to in itertools.product(Currency, Currency):
            vs = yapo.portfolio_asset(name='cbr/' + currency_from.name,
                                      start_period='2015-1', end_period='2016-12',
                                      currency=currency_to.name).close()

            self.assertEqual(vs.size, 2 * 12)
            self.assertTrue(np.all(vs.values > 0.))

    def test__currency_conversion_should_be_inversive(self):
        for currency1, currency2 in itertools.product(Currency, Currency):
            vs1 = yapo.portfolio_asset(name='cbr/' + currency1.name,
                                       start_period='2015-1', end_period='2016-12',
                                       currency=currency2.name).close()

            vs2 = yapo.portfolio_asset(name='cbr/' + currency2.name,
                                       start_period='2015-1', end_period='2016-12',
                                       currency=currency1.name).close()

            self.assertTrue(np.all(np.abs((vs1 * vs2 - 1.).values) < 1e-3))

    def test__asset_should_be_converted_correctly(self):
        vs_eur = yapo.portfolio_asset(name='mut_ru/0890-94127385',
                                      start_period='2011-1', end_period='2017-2',
                                      currency='EUR').close()

        vs_usd = yapo.portfolio_asset(name='mut_ru/0890-94127385',
                                      start_period='2011-1', end_period='2017-2',
                                      currency='USD').close()

        vs_curr = yapo.portfolio_asset(name='cbr/USD',
                                       start_period='2011-1', end_period='2017-2',
                                       currency='EUR').close()

        self.assertTrue(np.all(np.abs((vs_eur / vs_usd - vs_curr).values) < 1e-3))
