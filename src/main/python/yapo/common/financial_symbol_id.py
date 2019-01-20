class FinancialSymbolId:
    __delimiter = '/'

    @classmethod
    def parse(cls, fin_symbol_fullname):
        namespace, name = fin_symbol_fullname.split(FinancialSymbolId.__delimiter)
        return FinancialSymbolId(namespace, name)

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def format(self):
        return self.namespace + FinancialSymbolId.__delimiter + self.name

    def __repr__(self):
        return self.format()
