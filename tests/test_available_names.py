import pytest
from hamcrest import assert_that, none, empty, has_length, contains_inanyorder, has_items

import yapo as y


def test__return_namespaces_list_by_default():
    names = y.available_names()
    assert_that(names, contains_inanyorder('infl', 'cbr', 'micex', 'mut_ru', 'ny', 'index'))


def test__return_empty_list_or_none_if_symbol_doesnt_exist():
    nonexisting_id = 'nlu/xxx'

    asset = y.portfolio_asset(name=nonexisting_id)
    assert_that(asset, none())

    assets = y.portfolio_asset(names=[nonexisting_id])
    assert_that(assets, empty())

    assets = y.portfolio_asset(names=['micex/FXRU', nonexisting_id])
    assert_that(assets, has_length(1))

    portfolio = y.portfolio(assets={'micex/FXRU': 1., nonexisting_id: 1.}, currency='USD')
    assert len(portfolio.assets) == 1

    nonexisting_namespace = 'yyy/FXRU'

    asset = y.portfolio_asset(name=nonexisting_namespace)
    assert_that(asset, none())

    assets = y.portfolio_asset(names=[nonexisting_namespace])
    assert_that(assets, empty())

    assets = y.portfolio_asset(names=['micex/FXRU', nonexisting_namespace])
    assert_that(assets, has_length(1))

    portfolio = y.portfolio(assets={'micex/FXRU': 1., nonexisting_namespace: 1.}, currency='USD')
    assert_that(portfolio.assets, has_length(1))


@pytest.mark.quandl
def test__get_names_for_individual_namespace():
    def fin_sym_ids_by_namespace(namespace):
        return [available_name.fin_sym_id.format()
                for available_name in y.available_names(namespace=namespace)]

    assert_that(fin_sym_ids_by_namespace(namespace='infl'),
                contains_inanyorder('infl/RUB', 'infl/EUR', 'infl/USD'))

    assert_that(fin_sym_ids_by_namespace(namespace='cbr'),
                contains_inanyorder('cbr/TOP_rates', 'cbr/RUB', 'cbr/USD', 'cbr/EUR'))

    assert_that(fin_sym_ids_by_namespace(namespace='micex'),
                has_items('micex/MRKY', 'micex/URKZ', 'micex/VSMO', 'micex/ROSN'))

    assert_that(fin_sym_ids_by_namespace(namespace='mut_ru'),
                has_items('mut_ru/2277', 'mut_ru/0164-70287842', 'mut_ru/0890-94127385', 'mut_ru/2569'))

    assert_that(fin_sym_ids_by_namespace(namespace='ny'),
                has_items('ny/T', 'ny/MSFT', 'ny/GOOG', 'ny/AAPL'))


def test__return_several_namespaces():
    available_name_ids = [available_name.fin_sym_id.format()
                          for available_name in y.available_names(namespaces=['infl', 'micex'])]

    assert_that(available_name_ids,
                has_items('infl/RUB', 'infl/EUR', 'infl/USD',
                          'micex/SBER', 'micex/GAZP', 'micex/LKOH'))
