# -*- coding: utf-8 -*-

from nose.tools import assert_equal

from bareme_ipp_parsers.sheets import contract

def test_contract():
  values = {
  '2018-01-01': {'value': 200},
  '2017-01-01': {'value': 200},
  '2016-01-01': {'value': 200, 'reference': 'http://low.gov/example'},
  '2015-01-01': {'value': 100},
  '2014-01-01': {'value': 100},
  }

  assert_equal(contract(values), {
    '2017-01-01': {'value': 200},
    '2016-01-01': {'value': 200, 'reference': 'http://low.gov/example'},
    '2014-01-01': {'value': 100},
  })

