from pprint import pformat


class FinancialSymbolInfo:
    def __init__(self, fin_sym_id, short_name):
        self.fin_sym_id = fin_sym_id
        self.short_name = short_name

    def __repr__(self):
        return pformat(vars(self))
