import itertools
import unittest

from pandas.core.dtypes.dtypes import PeriodDtype
from pandas.tseries.offsets import MonthEnd

import yapo
from model.Enums import Currency


class DataTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_symbol_names = ['quandl/MSFT',
                                   'micex/SBER', 'micex/SBERP', 'micex/MCFTR',
                                   'nlu/419',
                                   'cbr/USD', 'cbr/EUR', 'cbr/RUB',
                                   'infl/RU', 'infl/US', 'infl/EU']
        cls.symbols_data = {}
        for symbol_name, currency in itertools.product(cls.sample_symbol_names, Currency):
            sym = yapo.information(symbol_name)
            dt = sym.get_table(start_period='2010-1', end_period='2015-6', currency=currency.name)
            cls.symbols_data.update({(symbol_name, currency.name): dt})

    def test_period_should_be_sorted(self):
        for symbol_name_currency in self.symbols_data.keys():
            dt = self.symbols_data[symbol_name_currency]
            values_period = dt.values['period'].values
            self.assertTrue(all(values_period[i] <= values_period[i + 1] for i in range(len(values_period) - 1)))

            values_period = dt.values.index
            self.assertTrue(all(values_period[i] <= values_period[i + 1] for i in range(len(values_period) - 1)))

    def test_values_should_have_correct_schema(self):
        for symbol_name_currency in self.symbols_data.keys():
            dt = self.symbols_data[symbol_name_currency]
            self.assertTrue(set(dt.values.columns) >= {'period', 'close'})

    def test_index_should_be_numerical(self):
        for symbol_name_currency in self.symbols_data.keys():
            dt = self.symbols_data[symbol_name_currency]
            self.assertTrue(set(dt.values.columns) >= {'period', 'close'})
            self.assertIsInstance(dt.values.index.dtype, PeriodDtype,
                                  msg='Incorrect index type for ' + symbol_name_currency[0])
            self.assertIsInstance(dt.values.index.dtype.freq, MonthEnd)
