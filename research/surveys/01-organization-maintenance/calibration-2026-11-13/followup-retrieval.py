"""Sequential retries and alternate author/institutional copies; preserve initial attempts."""
from pathlib import Path
import datetime, hashlib, json, urllib.request, urllib.parse, time
import fitz
ROOT=Path(__file__).resolve().parents[4]; RAW=ROOT/'wiki/raw/round-39'; DISC=RAW/'discovery'
if (DISC/'followup-retrieval-log.json').exists():
    raise SystemExit('Follow-up archive exists. Use a new attempt log/batch, preserving this one.')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (OpenEconomy literature research)'})
    with urllib.request.urlopen(req,timeout=30) as r: return r.read(),r.status,r.geturl(),r.headers.get('Content-Type')
attempts=[]
tasks=[
 ('L195-conant-ashby-1970','journal-scan.pdf','https://theisticscience.com/papers/tree/BioRegulation/Conant-IJSS1970.pdf'),
 ('L196-bechtel-bich-2024','original.pdf','https://pmc.ncbi.nlm.nih.gov/articles/PMC11613639/pdf/'),
 ('L196-bechtel-bich-2024','author-copy.pdf','https://mechanism.ucsd.edu/research/Bechtel.Bich.2024.Situatinghomeostasisinorganisms.pdf'),
 ('L197-cross-hohenberg-1993','original.pdf','https://moodle.uni-saarland.de/pluginfile.php/784115/mod_page/content/37/CRO93.pdf'),
 ('L196-bechtel-bich-2024','original.html','https://pmc.ncbi.nlm.nih.gov/articles/PMC11613639/'),
]
for dirname,filename,url in tasks:
    rec={'source':dirname,'url':url,'filename':filename,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        data,status,final,ctype=fetch(url); rec.update(status=status,final_url=final,content_type=ctype,bytes=len(data))
        if filename.endswith('.pdf') and not data.startswith(b'%PDF'): raise ValueError('Not PDF; success response not archived as original')
        p=RAW/dirname/filename;p.write_bytes(data);rec.update(sha256=hashlib.sha256(data).hexdigest(),saved=str(p.relative_to(RAW)))
        if filename.endswith('.pdf'):
            doc=fitz.open(stream=data,filetype='pdf');rec['pdf_pages']=len(doc)
            p.with_suffix('.txt').write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+page.get_text() for i,page in enumerate(doc)),encoding='utf-8')
    except Exception as e: rec['error']=repr(e)
    attempts.append(rec)
    (DISC/'followup-retrieval-log.json').write_text(json.dumps(attempts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for q in json.loads((DISC/'query-log.json').read_text(encoding='utf-8')):
    if q.get('status')==200: continue
    time.sleep(2)
    rec={'id':q['id'],'url':q['url'],'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'retry same calibration request, not extra search'}
    try:
        data,status,final,ctype=fetch(q['url']);p=DISC/(q['id']+'-retry-response.json');p.write_bytes(data)
        msg=json.loads(data)['message'];rec.update(status=status,final_url=final,response=p.name,returned=len(msg['items']),reported_total=msg['total-results'],sha256=hashlib.sha256(data).hexdigest())
    except Exception as e:rec.update(error=repr(e),returned=0)
    attempts.append(rec)
    (DISC/'followup-retrieval-log.json').write_text(json.dumps(attempts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(attempts,ensure_ascii=False,indent=2))
