"""Try public alternate copies while retaining prior failures and actual versions."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

spec=importlib.util.spec_from_file_location('acquire',Path(__file__).with_name('acquire-wealth-money-history.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ALT={
 'L86-marx-capital-1867':('https://marxists.pages.dev/archive/marx/works/1867-c1/ch01.htm','html'),
 'L87-jevons-political-economy':('https://oll.libertyfund.org/titles/jevons-the-theory-of-political-economy?html=true','html'),
 'L89-innes-1913':('https://moslereconomics.com/mandatory-readings/what-is-money/','html'),
 'L90-knapp-1924':('https://socialsciences.mcmaster.ca/econ/ugcm/3ll3/knapp/StateTheoryMoney.pdf','pdf'),
 'L92-grierson-origins':('https://dokumen.pub/the-origins-of-money-0485141159.html','html'),
}
def run(s):
 sid,title,author,pub,_,_=s;d=mod.ROOT/sid
 if (d/'original.pdf').exists() or (d/'original.html').exists():return {'id':sid,'status':'already_archived'}
 if sid not in ALT:
  if sid in ['L96-von-glahn-2005','L97-cantillon-1755']:return mod.acquire(s)
  return {'id':sid,'status':'no_new_attempt'}
 url,fmt=ALT[sid];d.mkdir(parents=True,exist_ok=True);lp=d/'acquisition-log.json';logs=json.loads(lp.read_text()) if lp.exists() else []
 try:
  r=requests.get(url,timeout=30);rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code!=200 or (fmt=='pdf' and not r.content.startswith(b'%PDF-')) or (fmt=='html' and len(r.content)<3000):
   (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);logs.append(rec);mod.save(lp,logs);return {'id':sid,'status':'failed','http':r.status_code}
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser')
   for t in soup(['script','style','nav']):t.decompose()
   text=(soup.find('main') or soup).get_text('\n',strip=True);pages=None
  (d/f'original.{fmt}').write_bytes(r.content);(d/'extracted.txt').write_text(text,encoding='utf-8');rec['validation']='Parsed; content and actual version pending inspection';logs.append(rec);mod.save(lp,logs)
  mod.save(d/'metadata.json',{'id':sid,'title':title,'authors':author,'publication':pub,'research_date_local':'2026-11-12','format':fmt,'pages':pages,'read_scope':'Pending targeted reading','sha256':hashlib.sha256(r.content).hexdigest(),'rights':'Original rights and source notices retained; local research archive.',**rec})
  return {'id':sid,'status':'archived','pages':pages,'text_characters':len(text)}
 except Exception as ex:
  logs.append({'url':url,'error':str(ex)});mod.save(lp,logs);return {'id':sid,'status':'failed','error':str(ex)}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(run,mod.SOURCES):print(json.dumps(result),flush=True)
