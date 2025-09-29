# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
from financial.models import SeatDetail, Account
from datetime import date
from calendar import monthrange

def seat_report(request, id):
    try:
        seatDetails = SeatDetail.objects.filter(seat__id=id)
    except SeatDetail.DoesNotExist:
        raise Http404

    debit = 0
    credit = 0
    debitTotal = 0
    creditTotal = 0
    debitAccounts = {}
    creditAccounts = {}

    for detail in seatDetails:
       if detail.debitAccount.account_type.id in [1,2,3]:
           debit += detail.mount
       if detail.creditAccount.account_type.id in [1,2,3]:
           credit += detail.mount

       if str(detail.debitAccount.id) in debitAccounts:
           debitAccounts[str(detail.debitAccount.id)]['mount'] += detail.mount
       else:
           debitAccounts[str(detail.debitAccount.id)] = { 'name': detail.debitAccount.name, 'mount': detail.mount }

       if str(detail.creditAccount.id) in creditAccounts:
           creditAccounts[str(detail.creditAccount.id)]['mount'] += detail.mount
       else:
           creditAccounts[str(detail.creditAccount.id)] = { 'name': detail.creditAccount.name, 'mount': detail.mount }

       debitTotal += detail.mount
       creditTotal += detail.mount
       
    context = {'debit': debit, 'credit': credit, 'seat': id, 'debitAccounts': debitAccounts, 'creditAccounts': creditAccounts, 'creditTotal': creditTotal, 'debitTotal': debitTotal, 'debitMinusCredit': debit - credit}

    # pdb.set_trace()
    return render(request, 'reports/seat.html', context)

def account_report(request, id):
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
            details = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
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
            details = SeatDetail.objects.filter(creditAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
            for detail in details:
                value += detail.mount 
            values[month - 1] = value
        credits.append(values)

    account = Account.objects.get(id=id)

    context = {'accountId': id, 'accountName': account.name, 'beforeLabel':str(before), 'afterLabel':str(after), 'beforeDebitMounts': debits[0], 'afterDebitMounts': debits[1], 'beforeCreditMounts': credits[0], 'afterCreditMounts': credits[1]}
    return render(request, 'reports/account.html', context)

