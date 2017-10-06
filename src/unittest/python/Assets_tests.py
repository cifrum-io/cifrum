import unittest

from yapo import FinancialSymbol as FSym
from yapo.Enums import Currency, SecurityType, Period


class AssetsTest(unittest.TestCase):

    def test_micex_stocks_should_have_correct_fields(self):
        info = FSym.information('micex/SBER')
        self.assertEqual(info.namespace, 'micex')
        self.assertEqual(info.ticker, 'SBER')
        self.assertEqual(info.isin, 'RU0009029540')
        self.assertEqual(info.short_name, 'Сбербанк')
        self.assertEqual(info.long_name, 'Сбербанк России ПАО ао')
        self.assertEqual(info.exchange, 'MICEX')
        self.assertEqual(info.currency, Currency.RUB)
        self.assertEqual(info.security_type, SecurityType.STOCK_ETF)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test_currency_usd__should_have_correct_fields(self):
        info = FSym.information('cbr/USD')
        self.assertEqual(info.namespace, 'cbr')
        self.assertEqual(info.ticker, 'USD')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Доллар США')
        self.assertIsNone(info.long_name)
        self.assertIsNone(info.exchange)
        self.assertEqual(info.currency, Currency.USD)
        self.assertEqual(info.security_type, SecurityType.CURRENCY)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test_inflation_ru__should_have_correct_fields(self):
        info = FSym.information('infl/RU')
        self.assertEqual(info.namespace, 'infl')
        self.assertEqual(info.ticker, 'RU')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Инфляция РФ')
        self.assertIsNone(info.long_name)
        self.assertIsNone(info.exchange)
        self.assertEqual(info.currency, Currency.RUB)
        self.assertEqual(info.security_type, SecurityType.INFLATION)
        self.assertEqual(info.period, Period.MONTH)
        self.assertEqual(info.adjusted_close, False)

    def test_all_data_should_be_available(self):
        self.assertIsNotNone(FSym.information('quandl/MSFT'))
        self.assertIsNotNone(FSym.information('micex/SBER'))
        self.assertIsNotNone(FSym.information('micex/SBERP'))
        self.assertIsNotNone(FSym.information('micex/MCFTR'))
        self.assertIsNotNone(FSym.information('nlu/419'))
        self.assertIsNotNone(FSym.information('cbr/USD'))
        self.assertIsNotNone(FSym.information('cbr/EUR'))
        self.assertIsNotNone(FSym.information('infl/RU'))
        self.assertIsNotNone(FSym.information('infl/US'))
        self.assertIsNotNone(FSym.information('infl/EU'))
        self.assertIsNotNone(FSym.information('cbr/TOP_rates'))

    def test_return_same_infos_count_as_provided(self):
        ids_arr = ['infl/RU', 'infl/EU', 'micex/MCFTR', 'micex/SBER']
        infos = FSym.information(', '.join(ids_arr))
        self.assertEqual(len(infos), len(ids_arr))

    def test_be_invariant_in_respect_to_space_separators(self):
        infos1 = FSym.information('infl/RU, infl/EU')
        infos2 = FSym.information('    infl/RU    ,      infl/EU      ')
        self.assertCountEqual(infos1, infos2)

    def test_be_invariant_in_respect_to_order(self):
        infos1 = FSym.information('infl/RU, infl/EU')
        infos2 = FSym.information('infl/EU, infl/RU')
        self.assertCountEqual(infos1, infos2)
