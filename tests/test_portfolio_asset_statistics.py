import numpy as np
import pandas as pd
from hamcrest import assert_that, close_to, calling, raises

import yapo as y
from conftest import decimal_places, delta
from yapo._settings import _MONTHS_PER_YEAR
from yapo.common.time_series import TimeSeriesKind

__asset_name = 'mut_ru/0890-94127385'
__portfolio_period_start = pd.Period('2011-1', freq='M')
__portfolio_period_end = pd.Period('2017-2', freq='M')
__asset = y.portfolio_asset(name=__asset_name,
                            start_period=str(__portfolio_period_start),
                            end_period=str(__portfolio_period_end),
                            currency='USD')


def test__cumulative_rate_of_return():
    arors = __asset.rate_of_return(kind='cumulative').values
    assert_that(arors.max(), close_to(.0924, delta))
    assert_that(arors.min(), close_to(-.5464, delta))

    arors_real = __asset.rate_of_return(kind='cumulative', real=True).values
    assert_that(arors_real.max(), close_to(.0765, delta))
    assert_that(arors_real.min(), close_to(-.5725, delta))


def test__ytd_rate_of_return():
    ror_ytd = __asset.rate_of_return(kind='ytd')
    assert ror_ytd.start_period == pd.Period('2012-1', freq='M')
    assert ror_ytd.end_period == pd.Period('2016-1', freq='M')
    assert ror_ytd.kind == TimeSeriesKind.YTD
    np.testing.assert_almost_equal(ror_ytd.values, [.2041, -.0344, -.4531, .0046, .5695], decimal=decimal_places)

    ror_ytd_real = __asset.rate_of_return(kind='ytd', real=True)
    assert ror_ytd_real.start_period == pd.Period('2012-1', freq='M')
    assert ror_ytd_real.end_period == pd.Period('2016-1', freq='M')
    assert ror_ytd_real.kind == TimeSeriesKind.YTD
    np.testing.assert_almost_equal(ror_ytd_real.values,
                                   [.1835, -.0486, -.4572, -.0026, .5376], decimal=decimal_places)


def test__get_cagr():
    cagr_default = __asset.get_cagr()
    assert_that(cagr_default.value, close_to(-.0562, delta))

    cagr_long_time = __asset.get_cagr(years_ago=20)
    assert_that(cagr_long_time.value, close_to(cagr_default.value, delta))

    cagr_one_year = __asset.get_cagr(years_ago=1)
    assert_that(cagr_one_year.value, close_to(.4738, delta))

    cagr_default1, cagr_long_time1, cagr_one_year1 = \
        __asset.get_cagr(years_ago=[None, 20, 1])
    assert_that(cagr_default1.value, close_to(cagr_default.value, delta))
    assert_that(cagr_long_time1.value, close_to(cagr_long_time.value, delta))
    assert_that(cagr_one_year1.value, close_to(cagr_one_year.value, delta))


def test__cagr_should_be_full_when_it_has_period_equal_to_ror():
    start_period = pd.Period('2011-01', freq='M')
    years_amount = 5
    end_period = start_period + years_amount * 12
    asset = y.portfolio_asset(name=__asset_name,
                              start_period=str(start_period),
                              end_period=str(end_period), currency='usd')
    cagr1 = asset.get_cagr()
    assert_that(cagr1.value, close_to(-.1426, delta))

    cagr2 = asset.get_cagr(years_ago=years_amount)
    assert_that(cagr2.value, close_to(cagr1.value, delta))


def test__get_cagr_real():
    cagr_default = __asset.get_cagr(real=True)
    assert_that(cagr_default.value, close_to(-.0717, delta))

    cagr_long_time = __asset.get_cagr(years_ago=20, real=True)
    assert_that(cagr_default.value, close_to(cagr_long_time.value, delta))

    cagr_one_year = __asset.get_cagr(years_ago=1, real=True)
    assert_that(cagr_one_year.value, close_to(.4345, delta))

    cagr_default1, cagr_long_time1, cagr_one_year1 = \
        __asset.get_cagr(years_ago=[None, 20, 1], real=True)
    assert_that(cagr_default1.value, close_to(cagr_default.value, delta))
    assert_that(cagr_long_time1.value, close_to(cagr_long_time.value, delta))
    assert_that(cagr_one_year1.value, close_to(cagr_one_year.value, delta))


def test__get_cagr_invariants():
    start_period = pd.Period('2009-3', freq='M')
    end_period = pd.Period('2019-3', freq='M')
    asset = y.portfolio_asset(name=__asset_name,
                              start_period=str(start_period), end_period=str(end_period),
                              currency='rub')
    years_ago = 10
    months_ago = years_ago * _MONTHS_PER_YEAR
    cagr = asset.get_cagr()
    cagr10 = asset.get_cagr(years_ago=years_ago)

    assert cagr.start_period == cagr10.start_period == start_period + 1
    assert cagr.end_period == cagr10.end_period == end_period
    assert cagr.period_size == months_ago

    ror_c = asset.rate_of_return(kind='cumulative')
    ror_from_cagr10 = (cagr10 + 1.) ** years_ago - 1.
    ror_from_cagr = (cagr + 1.) ** years_ago - 1.
    assert_that(ror_from_cagr.value, close_to(ror_c[-1].value, delta=delta))
    assert_that(ror_from_cagr10.value, close_to(ror_c[-1].value, delta=delta))


def test__risk():
    short_asset = y.portfolio_asset(name=__asset_name,
                                    start_period='2016-8', end_period='2016-12', currency='USD')

    assert_that(calling(short_asset.risk).with_args(period='year'), raises(Exception))

    assert __asset.risk().kind == TimeSeriesKind.REDUCED_VALUE
    assert __asset.risk(period='year').kind == TimeSeriesKind.REDUCED_VALUE
    assert __asset.risk(period='month').kind == TimeSeriesKind.REDUCED_VALUE

    assert_that(__asset.risk().value, close_to(.2860, delta))
    assert_that(__asset.risk(period='year').value, close_to(.2860, delta))
    assert_that(__asset.risk(period='month').value, close_to(.0823, delta))


def test__handle_related_inflation():
    assert_that(calling(__asset.inflation).with_args(kind='abracadabra'),
                raises(ValueError, 'inflation kind is not supported: abracadabra'))

    assert __asset.inflation(kind='values').size == __asset.rate_of_return().size

    assert_that(__asset.inflation(kind='cumulative').value, close_to(.1062, delta))
    assert_that(__asset.inflation(kind='a_mean').value, close_to(0.0014, delta))
    assert_that(__asset.inflation(kind='g_mean').value, close_to(0.0167, delta))

    infl_yoy = __asset.inflation(kind='yoy')
    assert infl_yoy.start_period == pd.Period('2012-1')
    assert infl_yoy.end_period == pd.Period('2016-1')
    np.testing.assert_almost_equal(infl_yoy.values, [.0174, .015, .0076, .0073, .0207], decimal_places)

    assert __asset.inflation(kind='values').size == __asset.rate_of_return().size
