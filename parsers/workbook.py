# -*- coding: utf-8 -*-

import os
import logging

from .sheets import SheetParser, SheetParsingError
from .summary import SummaryParser
from .commons import export_yaml, slugify

SHEETS_TO_IGNORE = ['Sommaire (FR)', 'Outline (EN)', 'Abréviations', 'CNRACL', 'IRCANTEC', 'FILLON']

log = logging.getLogger(__name__)


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
    log.info('Parsing sheet "{}"'.format(title))
    parser = SheetParser(wb[title])
    key = slugify(title)
    try:
      parser.parse()
      data = {}
      data.update(parser.sheet_data)
      sheets_metadata = summary_parser.sheets_data.get(key)
      if sheets_metadata is None:
        log.warning("Sheet {} does not seem to be included in the summary. Ignoring it.".format(title))
        continue
      data.update({'description': sheets_metadata['description']})
      path = os.path.join(directory, sheets_metadata['path'], "{}.yaml".format(key))
      export_yaml(data, path)
    except SheetParsingError as e:
      log.warning('Error parsing sheet "{}":\n  "{}".\nThis sheet will be ignored.'
        .format(title, e.args[0]))
