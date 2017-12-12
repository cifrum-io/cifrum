import unittest

import yapo
import pandas as pd
from model.Enums import Currency, SecurityType, Period
from model.FinancialSymbol import FinancialSymbol
from model.Settings import change_column_name


class FinancialSymbolInformationTest(unittest.TestCase):

    def test_returns_sym_info(self):
        info = yapo.information(name='micex/SBER')
        self.assertIsInstance(info, FinancialSymbol)

        info = yapo.information(names=[])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 0)

        info = yapo.information(names=['infl/RUB'])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 1)

        info = yapo.information(names=['micex/SBER', 'infl/RUB'])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 2)

    def test_micex_stocks_should_have_correct_fields(self):
        info = yapo.information(name='micex/SBER')
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

    def test_quandl_stocks_should_have_correct_fields(self):
        info = yapo.information(name='quandl/VNQ')
        self.assertEqual(info.namespace, 'quandl')
        self.assertEqual(info.ticker, 'VNQ')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Vanguard Real Estate')
        self.assertIsNone(info.long_name)
        self.assertEqual(info.exchange, 'NYSE Arca')
        self.assertEqual(info.currency, Currency.USD)
        self.assertEqual(info.security_type, SecurityType.STOCK_ETF)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test_currency_usd__should_have_correct_fields(self):
        info = yapo.information(name='cbr/USD')
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
        info = yapo.information(name='infl/RUB')
        self.assertEqual(info.namespace, 'infl')
        self.assertEqual(info.ticker, 'RUB')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Инфляция РФ')
        self.assertIsNone(info.long_name)
        self.assertIsNone(info.exchange)
        self.assertEqual(info.currency, Currency.RUB)
        self.assertEqual(info.security_type, SecurityType.INFLATION)
        self.assertEqual(info.period, Period.MONTH)
        self.assertEqual(info.adjusted_close, False)
        self.assertTrue(set(info.values(start_period=str(pd.Period.now(freq='M') - 2),
                                        end_period=str(pd.Period.now(freq='M'))).columns),
                        {'date', change_column_name})

    def test_top_rates__should_have_correct_fields(self):
        info = yapo.information(name='cbr/TOP_rates')
        self.assertEqual(info.namespace, 'cbr')
        self.assertEqual(info.ticker, 'TOP_rates')
        self.assertIsNone(info.isin)
        self.assertIsNone(info.short_name)
        self.assertTrue(info.long_name.startswith('Динамика максимальной процентной'))
        self.assertIsNone(info.exchange)
        self.assertEqual(info.currency, Currency.RUB)
        self.assertEqual(info.security_type, SecurityType.RATES)
        self.assertEqual(info.period, Period.DECADE)
        self.assertEqual(info.adjusted_close, False)
        self.assertTrue(set(info.values(start_period=str(pd.Period.now(freq='M') - 2),
                                        end_period=str(pd.Period.now(freq='M'))).columns),
                        {'date', change_column_name})

    def test_all_data_should_be_available(self):
        self.assertIsNotNone(yapo.information(name='quandl/MSFT'))
        self.assertIsNotNone(yapo.information(name='micex/SBER'))
        self.assertIsNotNone(yapo.information(name='micex/SBERP'))
        self.assertIsNotNone(yapo.information(name='micex/MCFTR'))
        self.assertIsNotNone(yapo.information(name='nlu/419'))
        self.assertIsNotNone(yapo.information(name='cbr/USD'))
        self.assertIsNotNone(yapo.information(name='cbr/EUR'))
        self.assertIsNotNone(yapo.information(name='infl/RUB'))
        self.assertIsNotNone(yapo.information(name='infl/USD'))
        self.assertIsNotNone(yapo.information(name='infl/EUR'))
        self.assertIsNotNone(yapo.information(name='cbr/TOP_rates'))

    def test_return_none_if_no_ticker_is_found(self):
        not_existing_id = 'micex/MCFTR_doesntexist'
        self.assertIsNone(yapo.information(name=not_existing_id))
        infos = yapo.information(names=['infl/RUB', not_existing_id])
        self.assertIsNotNone(infos[0])
        self.assertIsNone(infos[1])

    def test_return_same_infos_count_as_provided(self):
        ids_arr = ['infl/RUB', 'infl/EUR', 'micex/MCFTR', 'micex/SBER']
        infos = yapo.information(names=ids_arr)
        self.assertEqual(len(infos), len(ids_arr))

    def test_be_invariant_in_respect_to_order(self):
        infos1 = yapo.information(names=['infl/RUB', 'infl/EUR'])
        infos2 = yapo.information(names=['infl/EUR', 'infl/RUB'])
        self.assertCountEqual(infos1, infos2)
