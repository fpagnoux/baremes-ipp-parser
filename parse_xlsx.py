#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import openpyxl
import argparse
import os
import shutil

from parsers.workbook import parse_workbook

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_MAP = {
  'baremes-ipp-prelevements-sociaux-social-security-contributions.xlsx': 'prelevements_sociaux',
  'baremes-ipp-impot-revenu-income-tax.xlsx': 'impot_revenu',
  'baremes-ipp-taxation-capital.xlsx': 'taxation_capital'
}

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()

  file_path = args.xlsx_file
  file_name = os.path.basename(file_path)
  wb = openpyxl.load_workbook(file_path, data_only = True)
  directory = os.path.join(THIS_DIR, 'openfisca_baremes_ipp', 'parameters', NODE_MAP[file_name])
  if os.path.isdir(directory):
    shutil.rmtree(directory)
  os.makedirs(directory)
  parse_workbook(wb, directory)

if __name__ == "__main__":
    main()
