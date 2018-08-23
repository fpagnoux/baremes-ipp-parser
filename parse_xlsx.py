#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import openpyxl
import argparse
import os
import shutil
import logging
import glob

from bareme_ipp_parsers.workbook import parse_workbook


NODE_MAP = {
  'baremes-ipp-prelevements-sociaux-social-security-contributions.xlsx': 'prelevements_sociaux',
  # 'baremes-ipp-impot-revenu-income-tax.xlsx': 'impot_revenu',
  'baremes-ipp-taxation-capital.xlsx': 'taxation_capital'
  }


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_path', help = 'XLSX file or directory to convert to YAML parameters')
  argparser.add_argument('output_dir', help = 'Output directory')
  argparser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
  args = argparser.parse_args()

  logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING)

  xlsx_path = args.xlsx_path

  if os.path.isdir(xlsx_path):
    xlsx_files = glob.glob(os.path.join(xlsx_path, "*.xlsx"))
  else:
    xlsx_files = [xlsx_path]

  for file_path in xlsx_files:
    file_name = os.path.basename(file_path)
    if file_name not in NODE_MAP:
      continue
    wb = openpyxl.load_workbook(file_path, data_only = True)
    directory = os.path.join(args.output_dir, NODE_MAP[file_name])
    if os.path.isdir(directory):
      shutil.rmtree(directory)
    os.makedirs(directory)
    parse_workbook(wb, directory)


if __name__ == "__main__":
    main()
