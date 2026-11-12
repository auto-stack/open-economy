"""Retrieve explicitly linked public PDFs; keep actual editions and failure receipts."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-20'
JOBS=[
 ('L88-menger-1892','https://cdn.nakamotoinstitute.org/docs/on-the-origins-of-money.pdf'),
 ('L87-jevons-political-economy','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/625/Jevons_0237_EBk_v6.0.pdf'),
 ('L90-knapp-1924','https://commons.wikimedia.org/wiki/Special:FilePath/Georg%20Freidrich%20Knapp%20-%20The%20State%20Theory%20of%20Money%20%281924%20translation%29.pdf'),
 ('L86-marx-capital-1867','https://www.mit.edu/~allanmc/marx.capital.1.pdf'),
]
def run(job):
 sid,url=job;d=ROOT/sid;lp=d/'acquisition-log.json';logs=json.loads(lp.read_text()) if lp.exists() else []
 if (d/'original.pdf').exists():return {'id':sid,'status':'already_archived'}
 try:
  r=requests.get(url,timeout=30);rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code==200 and r.content.startswith(b'%PDF-'):
   doc=fitz.open(stream=r.content,filetype='pdf');(d/'original.pdf').write_bytes(r.content);text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);(d/'extracted.txt').write_text(text,encoding='utf-8')
   rec['validation']='PDF header and parser passed';mp=d/'metadata.json';m=json.loads(mp.read_text()) if mp.exists() else {'id':sid};m.update({'research_date_local':'2026-11-12','format':'pdf','pages':len(doc),'read_scope':'Pending targeted reading','sha256':hashlib.sha256(r.content).hexdigest(),'rights':'Original rights and source notices retained; actual edition to be checked.',**rec});mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');result={'id':sid,'status':'archived','pages':len(doc),'text_characters':len(text)}
  else:(d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);result={'id':sid,'status':'failed','http':r.status_code}
  logs.append(rec)
 except Exception as ex:logs.append({'url':url,'error':str(ex)});result={'id':sid,'status':'failed','error':str(ex)}
 lp.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8');return result
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(run,JOBS):print(json.dumps(r),flush=True)
