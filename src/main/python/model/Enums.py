from enum import Enum, auto
import yapo
import pandas as pd


class Currency(Enum):
    RUB = auto()
    USD = auto()
    EUR = auto()

    def inflation(self, start_period: pd.Period, end_period: pd.Period):
        inflation_sym = yapo.information(name='infl/' + self.name)
        values = inflation_sym.values(start_period=start_period, end_period=end_period)
        return values.value.values


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
