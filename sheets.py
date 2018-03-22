from openfisca_core.parameters import ParameterNode
import openpyxl

wb = openpyxl.load_workbook('/Users/florianpagnoux/dev/openfisca/baremes-ipp/baremes-ipp-prestations-sociales-social-benefits.xlsx')

sheet = wb['def_pac']
column = sheet['B']

class SheetParser(object):

  def __init__(self, sheet):
    self.sheet = sheet
    self.date_column = None
    self.reference_column = None
    self.data_columns = []
    self.dates = None
    self.references = None
    self.number_values = None

  def parse_headers(self):
    for cell in self.sheet['1']:
      key = cell.internal_value
      if key is None:
        break
      elif key == 'date':
        self.date_column = cell.column
      elif key == 'reference':
        self.reference_column = cell.column
      elif key == 'date_parution_jo' or key == 'notes':
        pass # Ignore those columns for the moment
      else:
        self.data_columns.append(cell.column)

  def parse_dates(self):
    dates = []
    for cell in self.sheet[self.date_column][2:]:
      if cell.internal_value is None:
        # Once you reach a blank cell in the date column, stop
        break
      date = cell.internal_value .strftime('%Y-%m-%d')
      dates.append(date)
    self.dates = dates
    self.number_values = len(self.dates)

  def parse_references(self):
    references = []
    for cell in self.sheet[self.reference_column][2:self.number_values + 2]:
      references.append(cell.internal_value)
    self.references = references

  def parse_column(self, column):
    data = {}
    code = column[0].internal_value
    data = { 'description': column[1].internal_value, 'values': {} }
    for date, reference, cell in zip(self.dates, self.references, column[2:]):
      item = {'value': cell.internal_value}
      if reference is not None:
        item['reference'] = reference
      data['values'][date] = item

    return code, data

  def parse(self):
    self.parse_headers()
    self.parse_dates()
    self.parse_references()

    parsed_columns = [self.parse_column(self.sheet[column_name]) for column_name in self.data_columns]

    return ParameterNode('', data = {
      code: data for code, data in parsed_columns
    })


parser = SheetParser(sheet)
x = parser.parse()
