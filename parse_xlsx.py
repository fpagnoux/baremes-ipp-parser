#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openfisca_core.parameters import load_parameter_file
from sheets import SheetParser
import openpyxl
import argparse
import os

SHEETS_TO_IGNORE = ['Sommaire (FR)', 'Outline (EN)']


def parse(wb, directory):
  for title in wb.sheetnames:
    if title in SHEETS_TO_IGNORE:
      continue
    parser = SheetParser(wb[title])
    parser.parse()
    parser.save_as_yaml('{}/{}.yaml'.format(directory, title))

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()
  file_name = args.xlsx_file
  wb = openpyxl.load_workbook(file_name)
  directory = 'parameters'
  if not os.path.isdir(directory):
    os.mkdir(directory)
  parse(wb, directory)

if __name__ == "__main__":
    main()
