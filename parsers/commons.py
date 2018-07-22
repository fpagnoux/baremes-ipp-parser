# -*- coding: utf-8 -*-

import yaml
import re
from slugify import slugify as slugify_

STOPWORDS = [
  'a',
  'au',
  'd',
  'de',
  'des',
  'du',
  'et',
  'l',
  'la',
  'le',
  'les',
  'ou',
  'pour',
  'sur',
  'un',
  ]

def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    yaml.safe_dump(data, file, default_flow_style = False, allow_unicode = True)

def slugify(text, stopwords = False):
  if stopwords:
    return slugify_(text, separator = '_', stopwords = STOPWORDS)
  return slugify_(text, separator = '_')
