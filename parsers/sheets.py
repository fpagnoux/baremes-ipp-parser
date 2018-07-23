# -*- coding: utf-8 -*-

from builtins import range
from builtins import object
import dpath
import datetime
import logging

from .commons import slugify

log = logging.getLogger(__name__)


def contract(values):
  result = values.copy()
  sorted_dates = sorted(values.keys())
  last_date = sorted_dates[0]
  for date in sorted_dates[1:]:
    if values[date] == values[last_date]:
      del result[date]
    last_date = date
  return result


class SheetParsingError(Exception):
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
        pass  # Ignore those columns for the moment
      elif key or any(cell.internal_value for cell in self.sheet[cell.column]):
        self.data_columns.append(cell.column)
      else:
        # Empty column encountered, we ignore the rest of the sheet
        break

    if self.date_column is None:
      raise SheetParsingError("Could not find a date column.")

  def parse_dates(self):
    dates = []
    visited_a_date = False

    for cell in self.sheet[self.date_column][2:]:

      if cell.internal_value is None or not isinstance(cell.internal_value, (datetime.date, int)):
        if not visited_a_date:  # We are still in the header
          continue
        else:
          # Once you reach a blank cell in the date column, stop
          self.last_data_row = cell.row - 1
          break

      if not visited_a_date:
        visited_a_date = True
        self.first_data_row = cell.row

      if isinstance(cell.internal_value, datetime.date):
        date = cell.internal_value.strftime('%Y-%m-%d')
      else:
        date = "{}-01-01".format(cell.internal_value)
      dates.append(date)

    self.dates = dates
    self.number_values = len(self.dates)

    if not self.first_data_row:
      raise SheetParsingError("Not able to parse the date columns.")

  def parse_references(self):
    if not self.reference_column:
      return
    references = []
    for cell in self.sheet[self.reference_column][self.first_data_row - 1:self.last_data_row]:
      references.append(cell.internal_value.strip() if cell.internal_value else None)
    self.references = references

  def parse_column_headers(self, column):
    path = ''
    descriptions_cells = column[1:self.first_data_row - 1]
    for cell in descriptions_cells:
      if cell.internal_value is None:
        continue
      description = cell.internal_value.strip()
      key = slugify(description, stopwords = True)
      path = '/'.join([path, key]) if path else key
      dpath.util.new(self.sheet_data, '/'.join([path, 'description']), description)

    return path

  def parse_cell(self, cell):
    value = cell.internal_value
    if isinstance(value, int):
      return float(value)
    if isinstance(value, str):
      try:
        return float(value)
      except ValueError:
        log.warning("Unable to interpret cell {} in sheet {}.".format(cell.coordinate, self.sheet.title))
        return value
    return value

  def parse_unit(self, cell):
    if cell.internal_value is None:
      return
    if '%' in cell.number_format:
      return '/1'
    elif '€' in cell.number_format:
      return 'currency-EUR'
    elif 'FRF' in cell.number_format:
      return 'currency-FRF'
    elif cell.number_format in ['General', '0.0']:
      return
    else:
      log.warning("Unknown unit encountered in cell {} in sheet {}".format(cell.coordinate, self.sheet.title))

  def parse_column(self, column):

    path = self.parse_column_headers(column)
    if not path:
      # If there is no path, there is no description, and the column doesn't contain data
      return
    parameter = dpath.util.get(self.sheet_data, path)
    parameter['metadata'] = {}

    values = {}
    unit = None

    for index, cell in enumerate(column[self.first_data_row - 1:self.last_data_row]):
      date = self.dates[index]
      value = self.parse_cell(cell)
      item = {'value': value, 'metadata': {}}

      cell_unit = self.parse_unit(cell)
      if unit is None and cell_unit is not None:
        parameter['metadata']['unit'] = cell_unit
        unit = cell_unit  # For the moment, take the unit of the first value as the param unit. TODO: Handle currency/unit change.

      if self.references is not None and self.references[index] is not None:
        item['metadata']['reference'] = self.references[index]
      values[date] = item

    values = contract(values)

    if parameter.get('values') is not None:
      raise SheetParsingError("Name collision: column '{}' alredy exists.".format(path))
    parameter['values'] = values

  def parse(self):
    self.unmerge_cells()
    self.parse_headers()
    self.parse_dates()
    self.parse_references()

    for column_name in self.data_columns:
      self.parse_column(self.sheet[column_name])

    return self.sheet_data
