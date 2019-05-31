import itertools

import numpy as np
import pandas as pd
import pytest
from serum import inject

import yapo as y
from yapo._sources.registries import CurrencySymbolsRegistry
from yapo.common.enums import Currency


@pytest.fixture
def csr():
    @inject
    def csr_instance(csr: CurrencySymbolsRegistry):
        return csr

    return csr_instance()


@pytest.mark.parametrize('currency', Currency)
def test__currency_should_not_be_converted_to_itself_inside_converter(csr: CurrencySymbolsRegistry, currency: Currency):
    dt = csr.convert(currency_from=currency, currency_to=currency,
                     start_period=pd.Period('1960-1', freq='M'), end_period=pd.Period('2015-1', freq='M'))
    vs = dt['close'].values
    np.testing.assert_equal(vs, 1.)


@pytest.mark.parametrize('currency', Currency)
def test__currency_should_not_be_converted_to_itself_inside_datatable(currency: Currency):
    vs = y.portfolio_asset(name='cbr/' + currency.name,
                           start_period='2015-1', end_period='2017-1',
                           currency=currency.name).close()
    np.testing.assert_equal(vs.values, 1.)


@pytest.mark.parametrize('currency, expected_start_period',
                         [(Currency.RUB, pd.Period('1990-1', freq='M')),
                          (Currency.USD, pd.Period('1913-1', freq='M')),
                          (Currency.EUR, pd.Period('1996-1', freq='M'))])
@inject
def test__identity_currency_conversion_should_be_of_max_period(csr: CurrencySymbolsRegistry,
                                                               currency: Currency,
                                                               expected_start_period: pd.Period):
    ts = csr.convert(currency_from=currency, currency_to=currency,
                     start_period=pd.Period('1900-1', freq='M'),
                     end_period=pd.Period.now(freq='M'))
    assert ts['period'].min() == expected_start_period


def test__currency_should_be_converted_other_currency():
    vs = y.portfolio_asset(name='cbr/EUR',
                           start_period='2015-1', end_period='2017-1',
                           currency='USD').close()

    assert np.all(vs.values > 1.05)


@pytest.mark.parametrize('currency_from, currency_to', itertools.product(Currency, Currency))
def test__support_all_types_of_currency_conversions(currency_from: Currency, currency_to: Currency):
    vs = y.portfolio_asset(name='cbr/' + currency_from.name,
                           start_period='2015-1', end_period='2016-12',
                           currency=currency_to.name).close()

    assert vs.size == 2 * 12
    assert np.all(vs.values > 0.)


@pytest.mark.parametrize('currency1, currency2', itertools.product(Currency, Currency))
def test__currency_conversion_should_be_inversive(currency1: Currency, currency2: Currency):
    vs1 = y.portfolio_asset(name='cbr/' + currency1.name,
                            start_period='2015-1', end_period='2016-12',
                            currency=currency2.name).close()

    vs2 = y.portfolio_asset(name='cbr/' + currency2.name,
                            start_period='2015-1', end_period='2016-12',
                            currency=currency1.name).close()

    np.testing.assert_almost_equal(vs1.values * vs2.values, 1.)


def test__asset_should_be_converted_correctly():
    vs_eur = y.portfolio_asset(name='mut_ru/0890-94127385',
                               start_period='2011-1', end_period='2017-2',
                               currency='EUR').close()

    vs_usd = y.portfolio_asset(name='mut_ru/0890-94127385',
                               start_period='2011-1', end_period='2017-2',
                               currency='USD').close()

    vs_curr = y.portfolio_asset(name='cbr/USD',
                                start_period='2011-1', end_period='2017-2',
                                currency='EUR').close()

    np.testing.assert_almost_equal((vs_eur / vs_usd).values, vs_curr.values)
