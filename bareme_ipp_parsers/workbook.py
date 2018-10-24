# -*- coding: utf-8 -*-

import os
import logging
from functools import reduce

from .sheets import SheetParser, SheetParsingError
from .summary import SummaryParser
from .commons import export_yaml, slugify

log = logging.getLogger(__name__)


def create_directories(sections, directory):
  for section_key, section_data in sections.items():
    dir_path = os.path.join(directory, section_key)
    meta_file_path = os.path.join(dir_path, 'index.yaml')
    section_metadata = {key: value for (key, value) in section_data.items() if key != 'subparams'}
    os.mkdir(dir_path)
    export_yaml(section_metadata, meta_file_path)
    if section_data.get('subparams'):
      create_directories(section_data['subparams'], dir_path)


def parse_workbook(wb, directory, config):
  sheets_to_ignore = config.get('ignore_sheets') or []
  columns_to_ignore = config.get('ignore_columns') or {}
  summary_sheet = next(sheet for sheet in wb.sheetnames if 'sommaire' in sheet.lower())
  summary_parser = SummaryParser(wb[summary_sheet], config)
  summary_parser.parse()
  create_directories(summary_parser.sections, directory)

  for title in wb.sheetnames:
    if sheets_to_ignore and title in sheets_to_ignore:
      continue

    log.info('Parsing sheet "{}"'.format(title))
    parser = SheetParser(wb[title], columns_to_ignore.get(title))
    key = slugify(title)
    try:
      parser.parse()
      data = {}
      data.update(parser.sheet_data)
      sheets_metadata = summary_parser.sheets_data.get(key)
      if sheets_metadata is None:
        log.warning("Sheet '{}' does not seem to be included in the summary. Ignoring it.".format(title))
        continue
      data.update({'description': sheets_metadata['description']})
      data.update({'metadata': {'rank': sheets_metadata['rank']}})
      fs_path = sheets_metadata['path'].replace('/subparams', '')
      path = os.path.join(directory, fs_path, "{}.yaml".format(key))
      export_yaml(data, path)
    except SheetParsingError as e:
      log.error('Error parsing sheet "{}":\n  "{}".\nThis sheet will be ignored.'
        .format(title, e.args[0]))
