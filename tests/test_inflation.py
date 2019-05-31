import itertools

import numpy as np
import pandas as pd
import pytest
from hamcrest import assert_that, not_none, calling, raises, close_to
from serum import inject

from conftest import decimal_places, delta
from yapo._portfolio.currency import PortfolioCurrencyFactory
from yapo.common.enums import Currency

__end_period = pd.Period('2018-12', freq='M')


@pytest.fixture
def pcf():
    @inject
    def pcf_instance(pcf: PortfolioCurrencyFactory):
        return pcf

    return pcf_instance()


@pytest.mark.parametrize('currency, inflation_kind',
                         itertools.product(Currency, ['values', 'cumulative', 'a_mean', 'g_mean']))
def test__exists_for_all_currencies(pcf: PortfolioCurrencyFactory, currency: Currency, inflation_kind: str):
    pc = pcf.create(currency=currency)
    infl = pc.inflation(kind=inflation_kind, end_period=__end_period, years_ago=4)
    assert_that(infl, not_none())


@pytest.mark.parametrize('currency, inflation_kind',
                         itertools.product(Currency, ['values', 'cumulative', 'a_mean', 'g_mean']))
def test__should_not_handle_both_start_date_and_years_ago(pcf: PortfolioCurrencyFactory,
                                                          currency: Currency, inflation_kind: str):
    pc = pcf.create(currency=currency)
    foo = calling(pc.inflation).with_args(kind=inflation_kind,
                                          start_period=pd.Period('2011-1', freq='M'),
                                          end_period=__end_period,
                                          years_ago=4)

    assert_that(foo, raises(ValueError, 'either `start_period` or `years_ago` should be provided'))


def test__inflation_values(pcf: PortfolioCurrencyFactory):
    pc = pcf.create(currency=Currency.USD)

    assert_that(pc.inflation(kind='cumulative', end_period=__end_period, years_ago=5).value,
                close_to(.0780, delta))
    assert_that(pc.inflation(kind='a_mean', end_period=__end_period, years_ago=5).value,
                close_to(.0013, delta))
    assert_that(pc.inflation(kind='g_mean', end_period=__end_period, years_ago=5).value,
                close_to(.0151, delta))

    infl_yoy = pc.inflation(kind='yoy', end_period=__end_period, years_ago=5)
    assert infl_yoy.start_period == pd.Period('2014-1')
    assert infl_yoy.end_period == pd.Period('2018-1')
    np.testing.assert_almost_equal(infl_yoy.values, [.0076, .0073, .0207, .0211, .0191], decimal_places)
