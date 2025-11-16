from financial.reports.models.shared import AccountRow
class OutReportRow(AccountRow):
    def __init__(self, outRow):
        super().__init__(outRow.account_id, outRow.account_name, outRow.debit, outRow.credit, outRow.saldo, outRow.currencyId, outRow.currencySymbol)
        self.total_today = 0
        self.total_mtd = 0
        self.total_last_30_days = 0
        self.total_last_365_days = 0
        self.total_last_3_months = 0
        self.total_last_6_months = 0
