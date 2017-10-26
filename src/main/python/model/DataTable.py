from .Enums import Currency


class DataTable:
    def __init__(self, financial_symbol, values, currency: Currency):
        self.values = values
        self.financial_symbol = financial_symbol

        self.period_min = values.index.min()
        self.period_max = values.index.max()

        self.__convert_currency(currency)

    def __convert_currency(self, currency_to: Currency):
        from .FinancialSymbolsSourceContainer import FinancialSymbolsSourceContainer

        currency_from = self.financial_symbol.currency
        if currency_from == currency_to:
            return

        currency_rate = FinancialSymbolsSourceContainer.currency_symbols_registry().rate(currency_from, currency_to)
        self.values['date'] = self.values.index
        currency_rate['date'] = currency_rate.index
        self.values = self.values.merge(currency_rate, on='date', how='left', suffixes=('', '_currency_rate'))
        self.values['close'] = self.values['close'] * self.values['close_currency_rate']
        self.values.index = self.values['date']
        del self.values['date'], self.values['close_currency_rate']
