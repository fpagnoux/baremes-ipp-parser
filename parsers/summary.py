# -*- coding: utf-8 -*-

from .commons import slugify

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
    first_row = next(row[0].row for row in  rows if self.is_first_row(row))
    for row in rows[first_row -1:]:
      if row[3].internal_value is not None:
        cell = row[3]
        description = cell.internal_value
        if cell.hyperlink is None:
          print("Warning: summary cell {} is not a link. Ignoring it.".format(cell.coordinate))
          continue
        key = slugify(cell.hyperlink.location.split('!')[0])
        self.sheets_data[key] = {'description': description, 'path': current_path}
      elif row[1].internal_value is not None:
        cell = row[1]
        description = ''.join(cell.internal_value.split('.')[1:]).strip()
        key = slugify(description, stopwords = True)
        self.sections[key] = {'description': description}
        current_path = key