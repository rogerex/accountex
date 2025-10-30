class DataLine:
    def __init__(self):
        self.label = None
        self.values = []

class AccountRow:
    def __init__(self, account_id, account_name, debit, credit, saldo, currencyId, currencySymbol):
        self.account_id = account_id
        self.account_name = account_name
        self.debit = debit
        self.credit = credit
        self.saldo = saldo
        self.currencyId = currencyId
        self.currencySymbol = currencySymbol

class CurrencyAccountList:
    def __init__(self, currency):
        self.currency = currency
        self.rows = []

class TagGroup:
    def __init__(self, name, prefixs):
        self.name = name
        self.prefixs = prefixs
        self.rows = []
        self.total = 0
        self.percentage = 0

class CurrencyTagGroups:
    def __init__(self, currency):
        self.currency = currency
        self.tagGroups = []
        self.total = 0