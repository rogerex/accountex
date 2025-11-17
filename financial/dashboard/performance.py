import calendar
from dateutil.relativedelta import relativedelta
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

  accountIdsStr = request.GET.getlist('accountId', ['116'])
  accounts = []
  for accountId in accountIdsStr:
    id = int(accountId)
    account = Account.objects.get(id=id)
    accounts.append(account)

  labels = []

  match presetMode:
    case PresetMode.Today:
      labels = ["Yesterday", "Today"]

      start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
      end_date = datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)

      debitLines = []
      for account in accounts:
        id = account.id

        debitDetailsTillYesterday = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__lte=start_date)
        debitDetailsToday = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
        debitDetailsTillBeforeTotal = 0
        for detail in debitDetailsTillYesterday:
          debitDetailsTillBeforeTotal += detail.mount
        debitDetailsTotal = debitDetailsTillBeforeTotal
        for detail in debitDetailsToday:
          debitDetailsTotal += detail.mount

        debitLine = DataLine()
        debitLine.label = account.name
        debitLine.values = [debitDetailsTillBeforeTotal, debitDetailsTotal]
        debitLines.append(debitLine)

      creditLines = []
      for account in accounts:
        id = account.id

        creditDetailsTillYesterday = SeatDetail.objects.filter(creditAccount__id=id, seat__datetime__lte=start_date)
        creditDetailsToday = SeatDetail.objects.filter(creditAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)
        creditDetailsTillYesterdayTotal = 0
        for detail in creditDetailsTillYesterday:
          creditDetailsTillYesterdayTotal += detail.mount
        creditDetailsTodayTotal = creditDetailsTillYesterdayTotal
        for detail in creditDetailsToday:
          creditDetailsTodayTotal += detail.mount

        creditLine = DataLine()
        creditLine.label = account.name
        creditLine.values = [creditDetailsTillYesterdayTotal, creditDetailsTodayTotal]
        creditLines.append(creditLine)


    case PresetMode.OneWeek:
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
        debitDetailsTillBeforeTotal = 0
        for detail in debitDetailsTillBefore:
          debitDetailsTillBeforeTotal += detail.mount

        debitDetailsRange = SeatDetail.objects.filter(debitAccount__id=id, seat__datetime__gte=start_date, seat__datetime__lte=end_date)

        debitDetailsTotal = debitDetailsTillBeforeTotal
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
      months = 1
      labels, debitLines, creditLines = get_data_by_month(months, accounts)

    case PresetMode.OneMonth:
      months = 2
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.ThreeMonths:
      months = 3
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.SixMonths:
      months = 6
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.YearToDate:
      today = datetime.today()
      months = today.month
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.OneYear:
      months = 12
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.TwoYears:
      months = 24
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


    case PresetMode.ThreeYears:
      months = 36
      labels, debitLines, creditLines = get_data_by_month(months, accounts)


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

def get_previous_month_names(num_months=3):
    """
    Returns a list containing the names of the specified number of previous months.
    The most recent previous month is listed first.
    """
    previous_months = []
    current_date = datetime.now()

    for i in range(num_months):
        # Go back one month by setting the day to 1 and subtracting one day
        # This reliably gets to the last day of the previous month
        previous_month_date = current_date.replace(day=1)
        previous_months.append(previous_month_date.strftime("%Y %B"))
        current_date = previous_month_date  - timedelta(days=1) # Update current_date for the next iteration

    return previous_months[::-1]

def get_data_lines(accounts, dataRaws, filterAccountProperty):
  dataLines = []
  for account in accounts:
      id = account.id

      dataLine = DataLine()
      dataLine.label = account.name

      amount = 0
      for dataRaw in dataRaws:
        dataRaw['filter'][filterAccountProperty] = id # eg. debitAccount__id

        detailsTill = SeatDetail.objects.filter(**dataRaw['filter'])
        detailsTillBeforeTotal = amount
        for detail in detailsTill:
          detailsTillBeforeTotal += detail.mount

        amount = detailsTillBeforeTotal

        dataLine.values.append(amount)

      dataLines.append(dataLine)
  return dataLines

def get_data_raws_by_month(end_date, num_months):
  dataRaws = []
  for i in range(num_months):
    first_date = end_date
    next_date = first_date + timedelta(days=calendar.monthrange(first_date.year, first_date.month)[1])

    start_date = first_date.replace(day=1,hour=0, minute=0, second=0, microsecond=0)
    end_date = next_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if i == 0:
      dataRaws.append({
        'filter': {
          'seat__datetime__lt': end_date
        }
      })
    else:
      dataRaws.append({
        'filter': {
            'seat__datetime__gte': start_date,
            'seat__datetime__lt': end_date
          }
      })
  return dataRaws

def get_data_by_month(months, accounts):
  labels = get_previous_month_names(months)

  today = datetime.today()
  end_date = today - relativedelta(months=months-1)

  dataRaws = get_data_raws_by_month(end_date, months)
  debitLines = get_data_lines(accounts, dataRaws, 'debitAccount__id')
  creditLines = get_data_lines(accounts, dataRaws, 'creditAccount__id')

  return labels, debitLines, creditLines