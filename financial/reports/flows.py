from datetime import datetime
from django.db import connection
from django.shortcuts import render
from financial.reports.models.shared import AccountRow
from financial.reports.shared.grouping import build_groups

def execute_flows_raw_sql(request):
  activeTab = request.GET.get('tab', 2)
  activeYear = request.GET.get('year', datetime.today().year)

  rawOutRows = __execute_out_raw_sql(activeYear)
  tagGroups = __tag_accounts()

  filteredOutRows, deletedOutRows, ignoredOutRows, currencyTagGroups, viewCurrencyTagGroups, dataCurrencies = build_groups(rawOutRows, tagGroups)

  rawInRows = __execute_in_raw_sql(activeYear)
  inRows = []
  for rawRow in rawInRows:
      obj = AccountRow(rawRow[0], rawRow[1], rawRow[2], rawRow[3], rawRow[4], rawRow[5], rawRow[6])
      inRows.append(obj)

  context = {
    'outRows': filteredOutRows,
    'deletedOutRows': deletedOutRows,
    'ignoredOutRows': ignoredOutRows,

    'currencyTagGroups': currencyTagGroups,
    'viewCurrencyTagGroups': viewCurrencyTagGroups,

    'inRows': inRows,

    'datetime': datetime.today(),
    'activeTab': int(activeTab),
    'activeYear': int(activeYear),
    'allowedYears': range(2010, datetime.today().year + 1),
  }

  return render(request, 'reports/flows.html', context)

def __execute_out_raw_sql(selectedYear):
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
    + (f" AND YEAR(s.seat_datetime) = {selectedYear} " if int(selectedYear) > 0 else "") +
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
      'prefixs': ['Pareja', 'Mireya', 'ZZ - Deprecated - Abigail'],
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

def __execute_in_raw_sql(selectedYear):
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
    + (f" AND YEAR(s.seat_datetime) = {selectedYear} " if int(selectedYear) > 0 else "") +
"""
GROUP BY
    b.account_id, b.account_name
ORDER BY b.account_name
                   """)
    rows = cursor.fetchall()
    return rows