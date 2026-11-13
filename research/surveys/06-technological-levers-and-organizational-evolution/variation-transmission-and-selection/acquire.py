"""Archive primary documents for the first evolution-mechanisms research round."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'wiki/raw/round-52'


def fetch(item):
    name, url, expected = item
    path = RAW / name
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {'path': name, 'requested_url': url, 'expected': expected,
             'retrieved_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as response:
            body = response.read()
            entry.update(status_code=response.status, final_url=response.url,
                         content_type=response.headers.get('Content-Type'))
        path.write_bytes(body)
        entry.update(saved=True, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        if expected == 'PDF':
            entry['valid_document'] = body.startswith(b'%PDF-')
        elif expected == 'PubMed XML':
            entry['valid_document'] = b'<PubmedArticleSet' in body
        else:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, 'html.parser')
            title = soup.title.get_text(' ', strip=True) if soup.title else ''
            entry['title'] = title
            entry['valid_document'] = ('Partial connectivity' in title or 'The cultural niche' in title)
    except urllib.error.HTTPError as error:
        body = error.read()
        path = path.with_name(path.name + '.http-error.txt')
        path.write_bytes(body)
        entry.update(saved=False, status_code=error.code, error_body=str(path.relative_to(RAW)).replace('\\', '/'))
    except Exception as error:
        entry.update(saved=False, error=str(error))
    return entry


if __name__ == '__main__':
    log = RAW / 'download-log.json'
    if log.exists():
        raise SystemExit('Existing acquisition log retained; append separately logged follow-up requests.')
    requests = [
        ('L229-lewontin-1970/original.pdf', 'https://www.zoology.ubc.ca/let/pdfs/Lewontin1970.pdf', 'PDF'),
        ('L230-mesoudi-thornton-2018/original.pdf', 'https://www.alexmesoudi.com/publication/mesoudi-what-2018/Mesoudi_Thornton_ProcB_2018.pdf', 'PDF'),
        ('L231-derex-boyd-2016/original.html', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4801235/', 'HTML'),
        ('L232-ostrom-basurto-2011/original.pdf', 'https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/CraftingAnalyticalToolsInstitutionalChange.LOstrom2011.pdf', 'PDF'),
        ('L179-boyd-richerson-henrich-2011/original.html', 'https://pmc.ncbi.nlm.nih.gov/articles/3131818/', 'HTML'),
        ('discovery/pubmed-records.xml', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29899071,21690340&retmode=xml', 'PubMed XML'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, requests))
    log.write_bytes((json.dumps(results, ensure_ascii=False, indent=2) + '\n').encode())
    for result in results:
        print(json.dumps({k: result[k] for k in ['path', 'status_code', 'valid_document', 'error'] if k in result}))
    import fitz
    for p in RAW.glob('L*/original.pdf'):
        if p.read_bytes().startswith(b'%PDF-'):
            doc = fitz.open(p)
            p.with_suffix('.txt').write_bytes('\n\n'.join(f'=== PDF {i+1} ===\n{page.get_text()}' for i, page in enumerate(doc)).encode())
            print(p.parent.name, 'pages', len(doc))
    from bs4 import BeautifulSoup
    for p in RAW.glob('L*/original.html'):
        soup = BeautifulSoup(p.read_bytes(), 'html.parser')
        main = soup.find('section', class_='body main-article-body') or soup.find('article') or soup.find('main')
        if main:
            p.with_suffix('.txt').write_bytes(main.get_text('\n', strip=True).encode())
            print(p.parent.name, 'body characters', len(main.get_text()))
