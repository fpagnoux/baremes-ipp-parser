#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openpyxl
import argparse
import os

MAP = {
  "Références législatives": "reference",
  "Parution au JO": "date_parution_jo",
  "Notes": "notes",
  "Note": "notes",
  "Date d'effet": "date",
}

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  argparser.add_argument('output_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()
  file_name = args.xlsx_file

  wb = openpyxl.load_workbook(file_name)
  for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    for cell in sheet[2]:
      up_cell = cell.offset(-1,0)
      if cell.internal_value in list(MAP.keys()):
        up_cell.set_explicit_value(MAP[cell.internal_value])

  wb.save(args.output_file)


if __name__ == "__main__":
    main()
