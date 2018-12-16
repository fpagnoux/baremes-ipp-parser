#!/usr/bin/env python

import glob
import os
import csv
import logging

import pandas as pd
import numpy as np

from ruamel.yaml import YAML
yaml=YAML(typ='safe')

with open("config.yaml") as yaml_file:
  sheets = yaml.load(yaml_file)

log = logging.getLogger('Comparator')
logging.basicConfig(level = logging.DEBUG if False else logging.WARNING)

CSV_GENERATED = '../csv-parsed'
CSV_SOURCE = '../csv'

csv_sources = glob.glob(os.path.join(CSV_SOURCE, "*.csv"))

# def read_csv(path):
#   with open(path, 'r') as f:
#     reader = csv.DictReader(f)
#     return [row for row in reader]

def compare_headers(src, dst):
  src_keys = set(src.keys())
  dst_keys = set(dst.keys())
  src_not_dst = src_keys.difference(dst_keys)
  if src_not_dst:
    print(f'  keys_missing_from_new_file:')
    for key in src_not_dst:
      print(f'    - {key}')
  dst_not_src = dst_keys.difference(src_keys)
  # if dst_not_src:
  #   print(f'  warning: Keys {dst_not_src} are present in the new CSV files, but not in the old')

  return src_keys.intersection(dst_keys)

def compare_values(src, dst, dates, dates_2):
  try:
    is_equal = np.isnan(src) & np.isnan(dst) | (np.round_(dst, 2) == np.round_(src, 2))
  except:
    is_equal = src == dst
  if not is_equal.all():
    first_different_value_idx = np.where(np.logical_not(is_equal))[0][0]
    date = dates[first_different_value_idx]
    src_value = src[first_different_value_idx]
    dst_value = dst[first_different_value_idx]
    print(f'    {src.name}:')
    print(f'      date: {date}')
    print(f'      old_value: {src_value}')
    print(f'      new_value: {dst_value}')

for src_path in csv_sources:
  src_name = os.path.basename(src_path).replace('.csv', '')
  dst_name = sheets[src_name + '.xlsx']['name']
  dst_path = os.path.join(CSV_GENERATED, dst_name + '.csv')
  print(f'{dst_name}:')

  dst_csv = pd.read_csv(dst_path)
  src_csv = pd.read_csv(src_path)

  keys_to_compare = compare_headers(src_csv, dst_csv)

  if len(src_csv.date) != len(dst_csv.date):
    print(f'  error: new csv has {len(dst_csv.date)} rows while old csv had {len(src_csv.date)}.')
    continue

  print(f'  values_difference:')
  for key in keys_to_compare:
    compare_values(src_csv[key], dst_csv[key], src_csv.date, dst_csv.date)

