from django.shortcuts import render
from django.http import Http404
from financial.models import SeatDetail, Currency

class DataSeat:
    def __init__(self):
        self.currency = None
        self.debit = 0
        self.credit = 0
        self.debitTotal = 0
        self.creditTotal = 0
        self.debitAccounts = {}
        self.creditAccounts = {}

    def getAmount(self):
        return self.debit - self.credit

def seat_report(request, id):
    try:
      seatDetails = SeatDetail.objects.filter(seat__id=id)
    except SeatDetail.DoesNotExist:
      raise Http404

    dataCurrencies = []

    currencies = Currency.objects.all()
    for currency in currencies:
      dataCurrency = DataSeat()
      dataCurrency.currency = currency

      for detail in seatDetails:
        if detail.debitAccount.currency.id != currency.id and detail.creditAccount.currency.id != currency.id:
          continue

        if detail.debitAccount.account_type.id in [1,2,3,9]:
            dataCurrency.debit += detail.mount
        if detail.creditAccount.account_type.id in [1,2,3,9]:
            dataCurrency.credit += detail.mount

        if str(detail.debitAccount.id) in dataCurrency.debitAccounts:
            dataCurrency.debitAccounts[str(detail.debitAccount.id)]['mount'] += detail.mount
        else:
            dataCurrency.debitAccounts[str(detail.debitAccount.id)] = { 'name': detail.debitAccount.name, 'mount': detail.mount }

        if str(detail.creditAccount.id) in dataCurrency.creditAccounts:
            dataCurrency.creditAccounts[str(detail.creditAccount.id)]['mount'] += detail.mount
        else:
            dataCurrency.creditAccounts[str(detail.creditAccount.id)] = { 'name': detail.creditAccount.name, 'mount': detail.mount }

        dataCurrency.debitTotal += detail.mount
        dataCurrency.creditTotal += detail.mount

      dataCurrencies.append(dataCurrency)

    seat = seatDetails[0].seat
    context = {'seatId': id, 'seatCode': seat.code, 'seatSummaryByCurrencies': dataCurrencies }

    # pdb.set_trace()
    return render(request, 'reports/seat.html', context)