# -*- coding: utf-8 -*-

import yaml
from slugify import slugify as slugify_

def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    yaml.safe_dump(data, file, default_flow_style = False, allow_unicode = True)

def slugify(text, stopwords = False):
  if stopwords:
    return slugify_(text, separator = '_', stopwords=[
      'd', 'de', 'la', 'du', 'le', 'et', 'les', 'au', 'l', 'des', 'sur']
      )
  return slugify_(text, separator = '_')
