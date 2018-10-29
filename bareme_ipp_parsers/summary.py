# -*- coding: utf-8 -*-

import logging

import dpath

from .commons import slugify
from .sheets import SheetParsingError


class SummaryParser(object):

  def __init__(self, sheet, workbook_name, config):
    self.sheet = sheet
    self.sheets_data = {}
    self.sections = {'metadata': {'order': []}, 'subparams': {}}
    self.depth = config.get('summary_depth', 2)

    self.log = logging.getLogger(workbook_name)

  def is_first_row(self, row):
    is_first_section = isinstance(row[1].internal_value, str) and row[1].internal_value.startswith('I. ')
    is_first_sheet = row[self.depth].internal_value == 1

    return is_first_sheet or is_first_section

  def parse(self):
    current_path = ''
    rows = list(self.sheet.rows)
    first_row = next(row[0].row for row in rows if self.is_first_row(row))
    for row in rows[first_row - 1:]:
      if row[self.depth + 1].internal_value is not None:
        self.parse_sheet_title(row[self.depth + 1], current_path)
      elif row[1].internal_value is not None:
        self.log.info(f"Parsing section title '{row[1].internal_value}'")
        current_path = self.parse_section_title(row[1])
      elif self.depth >= 3 and row[2].internal_value is not None:
        self.log.info(f"Parsing section title '{row[2].internal_value}'")
        current_section = current_path.split('/')[1]
        current_path = self.parse_section_title(row[2], current_section)

  def parse_section_title(self, cell, current_section = None):
    if not isinstance(cell.internal_value, str):
      raise SheetParsingError("Enable to parse summary: Unexpected value in cell '{}'".format(cell.coordinate))
    description = ''.join(cell.internal_value.split('.')[1:]).strip()
    key = slugify(description, stopwords = True)
    path = f"subparams/{current_section}/subparams/{key}" if current_section else f"subparams/{key}"
    if dpath.search(self.sections, path):
      raise SheetParsingError("Name collision: section '{}' alredy exists.".format(path))
    dpath.new(self.sections, path, {
      'description': description,
      'metadata': {'order': []}
      })

    # Keep track of the order
    order_path = f'subparams/{current_section}/metadata/order' if current_section else 'metadata/order'
    dpath.get(self.sections, order_path).append(key)

    return path

  def parse_sheet_title(self, cell, path):
    description = cell.internal_value
    if cell.hyperlink is None:
      self.log.warning("Summary cell {} is not a link. Ignoring it.".format(cell.coordinate))
      return
    key = slugify(cell.hyperlink.location.split('!')[0])
    if self.sheets_data.get(key):
      raise SheetParsingError("Name collision: sheet '{}' alredy exists.".format(key))
    self.sheets_data[key] = {'description': description, 'path': path}
    dpath.get(self.sections, f'{path}/metadata/order').append(key)
