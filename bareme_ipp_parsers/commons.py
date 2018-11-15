# -*- coding: utf-8 -*-

from ruamel.yaml import YAML

yaml = YAML()

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

def represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')


def represent_str(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style = '|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.default_flow_style = False
yaml.representer.add_representer(type(None), represent_none)
yaml.representer.add_representer(str, represent_str)


def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    yaml.dump(data, file)


def slugify(text, stopwords = False):
  if stopwords:
    return slugify_(text, separator = '_', stopwords = STOPWORDS)
  return slugify_(text, separator = '_')
