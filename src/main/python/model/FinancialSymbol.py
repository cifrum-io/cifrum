from pprint import pformat
from .DataTable import DataTable
import pandas as pd
from .Enums import Currency, Period


class FinancialSymbol:
    def __init__(self, namespace, ticker, values,
                 isin=None,
                 short_name=None,
                 long_name=None,
                 exchange=None,
                 currency=None,
                 security_type=None,
                 period=None,
                 adjusted_close=None):
        def values_transformer():
            vals = values()
            vals['date'] = pd.to_datetime(vals['date'])
            vals['period'] = vals['date'].dt.to_period('M')

            if period == Period.DAY:
                vals_lastdate_indices = vals.groupby(['period'])['date'].transform(max) == vals['date']
                vals = vals[vals_lastdate_indices]
            elif period == Period.MONTH:
                pass
            else:
                pass  # Consider what to do with other periods

            vals.sort_values(by='period', ascending=True, inplace=True)
            vals.index = vals['period']
            del vals['date']
            return vals

        self.namespace = namespace
        self.ticker = ticker
        self.values = values_transformer
        self.isin = isin
        self.short_name = short_name
        self.long_name = long_name
        self.exchange = exchange
        self.currency = currency
        self.security_type = security_type
        self.period = period
        self.adjusted_close = adjusted_close

    def get_table(self, start_period, end_period, currency) -> DataTable:
        start_period = pd.Period(start_period, freq='M')
        end_period = pd.Period(end_period, freq='M')
        vals = self.values().copy()
        vals = vals[(vals['period'] >= start_period) & (vals['period'] <= end_period)]
        currency = Currency.__dict__[currency]
        dt = DataTable(financial_symbol=self,
                       values=vals,
                       currency=currency)
        return dt

    def __repr__(self):
        return pformat(vars(self))
