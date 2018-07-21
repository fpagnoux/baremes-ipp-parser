#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sheets import SheetParser, HeaderError
from slugify import slugify
import openpyxl
import argparse
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SHEETS_TO_IGNORE = ['Sommaire (FR)', 'Outline (EN)', 'CNRACL', 'IRCANTEC', 'FILLON']
node_map = {
  'baremes-ipp-prelevements-sociaux-social-security-contributions.xlsx': 'prelevements_sociaux'
}


def parse(wb, directory):

  for title in wb.sheetnames:
    if title in SHEETS_TO_IGNORE:
      continue
    parser = SheetParser(wb[title])
    try:
      parser.parse()
      parser.save_as_yaml(u'{}/{}.yaml'.format(directory, slugify(title, separator='_')).encode('utf-8'))
    except HeaderError as e:
      print('Error parsing sheet "{}": "{}". It probably does not have a proper header. Ignoring the sheet.'
        .format(title, e.args[0]))

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()

  file_path = args.xlsx_file
  file_name = os.path.basename(file_path)
  wb = openpyxl.load_workbook(file_path, data_only = True)
  directory = os.path.join(THIS_DIR, 'openfisca_baremes_ipp', 'parameters', node_map[file_name])
  if not os.path.isdir(directory):
    os.mkdir(directory)
  parse(wb, directory)

if __name__ == "__main__":
    main()
