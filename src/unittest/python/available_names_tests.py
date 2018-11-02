import unittest

import yapo


class AvailableNamesTest(unittest.TestCase):

    def test__return_namespaces_list_by_default(self):
        self.assertEqual(set(yapo.available_names()),
                         {'infl', 'cbr', 'micex', 'nlu', 'quandl'})

    def test__return_empty_list_or_none_if_symbol_doesnt_exist(self):
        nonexisting_id = 'nlu/xxx'

        asset = yapo.portfolio_asset(name=nonexisting_id)
        self.assertIsNone(asset)

        assets = yapo.portfolio_asset(names=[nonexisting_id])
        self.assertEqual(len(assets), 0)

        assets = yapo.portfolio_asset(names=['micex/FXRU', nonexisting_id])
        self.assertEqual(len(assets), 1)

        portfolio = yapo.portfolio(assets={'micex/FXRU': 1., nonexisting_id: 1.}, currency='USD')
        self.assertEqual(len(portfolio.assets), 1)

        nonexisting_ns = 'yyy/xxx'

        asset = yapo.portfolio_asset(name=nonexisting_ns)
        self.assertIsNone(asset)

        assets = yapo.portfolio_asset(names=[nonexisting_ns])
        self.assertEqual(len(assets), 0)

        assets = yapo.portfolio_asset(names=['micex/FXRU', nonexisting_ns])
        self.assertEqual(len(assets), 1)

        portfolio = yapo.portfolio(assets={'micex/FXRU': 1., nonexisting_ns: 1.}, currency='USD')
        self.assertEqual(len(portfolio.assets), 1)

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
            {'quandl/T', 'quandl/MSFT', 'quandl/GOOG', 'quandl/AAPL'}
        ))

    def test__return_several_namespaces(self):
        available_name_ids = set(available_name.fin_sym_id.format()
                                 for available_name in yapo.available_names(namespaces=['infl', 'quandl']))

        self.assertTrue(available_name_ids.issuperset(
            {'infl/RUB', 'infl/EUR', 'infl/USD',
             'quandl/T', 'quandl/MSFT', 'quandl/GOOG', 'quandl/AAPL'}
        ))
