from django.contrib import admin
from financial.models import AccountType, Account, Balance, BalanceDetail, DiaryBook, Seat, SeatDetail, Vocabulary, VocabularyAdmin, Term, TermInline

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Balance)
admin.site.register(BalanceDetail)
admin.site.register(DiaryBook)
admin.site.register(Seat)
admin.site.register(SeatDetail)
admin.site.register(Vocabulary, VocabularyAdmin)


