# -*- coding: utf-8 -*-

import logging

from .commons import slugify
from .sheets import SheetParsingError

log = logging.getLogger(__name__)


class SummaryParser(object):

  def __init__(self, sheet):
    self.sheet = sheet
    self.sheets_data = {}
    self.sections = {}

  def is_first_row(self, row):
    is_first_section = isinstance(row[1].internal_value, str) and row[1].internal_value.startswith('I. ')
    is_first_sheet = row[2].internal_value == 1

    return is_first_sheet or is_first_section

  def parse(self):
    current_path = ''
    rows = list(self.sheet.rows)
    first_row = next(row[0].row for row in rows if self.is_first_row(row))
    section_index = 1
    sheet_index = 1
    for row in rows[first_row - 1:]:
      if row[3].internal_value is not None:
        self.parse_sheet_title(row[3], current_path, sheet_index)
        sheet_index += 1
      elif row[1].internal_value is not None:
        current_path = self.parse_section_title(row[1], section_index)
        section_index += 1
        sheet_index = 0

  def parse_section_title(self, cell, index):
    if not isinstance(cell.internal_value, str):
      raise SheetParsingError("Enable to parse summary: Unexpected value in cell '{}'".format(cell.coordinate))
    description = ''.join(cell.internal_value.split('.')[1:]).strip()
    key = slugify(description, stopwords = True)
    if self.sections.get(key):
      raise SheetParsingError("Name collision: section '{}' alredy exists.".format(key))
    self.sections[key] = {
      'description': description,
      'metadata': {
        'rank': index
        }
      }
    return key

  def parse_sheet_title(self, cell, path, index):
    description = cell.internal_value
    if cell.hyperlink is None:
      log.warning("Summary cell {} is not a link. Ignoring it.".format(cell.coordinate))
      return
    key = slugify(cell.hyperlink.location.split('!')[0])
    if self.sheets_data.get(key):
      raise SheetParsingError("Name collision: sheet '{}' alredy exists.".format(key))
    self.sheets_data[key] = {'description': description, 'path': path, 'rank': index}
