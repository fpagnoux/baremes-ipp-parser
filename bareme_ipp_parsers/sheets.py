# -*- coding: utf-8 -*-

from builtins import range
from builtins import object
import dpath
import datetime
import logging
import re
from collections import defaultdict
import datetime

from .commons import slugify


def contract(values):
  result = values.copy()
  sorted_dates = sorted(values.keys())
  last_date = sorted_dates[0]
  for date in sorted_dates[1:]:
    if values[date] == values[last_date]:
      del result[date]
    last_date = date
  return result


def combine(x, y):
  if x is None:
    return y
  if isinstance(x, list):
    return x + [y]
  return [x, y]


class SheetParsingError(Exception):
  pass



METADATA_COLUM = ['reference', 'date_parution_jo', 'notes']


class SheetParser(object):

  def __init__(self, sheet, workbook_name = '', columns_to_ignore = None):
    self.sheet = sheet
    self.date_column = None
    self.reference_column = None
    self.data_columns = []
    self.metadata_columns = defaultdict(lambda: [])
    self.dates = None
    self.references = None
    self.first_data_row = None
    self.last_data_row = None
    self.sheet_data = {}
    self.columns_to_ignore = columns_to_ignore or []

    self.log = logging.getLogger(f'{workbook_name}:{sheet.title}')

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
      elif cell.column in self.columns_to_ignore:
        pass
      elif key in METADATA_COLUM or isinstance(key, str) and key.startswith('metadata/'):
        key = key.replace('metadata/', '')
        self.metadata_columns[key].append(cell.column)
      elif key or any(cell.internal_value for cell in self.sheet[cell.column]):
        self.data_columns.append(cell.column)
      else:
        # Empty column encountered, we ignore the rest of the sheet
        break

    if self.date_column is None:
      raise SheetParsingError("Could not find a date column.")


  def parse_date_cell(self, cell):
      value = cell.internal_value
      if value is None:
        return
      if isinstance(value, str) and not value.strip():
        return
      if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
      if isinstance(value, int):
        return "{}-01-01".format(value)

  def parse_dates(self):
    date_column = self.sheet[self.date_column]
    dates = []

    # Find the first data line
    for cell in date_column[2:]:
      if isinstance(cell.internal_value, (datetime.date, int)):
        self.first_data_row = cell.row
        break

    # Parse the values
    for cell in date_column[self.first_data_row - 1:]:
      value = self.parse_date_cell(cell)
      if value is None:
        break
      dates.append(value)

    self.last_data_row =  self.first_data_row + len(dates) - 1

    for cell in date_column[self.last_data_row:]:
      if self.parse_date_cell(cell):
        self.log.warning(f'Cell {cell.coordinate} contains a date, but not precedent cell {date_column[self.last_data_row].coordinate}. There must be something wrong')

    self.dates = dates
    self.number_values = len(self.dates)

    if not self.first_data_row:
      raise SheetParsingError("Not able to parse the date columns.")

  def parse_references(self):
    if not self.reference_column:
      return
    references = []
    for cell in self.sheet[self.reference_column][self.first_data_row - 1: self.last_data_row]:
      references.append(str(cell.internal_value).strip() if cell.internal_value else None)
    self.references = references

  def parse_column_headers(self, column):
    path = ''
    descriptions_cells = column[1:self.first_data_row - 1]
    for cell in descriptions_cells:
      if cell.internal_value is None:
        continue
      description = str(cell.internal_value).strip()
      key = slugify(description, stopwords = True)
      parent_node = dpath.get(self.sheet_data, path) if path else self.sheet_data
      parent_node[key] = {}
      if parent_node.get('metadata') is None:
        parent_node['metadata'] = {'order': []}
      if not parent_node['metadata']['order'] or parent_node['metadata']['order'][-1] != key:  # avoid duplication for merged cells
        parent_node['metadata']['order'].append(key)
      path = f'{path}/{key}' if path else key
      dpath.util.new(self.sheet_data, f'{path}/description', description)

    return path

  def parse_cell(self, cell):
    value = cell.internal_value
    if isinstance(value, int):
      return float(value)
    if isinstance(value, str):
      if value == "nc":
        # TODO: handle placeholder
        return
      try:
        return float(value)
      except ValueError:
        self.log.warning("Unable to interpret cell '{}'. Content: '{}'".format(cell.coordinate, self.sheet.title, cell.internal_value))
        return value
    return value

  def parse_unit(self, cell):
    if cell.internal_value is None:
      return
    if '%' in cell.number_format:
      return '/1'
    if '€' in cell.number_format:
      return 'currency-EUR'
    if 'AFRF' in cell.number_format:
      return 'currency-AFRF'
    if 'FRF' in cell.number_format:
      return 'currency-FRF'
    if cell.number_format == 'General' or re.match('0.?(0)*',cell.number_format):
      return
    match = re.search(r'\[\$((?:.)*)\]', cell.number_format)  # Handle custom units
    if match:
      return match.group(1)
    self.log.warning("Unknown unit encountered in cell {cell.coordinate}")

  def parse_data_column(self, column):

    path = self.parse_column_headers(column)
    if not path:
      # If there is no path, there is no description, and the column doesn't contain data
      return
    parameter = dpath.util.get(self.sheet_data, path)
    metadata = {}

    values = {}
    units = {}

    for index, cell in enumerate(column[self.first_data_row - 1:self.last_data_row]):
      date = self.dates[index]
      value = self.parse_cell(cell)
      item = {'value': value, 'metadata': {}}

      if value is not None:
        cell_unit = self.parse_unit(cell)
        units[date] = cell_unit

      # if self.references is not None and self.references[index] is not None:
      #   item['metadata']['reference'] = self.references[index]
      if not item['metadata']:
        del item['metadata']
      values[date] = item

    values = contract(values)
    if units:
      units = contract(units)
      if len(units) == 1:
        units = list(units.values())[0]
      if units is not None:
        metadata['unit'] = units

    if parameter.get('values') is not None:
      raise SheetParsingError("Name collision: column '{}' alredy exists.".format(path))
    parameter['values'] = values
    if metadata:
      parameter['metadata'] = metadata

  def parse_metadata_column(self, field_id, column):
    values = self.sheet_data['metadata'].get(field_id, {})
    for index, cell in enumerate(column[self.first_data_row - 1:self.last_data_row]):
      value = cell.internal_value
      if isinstance(value, datetime.date):
        value = value.strftime('%Y-%m-%d')
      if isinstance(value, str):
        value = value.strip()
      if not value:
        continue
      date = self.dates[index]
      values[date] = combine(values.get(date), value)
    if values:
      self.sheet_data['metadata'][field_id] = values

  def parse_notes(self):
    doc = ""
    for row in list(self.sheet.rows)[self.last_data_row:]:
      for cell in row:
        if cell.internal_value is None:
          continue
        value = cell.internal_value
        if isinstance(value, datetime.date):
          value = value.strftime('%Y-%m-%d')
        if not isinstance(value, str):
          self.log.warning(f'Found numeric values in footnotes in cell "{cell.coordinate}". That is strange.')
          value = str(value)
        if not value.strip():
          continue
        doc = doc + value + "\n"

    self.sheet_data['documentation'] = doc

  def parse(self):
    self.unmerge_cells()
    self.parse_headers()
    self.parse_dates()
    self.parse_references()

    for column_name in self.data_columns:
      self.parse_data_column(self.sheet[column_name])

    for field_id, field_columns in self.metadata_columns.items():
      for column_name in field_columns:
        self.parse_metadata_column(field_id, self.sheet[column_name])

    self.parse_notes()

    return self.sheet_data
