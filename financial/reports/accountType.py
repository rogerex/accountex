from django.shortcuts import render
from financial.models import AccountType, SeatDetail, Currency
from datetime import date
from calendar import monthrange

class DataAccountType:
    def __init__(self):
        self.label = None
        self.values = []

def account_type_report(request, id):
    currencyId = request.GET.get('currencyId', 1)
    yearsTotal = request.GET.get('years', 2)
    yearsToCompare = int(yearsTotal)

    current_datetime = date.today()
    # Extract the year attribute
    year = current_datetime.year

    years = []
    while yearsToCompare > 0:
        years.append(year)
        year -= 1
        yearsToCompare -= 1

    years = sorted(years)
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

        debit = DataAccountType()
        debit.label = str(year)
        debit.values = values
        debits.append(debit)

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

        credit = DataAccountType()
        credit.label = str(year)
        credit.values = values
        credits.append(credit)

    accountType = AccountType.objects.get(id=id)
    currency = Currency.objects.get(id=currencyId)

    context = {'accountTypeId': id, 'accountTypeName': accountType.name, 'currencyId': currencyId, 'currencyName': currency.name, 'debits': debits, 'credits': credits, 'years': int(yearsTotal), 'allowedYears': range(1, 15)}
    return render(request, 'reports/account-type.html', context)