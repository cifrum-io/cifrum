class DataTable:
    def __init__(self, financial_symbol, values):
        self.values = values
        self.financial_symbol = financial_symbol

        self.date_min = values.index.min()
        self.date_max = values.index.max()
