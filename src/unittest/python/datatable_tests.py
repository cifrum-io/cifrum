import itertools
import unittest

from pandas.core.dtypes.dtypes import PeriodDtype

import yapo
from model.Enums import Currency


class DataTableTest(unittest.TestCase):
    sample_symbol_names = ['quandl/MSFT', 'micex/SBER', 'micex/SBERP', 'micex/MCFTR', 'nlu/419',
                           'cbr/USD', 'cbr/EUR', 'infl/RU', 'infl/US', 'infl/EU']

    def test_index_should_be_numerical(self):
        for symbol_name, currency in itertools.product(DataTableTest.sample_symbol_names, Currency):
            sym = yapo.information(symbol_name)
            dt = sym.get_table(start_period='2010-1', end_period='2015-6', currency=currency.name)
            self.assertIsInstance(dt.values.index.dtype, PeriodDtype,
                                  msg='Incorrect index type for ' + symbol_name)
