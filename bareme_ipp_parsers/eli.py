import datetime
import locale
import re
import urllib.request
import urllib.error
import http.client
import time                                                                                                                                                                    
from urllib.parse import quote
import sqlite3

locale.setlocale(locale.LC_TIME, "fr_FR")

db_conn  = sqlite3.connect('/Users/florianpagnoux/Dev/ipp/legi.py/legi.sqlite')
db_cursor = db_conn.cursor()

DATE_PATTERN = re.compile('(?:\d{1,2}\/){2}\d{4}')
DECRET = 'DECRET'
LOI = 'LOI'

def explicit_reference(reference):
    return DATE_PATTERN.sub(lambda match: explicit_date(match.group()), reference)

def explicit_date(date):
    return datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%d %B %Y')

def query_db(request):
    response = db_cursor.execute(request).fetchall()
    if not response:
        return 
    if len(response) > 1:
        import ipdb; ipdb.set_trace()
    return response[0][0]

def lookup_as_decret(reference):
    decret_decomp = get_decret_decomp(reference)
    if not decret_decomp:
        return
    return get_url_texte(DECRET, decret_decomp[0], decret_decomp[-1])

def lookup_as_loi(reference):
    loi_decomp = get_loi_decomp(reference)
    if not loi_decomp:
        return
    return get_url_texte(LOI, loi_decomp[0], loi_decomp[-1])

def lookup_as_arrete(reference):
    arrete_decomp = get_arreter_decomp(reference)

def get_url_texte(nature, texte_nb, article_nb):
    request = f"SELECT cid FROM textes_versions WHERE nature = '{nature}' AND num = '{texte_nb}';"
    cid = query_db(request)
    if not cid:
        return
    if not article_nb:
        return f"https://www.legifrance.gouv.fr/affichTexte.do?cidTexte={cid}"
    request_art = f"SELECT id FROM articles WHERE cid = '{cid}' AND num = ('{article_nb}') order by date_debut limit 1;"
    idArticle = query_db(request_art)
    if idArticle:
        return f"https://www.legifrance.gouv.fr/affichTexteArticle.do?idArticle={idArticle}&cidTexte={cid}"

def get_decret_decomp(reference):
    decret_decomp = re.findall('^Décret (\d{1,4}-\d+)(?:(?:(?: - )|(?:, )| )art. (\d+))?$', reference)
    if not decret_decomp:
        return

    return decret_decomp[0]  # decret_nb, article_nb

def get_loi_decomp(reference):
    loi_decomp = re.findall('^Loi (\d{1,4}-\d+)(?:(?:(?: - )|(?:, ))art. (\d+))?$', reference)
    if not loi_decomp:
        return
    return loi_decomp[0]  # loi_nb, article_nb

# def get_arrete_decomp(reference):


def get_eli(reference):
    decret_decomp = get_decret_decomp(reference)
    if decret_decomp:
        decret_nb, day, month, year = decret_decomp
        return f'eli/decret/{year}/{month}/{day}/{decret_nb}/jo/texte'
    loi_decomp = get_loi_decomp(reference)
    if loi_decomp:
        loi_nb, day, month, year, article_nb = get_loi_decomp()
        return f'eli/loi/{year}/{month}/{day}/{loi_nb}/jo/article_{article_nb}'

def lookup_eli(reference):
    eli = get_eli(reference)
    if not eli:
        return
    legifrance_eli = f'https://www.legifrance.gouv.fr/{eli}'

    print(f'Looking up Legifrance for {reference}')
    time.sleep(0.25)
    try:
        with urllib.request.urlopen(legifrance_eli) as response:
            if response.url not in {'https://www.legifrance.gouv.fr/initRechTexte.do', 'https://www.legifrance.gouv.fr/initRechExpTexteJorf.do'}:
                return response.url
    except urllib.error.HTTPError:
        pass
    except http.client.HTTPException:
        return lookup_eli(reference)
    
    import ipdb; ipdb.set_trace()

    eli_router_url = f'http://localhost:8080/legifrance/{eli}'
    eli_router_url = re.sub('/(\d)/', r'/0\1/', eli_router_url)
    
    time.sleep(0.25)
    try:
        with urllib.request.urlopen(eli_router_url) as response:
            return response.url
    except urllib.error.HTTPError:
        pass
    except http.client.HTTPException as error:
        return lookup_eli(reference)

def lookup_google(reference):
    decomp = re.findall('^Décret (\d{1,4}-\d+) du (\d{1,2}/\d{1,2}/\d{2,4})(?:(?:(?: - )|(?:, ))art. (\d+))?$', reference)
    if not decomp:
        return
    decret_nb, date, _ = decomp[0]
    date = explicit_date(date)
    query = f'Décret n°{decret_nb} du {date} site:https://www.legifrance.gouv.fr'
    time.sleep(2)
    result = query_google(query)
    if result:
        return result.split('&')[0]

def query_google(query):
    url = f"https://www.google.com/search?q={quote(query)}&num=1"                                                                                                                           
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        }
    )
    
    try:
        f = urllib.request.urlopen(req)
    except urllib.error.HTTPError as error:
        import ipdb; ipdb.set_trace()
        return
    print("Success requesting Google")
    content = f.read().decode('utf-8')
    result = re.findall('href=\"(https:\/\/www\.legifrance\.gouv\.fr(?:[^\"])*)', content)
    if result:
        return result[0]

def clean_reference(reference):
    reference = reference.replace(' ', ' ') # Remove unsecable space
    if ('(') in reference:
        reference = re.sub("[\(\[].*?[\)\]]", "", reference)
        reference = re.sub(' {2,}', ' ', reference)
    reference = re.sub(' du \d{1,2}/\d{1,2}/\d{2,4}', '', reference)
    reference = reference.replace(' , ', ', ')
    reference = re.sub('[I|V|X]+', '', reference)
    reference = re.sub('\d+°', '', reference)
    reference = re.sub('§\d+', '', reference)
    reference = reference.strip('. ,-')
    return reference

def find_url(reference):
    # url = lookup_as_decret(reference)
    # cleaned_reference = clean_reference(reference)
    # url = lookup_as_decret(cleaned_reference)
    # if url:
    #     return url
    # url = lookup_as_loi(cleaned_reference)
    # if url:
    #     return url
    # url = lookup_google(reference)
    return url
    # reference = explicit_reference(reference)
    # return lookup_google(reference)