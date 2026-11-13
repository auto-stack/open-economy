"""Archive primary-source material and exact acquisition responses for this research round."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import urllib.request
import urllib.error
import datetime
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'wiki/raw/round-47'
LOG = RAW / 'download-log.json'


def fetch(spec):
    relative, url, expected = spec
    dest = RAW / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = {'path': relative, 'requested_url': url, 'expected': expected,
              'retrieved_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenEconomyResearch/0.1 (public scholarly literature archival)'})
        with urllib.request.urlopen(req, timeout=45) as response:
            content = response.read()
            result.update(status_code=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'))
        dest.write_bytes(content)
        ok = (content.startswith(b'%PDF-') if expected == 'PDF' else
              b'<collection' in content if expected == 'BioC XML' else
              b'<PubmedArticleSet' in content if expected == 'PubMed XML' else
              b'<html' in content.lower() or b'<!doctype html' in content.lower())
        result.update(bytes=len(content), sha256=hashlib.sha256(content).hexdigest(),
                      classified_as_expected=ok, saved=True)
    except urllib.error.HTTPError as exc:
        content = exc.read()
        error_path = dest.with_name(dest.name + '.http-error.txt')
        error_path.write_bytes(content)
        result.update(status_code=exc.code, error=str(exc), saved=False,
                      error_body_path=str(error_path.relative_to(RAW)).replace('\\', '/'))
    except Exception as exc:
        result.update(error=str(exc), saved=False)
    return result


if __name__ == '__main__':
    if LOG.exists():
        raise SystemExit('Acquisition log already exists. Preserve it; log any additional requests separately and append explicitly.')
    specs = [
        ('L225-sandve-et-al-2013/original.pdf',
         'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1003285&type=printable', 'PDF'),
        ('L225-sandve-et-al-2013/publication-record.html',
         'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285', 'HTML'),
        ('L226-wilkinson-et-al-2016/original.pdf',
         'https://www.nature.com/articles/sdata201618.pdf', 'PDF'),
        ('L226-wilkinson-et-al-2016/publication-record.html',
         'https://www.nature.com/articles/sdata201618', 'HTML'),
        ('L227-hardwicke-et-al-2018/bioc.xml',
         'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC6124055/unicode', 'BioC XML'),
        ('L228-nosek-et-al-2018/bioc.xml',
         'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC5856500/unicode', 'BioC XML'),
        ('discovery/pubmed-records.xml',
         'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=24204232,26978244,30225032,29531091&retmode=xml', 'PubMed XML'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, specs))
    LOG.write_bytes((json.dumps(results, ensure_ascii=False, indent=2) + '\n').encode())
    for result in results:
        print(json.dumps({k: result[k] for k in ['path', 'status_code', 'saved', 'classified_as_expected', 'error'] if k in result}))
    for p in RAW.glob('L*/original.pdf'):
        if p.read_bytes().startswith(b'%PDF-'):
            import fitz
            doc = fitz.open(p)
            p.with_suffix('.txt').write_bytes('\n\n'.join(f'=== PDF {i + 1} ===\n{page.get_text()}' for i, page in enumerate(doc)).encode())
            print(p.parent.name, 'PDF pages',len(doc))
    for p in RAW.glob('L*/bioc.xml'):
        try:
            doc = ET.parse(p)
            parts = [f'=== passage {i} ===\n{q.findtext("text", "")}' for i, q in enumerate(doc.findall('.//passage'))]
            p.with_suffix('.txt').write_bytes('\n\n'.join(parts).encode())
            print(p.parent.name, 'BioC passages',len(parts))
        except ET.ParseError:
            print(p.parent.name, 'Not parseable BioC; do not adopt')
