# -*- coding: utf-8 -*-

from ruamel.yaml import YAML

yaml = YAML()

from slugify import slugify as slugify_
import re


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

def represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')


def represent_str(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style = '|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def represent_dict(dumper, data):
  if data.get('metadata'):
    metadata = data['metadata']
    del data['metadata']
    data['metadata'] = metadata
  if data.get('documentation'):
    documentation = data['documentation']
    del data['documentation']
    data['documentation'] = documentation

  return dumper.represent_dict(data)

yaml.default_flow_style = False
yaml.representer.add_representer(type(None), represent_none)
yaml.representer.add_representer(str, represent_str)
yaml.representer.add_representer(dict, represent_dict)


def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    yaml.dump(data, file)
  with open(file_path, 'r') as file:
    content = file.read()
    new_content = re.sub(
               r"'(\d{4}-\d{2}-\d{2})'",
               r"\1",
               content
           )
  with open(file_path, 'w') as file:
    file.write(new_content)


def slugify(text, stopwords = False):
  if re.match('-\d+$', text):
    return text
  if stopwords:
    return slugify_(text, separator = '_', stopwords = STOPWORDS)
  return slugify_(text, separator = '_')
