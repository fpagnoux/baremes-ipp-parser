from bareme_ipp_parsers.eli import explicit_reference, explicit_date, find_url, clean_reference

def test_date():
    assert explicit_date("29/03/2014") == "29 mars 2014"
    assert explicit_date("12/07/1994") == "12 juillet 1994"

def test_simple():
    assert explicit_reference("Décret 94-627 du 22/07/1994") == "Décret 94-627 du 22 juillet 1994"

def test_double():
    assert explicit_reference("Arrêté du 21/08/1988 portant agrément de la convention du 06/07/1988") == "Arrêté du 21 août 1988 portant agrément de la convention du 06 juillet 1988"

def test_decret():
    assert find_url("Décret 87-1175 du 24/12/1987") is not None

def test_decret_art():
    assert find_url("Décret 2001-1203 du 17/12/2001 - art. 25") is not None

def test_decret_art_2():
    assert find_url("Décret 2001-1203 du 17/12/2001, art. 25") is not None

def test_ignore_par():
    assert find_url("Loi 2014-1554 du 22/12/2014 (LFSS pour 2015) - art. 22") is not None

def test_1():
    assert find_url("Loi 2014-1654 du 29/12/2014 (LF pour 2015)") is not None

# def test_2():
#     assert find_url("Loi 2018-1317, art. 2 du 28/12/2018 (LF pour 2019)")

def test_cleaning():
    assert clean_reference("Loi 2018-1317, art. 2 du 28/12/2018 (LF pour 2019)") == "Loi 2018-1317, art. 2"
    