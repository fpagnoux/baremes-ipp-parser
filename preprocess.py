#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openpyxl
import argparse
import os

MAP = {
	u"Références législatives": "reference",
	u"Parution au JO": "date_parution_jo",
	u"Notes": "notes",
}

def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_file', help = 'XLSX file to convert to YAML parameters')
  args = argparser.parse_args()
  file_name = args.xlsx_file

  wb = openpyxl.load_workbook(file_name)
  for sheet_name in wb.sheetnames:
  	sheet = wb[sheet_name]
  	for cell in sheet[2]:
  		up_cell = cell.offset(-1,0)
  		if cell.internal_value in MAP.keys() and up_cell.internal_value is None:
  			up_cell.set_explicit_value(MAP[cell.internal_value])

  wb.save('output.xlsx')


if __name__ == "__main__":
    main()
