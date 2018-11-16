#!/usr/bin/env python

import argparse
import csv
import logging
from functools import reduce

from openfisca_core.periods import period, MONTH

from openfisca_baremes_ipp import CountryTaxBenefitSystem
tbs = CountryTaxBenefitSystem()

log = logging.getLogger(__name__)


def extract_dates(csv_params):
  return sorted(reduce(
    lambda dates, param: dates.union((value.instant_str for value in param.values_list)),
    csv_params.values(),
    set()
    ))

def get_row(csv_params, date):
  result = {'date': date}
  result.update({
    key: param.get_at_instant(date)
    for (key, param) in csv_params.items()
  })
  return result


def export_node_to_csv(node):
  csv_params = {
  param.metadata['ipp_csv_id']: param
  for param in node.get_descendants()
  if param.metadata.get('ipp_csv_id')
  }

  all_dates = extract_dates(csv_params)
  first_month = period(f"{all_dates[0].split('-')[0]}-01")
  last_month = period("2018-12")

  with open(f'csv/{node.name}.csv', mode='w') as csv_file:
      fieldnames = ['date'] + list(csv_params.keys())
      writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
      writer.writeheader()
      current_month = first_month
      while current_month <= last_month:
        writer.writerow(get_row(csv_params, current_month))
        current_month = current_month.offset(1, MONTH)


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
  args = argparser.parse_args()

  logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING)

  for node in tbs.parameters.children.values():
    export_node_to_csv(node)


if __name__ == "__main__":
    main()
