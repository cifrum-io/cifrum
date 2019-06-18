import pytest
from hamcrest.core.base_matcher import BaseMatcher

decimal_places = 4
delta = 10 ** (-decimal_places)


class ListIsSorted(BaseMatcher):

    def __init__(self):
        pass

    def matches(self, item, mismatch_description=None):
        if not isinstance(item, list):
            return False
        return item == sorted(item)

    def describe_to(self, description):
        description.append_text('list was not sorted')


def sorted_asc():
    return ListIsSorted()


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--runslow", default=False):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if 'slow' in item.keywords:
                item.add_marker(skip_slow)
