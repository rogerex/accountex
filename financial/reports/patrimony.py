from datetime import datetime
from django.db import connection
from django.shortcuts import render
from financial.models import Currency
from financial.reports.patrimoning.models import CurrencyPatrimony, PatrimonyRow, CurrencyTagGroups, TagGroup
from financial.reports.patrimoning.assets import calculate_assets


def execute_patrimony_raw_sql(request):
  activeTab = request.GET.get('tab', 1)

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
    ac.account_type_id IN (1, 2, 3, 9)
GROUP BY
    b.account_id, b.account_name
ORDER BY b.account_name
                   """)
    rows = cursor.fetchall()

  rawRows = []
  for row in rows:
      obj = PatrimonyRow(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
      rawRows.append(obj)

  deletedRows = []
  patrimonyRows = []
  for row in rawRows:
      if row.account_name.startswith('ZZ -') and row.saldo == 0:
          deletedRows.append(row)
      else:
          patrimonyRows.append(row)

  dataCurrencies = []
  currencies = Currency.objects.all()
  for currency in currencies:
      dataCurrency = CurrencyPatrimony(currency)
      for row in patrimonyRows:
          if row.currencyId == currency.id:
              dataCurrency.rows.append(row)

      dataCurrencies.append(dataCurrency)

  tagGroups = __tag_accounts()

  currencyTagGroups = []
  rowsInTagGroups = []
  for dataCurrency in dataCurrencies:
      currencyTagGroup = CurrencyTagGroups(dataCurrency.currency)
      for tagGroup in tagGroups:
          tg = TagGroup(tagGroup['name'], tagGroup['prefixs'])
          for row in dataCurrency.rows:
              for prefix in tagGroup['prefixs']:
                  if row.account_name.startswith(prefix):
                      tg.rows.append(row)
                      rowsInTagGroups.append(row)
                      tg.total += row.saldo
                      break

          currencyTagGroup.tagGroups.append(tg)
          currencyTagGroup.total += tg.total
      currencyTagGroups.append(currencyTagGroup)

  ignoredRows = []
  for row in patrimonyRows:
      if row not in rowsInTagGroups:
          ignoredRows.append(row)

  viewCurrencyTagGroups = []
  for currencyTagGroup in currencyTagGroups:
      viewCurrencyTagGroup = CurrencyTagGroups(currencyTagGroup.currency)

      for tagGroup in currencyTagGroup.tagGroups:
          tagGroup.percentage = tagGroup.total / currencyTagGroup.total * 100
          if len(tagGroup.rows) > 0 and tagGroup.total != 0:
              viewCurrencyTagGroup.tagGroups.append(tagGroup)
              viewCurrencyTagGroup.total += tagGroup.total

      if len(viewCurrencyTagGroup.tagGroups) > 0 and viewCurrencyTagGroup.total != 0:
          viewCurrencyTagGroups.append(viewCurrencyTagGroup)

  # Assets Groups
  currencyAssetsGroups, assetRows = calculate_assets(dataCurrencies)

  context = {
      'rows': patrimonyRows,
      'deletedRows': deletedRows,
      'ignoredRows': ignoredRows,

      'currencyTagGroups': currencyTagGroups,
      'viewCurrencyTagGroups': viewCurrencyTagGroups,
      'assetsGroups': currencyAssetsGroups,
      'assetRows': sorted(assetRows, key=lambda p: p.account_name),

      'datetime': datetime.today(),
      'activeTab': int(activeTab),
  }

  # pdb.set_trace()
  return render(request, 'reports/patrimony.html', context)

def __tag_accounts():
  return [
      {
          'name': 'Artefactos',
          'prefixs': ['Artefactos', 'Z - Depreciacion Acumulada de Artefactos'],
      },
      {
          'name': 'Bancos',
          'prefixs': ['Banco', 'BCP'],
      },
      {
          'name': 'Ahorro',
          'prefixs': ['Caja Ahorro', 'Caja P2P'],
      },
      {
          'name': 'Efectivo',
          'prefixs': ['Caja Chica', 'Caja Billetera'],
      },
      {
          'name': 'Departamentos',
          'prefixs': ['Departamento'],
      },
      {
          'name': 'Deudas',
          'prefixs': ['Deuda por cobrar'],
      },
      {
          'name': 'Equipos Electronicos',
          'prefixs': ['EE', 'Z - Depreciacion Acumulada de Equipos Electronicos'],
      },
      {
          'name': 'Entretenimientos',
          'prefixs': ['Entretenimiento'],
      },
      {
          'name': 'Fondo de Emergencias',
          'prefixs': ['FE -'],
      },
      {
          'name': 'Garantias',
          'prefixs': ['Garantia'],
      },
      {
          'name': 'Especulaciones - Cryptos',
          'prefixs': ['Inversiones - Crypto', 'Z - Inversiones - Crypto'],
      },
      {
          'name': 'Inversiones - Brokers',
          'prefixs': ['Inversiones - Broker:', 'Z - Inversiones - Broker:'],
      },
      {
          'name': 'Impuesto a las transacciones',
          'prefixs': ['IT'],
      },
      {
          'name': 'Muebles',
          'prefixs': ['Muebles', 'Z - Depreciacion Acumulada de Muebles'],
      },
      {
          'name': 'Ropa',
          'prefixs': ['Ropa', 'Z - Depreciacion Acumulada de Ropa'],
      },
      {
          'name': 'Vehiculos',
          'prefixs': ['Vehiculo:', 'Z - Depreciacion Acumulada de Vehiculo'],
      },
      {
          'name': 'Zapatillas',
          'prefixs': ['Zapatillas', 'Z - Depreciacion Acumulada de Zapatillas'],
      },
  ]
