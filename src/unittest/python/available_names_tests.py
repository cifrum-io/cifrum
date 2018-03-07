import unittest

import yapo


class AvailableNamesTest(unittest.TestCase):

    def test__return_namespaces_list_by_default(self):
        self.assertEqual(set(yapo.available_names()),
                         {'infl', 'cbr', 'micex', 'nlu', 'quandl'})

    def test__get_names_for_individual_namespace(self):
        def __fin_sim_ids(namespace):
            return set(available_name.fin_sym_id.format()
                       for available_name in yapo.available_names(namespace=namespace))

        self.assertEqual(__fin_sim_ids(namespace='infl'), {'infl/RUB', 'infl/EUR', 'infl/USD'})
        self.assertEqual(__fin_sim_ids(namespace='cbr'), {'cbr/TOP_rates', 'cbr/RUB', 'cbr/USD', 'cbr/EUR'})
        self.assertTrue(__fin_sim_ids(namespace='micex').issuperset(
            {'micex/MCFTR', 'micex/MRKY', 'micex/URKZ', 'micex/VSMO', 'micex/ROSN'}
        ))
        self.assertTrue(__fin_sim_ids(namespace='nlu').issuperset(
            {'nlu/1129', 'nlu/630', 'nlu/6', 'nlu/617'}
        ))
        self.assertTrue(__fin_sim_ids(namespace='quandl').issuperset(
            {'quandl/A', 'quandl/AA', 'quandl/AAAP', 'quandl/AABA', 'quandl/AAC'}
        ))

    def test__return_several_namespaces(self):
        available_name_ids = set(available_name.fin_sym_id.format()
                                 for available_name in yapo.available_names(namespaces=['infl', 'quandl']))

        self.assertTrue(available_name_ids.issuperset(
            {'infl/RUB', 'infl/EUR', 'infl/USD',
             'quandl/A', 'quandl/AA', 'quandl/AAAP', 'quandl/AABA', 'quandl/AAC'}
        ))
