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

def test_cleaning():
    assert clean_reference("Loi 2018-1317, art. 2 du 28/12/2018 (LF pour 2019)") == "Loi 2018-1317, art. 2"

def test_cleaning_2():
    assert clean_reference('Loi 2017-1837 du 30/12/2017 (LF pour 2018), art. 86') == 'Loi 2017-1837, art. 86'
    
def test_cleaning_3():
    assert clean_reference('Loi 2017-1837 du 30/12/2017, art. 31 (LF pour 2018) (crée art. 885-0 V bis et885-0 V bis A du CGI).') == 'Loi 2017-1837, art. 31'

def test_cleaning_4():
    assert clean_reference('Loi 2005-1719, art. 154, du 30/12/2005') == 'Loi 2005-1719, art. 154'
    
def test_cleaning_5():
    assert clean_reference('Décret 2004-144 du 13/02/2004, art. 5-II') == 'Décret 2004-144, art. 5'
    assert clean_reference('Décret 2014-1531 du 17/12/2014, art. 4, 1°') == 'Décret 2014-1531, art. 4'
    assert clean_reference('Décret 97-222 du 1997-03-13 art. 2 I, II') == 'Décret 97-222 du 1997-03-13 art. 2' # TODO: Check it is parsed!!
    assert clean_reference('Décret 45-0179 du 29/12/1945, art. 71, §2') == 'Décret 45-0179, art. 71'

def test_ignore_par():
    assert find_url("Loi 2014-1554 du 22/12/2014 (LFSS pour 2015) - art. 22") is not None

def test_1():
    assert find_url("Loi 2014-1654 du 29/12/2014 (LF pour 2015)") is not None

def test_2():
    assert find_url("Loi 2018-1317, art. 2 du 28/12/2018 (LF pour 2019)") == 'https://www.legifrance.gouv.fr/affichTexteArticle.do?idArticle=LEGIARTI000037935215&cidTexte=JORFTEXT000037882341'

def test_3():
    assert find_url("Loi 2017-1837 du 30/12/2017 (LF pour 2018), art. 86") is not None

def test_4():
    assert find_url("Décret 2007-1056 du 28/06/2007.") is not None

def test_5():
    find_url('Décret 62-440 du 14/04/1962')