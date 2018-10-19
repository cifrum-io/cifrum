import unittest

from model.FinancialSymbol import ValuesFetcher
from serum import inject
import pandas as pd
import numpy as np


@inject
class ValuesFetcherTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.epsilon = 1e-3

    class __ValuesFun:
        def __init__(self):
            self.requests = []
            self.period_min = pd.Period('2013-1', freq='M')
            self.period_max = pd.Period('2016-6', freq='M')

        def __call__(self, start_period: pd.Period, end_period: pd.Period):
            self.requests.append((start_period, end_period))
            start_period = max(self.period_min, start_period)
            end_period = min(self.period_max, end_period)

            values = [
                start_period - self.period_min + v + 1
                for v in range(end_period - start_period + 1)
            ]
            df = pd.DataFrame.from_dict({
                'close': values,
                'date': pd.date_range(str(start_period), str(end_period + 1), freq='M'),
            })
            return df

    def __create_values_fetcher(self):
        values_fun = self.__ValuesFun()
        values_fetcher = ValuesFetcher(
            values_fun=values_fun,
            period_min=values_fun.period_min,
            period_max=values_fun.period_max,
        )
        return values_fetcher, values_fun

    def test__initial_state(self):
        values_fetcher, _ = self.__create_values_fetcher()

        self.assertEqual(values_fetcher._period_range, (None, None))

    def test__first_fetch(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps = pd.Period('2014-1', freq='M')
        pe = pd.Period('2015-1', freq='M')
        values = values_fetcher._fetch(start_period=ps, end_period=pe)

        self.assertEqual(len(values), pe - ps + 1)
        self.assertEqual(len(values_fun.requests), 1)
        self.assertEqual(min(values.date.dt.to_period(freq='M')), ps)
        self.assertEqual(max(values.date.dt.to_period(freq='M')), pe)
        np.testing.assert_equal(values.close.values,
                                values_fun(start_period=ps, end_period=pe).close.values)

    def test__repeated_fetch_within_known_range(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2014-3', freq='M')
        pe2 = pd.Period('2014-9', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 1)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps1, pe1))

    def test__fetch_before_begin_period_with_intersection(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2013-9', freq='M')
        pe2 = pd.Period('2014-3', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 2)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps2, pe1))

    def test__fetch_before_begin_period_with_separate_regions(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2013-1', freq='M')
        pe2 = pd.Period('2013-6', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 2)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps2, pe1))

    def test__fetch_after_end_period_with_intersection(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2014-6', freq='M')
        pe2 = pd.Period('2015-6', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 2)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps1, pe2))

    def test__fetch_before_end_period_with_separate_regions(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2015-6', freq='M')
        pe2 = pd.Period('2016-1', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 2)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps1, pe2))

    def test__fetch_broader_than_stored_region(self):
        values_fetcher, values_fun = self.__create_values_fetcher()

        ps1 = pd.Period('2014-1', freq='M')
        pe1 = pd.Period('2015-1', freq='M')
        _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

        ps2 = pd.Period('2013-6', freq='M')
        pe2 = pd.Period('2016-6', freq='M')
        values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

        self.assertEqual(len(values_fun.requests), 2)
        self.assertEqual(len(values2), pe2 - ps2 + 1)
        np.testing.assert_equal(values2.close.values,
                                values_fun(start_period=ps2, end_period=pe2).close.values)
        self.assertEqual(values_fetcher._period_range, (ps2, pe2))
