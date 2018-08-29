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
from bareme_ipp_parsers.sheets import SheetParsingError

from config import sheets

log = logging.getLogger(__name__)


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('xlsx_path', help = 'XLSX file or directory to convert to YAML parameters')
  argparser.add_argument('output_dir', help = 'Output directory')
  argparser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
  args = argparser.parse_args()

  logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING)

  xlsx_path = args.xlsx_path

  if os.path.isdir(xlsx_path):
    xlsx_files = glob.glob(os.path.join(xlsx_path, "*.xlsx"))
  else:
    xlsx_files = [xlsx_path]

  for file_path in xlsx_files:
    file_name = os.path.basename(file_path)
    if file_name not in sheets:
      continue
    wb = openpyxl.load_workbook(file_path, data_only = True)
    directory = os.path.join(args.output_dir, sheets[file_name]['name'])
    if os.path.isdir(directory):
      shutil.rmtree(directory)
    os.makedirs(directory)
    log.info('Parsing file {}'.format(file_name))
    try:
      parse_workbook(wb, directory, config = sheets[file_name])
    except SheetParsingError as e:
      log.error('Error parsing workbook "{}":\n  "{}".\n  This workbook will be ignored.'
        .format(file_name, e.args[0]))

if __name__ == "__main__":
    main()
