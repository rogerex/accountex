import calendar
from dateutil.relativedelta import relativedelta
from django import forms
from django.shortcuts import render
from financial.models import SeatDetail, Account
from datetime import date, datetime, timedelta
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

class AccountForm(forms.ModelForm):
    accounts = forms.ModelMultipleChoiceField(
        #choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green')],
        queryset=Account.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Account
        fields = []

def performance_widget(request):
  presetModeStr = request.GET.get('presetMode', 1)
  presetMode = int(presetModeStr)

  accountIdsStr = request.GET.getlist('accountId', ['1', '43'])
  
  if request.method == 'POST':
    form = AccountForm(request.POST)
    if form.is_valid():
      selected_items = form.cleaned_data['accounts']
      request.session['saved_accounts'] = [str(item.id) for item in selected_items]
      accountIdsStr = [str(item.id) for item in selected_items]
  else:
    selected_items = request.session.get('saved_accounts', accountIdsStr)
    selected_accounts = Account.objects.filter(id__in=selected_items)
    accountIdsStr = [str(item.id) for item in selected_accounts]

    form = AccountForm(initial={'accounts': selected_accounts})

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
      days = 7
      labels, debitLines, creditLines = get_data_by_day(days, accounts)


    case PresetMode.MonthToDate:
      weeks = get_week_of_month(datetime.today())
      labels, debitLines, creditLines = get_data_by_week(weeks, accounts)


    case PresetMode.OneMonth:
      weeks = 4
      labels, debitLines, creditLines = get_data_by_week(weeks, accounts)


    case PresetMode.ThreeMonths:
      weeks = 12
      labels, debitLines, creditLines = get_data_by_week(weeks, accounts)


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
      years = 5
      labels, debitLines, creditLines = get_data_by_year(years, accounts)


    case PresetMode.TenYears:
      years = 10
      labels, debitLines, creditLines = get_data_by_year(years, accounts)


    case PresetMode.All:
      years = 15
      labels, debitLines, creditLines = get_data_by_year(years, accounts)


    case _: # Default case for any other value (optional)
        print("Unknown color.")

  context = {
    'datetime': datetime.today(),
    'accounts': accounts,
    'labels': labels,
    'debitLines': debitLines,
    'creditLines': creditLines,
    'presetMode': presetMode,
    'form': form
  }
  return render(request, 'dashboard/performance.html', context)

def get_last_n_month_names(num_months=3):
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

def get_data_lines(accounts, baseFilters, filterAccountProperty):
  dataLines = []
  for account in accounts:
      id = account.id

      dataLine = DataLine()
      dataLine.label = account.name

      amount = 0
      for filter in baseFilters:
        filter['filter'][filterAccountProperty] = id # eg. debitAccount__id

        detailsTill = SeatDetail.objects.filter(**filter['filter'])
        detailsTillBeforeTotal = amount
        for detail in detailsTill:
          detailsTillBeforeTotal += detail.mount

        amount = detailsTillBeforeTotal

        dataLine.values.append(amount)

      dataLines.append(dataLine)
  return dataLines

def get_base_filters_by_month(end_date, num_months):
  dataRaws = []
  for i in range(num_months):
    first_date = end_date
    next_date = first_date + timedelta(days=calendar.monthrange(first_date.year, first_date.month)[1])

    start_date = first_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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
  labels = get_last_n_month_names(months)

  today = datetime.today()
  end_date = today - relativedelta(months=months-1)

  debitBaseFilters = get_base_filters_by_month(end_date, months)
  creditBaseFilters = get_base_filters_by_month(end_date, months) # Same as debit however it could add more filters and references in future
  debitLines = get_data_lines(accounts, debitBaseFilters, 'debitAccount__id')
  creditLines = get_data_lines(accounts, creditBaseFilters, 'creditAccount__id')

  return labels, debitLines, creditLines

def get_base_filters_by_year(end_date, num_years):
  dataRaws = []
  for i in range(num_years):
    first_date = end_date
    next_date = first_date.replace(year=first_date.year + 1)

    start_date = first_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = next_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

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

def get_data_by_year(years, accounts):
  labels = get_last_n_year_names(years)

  today = datetime.today()
  end_date = today - relativedelta(years=years-1)
  debitBaseFilters = get_base_filters_by_year(end_date, years)
  creditBaseFilters = get_base_filters_by_year(end_date, years) # Same as debit however it could add more filters and references in future
  debitLines = get_data_lines(accounts, debitBaseFilters, 'debitAccount__id')
  creditLines = get_data_lines(accounts, creditBaseFilters, 'creditAccount__id')

  return labels, debitLines, creditLines

def get_last_n_year_names(num_years=3):
    previous_years = []
    current_date = datetime.now()

    for i in range(num_years):
        previous_year_date = current_date.replace(day=1)
        previous_years.append(previous_year_date.strftime("%Y"))
        current_date = previous_year_date  - timedelta(days=365) # Update current_date for the next iteration

    return previous_years[::-1]

def get_last_n_weeks_names(n):
    today = date.today()
    # Find the start of the current week (Monday)
    start_of_current_week = today - timedelta(days=today.weekday())

    weeks = []
    for i in range(n):
        week_start = start_of_current_week - timedelta(weeks=i)
        weeks.append(week_start.strftime("%Y %B") + " Week " + str(week_start.isocalendar()[1]))
    return weeks[::-1]

def get_data_by_week(weeks, accounts):
  labels = get_last_n_weeks_names(weeks)

  today = date.today()
  end_date = today - relativedelta(weeks=weeks-1)
  debitBaseFilters = get_base_filters_by_week(end_date, weeks)
  creditBaseFilters = get_base_filters_by_week(end_date, weeks) # Same as debit however it could add more filters and references in future
  debitLines = get_data_lines(accounts, debitBaseFilters, 'debitAccount__id')
  creditLines = get_data_lines(accounts, creditBaseFilters, 'creditAccount__id')

  return labels, debitLines, creditLines

def get_base_filters_by_week(end_date, num_weeks):
  dataRaws = []
  for i in range(num_weeks):
    first_date = end_date

    start_date = first_date
    # Calculate the end of the current week in the loop (Sunday)
    end_date = start_date + timedelta(days=7)

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

def get_week_of_month(date_obj):
    """
    Calculates the week number of a given date within its respective month.
    """
    # Get the first day of the month
    first_day_of_month = date_obj.replace(day=1)

    # Get the ISO week number for the given date and the first day of the month
    iso_week_current_date = date_obj.isocalendar()[1]
    iso_week_first_day = first_day_of_month.isocalendar()[1]

    # Calculate the week number within the month
    # This accounts for cases where the first day of the month might be in the
    # last week of the previous ISO year, or the given date is in a later ISO year
    if iso_week_current_date < iso_week_first_day:
        # This handles cases where the current date's week number wraps around
        # to a lower number in the new ISO year, even if it's later in the month.
        # We need to consider the total number of ISO weeks in the previous year
        # to get an accurate week number within the current month.
        # For simplicity, we assume a standard year here; more robust solutions
        # might involve checking the year of iso_week_first_day.
        return iso_week_current_date + (52 - iso_week_first_day) + 1
    else:
        return iso_week_current_date - iso_week_first_day + 1

def get_base_filters_by_day(end_date, days):
  dataRaws = []
  for i in range(days):
    first_date = end_date

    start_date = first_date
    # Calculate the end of the current week in the loop (Sunday)
    end_date = start_date + timedelta(days=1)

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

def get_data_by_day(days, accounts):
  labels = get_last_n_day_names(days)

  today = date.today()
  end_date = today - relativedelta(days=days-1)
  debitBaseFilters = get_base_filters_by_day(end_date, days)
  creditBaseFilters = get_base_filters_by_day(end_date, days) # Same as debit however it could add more filters and references in future
  debitLines = get_data_lines(accounts, debitBaseFilters, 'debitAccount__id')
  creditLines = get_data_lines(accounts, creditBaseFilters, 'creditAccount__id')

  return labels, debitLines, creditLines

def get_last_n_day_names(n):
  today = datetime.now()
  day_names = []
  for i in range(7):
      # Calculate the date for each of the last 7 days
      current_date = today - timedelta(days=i)
      # Format the date to get the full weekday name
      day_name = current_date.strftime('%A')
      # Add the day name to the beginning of the list to maintain chronological order (last day first)
      day_names.insert(0, day_name)
  return day_names
