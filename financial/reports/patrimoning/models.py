class PatrimonyRow:
    def __init__(self, account_id, account_name, debit, credit, saldo, currencyId, currencySymbol):
        self.account_id = account_id
        self.account_name = account_name
        self.debit = debit
        self.credit = credit
        self.saldo = saldo
        self.currencyId = currencyId
        self.currencySymbol = currencySymbol

class AssetRow(PatrimonyRow):
    def __init__(self, patrimonyRow):
        super().__init__(patrimonyRow.account_id, patrimonyRow.account_name, patrimonyRow.debit, patrimonyRow.credit, patrimonyRow.saldo, patrimonyRow.currencyId, patrimonyRow.currencySymbol)
        self.total_today = 0
        self.total_mtd = 0
        self.total_ytd = 0
        self.total_last_30_days = 0
        self.total_last_365_days = 0
        self.total_last_3_months = 0
        self.total_last_6_months = 0

class CurrencyPatrimony:
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