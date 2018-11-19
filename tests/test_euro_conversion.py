from openfisca_core.periods import period
from openfisca_baremes_ipp import CountryTaxBenefitSystem

from bareme_ipp_parsers.csv import unit_at

tbs = CountryTaxBenefitSystem()
param = tbs.parameters.prelevements_sociaux.autres_taxes_participations_assises_salaires.taxsal.plafond1
def test_unit_at():
  # assert unit_at(param, period('2001-12')) == 'currency-FRF'
  assert unit_at(param, period('2003-01')) == 'currency-EUR'
  assert unit_at(param, period('2002-01')) == 'currency-EUR'
