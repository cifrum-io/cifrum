from .Enums import Currency


class DataTable:
    def __init__(self, financial_symbol, values, currency: Currency):
        self.values = values
        self.financial_symbol = financial_symbol

        self.period_min = values['period'].min()
        self.period_max = values['period'].max()

        self.__convert_currency(currency)

        self.values['close_pctchange'] = self.values['close'].pct_change().fillna(value=0.)

    def accumulated_rate_of_return(self):
        cumprod = (self.values['close_pctchange'] + 1.).cumprod()
        aror = cumprod[-1]
        return aror

    def __convert_currency(self, currency_to: Currency):
        from .FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer

        currency_from = self.financial_symbol.currency
        if currency_from == currency_to:
            return

        currency_rate = FinancialSymbolsSourceContainer.currency_symbols_registry().rate(currency_from, currency_to)
        self.values = self.values.merge(currency_rate, on='period', how='left', suffixes=('', '_currency_rate'))
        self.values['close'] = self.values['close'] * self.values['close_currency_rate']
        self.values.index = self.values['period']
        self.values.sort_values(by='period', ascending=True, inplace=True)
        del self.values['close_currency_rate']
