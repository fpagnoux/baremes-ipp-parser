#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openpyxl
import argparse

MAP = {
  "Références législatives": "metadata/reference",
  "Parution au JO": "metadata/date_parution_jo",
  "Notes": "metadata/notes",
  "Note": "metadata/notes",
  "Date d'effet": "date",
  }


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  argparser.add_argument('-o', '--output-file', default = None, help = "Output file")
  argparser.add_argument('-i', '--infile', action = 'store_true', help = "Apply editions directly to the input file")

  args = argparser.parse_args()
  input_file = args.xlsx_file
  output_file = args.output_file if args.output_file else input_file
  wb = openpyxl.load_workbook(input_file)

  for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    for cell in sheet[2]:
      up_cell = cell.offset(-1, 0)
      if cell.internal_value in list(MAP.keys()):
        up_cell.set_explicit_value(MAP[cell.internal_value])

  wb.save(output_file)


if __name__ == "__main__":
    main()
