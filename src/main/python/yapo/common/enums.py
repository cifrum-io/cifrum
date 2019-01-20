from enum import Enum, auto
import yapo
import pandas as pd


class Currency(Enum):
    RUB = auto()
    USD = auto()
    EUR = auto()

    def inflation(self):
        inflation_sym = yapo.information(name='infl/' + self.name)
        return inflation_sym

    @property
    def period_min(self):
        currency_sym = yapo.information(name='cbr/' + self.name)
        period_min = pd.Period(currency_sym.start_period, freq='M')
        return period_min

    @property
    def period_max(self):
        currency_sym = yapo.information(name='cbr/' + self.name)
        period_max = pd.Period(currency_sym.end_period, freq='M')
        return period_max


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
