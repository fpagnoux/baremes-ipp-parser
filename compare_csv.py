#!/usr/bin/env python

import glob
import os
import csv
import logging

from ruamel.yaml import YAML
yaml=YAML(typ='safe')

with open("config.yaml") as yaml_file:
  sheets = yaml.load(yaml_file)

log = logging.getLogger('Comparator')
logging.basicConfig(level = logging.DEBUG if False else logging.WARNING)

CSV_GENERATED = '../csv-parsed'
CSV_SOURCE = '../csv'

csv_sources = glob.glob(os.path.join(CSV_SOURCE, "*.csv"))

def read_csv(path):
  with open(path, 'r') as f:
    reader = csv.DictReader(f)
    return [row for row in reader]

def compare_headers(src, dst):
  src_keys = set(src[0].keys())
  dst_keys = set(dst[0].keys())
  src_not_dst = src_keys.difference(dst_keys)
  if src_not_dst:
    log.error(f"Keys {src_not_dst} are present in the source CSV, but not in the destination")
  dst_not_src = dst_keys.difference(src_keys)
  if dst_not_src:
    log.warning(f"Keys {dst_not_src} are present in the destination CSV, but not in the source")

  return src_keys.intersection(dst_keys)

def compare_dicts(src, dst, keys_to_compare):
  pass
  # assert src['date'] == dst['date']
  # for key in keys_to_compare:
  #   try:
  #     round(float(src[key]), 2)
  #     round(float(dst[key]), 2)
  #   except:
  #     from nose.tools import set_trace; set_trace(); import ipdb; ipdb.set_trace()
  #   if round(float(src[key]), 2) != round(float(dst[key]), 2):
  #     print(f"Value difference: for {src['date']} for {key}: {src[key]} vs {dst[key]}'")



for src_path in csv_sources:
  src_name = os.path.basename(src_path).replace('.csv', '')
  dst_name = sheets[src_name + '.xlsx']['name']
  dst_path = os.path.join(CSV_GENERATED, dst_name + '.csv')

  dst_csv = read_csv(dst_path)
  src_csv = read_csv(src_path)

  log.info(f"Comparing {src_path} and {dst_path}")
  keys_to_compare = compare_headers(src_csv, dst_csv)

  for src_row, dst_row in zip(src_csv, dst_csv):
    compare_dicts(src_row, dst_row, keys_to_compare)
