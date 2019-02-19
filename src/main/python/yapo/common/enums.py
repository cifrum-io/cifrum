from enum import Enum, auto
import yapo
import pandas as pd


class Currency(Enum):
    RUB = auto()
    USD = auto()
    EUR = auto()


class SecurityType(Enum):
    STOCK_ETF = auto()
    INDEX = auto()
    MUT = auto()
    CURRENCY = auto()
    INFLATION = auto()
    RATES = auto()


class Period(Enum):
    DAY = auto()
    MONTH = auto()
    DECADE = auto()
