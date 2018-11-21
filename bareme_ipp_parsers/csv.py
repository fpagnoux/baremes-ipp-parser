#!/usr/bin/env python

EUR_TO_FRF = 6.55957

import csv
from functools import reduce
from openfisca_core.periods import period, MONTH

def groupby(collection, function):
  result = {}
  for item in collection:
    key = function(item)
    if result.get(key):
      result[key].append(item)
    else:
      result[key] = [item]

  return result


def extract_dates_from_list(collection):
  return reduce(
    lambda dates, param: dates.union((value.instant_str for value in param.values_list)),
    collection,
    set()
    )

def extract_dates(csv_params):
  return sorted(reduce(
    lambda dates, param: dates.union((value.instant_str for value in param.values_list)),
    csv_params.values(),
    set()
    ))


def unit_at(param, date):
  unit_by_date = param.metadata['unit']
  if isinstance(unit_by_date, str):
    return unit_by_date
  unit_date =  max({u_date for (u_date, unit) in unit_by_date.items() if u_date <= str(date.start)})
  return unit_by_date[unit_date]

def value_in_euro(param, date):
  value = param.get_at_instant(date)
  if not value:
    return value
  if not param.metadata.get('unit'):
    return value
  unit = unit_at(param, date)
  if unit == 'currency-FRF':
    return round(value / EUR_TO_FRF, 2)
  if unit == 'currency-AFRF':
    return round(value / (EUR_TO_FRF * 100), 2)
  return value

def get_row(csv_params, date):
  result = {'date': date}
  result.update({
    key: value_in_euro(param, date)
    for (key, param) in csv_params.items()
  })
  return result

def check_for_doublons(node):
  csv_params = [
    param
    for param in node.get_descendants()
    if param.metadata.get('ipp_csv_id')
    ]
  csv_params = groupby(csv_params, lambda param: param.metadata['ipp_csv_id'])
  doublons = {}
  for csv_key, params in csv_params.items():
    if len(params) == 1:
      continue
    doublons[csv_key] = []
    for param in params:
      doublons[csv_key].append(param.name)

  if not doublons:
    return

  print(f'{node.name}:')
  for csv_key, param_names in doublons.items():
    print(f'  {csv_key}:')
    for param in param_names:
      print(f'    {param}')
  print()

def export_node_to_csv(node, output_dir):

  check_for_doublons(node)

  csv_params = {
    param.metadata['ipp_csv_id']: param
    for param in node.get_descendants()
    if param.metadata.get('ipp_csv_id')
    }

  all_dates = extract_dates(csv_params)
  first_month = period(f"{all_dates[0].split('-')[0]}-01")
  last_month = period("2018-12")

  with open(f'{output_dir}/{node.name}.csv', mode='w') as csv_file:
      fieldnames = ['date'] + list(csv_params.keys())
      writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
      writer.writeheader()
      current_month = first_month
      while current_month <= last_month:
        writer.writerow(get_row(csv_params, current_month))
        current_month = current_month.offset(1, MONTH)
