import numpy as np
import pandas as pd
import pytest
from hamcrest import assert_that, has_length, none

from cifrum.common.financial_symbol import ValuesFetcher


@pytest.fixture
def values_fetcher():
    class __ValuesFunc:
        def __init__(self):
            self.requests = []
            self.period_min = pd.Period('2013-1', freq='M')
            self.period_max = pd.Period('2016-6', freq='M')

        def __call__(self, start_period: pd.Period, end_period: pd.Period):
            self.requests.append((start_period, end_period))
            start_period = max(self.period_min, start_period)
            end_period = min(self.period_max, end_period)

            values = [
                (start_period - self.period_min).n + v + 1
                for v in range((end_period - start_period).n + 1)
            ]
            df = pd.DataFrame.from_dict({
                'close': values,
                'date': pd.date_range(str(start_period), str(end_period + 1), freq='M'),
            })
            return df

    values_func = __ValuesFunc()
    values_fetcher = ValuesFetcher(
        values_func=values_func,
        period_min=values_func.period_min,
        period_max=values_func.period_max,
    )
    return values_fetcher


def test__initial_state(values_fetcher):
    assert_that(values_fetcher._period_range.start, none())
    assert_that(values_fetcher._period_range.end, none())


def test__first_fetch(values_fetcher):
    ps = pd.Period('2014-1', freq='M')
    pe = pd.Period('2015-1', freq='M')
    values = values_fetcher._fetch(start_period=ps, end_period=pe)

    assert_that(values, has_length((pe - ps).n + 1))
    assert_that(values_fetcher._values_func.requests, has_length(1))
    assert min(values.date.dt.to_period(freq='M')) == ps
    assert max(values.date.dt.to_period(freq='M')) == pe
    np.testing.assert_equal(values.close.values,
                            values_fetcher._values_func(start_period=ps, end_period=pe).close.values)


def test__repeated_fetch_within_known_range(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2014-3', freq='M')
    pe2 = pd.Period('2014-9', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(1))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps1
    assert values_fetcher._period_range.end == pe1


def test__fetch_before_begin_period_with_intersection(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2013-9', freq='M')
    pe2 = pd.Period('2014-3', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(2))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps2
    assert values_fetcher._period_range.end == pe1


def test__fetch_before_begin_period_with_separate_regions(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2013-1', freq='M')
    pe2 = pd.Period('2013-6', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(2))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps2
    assert values_fetcher._period_range.end == pe1


def test__fetch_after_end_period_with_intersection(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2014-6', freq='M')
    pe2 = pd.Period('2015-6', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(2))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps1
    assert values_fetcher._period_range.end == pe2


def test__fetch_before_end_period_with_separate_regions(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2015-6', freq='M')
    pe2 = pd.Period('2016-1', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(2))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps1
    assert values_fetcher._period_range.end == pe2


def test__fetch_broader_than_stored_region(values_fetcher):
    ps1 = pd.Period('2014-1', freq='M')
    pe1 = pd.Period('2015-1', freq='M')
    _ = values_fetcher._fetch(start_period=ps1, end_period=pe1)

    ps2 = pd.Period('2013-6', freq='M')
    pe2 = pd.Period('2016-6', freq='M')
    values2 = values_fetcher._fetch(start_period=ps2, end_period=pe2)

    assert_that(values_fetcher._values_func.requests, has_length(2))
    assert_that(values2, has_length((pe2 - ps2).n + 1))
    np.testing.assert_equal(values2.close.values,
                            values_fetcher._values_func(start_period=ps2, end_period=pe2).close.values)
    assert values_fetcher._period_range.start == ps2
    assert values_fetcher._period_range.end == pe2
