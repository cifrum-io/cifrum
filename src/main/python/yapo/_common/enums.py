from enum import Enum, auto
import yapo


class Currency(Enum):
    RUB = auto()
    USD = auto()
    EUR = auto()

    def inflation(self):
        inflation_sym = yapo.information(name='infl/' + self.name)
        return inflation_sym


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
