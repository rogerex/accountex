from django.shortcuts import render
from financial.models import SeatDetail, Account
from datetime import datetime, timedelta
from ..reports.models.shared import DataLine

class PresetMode:
    Today = 1
    OneWeek = 2
    MonthToDate = 3
    OneMonth = 4
    ThreeMonths = 5
    SixMonths = 6
    YearToDate = 7
    OneYear = 8
    TwoYears = 9
    ThreeYears = 10
    FiveYears = 11
    TenYears = 12
    All = 13

def performance_widget(request):
  presetModeStr = request.GET.get('presetMode', 1)
  presetMode = int(presetModeStr)

  accountIdsStr = request.GET.getlist('accountId', ['125'])
  accounts = []
  for accountId in accountIdsStr:
    id = int(accountId)
    account = Account.objects.get(id=id)
    accounts.append(account)

  labels = []

  match presetMode:
    case PresetMode.Today:
      print("The color is Today.")
      labels = ["Yesterday", "Today"]

      start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
      end_date = datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)

      debitLines = [];
      for account in accounts:
        id = account.id

        debitDetailsTillYesterday = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__lte=start_date)
        debitDetailsToday = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
        debitDetailsTillBeforeTotal = 0;
        for detail in debitDetailsTillYesterday:
          debitDetailsTillBeforeTotal += detail.mount
        debitDetailsTotal = debitDetailsTillBeforeTotal;
        for detail in debitDetailsToday:
          debitDetailsTotal += detail.mount

        debitLine = DataLine()
        debitLine.label = account.name
        debitLine.values = [debitDetailsTillBeforeTotal, debitDetailsTotal]
        debitLines.append(debitLine)

      creditLines = [];
      for account in accounts:
        id = account.id

        creditDetailsTillYesterday = SeatDetail.objects.filter(creditAccount__id=id, seat__datetime__lte=start_date)
        creditDetailsToday = SeatDetail.objects.filter(creditAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
        creditDetailsTillYesterdayTotal = 0;
        for detail in creditDetailsTillYesterday:
          creditDetailsTillYesterdayTotal += detail.mount
        creditDetailsTodayTotal = creditDetailsTillYesterdayTotal;
        for detail in creditDetailsToday:
          creditDetailsTodayTotal += detail.mount

        creditLine = DataLine()
        creditLine.label = account.name
        creditLine.values = [creditDetailsTillYesterdayTotal, creditDetailsTodayTotal]
        creditLines.append(creditLine)

    case PresetMode.OneWeek:
      print("The color is OneWeek.")
      labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

      today = datetime.today()
      one_week = timedelta(weeks=1)
      new_date = today - one_week

      start_date = new_date.replace(hour=0, minute=0, second=0, microsecond=0)
      end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)

      debitLines = [];
      for account in accounts:
        id = account.id

        debitDetailsTillBefore = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__lte=start_date)
        debitDetailsTillBeforeTotal = 0;
        for detail in debitDetailsTillBefore:
          debitDetailsTillBeforeTotal += detail.mount

        debitDetailsRange = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)

        debitDetailsTotal = debitDetailsTillBeforeTotal;
        debitLine = DataLine()
        debitLine.label = account.name

        for label in labels:
          debitDetails = debitDetailsRange.filter(seat__datetime__week_day=labels.index(label)+1)
          for detail in debitDetails:
            debitDetailsTotal += detail.mount

          debitLine.values.append(debitDetailsTotal)
        debitLines.append(debitLine)

      creditLines = [];


    case PresetMode.MonthToDate:
      print("The color is MonthToDate.")
    case PresetMode.OneMonth:
      print("The color is OneMonth.")
    case PresetMode.ThreeMonths:
      print("The color is ThreeMonths.")
    case PresetMode.SixMonths:
      print("The color is SixMonths.")
    case PresetMode.YearToDate:
      print("The color is YearToDate.")
    case PresetMode.OneYear:
      print("The color is OneYear.")
    case PresetMode.TwoYears:
      print("The color is TwoYears.")
    case PresetMode.ThreeYears:
      print("The color is ThreeYears.")
    case PresetMode.FiveYears:
      print("The color is FiveYears.")
    case PresetMode.TenYears:
      print("The color is TenYears.")
    case PresetMode.All:
      print("The color is All.")
    case _: # Default case for any other value (optional)
        print("Unknown color.")

  context = {
    'datetime': datetime.today(),
    'accounts': accounts,
    'labels': labels,
    'debitLines': debitLines,
    'creditLines': creditLines,
    'presetMode': presetMode,
  }
  return render(request, 'dashboard/performance.html', context)