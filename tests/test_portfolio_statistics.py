import itertools

import numpy as np
import pandas as pd
import pytest
from hamcrest import assert_that, has_length, contains, not_none, close_to, calling, raises, is_not, empty

import yapo as y
from conftest import delta, decimal_places
from yapo.common.enums import Currency
from yapo.common.time_series import TimeSeriesKind

_portfolio_period_start = pd.Period('2015-3', freq='M')
_portfolio_period_end = pd.Period('2017-5', freq='M')
_asset_names = {'mut_ru/0890-94127385': 4, 'micex/FXRU': 3, 'micex/FXMM': 2}
_portfolio = y.portfolio(assets=_asset_names,
                         start_period=str(_portfolio_period_start),
                         end_period=str(_portfolio_period_end),
                         currency='USD')


def test__initial_data():
    assert_that(_portfolio.assets, has_length(3))

    p = y.portfolio(assets=_asset_names,
                    start_period=str(_portfolio_period_start),
                    end_period=str(_portfolio_period_end),
                    currency='RUB')
    assert_that(p.assets, has_length(3))

    assert_that(p.assets['mut_ru/0890-94127385'].close().values, contains(
        *[1055.64, 1094.14, 1080.76, 1074.51, 1091.37, 1151.83, 1103.9, 1147.5,
          1193.69, 1175.64, 1199.64, 1233.88, 1252.67, 1302.46, 1268.7,
          1269.31, 1334.93, 1351.45, 1357.41, 1366.64, 1444.08, 1535.61,
          1525.6, 1403.08, 1375.97, 1390.39, 1314.96]
    ))
    assert_that(p.assets['micex/FXRU'].close().values, contains(
        *[5070., 4670., 4830., 5110., 5650., 6130., 6160., 6140., 6330., 7020.,
          7230., 7250., 6720., 6540., 6710., 6630., 6760., 6770., 6550.,
          6610., 6570., 6260., 6310., 6110., 5970., 6110., 6190.]
    ))
    assert_that(p.assets['micex/FXMM'].close().values, contains(
        *[1097.2, 1110., 1121.7, 1135.5, 1146.5, 1155.7, 1164.4, 1174.3, 1183.8,
          1194.7, 1203.8, 1215.1, 1228.6, 1233.2, 1237.3, 1246.6, 1253.7,
          1265.5, 1273.4, 1282.7, 1292.1, 1302.2, 1308.6, 1317.2, 1327.5,
          1336.8, 1346.1]
    ))

    assert_that(np.round(_portfolio.rate_of_return().values, 8).tolist(), contains(
        *[0.12229691, -0.01582228, -0.02737772, -0.01702011, -0.06406856, -0.01160388, 0.04782469, 0.00100095,
          -0.06237734, -0.0103524, 0.01680251, 0.09387303, 0.06095007, -0.02852904, 0.02625182, -0.01216933,
          0.04138359, 0.02000188, 0.01177389, -0.00741344, 0.08587424, 0.00909396, -0.00811951, 0.01276804,
          0.00324936, -0.0100885]))

    assert_that(np.round(_portfolio.rate_of_return(real=True).values, 8).tolist(), contains(
        *[0.12001991, -0.0208132, -0.03077293, -0.01708596, -0.0627414, -0.01006255, 0.04829642, 0.00311853,
          -0.05916249, -0.01198559, 0.01596637, 0.08918301, 0.05594384, -0.03244377, 0.02289264, -0.01056843,
          0.04042848, 0.01755568, 0.01051378, -0.00586757, 0.08551928, 0.00324703, -0.01123018, 0.01194533,
          0.00028252, -0.01093415]
    ))


class Test__compute_statistics_for_partially_incomplete_portfolio():
    @staticmethod
    @pytest.fixture
    def portfolio():
        asset_names = {'nlu/xxxx': 1, 'micex/FXRU': 2, 'micex/FXMM': 3}
        portfolio = y.portfolio(assets=asset_names,
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
    portfolio_misprint = y.portfolio(assets=asset_names,
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
    assert_that(arors.max(), close_to(.3017, delta))

    arors_real = _portfolio.rate_of_return(kind='accumulated', real=True).values
    assert_that(arors_real.min(), close_to(-.0524, delta))
    assert_that(arors_real.max(), close_to(.2569, delta))


def test__ytd_rate_of_return():
    ror_ytd = _portfolio.rate_of_return(kind='ytd')
    assert ror_ytd.start_period == pd.Period('2016-1', freq='M')
    assert ror_ytd.end_period == pd.Period('2016-1', freq='M')
    np.testing.assert_almost_equal(ror_ytd.values, [.3457], decimal_places)

    ror_ytd_real = _portfolio.rate_of_return(kind='ytd', real=True)
    assert ror_ytd_real.start_period == pd.Period('2016-1', freq='M')
    assert ror_ytd_real.end_period == pd.Period('2016-1', freq='M')
    np.testing.assert_almost_equal(ror_ytd_real.values, [.3184], decimal_places)


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
    assert_that(cagr_one_year.value, close_to(.1821, delta))

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
    assert_that(cagr_one_year.value, close_to(.1604, delta))

    cagr_default1, cagr_long_time1, cagr_one_year1 = \
        _portfolio.compound_annual_growth_rate(years_ago=[None, 20, 1], real=True)
    assert_that(cagr_default1.value, close_to(cagr_default.value, delta))
    assert_that(cagr_long_time1.value, close_to(cagr_long_time.value, delta))
    assert_that(cagr_one_year1.value, close_to(cagr_one_year.value, delta))


def test__risk():
    short_portfolio = y.portfolio(assets=_asset_names,
                                  start_period='2016-8', end_period='2016-12', currency='USD')

    assert_that(calling(short_portfolio.risk).with_args(period='year'),
                raises(Exception))

    assert _portfolio.risk().kind == TimeSeriesKind.REDUCED_VALUE
    assert _portfolio.risk(period='year').kind == TimeSeriesKind.REDUCED_VALUE
    assert _portfolio.risk(period='month').kind == TimeSeriesKind.REDUCED_VALUE

    assert_that(_portfolio.risk(period='year').value, close_to(.1688, delta))
    assert_that(_portfolio.risk(period='month').value, close_to(.0432, delta))
    assert_that(_portfolio.risk().value, close_to(.1688, delta))


@pytest.mark.quandl
@pytest.mark.parametrize('currency', Currency)
def test__handle_portfolio_with_asset_with_dot_in_name(currency: Currency):
    p = y.portfolio(assets={'ny/BRK.B': 1}, currency=currency.name)
    assert_that(p, not_none())
    assert_that(p.assets, has_length(1))
    assert_that(p.rate_of_return(), is_not(empty()))


@pytest.mark.parametrize('currency', Currency)
def test__handle_assets_with_monthly_data_gaps(currency: Currency):
    p = y.portfolio(assets={'micex/KUBE': 1}, currency=currency.name)
    assert_that(p, not_none())
    assert_that(p.assets, has_length(1))
    assert_that(p.rate_of_return(), is_not(empty()))
