import numpy as np
import pandas as pd
from hamcrest import *

import yapo as l
from conftest import decimal_places
from yapo._settings import _MONTHS_PER_YEAR

__asset_name = 'index/OKID10'


def test__present_in_available_names():
    sym_ids = [x.fin_sym_id.format() for x in l.available_names(namespace='index')]
    assert_that(sym_ids, has_item(__asset_name))


def test__have_valid_max_period_range():
    okid10 = l.portfolio_asset(name=__asset_name)
    cbr_top10 = l.information(name='cbr/TOP_rates')

    assert okid10.close().start_period == cbr_top10.start_period + _MONTHS_PER_YEAR
    assert (cbr_top10.end_period - okid10.close().end_period).n < 2


def test__have_valid_selected_period_range():
    start_period = pd.Period('2013-1', freq='M')
    end_period = pd.Period('2015-3', freq='M')

    okid10 = l.portfolio_asset(name=__asset_name, start_period=str(start_period), end_period=str(end_period))
    assert okid10.close().start_period == start_period
    assert okid10.close().end_period == end_period


def test__have_correct_values():
    okid10 = l.portfolio_asset(name=__asset_name, end_period='2018-12')
    np.testing.assert_almost_equal(okid10.close()[:5].values,
                                   [100., 100.9854, 101.9356, 102.8515, 103.7328], decimal_places)
    np.testing.assert_almost_equal(okid10.close()[-5:].values,
                                   [212.0694, 213.2737, 214.4767, 215.6832, 216.8961], decimal_places)


def test__compute_correctly_in_other_currencies():
    okid10_usd = l.portfolio_asset(name=__asset_name, end_period='2018-12', currency='usd')
    okid10_rub = l.portfolio_asset(name=__asset_name, end_period='2018-12', currency='rub')

    okid10_currency_rate = okid10_usd.close() / okid10_rub.close()

    vs_rub = l.portfolio_asset(name='cbr/RUB',
                               start_period=okid10_currency_rate.start_period,
                               end_period=okid10_currency_rate.end_period,
                               currency='usd').close()

    np.testing.assert_almost_equal(okid10_currency_rate.values, vs_rub.values, decimal_places)
