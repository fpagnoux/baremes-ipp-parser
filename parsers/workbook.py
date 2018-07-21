# -*- coding: utf-8 -*-

import os

from .sheets import SheetParser, HeaderError
from .summary import SummaryParser
from .commons import export_yaml, slugify

SHEETS_TO_IGNORE = ['Sommaire (FR)', 'Outline (EN)', 'CNRACL', 'IRCANTEC', 'FILLON']


def create_directories(sections, directory):
  for section_key, section_data in sections.items():
    dir_path = os.path.join(directory, section_key)
    meta_file_path = os.path.join(dir_path, 'index.yaml')
    os.mkdir(dir_path)
    export_yaml(section_data, meta_file_path)

def parse_workbook(wb, directory):
  summary_parser = SummaryParser(wb['Sommaire (FR)'])
  summary_parser.parse()
  create_directories(summary_parser.sections, directory)

  for title in wb.sheetnames:
    if title in SHEETS_TO_IGNORE:
      continue
    parser = SheetParser(wb[title])
    key = slugify(title)
    try:
      parser.parse()
      data = {}
      data.update(parser.sheet_data)
      sheets_metadata = summary_parser.sheets_data.get(key)
      if sheets_metadata is None:
        print("Warning: Sheet {} does not seem to be included in the summary. Ignoring it.".format(title))
        continue
      data.update({'description': sheets_metadata['description']})
      path = os.path.join(directory, sheets_metadata['path'], "{}.yaml".format(key))
      export_yaml(data, path)
    except HeaderError as e:
      print('Error parsing sheet "{}": "{}". It probably does not have a proper header. Ignoring the sheet.'
        .format(title, e.args[0]))

def parse_data_sheet(wb, directory):
      parser.save_as_yaml(u'{}/{}.yaml'.format(directory, slugify(title, separator='_')))
