"""Acquire a bounded primary-source set on shared plans and revisable commitments."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-15'
SOURCES=[
 ('L71-bratman-1992','Shared Cooperative Activity','Michael E. Bratman','10.2307/2185537','The Philosophical Review 101(2) (1992),327-341',['https://danielwharris.com/teaching/fall23/readings/BratmanShared.pdf']),
 ('L72-ostrom-walker-gardner-1992','Covenants With and Without a Sword: Self-Governance Is Possible','Elinor Ostrom; James Walker; Roy Gardner','10.2307/1964229','American Political Science Review 86(2) (1992),404-417',['https://www.wtf.tw/ref/ostrom_1992.pdf']),
 ('L73-hart-moore-1988','Incomplete Contracts and Renegotiation','Oliver Hart; John Moore','10.2307/1912698','Econometrica 56(4) (1988),755-785',['https://www.edegan.com/pdfs/Hart%20Moore%20%281988%29%20-%20Incomplete%20Contracts%20and%20Renegotiation.pdf']),
 ('L74-hamann-et-al-2012','Children\u2019s Developing Commitments to Joint Goals','Katharina Hamann; Felix Warneken; Michael Tomasello','10.1111/j.1467-8624.2011.01695.x','Child Development 83(1) (2012),137-145',['https://www.eva.mpg.de/documents/Wiley-Blackwell/Hamann_Children_ChildDev_2012_1562278.pdf']),
]

def acquire(s):
 sid,title,authors,doi,pub,urls=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/'metadata.json').exists() and (d/'original.pdf').exists():return {'id':sid,'status':'already_archived'}
 logpath=d/'acquisition-log.json'
 attempts=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
 for i,url in enumerate(urls,1):
  try:
   r=requests.get(url,timeout=35)
   log={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   if r.status_code!=200 or not r.content.lstrip().startswith(b'%PDF-'):
    (d/f'failed-response-{len(attempts)+1}.bin').write_bytes(r.content);log['validation']='failed_http_or_pdf_validation';attempts.append(log);continue
   doc=fitz.open(stream=r.content,filetype='pdf');(d/'original.pdf').write_bytes(r.content)
   (d/'extracted.txt').write_text('\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc),encoding='utf-8');log['validation']='PDF header and parser passed';attempts.append(log)
   m={'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':'pdf','source_url':url,'pages':len(doc),'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights retained; local research archive, not redistribution permission.',**log}
   (d/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(d/'acquisition-log.json').write_text(json.dumps(attempts,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'archived','pages':len(doc),'bytes':len(r.content)}
  except Exception as ex:attempts.append({'url':url,'error':str(ex)})
 (d/'acquisition-log.json').write_text(json.dumps(attempts,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed','attempts':attempts}

if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
