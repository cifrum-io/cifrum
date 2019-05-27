import itertools

import numpy as np
import pandas as pd
import pytest
from hamcrest import *

import yapo as l
from conftest import delta, decimal_places
from yapo.common.time_series import TimeSeriesKind

_portfolio_period_start = pd.Period('2015-4', freq='M')
_portfolio_period_end = pd.Period('2017-5', freq='M')
_asset_names = {'mut_ru/0890-94127385': 4, 'micex/FXRU': 3, 'micex/FXMM': 2}
_portfolio = l.portfolio(assets=_asset_names,
                         start_period=str(_portfolio_period_start),
                         end_period=str(_portfolio_period_end),
                         currency='USD')


class Test__compute_statistics_for_partially_incomplete_portfolio():
    @staticmethod
    @pytest.fixture
    def portfolio():
        asset_names = {'nlu/xxxx': 1, 'micex/FXRU': 2, 'micex/FXMM': 3}
        portfolio = l.portfolio(assets=asset_names,
                                start_period=str(_portfolio_period_start),
                                end_period=str(_portfolio_period_end),
                                currency='USD')
        assert_that(portfolio.assets, has_length(2))
        return portfolio

    @pytest.mark.parametrize('kind, real',
                             itertools.product(['values', 'accumulated', 'ytd'], [True, False]))
    def test__rate_of_return(self, portfolio, kind, real):
        assert_that(portfolio.rate_of_return(kind=kind, real=real), not_none())

    @pytest.mark.parametrize('years_ago, real',
                             itertools.product([None, 1, 5, 20, 50], [True, False]))
    def test__compound_annual_growth_rate(self, portfolio, years_ago, real):
        assert_that(portfolio.compound_annual_growth_rate(years_ago=years_ago, real=real), not_none())

    @pytest.mark.parametrize('period', ['year', 'month'])
    def test__risk(self, portfolio, period):
        assert_that(portfolio.risk(period=period), not_none())


def test__normalize_weights():
    assert_that(np.sum(_portfolio.weights), close_to(1., delta))

    assert_that(_portfolio.assets['mut_ru/0890-94127385'].weight, close_to(.4444, delta))
    assert_that(_portfolio.assets['micex/FXRU'].weight, close_to(.3333, delta))
    assert_that(_portfolio.assets['micex/FXMM'].weight, close_to(.2222, delta))

    asset_names = {'mut_ru/xxxx-xxxxxxxx': 1, 'micex/FXRU': 2, 'micex/FXMM': 3}
    portfolio_misprint = l.portfolio(assets=asset_names,
                                     start_period=str(_portfolio_period_start),
                                     end_period=str(_portfolio_period_end),
                                     currency='USD')
    assert_that(np.sum(portfolio_misprint.weights), close_to(1., delta))
    assert_that(portfolio_misprint.assets['micex/FXRU'].weight, close_to(.4, delta))
    assert_that(portfolio_misprint.assets['micex/FXMM'].weight, close_to(.6, delta))


def test__rate_of_return():
    rate_of_return_definition = \
        sum(asset.rate_of_return() * asset.weight for asset in _portfolio.assets.values())
    np.testing.assert_almost_equal(_portfolio.rate_of_return().values,
                                   rate_of_return_definition.values, decimal_places)


def test__accumulated_rate_of_return():
    arors = _portfolio.rate_of_return(kind='accumulated').values
    assert_that(arors.min(), close_to(-.0492, delta))
    assert_that(arors.max(), close_to(.3015, delta))

    arors_real = _portfolio.rate_of_return(kind='accumulated', real=True).values
    assert_that(arors_real.min(), close_to(-.0524, delta))
    assert_that(arors_real.max(), close_to(.2568, delta))


def test__ytd_rate_of_return():
    ror_ytd = _portfolio.rate_of_return(kind='ytd')
    assert ror_ytd.start_period == pd.Period('2016-1', freq='M')
    assert ror_ytd.end_period == pd.Period('2016-1', freq='M')
    np.testing.assert_almost_equal(ror_ytd.values, [.3480], decimal_places)

    ror_ytd_real = _portfolio.rate_of_return(kind='ytd', real=True)
    assert ror_ytd_real.start_period == pd.Period('2016-1', freq='M')
    assert ror_ytd_real.end_period == pd.Period('2016-1', freq='M')
    np.testing.assert_almost_equal(ror_ytd_real.values, [.3206], decimal_places)


def test__handle_related_inflation():
    assert_that(calling(_portfolio.inflation).with_args(kind='abracadabra'),
                raises(ValueError, 'inflation kind is not supported: abracadabra'))

    assert_that(_portfolio.inflation(kind='accumulated').value, close_to(.0365, delta))
    assert_that(_portfolio.inflation(kind='a_mean').value, close_to(.0014, delta))
    assert_that(_portfolio.inflation(kind='g_mean').value, close_to(.0167, delta))

    infl_yoy = _portfolio.inflation(kind='yoy')
    assert infl_yoy.start_period == pd.Period('2016-1')
    assert infl_yoy.end_period == pd.Period('2016-1')
    np.testing.assert_almost_equal(infl_yoy.values, [.0207], decimal_places)

    assert _portfolio.inflation(kind='values').size == _portfolio.rate_of_return().size


def test__compound_annual_growth_rate():
    cagr_default = _portfolio.compound_annual_growth_rate()
    assert_that(cagr_default.value, close_to(.1293, delta))

    cagr_long_time = _portfolio.compound_annual_growth_rate(years_ago=20)
    assert_that((cagr_default - cagr_long_time).value, close_to(0., delta))

    cagr_one_year = _portfolio.compound_annual_growth_rate(years_ago=1)
    assert_that(cagr_one_year.value, close_to(.1814, delta))

    cagr_default1, cagr_long_time1, cagr_one_year1 = \
        _portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1])
    assert_that((cagr_default1 - cagr_default).value, close_to(0., delta))
    assert_that((cagr_long_time1 - cagr_long_time).value, close_to(0., delta))
    assert_that((cagr_one_year1 - cagr_one_year).value, close_to(0., delta))


def test__compound_annual_growth_rate_real():
    cagr_default = _portfolio.compound_annual_growth_rate(real=True)
    assert_that(cagr_default.value, close_to(.1101, delta))

    cagr_long_time = _portfolio.compound_annual_growth_rate(years_ago=20, real=True)
    assert_that(cagr_default.value, close_to(cagr_long_time.value, delta))

    cagr_one_year = _portfolio.compound_annual_growth_rate(years_ago=1, real=True)
    assert_that(cagr_one_year.value, close_to(.1597, delta))

    cagr_default1, cagr_long_time1, cagr_one_year1 = \
        _portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
    assert_that(cagr_default1.value, close_to(cagr_default.value, delta))
    assert_that(cagr_long_time1.value, close_to(cagr_long_time.value, delta))
    assert_that(cagr_one_year1.value, close_to(cagr_one_year.value, delta))


def test__risk():
    short_portfolio = l.portfolio(assets=_asset_names,
                                  start_period='2016-8', end_period='2016-12', currency='USD')

    assert_that(calling(short_portfolio.risk).with_args(period='year'),
                raises(Exception))

    assert _portfolio.risk().kind == TimeSeriesKind.REDUCED_VALUE
    assert _portfolio.risk(period='year').kind == TimeSeriesKind.REDUCED_VALUE
    assert _portfolio.risk(period='month').kind == TimeSeriesKind.REDUCED_VALUE

    assert_that(_portfolio.risk(period='year').value, close_to(.1689, delta))
    assert_that(_portfolio.risk(period='month').value, close_to(.0432, delta))
    assert_that(_portfolio.risk().value, close_to(.1689, delta))
