import datetime as dtm

import numpy as np
import pandas as pd
import pytest
from freezegun import freeze_time
from hamcrest import assert_that, calling, raises, is_, is_not, not_none, empty
from serum import Context

import yapo as y
from conftest import sorted_asc, decimal_places
from yapo._sources.all_sources import SymbolSources
from yapo._sources.base_classes import SingleFinancialSymbolSource
from yapo.common.enums import Currency, SecurityType, Period


@pytest.fixture
def yapo_instance_factory():
    class YapoInstanceFactory:

        def create(self, date_list):
            class TestSymbolSources(SymbolSources):
                def __init__(self):
                    self.values = pd.DataFrame({'close': np.linspace(start=1., stop=100., num=len(date_list)),
                                                'date': date_list})

                @property
                def sources(self):
                    return [SingleFinancialSymbolSource(
                        namespace='test_ns', name='test',
                        values_fetcher=lambda: self.values,
                        security_type=SecurityType.STOCK_ETF,
                        start_period=pd.Period(self.values['date'].min(), freq='D'),
                        end_period=pd.Period(self.values['date'].max(), freq='D'),
                        period=Period.DAY,
                        currency=Currency.RUB)]

            with Context(TestSymbolSources):
                yapo_instance = y._instance.Yapo()
                return yapo_instance

    return YapoInstanceFactory()


__portfolio = y.portfolio(assets={'mut_ru/0890-94127385': 1.,
                                  'micex/FXRU': 1.,
                                  'micex/FXMM': 1.,
                                  'cbr/USD': 1.,
                                  'cbr/EUR': 1.,
                                  'cbr/RUB': 1.},
                          start_period='2015-3', end_period='2017-5', currency='USD')


@pytest.mark.parametrize('unsupported_id', ['infl/RUB', 'infl/USD', 'infl/EUR', 'cbr/TOP_rates'])
def test__fail_if_asset_security_type_is_not_supported(unsupported_id):
    foo = calling(y.portfolio_asset).with_args(name=unsupported_id,
                                               start_period='2011-3', end_period='2015-5', currency='USD')
    assert_that(foo, raises(AssertionError))


def test__period_should_be_sorted():
    for asset in __portfolio.assets.values():
        period_range = asset.close().period_range()
        assert_that(period_range, is_(sorted_asc()))


def test__default_periods():
    asset = y.portfolio_asset(name='micex/SBER')
    assert asset.close().start_period >= pd.Period('1900-1', freq='M')
    assert pd.Period.now(freq='M') >= asset.close().end_period
    assert asset.currency.value == Currency.RUB

    portfolio = y.portfolio(assets={'micex/SBER': 1.}, currency='rub')
    assert portfolio.rate_of_return().start_period >= pd.Period('1900-1', freq='M')
    assert pd.Period.now(freq='M') >= portfolio.rate_of_return().end_period


@pytest.mark.quandl
def test__usd_assets_that_is_older_than_rub():
    p_usd = y.portfolio(assets={'ny/T': 1}, currency='usd')
    assert p_usd.rate_of_return().start_period == pd.Period('1984-08', freq='M')

    p_rub = y.portfolio(assets={'ny/T': 1}, currency='rub')
    assert p_rub.rate_of_return().start_period == pd.Period('1992-08', freq='M')
    assert p_usd.rate_of_return().end_period == p_rub.rate_of_return().end_period


@pytest.mark.slow
@freeze_time('2018-10-31 1:0:0')
def test__data_for_last_month_period_should_be_dropped(yapo_instance_factory):
    num_days = 70
    date_start = dtm.datetime.now() - dtm.timedelta(days=num_days)
    date_list = pd.date_range(date_start, periods=num_days, freq='D')
    yi = yapo_instance_factory.create(date_list=date_list)

    end_period = pd.Period.now(freq='M')
    start_period = end_period - 2
    asset = yi.portfolio_asset(name='test_ns/test',
                               start_period=str(start_period), end_period=str(end_period),
                               currency='USD')
    period_range_expected = pd.period_range(start=start_period, end=end_period - 1, freq='M')
    assert asset.close().period_range() == list(period_range_expected)


@pytest.mark.quandl
@pytest.mark.slow
@freeze_time('2018-1-30 1:0:0')
def test__quandl_values():
    asset = y.portfolio_asset(name='ny/MSFT',
                              start_period='2017-11', end_period='2018-2', currency='usd')
    period_range_expected = pd.period_range(start='2017-11', end='2017-12', freq='M')
    assert asset.close().period_range() == list(period_range_expected)


@pytest.mark.slow
@freeze_time('2018-10-31 1:0:0')
def test__drop_last_month_data_if_no_activity_within_last_full_month(yapo_instance_factory):
    num_days = 58
    date_start = dtm.datetime.now() - dtm.timedelta(days=num_days + 32)
    date_list = pd.date_range(date_start, periods=num_days, freq='D')
    yi = yapo_instance_factory.create(date_list=date_list)

    end_period = pd.Period.now(freq='M')
    start_period = end_period - 2
    asset = yi.portfolio_asset(name='test_ns/test',
                               start_period=str(start_period), end_period=str(end_period),
                               currency='USD')

    period_range_expected = pd.period_range(start=start_period, end=end_period - 2, freq='M')
    assert asset.close().period_range() == list(period_range_expected)


def test__compute_accumulated_rate_of_return():
    for asset in __portfolio.assets.values():
        aror = asset.rate_of_return(kind='accumulated').values
        assert not np.any(np.isnan(aror))

    aror = __portfolio.rate_of_return(kind='accumulated').values
    assert not np.any(np.isnan(aror))


def test__close_and_its_change_should_preserve_ratio():
    for asset in __portfolio.assets.values():
        rate_of_return_given = asset.rate_of_return().values
        rate_of_return_expected = np.diff(asset.close().values) / asset.close().values[:-1]
        np.testing.assert_almost_equal(rate_of_return_given, rate_of_return_expected, decimal_places)


@freeze_time('2018-5-20 1:0:0')
def test__fail_if_date_range_is_short():
    assert_that(calling(y.portfolio_asset).with_args(name='micex/FXRU',
                                                     start_period='2015-3', end_period='2015-4'),
                raises(ValueError, r'period range should be at least \d+ months'))

    assert_that(calling(y.portfolio).with_args(assets={'micex/FXRU': 1.},
                                               start_period='2015-4', end_period='2015-4',
                                               currency='rub'),
                raises(ValueError, r'period range should be at least \d+ months'))

    assert_that(calling(y.portfolio).with_args(assets={'micex/FXUS': 1, 'micex/FXTB': 1},
                                               currency='rub', start_period='2019-03'),
                raises(ValueError, r'period range should be at least \d+ months'))


@freeze_time('2018-5-1 1:0:0')
def test__fail_if_awkwardly_current_time_is_less_than_asset_start_date():
    assert_that(calling(y.portfolio).with_args(assets={'mut_ru/3647': 1.}, currency='rub'),
                raises(ValueError, '`self._period_min` must not be >= `self._period_max`'))


@pytest.mark.quandl
def test__handle_asset_with_dot_in_name():
    asset = y.portfolio_asset(name='ny/BRK.B')
    assert_that(asset, not_none())
    assert_that(asset.close(), is_not(empty()))
