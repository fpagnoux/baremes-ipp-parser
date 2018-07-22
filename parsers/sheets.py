# -*- coding: utf-8 -*-

from builtins import range
from builtins import object
import dpath
import datetime
from pprint import pprint

from .commons import slugify


def clean_none_values(values):
  sorted_dates = sorted(values.keys())
  first_value_found = False
  first_none_found = False
  for date in sorted_dates:
    value = values[date]['value']
    if value is None and (first_none_found or not first_value_found):
      del values[date]
    elif value is None:
      first_none_found = True
    elif value is not None and not first_value_found:
      first_value_found = True

class HeaderError(Exception):
  pass


class SheetParser(object):

  def __init__(self, sheet):
    self.sheet = sheet
    self.date_column = None
    self.reference_column = None
    self.data_columns = []
    self.dates = None
    self.references = None
    self.first_data_row = None
    self.last_data_row = None
    self.sheet_data = {}

  def unmerge_cells(self):
    merged_ranges = self.sheet.merged_cells.ranges.copy()
    for cell_range in merged_ranges:
      self.sheet.unmerge_cells(cell_range.coord)
      main_cell = self.sheet.cell(cell_range.min_row, cell_range.min_col)
      for column in range(cell_range.min_col + 1, cell_range.max_col + 1):
        cell = self.sheet.cell(cell_range.min_row, column)
        cell.set_explicit_value(main_cell.internal_value)

  def parse_headers(self):
    for cell in self.sheet['1']:
      key = cell.internal_value
      if key == 'date':
        self.date_column = cell.column
      elif key == 'reference':
        self.reference_column = cell.column
      elif key == 'date_parution_jo' or key == 'notes':
        pass # Ignore those columns for the moment
      elif key or any(cell.internal_value for cell in self.sheet[cell.column]):
        self.data_columns.append(cell.column)
      else:
        # Empty column encountered, we ignore the rest of the sheet
        break

    if self.date_column is None:
      raise HeaderError("Could not find a date column.")

  def parse_dates(self):
    dates = []
    visited_a_date = False

    for cell in self.sheet[self.date_column][2:]:

      if cell.internal_value is None or not isinstance(cell.internal_value, datetime.date):
        if not visited_a_date: # We are still in the header
          continue
        else:
          # Once you reach a blank cell in the date column, stop
          self.last_data_row = cell.row - 1
          break

      if not visited_a_date:
        visited_a_date = True
        self.first_data_row = cell.row

      date = cell.internal_value .strftime('%Y-%m-%d')
      dates.append(date)

    self.dates = dates
    self.number_values = len(self.dates)

  def parse_references(self):
    if not self.reference_column:
      return
    references = []
    for cell in self.sheet[self.reference_column][self.first_data_row - 1:self.last_data_row]:
      references.append(cell.internal_value.strip() if cell.internal_value else None)
    self.references = references

  def build_description(self, column):
    description_cells = column[1:self.first_data_row -1]
    return "; ".join([
      cell.internal_value.strip()
      for cell in description_cells
      if cell.internal_value is not None
      ])

  def parse_cell(self, cell):
    value = cell.internal_value
    if isinstance(value, int):
      return float(value)
    if isinstance(value, str):
      try:
        return float(value)
      except ValueError:
        print("Warning, unable to interpret cell {} in sheet {}.".format(cell.coordinate, self.sheet.title))
        return value
    return value

  def parse_column(self, column):
    path = ''
    descriptions_cells = column[1:self.first_data_row - 1]
    for cell in descriptions_cells:
      if cell.internal_value is None:
        continue
      description = cell.internal_value.strip()
      key = slugify(description, stopwords = True)
      path = '/'.join([path, key]) if path else key
      dpath.util.new(self.sheet_data, '/'.join([path, 'description']), description)

    if not path:
      # If there is no path, there is no description, and the column doesn't contain data
      return
    values = {}

    for index, cell in enumerate(column[self.first_data_row - 1:self.last_data_row]):
      date = self.dates[index]
      value = self.parse_cell(cell)
      item = {'value': value}
      if self.references is not None and self.references[index] is not None:
        item['reference'] = self.references[index]
      values[date] = item

    clean_none_values(values)

    dpath.util.new(self.sheet_data, '/'.join([path, 'values']), values)


  def parse(self):
    self.unmerge_cells()
    self.parse_headers()
    self.parse_dates()
    self.parse_references()

    for column_name in self.data_columns:
      self.parse_column(self.sheet[column_name])

    return self.sheet_data
