from financial.models import Currency
from financial.reports.models.shared import CurrencyAccountList, AccountRow, CurrencyTagGroups, TagGroup

def build_groups(rawRows, tagGroups):
  allRows = []
  for rawRow in rawRows:
      obj = AccountRow(rawRow[0], rawRow[1], rawRow[2], rawRow[3], rawRow[4], rawRow[5], rawRow[6])
      allRows.append(obj)

  deletedRows = []
  filteredRows = []
  for row in allRows:
      if row.account_name.startswith('ZZ -') and row.saldo == 0:
          deletedRows.append(row)
      else:
          filteredRows.append(row)

  dataCurrencies = []
  currencies = Currency.objects.all()
  for currency in currencies:
      dataCurrency = CurrencyAccountList(currency)
      for row in filteredRows:
          if row.currencyId == currency.id:
              dataCurrency.rows.append(row)

      dataCurrencies.append(dataCurrency)

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
  for row in filteredRows:
      if row not in rowsInTagGroups:
          ignoredRows.append(row)

  viewCurrencyTagGroups = []
  for currencyTagGroup in currencyTagGroups:
      viewCurrencyTagGroup = CurrencyTagGroups(currencyTagGroup.currency)

      for tagGroup in currencyTagGroup.tagGroups:
          tagGroup.percentage = tagGroup.total / currencyTagGroup.total * 100 if currencyTagGroup.total != 0 else 1
          if len(tagGroup.rows) > 0 and tagGroup.total != 0:
              viewCurrencyTagGroup.tagGroups.append(tagGroup)
              viewCurrencyTagGroup.total += tagGroup.total

      if len(viewCurrencyTagGroup.tagGroups) > 0 and viewCurrencyTagGroup.total != 0:
          viewCurrencyTagGroups.append(viewCurrencyTagGroup)

  return filteredRows, deletedRows, ignoredRows, currencyTagGroups, viewCurrencyTagGroups, dataCurrencies