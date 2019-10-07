class FinancialSymbolId:
    __delimiter = '/'

    @classmethod
    def parse(cls, fin_symbol_fullname: str):
        namespace, name = fin_symbol_fullname.split(FinancialSymbolId.__delimiter)
        return FinancialSymbolId(namespace, name)

    def __init__(self, namespace: str, name: str):
        self.namespace = namespace
        self.name = name

    def format(self) -> str:
        return self.namespace + FinancialSymbolId.__delimiter + self.name

    def __repr__(self):
        return self.format()
