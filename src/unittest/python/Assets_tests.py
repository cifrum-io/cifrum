import unittest

import yapo.Assets


class AssetsTest(unittest.TestCase):

    def test_return_same_infos_count_as_provided(self):
        ids_arr = ['infl/RU', 'infl/EU', 'micex/MCFTR', 'micex/SBER']
        infos = yapo.Assets.info(', '.join(ids_arr))
        self.assertEqual(len(infos), len(ids_arr))

    def test_be_invariant_in_respect_to_space_separators(self):
        infos1 = yapo.Assets.info('infl/RU, infl/EU')
        infos2 = yapo.Assets.info('    infl/RU    ,      infl/EU      ')
        self.assertCountEqual(infos1, infos2)

    def test_be_invariant_in_respect_to_order(self):
        infos1 = yapo.Assets.info('infl/RU, infl/EU')
        infos2 = yapo.Assets.info('infl/EU, infl/RU')
        self.assertCountEqual(infos1, infos2)
