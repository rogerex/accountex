from datetime import datetime
from django.db import connection
from django.shortcuts import render
from datetime import datetime, timedelta
from financial.models import Currency, SeatDetail
from django.db.models import Sum
from financial.reports.flowing.models import OutReportRow
from financial.reports.models.shared import AccountRow
from financial.reports.shared.grouping import build_groups

def execute_flows_raw_sql(request):
  activeTab = request.GET.get('tab', 2)
  activeYears = [int(year) for year in request.GET.getlist('year')] or [datetime.today().year]

  rawOutRows = __execute_out_raw_sql(activeYears)
  tagGroups = __tag_accounts()

  filteredOutRows, deletedOutRows, ignoredOutRows, currencyTagGroups, viewCurrencyTagGroups, dataCurrencies = build_groups(rawOutRows, tagGroups)

  isThisYear = activeYears == [datetime.today().year]
  if isThisYear:
    filteredOutRows = [__calculate_asset_totals(item) for item in filteredOutRows]

  rawInRows = __execute_in_raw_sql(activeYears)
  inRows = []
  for rawRow in rawInRows:
      obj = AccountRow(rawRow[0], rawRow[1], rawRow[2], rawRow[3], rawRow[4], rawRow[5], rawRow[6])
      inRows.append(obj)

  currencies = Currency.objects.all()
  summaryOutTotals = []
  summaryInTotals = []
  for currency in currencies:
    summaryInTotals.append({
      'currency': currency,
      'total': sum(item.saldo for item in list(filter(lambda n: n.currencyId==currency.id, inRows)))
    })
    summaryOutTotals.append({
      'currency': currency,
      'total': sum(item.saldo for item in list(filter(lambda n: n.currencyId==currency.id, filteredOutRows)))
    })

  context = {
    'outRows': filteredOutRows,
    'deletedOutRows': deletedOutRows,
    'ignoredOutRows': ignoredOutRows,
    'summaryOutTotals': summaryOutTotals,

    'currencyTagGroups': currencyTagGroups,
    'viewCurrencyTagGroups': viewCurrencyTagGroups,

    'inRows': inRows,
    'summaryInTotals': summaryInTotals,

    'datetime': datetime.today(),
    'activeTab': int(activeTab),
    'activeYears': activeYears,
    'allowedYears': range(2010, datetime.today().year + 1),
    'isCurrentYear': isThisYear,
  }

  return render(request, 'reports/flows.html', context)

def __execute_out_raw_sql(selectedYears):
  with connection.cursor() as cursor:

    cursor.execute("""
SELECT b.account_id, b.account_name, SUM(b.debit) AS debit, SUM(b.credit) AS credit, SUM(b.debit) - SUM(b.credit) AS saldo, ac.currency_id, c.currency_symbol FROM
(
SELECT a.account_id, a.account_name, SUM(seat_detail_mount) AS debit, 0 AS credit, sd.seat_id FROM account a 
INNER JOIN seat_detail sd ON sd.account_debit_id = a.account_id
GROUP BY account_id, account_name, sd.seat_id
UNION ALL
SELECT a.account_id, a.account_name, 0 AS debit, SUM(seat_detail_mount) AS credit, sd.seat_id FROM account a 
INNER JOIN seat_detail sd ON sd.account_credit_id = a.account_id
GROUP BY account_id, account_name, sd.seat_id
) as b
INNER JOIN seat s ON s.seat_id = b.seat_id
INNER JOIN diary_book db ON db.diary_book_id = s.diary_book_id
INNER JOIN account ac ON ac.account_id = b.account_id
INNER JOIN currency c ON c.currency_id = ac.currency_id
WHERE
    ac.account_type_id IN (6, 8, 10)
"""
    + (f" AND YEAR(s.seat_datetime) IN ({','.join(str(year) for year in selectedYears)}) " if 0 not in selectedYears else "") +
"""
GROUP BY
    b.account_id, b.account_name
ORDER BY b.account_name
                   """)
    rows = cursor.fetchall()
    return rows

def __tag_accounts():
  return [
    {
      'name': 'Comisiones',
      'prefixs': ['Comisiones', 'ZZ - Deprecated - Comisiones -'],
    },
    {
      'name': 'Depreciacion',
      'prefixs': ['Depreciacion'],
    },
    {
      'name': 'Varios',
      'prefixs': ['Dinero Perdido', 'Perdida por tipo de cambio', 'ZZ Seguro Vitalicia', 'ZZ - AFP'],
    },
    {
      'name': 'Egresos',
      'prefixs': ['Egreso:'],
    },
    {
      'name': 'Familia',
      'prefixs': ['Familia -'],
    },
    {
      'name': 'Gastos',
      'prefixs': ['Gasto:'],
    },
    {
      'name': 'Impuestos',
      'prefixs': ['Impuestos'],
    },
    {
      'name': 'Mascotas',
      'prefixs': ['Mascotas:'],
    },
    {
      'name': 'Especiales',
      'prefixs': ['Pareja', 'Mireya', 'ZZ - Deprecated - Abigail', 'ZZ - Deprecated - Mireya'],
    },
    {
      'name': 'Regalos',
      'prefixs': ['Regalos'],
    },
    {
      'name': 'Salud',
      'prefixs': ['Salud -'],
    },
    {
      'name': 'Servicios Basicos',
      'prefixs': ['Servicios:'],
    },
    {
      'name': 'Viajes',
      'prefixs': ['Viajes'],
    },
    {
      'name': 'Xitas',
      'prefixs': ['Xitas', 'ZZ - Deprecated - Xitas:'],
    },
  ]

def __execute_in_raw_sql(selectedYears):
  with connection.cursor() as cursor:

    cursor.execute("""
SELECT b.account_id, b.account_name, SUM(b.debit) AS debit, SUM(b.credit) AS credit, SUM(b.credit) - SUM(b.debit) AS saldo, ac.currency_id, c.currency_symbol FROM
(
SELECT a.account_id, a.account_name, SUM(seat_detail_mount) AS debit, 0 AS credit, sd.seat_id FROM account a 
INNER JOIN seat_detail sd ON sd.account_debit_id = a.account_id
GROUP BY account_id, account_name, sd.seat_id
UNION ALL
SELECT a.account_id, a.account_name, 0 AS debit, SUM(seat_detail_mount) AS credit, sd.seat_id FROM account a 
INNER JOIN seat_detail sd ON sd.account_credit_id = a.account_id
GROUP BY account_id, account_name, sd.seat_id
) as b
INNER JOIN seat s ON s.seat_id = b.seat_id
INNER JOIN diary_book db ON db.diary_book_id = s.diary_book_id
INNER JOIN account ac ON ac.account_id = b.account_id
INNER JOIN currency c ON c.currency_id = ac.currency_id
WHERE
    ac.account_type_id IN (4, 5, 11)
"""
    + (f" AND YEAR(s.seat_datetime) IN ({','.join(str(year) for year in selectedYears)}) " if 0 not in selectedYears else "") +
"""
GROUP BY
    b.account_id, b.account_name
ORDER BY b.account_name
                   """)
    rows = cursor.fetchall()
    return rows
  
def __calculate_asset_totals(patrimonyRow):
    row = OutReportRow(patrimonyRow)

    current_datetime = datetime.today()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day

    #Today
    start_date = datetime(year, month, day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_today = __calculate_total(start_date, end_date, row.account_id)

    #MTD
    start_date = datetime(year, month, 1, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_mtd = __calculate_total(start_date, end_date, row.account_id)

    #Last year
    start_date = datetime(year - 1, month, day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_last_365_days = __calculate_total(start_date, end_date, row.account_id)

    #Last 30 days
    days_ago_30 = current_datetime - timedelta(days=30)
    start_date = datetime(days_ago_30.year, days_ago_30.month, days_ago_30.day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_last_30_days = __calculate_total(start_date, end_date, row.account_id)

    #Last 3 months
    months_ago_3 = current_datetime - timedelta(days=90)
    start_date = datetime(months_ago_3.year, months_ago_3.month, months_ago_3.day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_last_3_months = __calculate_total(start_date, end_date, row.account_id)

    #Last 6 months
    months_ago_6 = current_datetime - timedelta(days=180)
    start_date = datetime(months_ago_6.year, months_ago_6.month, months_ago_6.day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_last_6_months = __calculate_total(start_date, end_date, row.account_id)

    return row

def __calculate_total(start_date, end_date, account_id):
    debitTotal = SeatDetail.objects.filter(debitAccount__id=account_id, seat__datetime__gte=start_date, seat__datetime__lte=end_date).aggregate(total=Sum('mount'))
    creditTotal = SeatDetail.objects.filter(creditAccount__id=account_id, seat__datetime__gte=start_date, seat__datetime__lte=end_date).aggregate(total=Sum('mount'))

    total = (debitTotal['total'] if debitTotal and debitTotal['total'] else 0) - (creditTotal['total'] if creditTotal and creditTotal['total'] else 0)
    return total