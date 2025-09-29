from django.shortcuts import render
from financial.models import AccountType, SeatDetail, Currency
from datetime import date
from calendar import monthrange

def account_type_report(request, id):
    currencyId = request.GET.get('currencyId', 1)
    before = 2024
    after = 2025
    years = [before, after]
    debits = []
    credits = []

    for year in years:
        values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            days = monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, days[1])
            value = 0
            details = SeatDetail.objects.filter(debitAccount__account_type__id=id, debitAccount__currency__id=currencyId, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
            # pdb.set_trace()
            for detail in details:
                value += detail.mount 
            values[month - 1] = value
        debits.append(values)

    for year in years:
        values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            days = monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, days[1])
            value = 0
            # pdb.set_trace()
            details = SeatDetail.objects.filter(creditAccount__account_type__id=id, creditAccount__currency__id=currencyId, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
            for detail in details:
                value += detail.mount 
            values[month - 1] = value
        credits.append(values)

    accountType = AccountType.objects.get(id=id)
    currency = Currency.objects.get(id=currencyId)

    context = {'accountTypeId': id, 'accountTypeName': accountType.name, 'currencyId': currencyId, 'currencyName': currency.name, 'beforeLabel':str(before), 'afterLabel':str(after), 'beforeDebitMounts': debits[0], 'afterDebitMounts': debits[1], 'beforeCreditMounts': credits[0], 'afterCreditMounts': credits[1]}
    return render(request, 'reports/account-type.html', context)