import pandas as pd
from hamcrest import assert_that, instance_of, empty, not_none, has_length, has_property, starts_with, \
    contains_inanyorder, none

import yapo as y
from yapo.common.enums import Currency, SecurityType, Period
from yapo.common.financial_symbol import FinancialSymbol


def test__returns_sym_info():
    info = y.information(name='micex/FXRU')
    assert_that(info, instance_of(FinancialSymbol))

    info = y.information(names=[])
    assert_that(info, instance_of(list))
    assert_that(info, empty())

    info = y.information(names=['infl/RUB'])
    assert_that(info, instance_of(list))
    assert_that(info, has_length(1))

    info = y.information(names=['micex/FXRU', 'infl/RUB'])
    assert_that(info, instance_of(list))
    assert_that(info, has_length(2))


def test__micex_stocks_should_have_correct_fields():
    info = y.information(name='micex/SBER')
    assert_that(info, has_property('namespace', 'micex'))
    assert_that(info, has_property('name', 'SBER'))
    assert_that(info, has_property('isin', 'RU0009029540'))
    assert_that(info, has_property('short_name', 'Сбербанк'))
    assert_that(info, has_property('long_name', 'Сбербанк России ПАО ао'))
    assert_that(info, has_property('exchange', 'MICEX'))
    assert_that(info, has_property('currency', Currency.RUB))
    assert_that(info, has_property('security_type', SecurityType.STOCK_ETF))
    assert_that(info, has_property('period', Period.DAY))
    assert_that(info, has_property('adjusted_close', True))


def test__us_data_source_should_have_correct_fields():
    info = y.information(name='ny/VNQ')
    assert_that(info, has_property('namespace', 'ny'))
    assert_that(info, has_property('name', 'VNQ'))
    assert_that(info, has_property('isin', None))
    assert_that(info, has_property('short_name', 'Vanguard Real Estate Index Fund ETF Shares'))
    assert_that(info, has_property('long_name', None))
    assert_that(info, has_property('exchange', 'NYSE MKT'))
    assert_that(info, has_property('currency', Currency.USD))
    assert_that(info, has_property('security_type', SecurityType.STOCK_ETF))
    assert_that(info, has_property('period', Period.MONTH))
    assert_that(info, has_property('adjusted_close', True))


def test__currency_usd__should_have_correct_fields():
    info = y.information(name='cbr/USD')
    assert_that(info, has_property('namespace', 'cbr'))
    assert_that(info, has_property('name', 'USD'))
    assert_that(info, has_property('isin', None))
    assert_that(info, has_property('short_name', 'Доллар США'))
    assert_that(info, has_property('long_name', None))
    assert_that(info, has_property('exchange', None))
    assert_that(info, has_property('currency', Currency.USD))
    assert_that(info, has_property('security_type', SecurityType.CURRENCY))
    assert_that(info, has_property('period', Period.DAY))
    assert_that(info, has_property('adjusted_close', True))


def test__inflation_ru__should_have_correct_fields():
    info = y.information(name='infl/RUB')
    assert_that(info, has_property('namespace', 'infl'))
    assert_that(info, has_property('name', 'RUB'))
    assert_that(info, has_property('isin', None))
    assert_that(info, has_property('short_name', 'Инфляция РФ'))
    assert_that(info, has_property('long_name', None))
    assert_that(info, has_property('exchange', None))
    assert_that(info, has_property('currency', Currency.RUB))
    assert_that(info, has_property('security_type', SecurityType.INFLATION))
    assert_that(info, has_property('period', Period.MONTH))
    assert_that(info, has_property('adjusted_close', False))
    assert_that(info.values(start_period=pd.Period.now(freq='M') - 2,
                            end_period=pd.Period.now(freq='M')).columns,
                contains_inanyorder('period', 'value'))


def test__top_rates__should_have_correct_fields():
    info = y.information(name='cbr/TOP_rates')
    assert_that(info, has_property('namespace', 'cbr'))
    assert_that(info, has_property('name', 'TOP_rates'))
    assert_that(info, has_property('isin', None))
    assert_that(info, has_property('short_name', None))
    assert_that(info.long_name, starts_with('Динамика максимальной процентной'))
    assert_that(info, has_property('exchange', None))
    assert_that(info, has_property('currency', Currency.RUB))
    assert_that(info, has_property('security_type', SecurityType.RATES))
    assert_that(info, has_property('period', Period.DECADE))
    assert_that(info, has_property('adjusted_close', False))
    assert_that(info.values(start_period=pd.Period.now(freq='M') - 2,
                            end_period=pd.Period.now(freq='M')).columns,
                contains_inanyorder('period', 'rate'))


def test__all_data_should_be_available():
    assert_that(y.information(name='ny/MSFT'), not_none())
    assert_that(y.information(name='micex/FXRU'), not_none())
    assert_that(y.information(name='micex/FXMM'), not_none())
    assert_that(y.information(name='index/MCFTR'), not_none())
    assert_that(y.information(name='index/IMOEX'), not_none())
    assert_that(y.information(name='index/OKID10'), not_none())
    assert_that(y.information(name='index/^STOXX50E'), not_none())
    assert_that(y.information(name='mut_ru/0890-94127385'), not_none())
    assert_that(y.information(name='cbr/USD'), not_none())
    assert_that(y.information(name='cbr/EUR'), not_none())
    assert_that(y.information(name='infl/RUB'), not_none())
    assert_that(y.information(name='infl/USD'), not_none())
    assert_that(y.information(name='infl/EUR'), not_none())
    assert_that(y.information(name='cbr/TOP_rates'), not_none())


def test__return_none_if_no_finsym_is_found():
    not_existing_id = 'micex/MCFTR_doesntexist'
    assert_that(y.information(name=not_existing_id), none())

    infos = y.information(names=['infl/RUB', not_existing_id])
    assert_that(infos[0], not_none())
    assert_that(infos[1], none())


def test__return_same_infos_count_as_provided():
    ids_arr = ['infl/RUB', 'infl/EUR', 'micex/MCFTR', 'micex/FXRU']
    infos = y.information(names=ids_arr)
    assert len(infos) == len(ids_arr)


def test__be_invariant_in_respect_to_order():
    infos1 = [info.identifier.format() for info in y.information(names=['infl/RUB', 'infl/EUR'])]
    infos2 = [info.identifier.format() for info in y.information(names=['infl/EUR', 'infl/RUB'])]
    assert_that(infos1, contains_inanyorder(*infos2))
