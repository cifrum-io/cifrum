import unittest
import yapo
from yapo.common.enums import SecurityType


class SearchTest(unittest.TestCase):

    def test__search_exact_ticker(self):
        rs = yapo.search(query='spy')
        self.assertEqual(rs[0].identifier_str, 'ny/SPY')

        rs = yapo.search(query='sber')
        self.assertEqual(rs[0].identifier_str, 'micex/SBER')

        rs = yapo.search(query='0890-94127385')
        self.assertEqual(rs[0].identifier_str, 'mut_ru/0890-94127385')

    def test__search_exchange(self):
        rs = yapo.search(query='nyse')
        for r in rs:
            self.assertTrue(r.exchange.startswith('NYSE'))

        rs = yapo.search(query='nasdaq')
        for r in rs:
            self.assertTrue(r.exchange.startswith('NASDAQ'))

        rs = yapo.search(query='micex')
        for r in rs:
            self.assertTrue(r.exchange.startswith('MICEX'))

    def test__search_custom_query(self):
        rs = yapo.search(query='сбербанк', top=30)
        self.assertEqual(set(r.security_type for r in rs),
                         {SecurityType.STOCK_ETF, SecurityType.MUT})

        rs = yapo.search(query='microsoft', top=30)
        self.assertEqual(rs[0].identifier_str, 'ny/MSFT')
