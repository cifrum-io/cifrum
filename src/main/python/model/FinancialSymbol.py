import pandas as pd


class FinancialSymbol:
    def __init__(self,
                 identifier,
                 values,
                 start_period=None,
                 end_period=None,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        self.identifier = identifier
        self.__values = values
        self.isin = isin
        self.short_name = short_name
        self.long_name = long_name
        self.exchange = exchange
        self.currency = currency
        self.security_type = security_type
        self.start_period = start_period
        self.end_period = end_period
        self.period = period
        self.adjusted_close = adjusted_close

    def values(self, start_period, end_period):
        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        return self.__values(start_period=start_period, end_period=end_period)

    @property
    def name(self):
        return self.identifier.name

    @property
    def namespace(self):
        return self.identifier.namespace

    def __repr__(self):
        from pprint import pformat
        return pformat(vars(self))
