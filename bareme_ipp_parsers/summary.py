# -*- coding: utf-8 -*-

import logging

import dpath

from .commons import slugify
from .sheets import SheetParsingError

log = logging.getLogger(__name__)


class SummaryParser(object):

  def __init__(self, sheet, config):
    self.sheet = sheet
    self.sheets_data = {}
    self.sections = {}
    self.config = config or {}
    self.depth = self.config.get('summary_depth', 2)

  def is_first_row(self, row):
    is_first_section = isinstance(row[1].internal_value, str) and row[1].internal_value.startswith('I. ')
    is_first_sheet = row[self.depth].internal_value == 1

    return is_first_sheet or is_first_section

  def parse(self):
    current_path = ''
    rows = list(self.sheet.rows)
    first_row = next(row[0].row for row in rows if self.is_first_row(row))
    section_index = 1
    subsection_index = 1  # Use only when summary has depth 3
    sheet_index = 1
    for row in rows[first_row - 1:]:
      if row[self.depth + 1].internal_value is not None:
        self.parse_sheet_title(row[self.depth + 1], current_path, sheet_index)
        sheet_index += 1
      elif row[1].internal_value is not None:
        log.info(f"Parsing section title '{row[1].internal_value}'")
        current_path = self.parse_section_title(row[1], section_index)
        section_index += 1
        sheet_index = 0
        subsection_index = 0
      elif self.depth >= 3 and row[2].internal_value is not None:
        log.info(f"Parsing section title '{row[2].internal_value}'")
        current_section = current_path.split('/')[0]
        current_path = self.parse_section_title(row[2], subsection_index, current_section)
        subsection_index  += 1
        sheet_index = 0

  def parse_section_title(self, cell, index, current_section = None):
    if not isinstance(cell.internal_value, str):
      raise SheetParsingError("Enable to parse summary: Unexpected value in cell '{}'".format(cell.coordinate))
    description = ''.join(cell.internal_value.split('.')[1:]).strip()
    key = slugify(description, stopwords = True)
    path = f"{current_section}/subparams/{key}" if current_section else key
    if dpath.search(self.sections, path):
      raise SheetParsingError("Name collision: section '{}' alredy exists.".format(path))
    dpath.new(self.sections, path, {
      'description': description,
      'metadata': {
        'rank': index
        }
      })

    return path

  def parse_sheet_title(self, cell, path, index):
    description = cell.internal_value
    if cell.hyperlink is None:
      log.warning("Summary cell {} is not a link. Ignoring it.".format(cell.coordinate))
      return
    key = slugify(cell.hyperlink.location.split('!')[0])
    if self.sheets_data.get(key):
      raise SheetParsingError("Name collision: sheet '{}' alredy exists.".format(key))
    self.sheets_data[key] = {'description': description, 'path': path, 'rank': index}
