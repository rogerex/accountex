from django.contrib import admin
from financial.models import AccountType, Account, Balance

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Balance)

