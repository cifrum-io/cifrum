import unittest

import yapo


class AvailableNamesTest(unittest.TestCase):

    def test__return_namespaces_list_by_default(self):
        self.assertEqual(set(yapo.available_names()),
                         {'infl', 'cbr', 'micex', 'nlu', 'quandl'})

    def test__get_names_for_individual_namespace(self):
        self.assertEqual(set(yapo.available_names(namespace='infl')),
                         {'infl/RUB', 'infl/EUR', 'infl/USD'})
        self.assertEqual(set(yapo.available_names(namespace='cbr')),
                         {'cbr/TOP_rates', 'cbr/RUB', 'cbr/USD', 'cbr/EUR'})
        self.assertTrue(set(yapo.available_names(namespace='micex')).issuperset(
            {'micex/MCFTR', 'micex/MRKY', 'micex/URKZ', 'micex/VSMO', 'micex/ROSN'}
        ))
        self.assertTrue(set(yapo.available_names(namespace='nlu')).issuperset(
            {'nlu/1129', 'nlu/630', 'nlu/6', 'nlu/617'}
        ))
        self.assertTrue(set(yapo.available_names(namespace='quandl')).issuperset(
            {'quandl/A', 'quandl/AA', 'quandl/AAAP', 'quandl/AABA', 'quandl/AAC'}
        ))

    def test__return_several_namespaces(self):
        self.assertTrue(set(yapo.available_names(namespaces=['infl', 'quandl'])).issuperset(
            {'infl/RUB', 'infl/EUR', 'infl/USD',
             'quandl/A', 'quandl/AA', 'quandl/AAAP', 'quandl/AABA', 'quandl/AAC'}
        ))
