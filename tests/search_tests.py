import unittest

from serum import Context

import yapo
from yapo._search import _Search
from yapo._sources.all_sources import AllSymbolSources
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

    def test__search_exact_finsym(self):
        qry = 'micex/SBER'

        with Context(AllSymbolSources):
            search_instance = _Search()

        r = search_instance._check_finsym_access(query=qry)
        self.assertIsNotNone(r)
        self.assertEqual(r.identifier_str, 'micex/SBER')

        rs = yapo.search(query=qry)
        self.assertEqual(len(rs), 1)
        self.assertEqual(rs[0].identifier_str, 'micex/SBER')
