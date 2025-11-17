from django.contrib import admin
from financial.menu_items import Dashboard, DashboardAdmin, Flows, FlowsAdmin, Patrimony, PatrimonyAdmin
from financial.models import AccountType, AccountTypeAdmin, Account, AccountAdmin, Balance, BalanceDetail, DiaryBook, Seat, SeatDetail, Vocabulary, VocabularyAdmin, Term, TermInline, SeatAdmin, Currency


admin.site.register(AccountType, AccountTypeAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Balance)
admin.site.register(BalanceDetail)
admin.site.register(DiaryBook)
admin.site.register(SeatDetail)
admin.site.register(Vocabulary, VocabularyAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Currency)
admin.site.register(Patrimony, PatrimonyAdmin)
admin.site.register(Flows, FlowsAdmin)
admin.site.register(Dashboard, DashboardAdmin)


