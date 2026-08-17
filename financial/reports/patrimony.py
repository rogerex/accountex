from datetime import datetime
from django.db import connection
from django.shortcuts import render
from financial.reports.patrimoning.assets import calculate_assets
from financial.reports.shared.grouping import build_groups

def execute_patrimony_raw_sql(request):
  activeTab = request.GET.get('tab', 2)

  rawRows = __execute_raw_sql()
  tagGroups = __tag_accounts()

  filteredRows, deletedRows, ignoredRows, currencyTagGroups, viewCurrencyTagGroups, dataCurrencies = build_groups(rawRows, tagGroups)

  # Assets Groups
  currencyAssetsGroups, assetRows = calculate_assets(dataCurrencies)

  context = {
      'rows': filteredRows,
      'deletedRows': deletedRows,
      'ignoredRows': ignoredRows,
      'currency_matrix': __build_currency_matrix(viewCurrencyTagGroups),

      'currencyTagGroups': currencyTagGroups,
      'viewCurrencyTagGroups': viewCurrencyTagGroups,
      'assetsGroups': currencyAssetsGroups,
      'assetRows': sorted(assetRows, key=lambda p: p.account_name),

      'datetime': datetime.today(),
      'activeTab': int(activeTab),
  }

  # pdb.set_trace()
  return render(request, 'reports/patrimony.html', context)

def __execute_raw_sql():
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
    ac.account_type_id IN (1, 2, 3, 4, 5, 9)
GROUP BY
    b.account_id, b.account_name
ORDER BY b.account_name
                   """)
    rows = cursor.fetchall()
    return rows

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
          'name': 'Devices',
          'prefixs': ['Devices', 'Z - Depreciacion Acumulada de Devices'],
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

_CONVERSION_RATES = {
    ('USD', 'USD', 'Oficial'):   1.0,
    ('USD', 'USD', 'Paralelo'):  1.0,
    ('BOB', 'BOB', 'Oficial'):   1.0,
    ('BOB', 'BOB', 'Paralelo'):  1.0,
    ('USD', 'BOB', 'Oficial'):   6.86,
    ('USD', 'BOB', 'Paralelo'):  11.54,
    ('BOB', 'USD', 'Oficial'):   1 / 6.86,
    ('BOB', 'USD', 'Paralelo'):  1 / 11.54,
}

def __build_currency_matrix(viewCurrencyTagGroups):
    # One column per (target_currency × rate_type)
    columns = []
    for target_group in viewCurrencyTagGroups:
        for rate_label in ['Oficial', 'Paralelo']:
            columns.append({
                'header': f"{target_group.currency.symbol} ({rate_label})",
                'target_code': target_group.currency.code,
                'target_symbol': target_group.currency.symbol,
                'rate_label': rate_label,
            })

    col_totals = [0.0] * len(columns)
    rows = []
    for source_group in viewCurrencyTagGroups:
        source_code = source_group.currency.code
        source_total = source_group.total
        cells = []
        for i, col in enumerate(columns):
            rate = _CONVERSION_RATES.get((source_code, col['target_code'], col['rate_label']))
            value = round(source_total * rate, 2) if rate is not None else None
            if value is not None:
                col_totals[i] += value
            cells.append({'symbol': col['target_symbol'], 'value': value})

        rows.append({
            'source_symbol': source_group.currency.symbol,
            'source_total': round(source_total, 2),
            'cells': cells,
        })

    total_cells = [
        {'symbol': col['target_symbol'], 'value': round(col_totals[i], 2)}
        for i, col in enumerate(columns)
    ]

    return {'columns': columns, 'rows': rows, 'total_cells': total_cells}
