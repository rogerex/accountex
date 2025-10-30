from financial.reports.models.shared import AccountRow
class AssetRow(AccountRow):
    def __init__(self, patrimonyRow):
        super().__init__(patrimonyRow.account_id, patrimonyRow.account_name, patrimonyRow.debit, patrimonyRow.credit, patrimonyRow.saldo, patrimonyRow.currencyId, patrimonyRow.currencySymbol)
        self.total_today = 0
        self.total_mtd = 0
        self.total_ytd = 0
        self.total_last_30_days = 0
        self.total_last_365_days = 0
        self.total_last_3_months = 0
        self.total_last_6_months = 0
