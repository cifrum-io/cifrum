import unittest

import yapo
import pandas as pd
from yapo.common.enums import Currency, SecurityType, Period
from yapo.common.financial_symbol import FinancialSymbol
from yapo._settings import change_column_name


class FinancialSymbolInformationTest(unittest.TestCase):

    def test__returns_sym_info(self):
        info = yapo.information(name='micex/FXRU')
        self.assertIsInstance(info, FinancialSymbol)

        info = yapo.information(names=[])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 0)

        info = yapo.information(names=['infl/RUB'])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 1)

        info = yapo.information(names=['micex/FXRU', 'infl/RUB'])
        self.assertIsInstance(info, list)
        self.assertEqual(len(info), 2)

    def test__micex_stocks_should_have_correct_fields(self):
        info = yapo.information(name='micex/SBER')
        self.assertEqual(info.namespace, 'micex')
        self.assertEqual(info.name, 'SBER')
        self.assertEqual(info.isin, 'RU0009029540')
        self.assertEqual(info.short_name, 'Сбербанк')
        self.assertEqual(info.long_name, 'Сбербанк России ПАО ао')
        self.assertEqual(info.exchange, 'MICEX')
        self.assertEqual(info.currency, Currency.RUB)
        self.assertEqual(info.security_type, SecurityType.STOCK_ETF)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test__quandl_stocks_should_have_correct_fields(self):
        info = yapo.information(name='ny/VNQ')
        self.assertEqual(info.namespace, 'ny')
        self.assertEqual(info.name, 'VNQ')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Vanguard Real Estate')
        self.assertIsNone(info.long_name)
        self.assertEqual(info.exchange, 'NYSE Arca')
        self.assertEqual(info.currency, Currency.USD)
        self.assertEqual(info.security_type, SecurityType.STOCK_ETF)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test__currency_usd__should_have_correct_fields(self):
        info = yapo.information(name='cbr/USD')
        self.assertEqual(info.namespace, 'cbr')
        self.assertEqual(info.name, 'USD')
        self.assertIsNone(info.isin)
        self.assertEqual(info.short_name, 'Доллар США')
        self.assertIsNone(info.long_name)
        self.assertIsNone(info.exchange)
        self.assertEqual(info.currency, Currency.USD)
        self.assertEqual(info.security_type, SecurityType.CURRENCY)
        self.assertEqual(info.period, Period.DAY)
        self.assertEqual(info.adjusted_close, True)

    def test__inflation_ru__should_have_correct_fields(self):
        info = yapo.information(name='infl/RUB')
        self.assertEqual(info.namespace, 'infl')
        self.assertEqual(info.name, 'RUB')
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

    def test__top_rates__should_have_correct_fields(self):
        info = yapo.information(name='cbr/TOP_rates')
        self.assertEqual(info.namespace, 'cbr')
        self.assertEqual(info.name, 'TOP_rates')
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

    def test__all_data_should_be_available(self):
        self.assertIsNotNone(yapo.information(name='ny/MSFT'))
        self.assertIsNotNone(yapo.information(name='micex/FXRU'))
        self.assertIsNotNone(yapo.information(name='micex/FXMM'))
        self.assertIsNotNone(yapo.information(name='micex/MCFTR'))
        self.assertIsNotNone(yapo.information(name='mut_ru/0890-94127385'))
        self.assertIsNotNone(yapo.information(name='cbr/USD'))
        self.assertIsNotNone(yapo.information(name='cbr/EUR'))
        self.assertIsNotNone(yapo.information(name='infl/RUB'))
        self.assertIsNotNone(yapo.information(name='infl/USD'))
        self.assertIsNotNone(yapo.information(name='infl/EUR'))
        self.assertIsNotNone(yapo.information(name='cbr/TOP_rates'))

    def test__return_none_if_no_finsym_is_found(self):
        not_existing_id = 'micex/MCFTR_doesntexist'
        self.assertIsNone(yapo.information(name=not_existing_id))
        infos = yapo.information(names=['infl/RUB', not_existing_id])
        self.assertIsNotNone(infos[0])
        self.assertIsNone(infos[1])

    def test__return_same_infos_count_as_provided(self):
        ids_arr = ['infl/RUB', 'infl/EUR', 'micex/MCFTR', 'micex/FXRU']
        infos = yapo.information(names=ids_arr)
        self.assertEqual(len(infos), len(ids_arr))

    def test__be_invariant_in_respect_to_order(self):
        infos1 = yapo.information(names=['infl/RUB', 'infl/EUR'])
        infos2 = yapo.information(names=['infl/EUR', 'infl/RUB'])
        self.assertCountEqual(infos1, infos2)
