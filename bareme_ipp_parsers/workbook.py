# -*- coding: utf-8 -*-

import os
import shutil
import logging

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

class WorkbookParser(object):

  def __init__(self, workbook, config, output_dir):
    self.workbook = workbook
    self.config = config
    self.name = config['name']
    self.output_dir = os.path.join(output_dir, self.name)

    if os.path.isdir(self.output_dir):
      shutil.rmtree(self.output_dir)
    os.makedirs(self.output_dir)

  def parse(self):
    sheets_to_ignore = self.config.get('ignore_sheets') or []
    columns_to_ignore = self.config.get('ignore_columns') or {}
    summary_sheet = next(sheet for sheet in self.workbook.sheetnames if 'sommaire' in sheet.lower())
    summary_parser = SummaryParser(self.workbook[summary_sheet], self.config)
    summary_parser.parse()
    create_directories(summary_parser.sections, self.output_dir)

    for title in self.workbook.sheetnames:
      if sheets_to_ignore and title in sheets_to_ignore:
        continue

      log.info('Parsing sheet "{}"'.format(title))
      parser = SheetParser(self.workbook[title], columns_to_ignore.get(title))
      key = slugify(title)
      try:
        parser.parse()
        data = {}
        data.update(parser.sheet_data)
        sheets_metadata = summary_parser.sheets_data.get(key)
        if sheets_metadata is None:
          log.warning(f"Sheet '{title}' does not seem to be included in the summary in '{self.name}'. Ignoring it.".format(title))
          continue
        data.update({'description': sheets_metadata['description']})
        data.update({'metadata': {'rank': sheets_metadata['rank']}})
        fs_path = sheets_metadata['path'].replace('/subparams', '')
        path = os.path.join(self.output_dir, fs_path, "{}.yaml".format(key))
        export_yaml(data, path)
      except SheetParsingError as e:
        log.error(f'Error parsing sheet "{title}" in workbook "{self.name}":\n  "{e.args[0]}".\nThis sheet will be ignored.')
