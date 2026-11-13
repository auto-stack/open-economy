"""Bounded retrieval calibration, not a systematic search or automated eligibility screen."""
from pathlib import Path
import concurrent.futures, datetime, hashlib, json, urllib.request, urllib.parse
import fitz

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'wiki/raw/round-39'
DISC = RAW / 'discovery'
DISC.mkdir(parents=True, exist_ok=True)
if (DISC / 'query-log.json').exists():
    raise SystemExit('This archived run already exists. Use a new batch; do not overwrite it.')
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'OpenEconomyResearch/0.2 (local literature calibration)', 'Accept':'*/*'})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read(), r.status, r.geturl(), r.headers.get('Content-Type','')

QUERIES=[
 ('P-broad','physics','query.bibliographic','dissipative structures nonequilibrium organization',10),
 ('P-title','physics','query.title','dissipative structures stability',10),
 ('C-broad','control','query.bibliographic','cybernetics regulation viability self-maintenance',10),
 ('C-title','control','query.title','cybernetics regulation good regulator',10),
 ('B-broad','biology','query.bibliographic','biological organisation closure constraints autonomy',10),
 ('B-title','biology','query.title','biological organisation closure constraints',10),
 ('C-seed','control','query.title','Every good regulator of a system must be a model of that system',1),
]
def query(q):
    qid,branch,field,term,rows=q
    params={field:term,'rows':rows,'filter':'until-pub-date:2026-11-13'}
    url='https://api.crossref.org/works?'+urllib.parse.urlencode(params)
    rec={'id':qid,'branch':branch,'platform':'Crossref REST','time_utc':stamp(),'url':url,'params':params,'sort':'default relevance','pagination':'first page only; no cursor traversal','purpose':'calibration, not formal search'}
    try:
        data,status,final,ctype=get(url)
        p=DISC/(qid+'-response.json'); p.write_bytes(data)
        msg=json.loads(data)['message']
        rec.update(status=status,final_url=final,reported_total=msg['total-results'],returned=len(msg['items']),response=p.name,sha256=hashlib.sha256(data).hexdigest())
    except Exception as e: rec.update(error=repr(e),returned=0)
    return rec
logs=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(query,QUERIES))
save(DISC/'query-log.json',logs)

SOURCES=[
 ('L195-conant-ashby-1970','10.1080/00207727008920220',1970,[
 'https://pespmc1.vub.ac.be/books/Conant_Ashby.pdf',
 'https://theisticscience.com/papers/tree/BioRegulation/Conant-IJSS1970.pdf']),
 ('L196-bechtel-bich-2024','10.1113/JP286883',2024,[
 'https://philsci-archive.pitt.edu/24047/1/Bechtel%2C%20Bich%20-%202024%20-%20Situating%20homeostasis%20in%20organisms%20maintaining%20organization%20through%20time.pdf',
 'https://onlinelibrary.wiley.com/doi/pdfdirect/10.1113/JP286883']),
 ('L197-cross-hohenberg-1993','10.1103/RevModPhys.65.851',1993,[
 'https://www.damtp.cam.ac.uk/user/gold/pdfs/teaching/old_literature/CrossHohenberg1993.pdf',
 'https://journals.aps.org/rmp/pdf/10.1103/RevModPhys.65.851']),
]
def source(s):
    dirname,doi,year,urls=s
    dest=RAW/dirname; dest.mkdir(parents=True,exist_ok=True)
    attempts=[]; meta={'id':dirname.split('-')[0],'doi':doi,'original_publication_year':year,'fetched_at_utc':stamp(),'read_scope':'pending; see subsequent read-scope record','role':'pilot source; not formal inclusion'}
    for url in urls:
        rec={'requested_url':url,'time_utc':stamp()}
        try:
            data,status,final,ctype=get(url)
            rec.update(status=status,final_url=final,content_type=ctype,bytes=len(data))
            if not data.startswith(b'%PDF'): raise ValueError('Not a PDF; not stored as original.pdf')
            (dest/'original.pdf').write_bytes(data)
            doc=fitz.open(stream=data,filetype='pdf')
            (dest/'extracted.txt').write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+p.get_text() for i,p in enumerate(doc)),encoding='utf-8')
            meta.update(download_url=url,final_url=final,sha256=hashlib.sha256(data).hexdigest(),pdf_pages=len(doc),bytes=len(data))
            attempts.append(rec); break
        except Exception as e: rec['error']=repr(e); attempts.append(rec)
    save(dest/'download-log.json',attempts);save(dest/'metadata.json',meta)
    return meta
sources=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(source,SOURCES))

# Probe availability only: no claims of a completed search in these indexes.
probes=[]
for name,url in [
 ('OpenAlex','https://api.openalex.org/works?search=organizational%20closure&per-page=1'),
 ('PubMed','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=10.1113%2FJP286883%5BAID%5D&retmode=json'),
 ('arXiv','https://export.arxiv.org/api/query?search_query=all%3Adissipative%20AND%20all%3Astructures&start=0&max_results=1')]:
    rec={'platform':name,'url':url,'time_utc':stamp(),'purpose':'availability/known-work probe only; not formal screening pool'}
    try:
        data,status,final,ctype=get(url); p=DISC/(name.lower()+'-probe-response.txt'); p.write_bytes(data)
        rec.update(status=status,final_url=final,response=p.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    except Exception as e: rec['error']=repr(e)
    probes.append(rec)
save(DISC/'availability-probes.json',probes)
print(json.dumps({'queries':logs,'sources':sources,'probes':probes},ensure_ascii=False,indent=2))
