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


yaml.default_flow_style = False
yaml.representer.add_representer(type(None), represent_none)


def export_yaml(data, file_path):
  with open(file_path, 'w') as file:
    # from nose.tools import set_trace; set_trace(); import ipdb; ipdb.set_trace()
    yaml.dump(data, file)


def slugify(text, stopwords = False):
  if stopwords:
    return slugify_(text, separator = '_', stopwords = STOPWORDS)
  return slugify_(text, separator = '_')
