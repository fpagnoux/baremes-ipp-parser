#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

from deepmerge import always_merger
from bareme_ipp_parsers.commons import export_yaml, yaml


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument('input_dir')
  argparser.add_argument('output_dir')
  argparser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
  args = argparser.parse_args()
  merge_dir(args.input_dir, args.output_dir)


def merge_dir(input_dir, output_dir):
  for file_or_dict in os.listdir(input_dir):
    input_sub_path = os.path.join(input_dir, file_or_dict)
    output_sub_path = os.path.join(output_dir, file_or_dict)
    if os.path.isdir(input_sub_path):
      merge_dir(input_sub_path  , output_sub_path)
    else:
      merge_file(input_sub_path, output_sub_path)

def merge_file(input_file, output_file):
  with open(input_file) as file:
    input_dict = yaml.load(file)
  with open(output_file) as file:
    output_dict = yaml.load(file)
  merged_dict = always_merger.merge(output_dict, input_dict)
  export_yaml(merged_dict, output_file)

if __name__ == "__main__":
    main()
