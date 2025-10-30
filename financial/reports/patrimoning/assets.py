from datetime import datetime, timedelta
from financial.models import SeatDetail
from django.db.models import Sum
from financial.reports.patrimoning.models import AssetRow
from financial.reports.models.shared import CurrencyTagGroups, TagGroup

def __tag_assets():
  return [
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

def calculate_assets(accountsByCurrencyList):
  assetsTags = __tag_assets()

  assetRows = []
  currencyAssetsGroups = []
  for accountsByCurrency in accountsByCurrencyList:
      currencyTagGroup = CurrencyTagGroups(accountsByCurrency.currency)
      for tagGroup in assetsTags:
          tg = TagGroup(tagGroup['name'], tagGroup['prefixs'])
          for row in accountsByCurrency.rows:
              for prefix in tagGroup['prefixs']:
                  if row.account_name.startswith(prefix):
                      tg.rows.append(row)
                      tg.total += row.saldo
                      assetRows.append(__calculate_asset_totals(row))
                      break

          currencyTagGroup.tagGroups.append(tg)
          currencyTagGroup.total += tg.total

      if currencyTagGroup.total != 0 and len(currencyTagGroup.tagGroups) > 0:
          currencyAssetsGroups.append(currencyTagGroup)

  for currencyAssetsGroup in currencyAssetsGroups:
      for tagGroup in currencyAssetsGroup.tagGroups:
          if currencyAssetsGroup.total != 0:
              tagGroup.percentage = tagGroup.total / currencyAssetsGroup.total * 100

  return currencyAssetsGroups, assetRows

def __calculate_asset_totals(patrimonyRow):
    row = AssetRow(patrimonyRow)

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

    #YTD
    start_date = datetime(year, 1, 1, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)
    row.total_ytd = __calculate_total(start_date, end_date, row.account_id)

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