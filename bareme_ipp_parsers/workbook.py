# -*- coding: utf-8 -*-

import os
import shutil
import logging

from .sheets import SheetParser, SheetParsingError
from .summary import SummaryParser
from .commons import export_yaml, slugify

log = logging.getLogger('Parser')


def create_directories(sections, directory):
  meta_file_path = os.path.join(directory, 'index.yaml')
  meta_file_path_content = {key: value for (key, value) in sections.items() if key != 'subparams'}
  export_yaml(meta_file_path_content, meta_file_path)

  for section_key, section_data in sections.get('subparams', {}).items():
    dir_path = os.path.join(directory, section_key)
    os.mkdir(dir_path)
    create_directories(section_data, dir_path)

class WorkbookParser(object):

  def __init__(self, workbook, config, root_output_dir):
    self.workbook = workbook
    self.name = config['name']
    self.sheets_to_ignore = config.get('ignore_sheets') or []
    self.columns_to_ignore = config.get('ignore_columns') or {}
    self.config = config
    self.output_dir = os.path.join(root_output_dir, self.name)

    if os.path.isdir(self.output_dir):
      shutil.rmtree(self.output_dir)
    os.makedirs(self.output_dir)

  def parse(self):
    summary_sheet = next(sheet for sheet in self.workbook.sheetnames if 'sommaire' in sheet.lower())
    summary_parser = SummaryParser(self.workbook[summary_sheet], self.config)
    summary_parser.parse()
    create_directories(summary_parser.sections, self.output_dir)

    for title in self.workbook.sheetnames:
      if self.sheets_to_ignore and title in self.sheets_to_ignore:
        continue

      log.info(f'{self.name}: Parsing sheet "{title}"')
      parser = SheetParser(self.workbook[title], self.columns_to_ignore.get(title))
      key = slugify(title)
      try:
        parser.parse()
        data = {}
        data.update(parser.sheet_data)
        sheets_metadata = summary_parser.sheets_data.get(key)
        if sheets_metadata is None:
          log.warning(f"Sheet '{title}' does not seem to be included in the summary in '{self.name}'. Ignoring it.")
          continue
        data.update({'description': sheets_metadata['description']})
        fs_path = sheets_metadata['path'].replace('subparams/', '')
        path = os.path.join(self.output_dir, fs_path, f"{key}.yaml")
        export_yaml(data, path)
      except SheetParsingError as e:
        log.error(f'Error parsing sheet "{title}" in workbook "{self.name}":\n  "{e.args[0]}".\nThis sheet will be ignored.')
