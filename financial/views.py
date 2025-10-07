from datetime import datetime
from django.db import connection
from django.shortcuts import render
from financial.models import Currency

class PatrimonyRow:
    def __init__(self, account_id, account_name, debit, credit, saldo, currencyId, currencySymbol):
        self.account_id = account_id
        self.account_name = account_name
        self.debit = debit
        self.credit = credit
        self.saldo = saldo
        self.currencyId = currencyId
        self.currencySymbol = currencySymbol

class CurrencyPatrimony:
    def __init__(self, currency):
        self.currency = currency
        self.rows = []

class TagGroup:
    def __init__(self, name, prefixs):
        self.name = name
        self.prefixs = prefixs
        self.rows = []
        self.total = 0
        self.percentage = 0

class CurrencyTagGroups:
    def __init__(self, currency):
        self.currency = currency
        self.tagGroups = []
        self.total = 0

def execute_patrimony_raw_sql(request):

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

  tagGroups = [
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

  assetsTags = [
      {
          'name': 'Cryptos',
          'prefixs': ['Inversiones - Crypto', 'Z - Inversiones - Crypto'],
          'currencyId': 2,
      },
      {
          'name': 'IBKR',
          'prefixs': ['Inversiones - Broker: IB', 'Z - Inversiones - Broker: IB'],
          'currencyId': 2,
      },
      {
          'name': 'Hapi',
          'prefixs': ['Inversiones - Broker: Hapi', 'Z - Inversiones - Broker: Hapi'],
          'currencyId': 2,
      },
  ]

  currencyAssetsGroups = []
  for dataCurrency in dataCurrencies:
      currencyTagGroup = CurrencyTagGroups(dataCurrency.currency)
      for tagGroup in assetsTags:
          tg = TagGroup(tagGroup['name'], tagGroup['prefixs'])
          for row in dataCurrency.rows:
              for prefix in tagGroup['prefixs']:
                  if row.account_name.startswith(prefix):
                      tg.rows.append(row)
                      tg.total += row.saldo
                      break

          currencyTagGroup.tagGroups.append(tg)
          currencyTagGroup.total += tg.total

      if currencyTagGroup.total != 0 and len(currencyTagGroup.tagGroups) > 0:
          currencyAssetsGroups.append(currencyTagGroup)

  for currencyAssetsGroup in currencyAssetsGroups:
      for tagGroup in currencyAssetsGroup.tagGroups:
          if currencyAssetsGroup.total != 0:
              tagGroup.percentage = tagGroup.total / currencyAssetsGroup.total * 100

  context = {
      'rows': patrimonyRows,
      'datetime': datetime.today(),
      'deletedRows': deletedRows,
      'ignoredRows': ignoredRows,
      'currencyTagGroups': currencyTagGroups,
      'viewCurrencyTagGroups': viewCurrencyTagGroups,
      'assetsGroups': currencyAssetsGroups,
  }

  # pdb.set_trace()
  return render(request, 'reports/patrimony.html', context)