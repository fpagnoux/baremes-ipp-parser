#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openpyxl
import argparse

MAP = {
  "Références législatives": "metadata/reference",
  "Références BOI": "metadata/reference_boi",
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
        header = MAP[cell.internal_value]
        if up_cell.internal_value != header:
          up_cell.set_explicit_value(header)
          print(f"Applying header {header} to cell {cell.coordinate} as lower cell contains '{cell.internal_value}' in sheet {sheet_name}")
    # Preprocessing spécifique aux impots revenu
    for cell in sheet[1]:
      if cell.internal_value == "date_ir":
        print(f"Applying header 'date_ir' to cell {cell.coordinate} in sheet {sheet_name}")
        cell.set_explicit_value("date")
    for row in sheet.rows:
      for cell in row:
        if isinstance(cell.internal_value, str) and cell.internal_value.endswith(' FRF'):
          try:
            clean_value = float(cell.internal_value.replace(' FRF', '').replace(' ', ''))
            cell.set_explicit_value(clean_value)
            cell.data_type = "n"
            cell.number_format = '#,##0\\ [$FRF]'
            print(f"Value cleaning: Edited cell {cell.coordinate} in sheet {sheet_name}")
          except ValueError:
            print(f"Value cleaning: Ignoring cell {cell.coordinate} in sheet {sheet_name}")
  wb.save(output_file)


if __name__ == "__main__":
    main()
