#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sheets import SheetParser, HeaderError
import openpyxl
import argparse
import os

SHEETS_TO_IGNORE = ['Sommaire (FR)', 'Outline (EN)']


def parse(wb, directory):

  for title in wb.sheetnames:
    if title in SHEETS_TO_IGNORE:
      continue
    parser = SheetParser(wb[title])
    try:
      parser.parse()
      parser.save_as_yaml(u'{}/{}.yaml'.format(directory, title).encode('utf-8'))
    except HeaderError as e:
      print('Error parsing sheet "{}": "{}". It probably does not have a proper header. Ignoring the sheet.'
        .format(title, e.args[0]))

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()

  file_name = args.xlsx_file
  wb = openpyxl.load_workbook(file_name, data_only = True)
  directory = 'parameters'
  if not os.path.isdir(directory):
    os.mkdir(directory)
  parse(wb, directory)

if __name__ == "__main__":
    main()
