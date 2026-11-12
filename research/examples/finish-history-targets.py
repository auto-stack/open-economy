"""Finish a few public edition targets, preserving failures and partial transcript status."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-20'
def job(sid,url,fmt,filename=None):
 d=ROOT/sid;d.mkdir(parents=True,exist_ok=True);lp=d/'acquisition-log.json';logs=json.loads(lp.read_text()) if lp.exists() else []
 try:
  r=requests.get(url,timeout=(10,45));rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code!=200 or (fmt=='pdf' and not r.content.startswith(b'%PDF-')):
   (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);logs.append(rec);lp.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed','http':r.status_code}
  name=filename or f'original.{fmt}';(d/name).write_bytes(r.content)
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser');main=soup.select_one('.pagetext') or soup.select_one('.mw-parser-output') or soup.find('main') or soup
   for t in main(['script','style','nav']):t.decompose()
   text=main.get_text('\n',strip=True);pages=None
  (d/(name+'.txt' if filename else 'extracted.txt')).write_text(text,encoding='utf-8');logs.append(rec);lp.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8')
  if not filename:
   mp=d/'metadata.json';m=json.loads(mp.read_text()) if mp.exists() else {'id':sid};m.update({'format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'research_date_local':'2026-11-12','read_scope':'Pending targeted reading',**rec});mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  return {'id':sid,'status':'archived','file':name,'pages':pages,'text_characters':len(text)}
 except Exception as ex:
  logs.append({'url':url,'error':str(ex)});lp.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed','error':str(ex)}
if __name__=='__main__':
 jobs=[('L97-cantillon-1755','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/285/Cantillon_0039_EBk_v6.0.pdf','pdf',None),('L96-von-glahn-2005','https://glia.ca/2014/money-art/pdfs/2_ORIGINS_GE1127_2014.pdf','pdf',None),('L90-knapp-1924','https://en.wikisource.org/wiki/Page:Georg_Freidrich_Knapp_-_The_State_Theory_of_Money_(1924_translation).pdf/18','html','page-18.html')]
 with ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(lambda args:job(*args),jobs):print(json.dumps(result),flush=True)
