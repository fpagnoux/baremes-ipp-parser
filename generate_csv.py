#!/usr/bin/env python

import argparse
import logging

from openfisca_baremes_ipp import CountryTaxBenefitSystem
from bareme_ipp_parsers.csv import export_node_to_csv


tbs = CountryTaxBenefitSystem()

log = logging.getLogger(__name__)


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
  args = argparser.parse_args()

  logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING)

  for node in tbs.parameters.children.values():
    export_node_to_csv(node, '../csv-parsed')


if __name__ == "__main__":
    main()
