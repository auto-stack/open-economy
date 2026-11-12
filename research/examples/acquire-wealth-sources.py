"""Acquire two bounded primary sources for the wealth-emergence research bridge."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-19'
SOURCES=[
 ('L83-smith-1776','An Inquiry into the Nature and Causes of the Wealth of Nations','Adam Smith',None,'First published 1776; Project Gutenberg ebook 3300, later text edition','https://www.gutenberg.org/files/3300/3300-h/3300-h.htm','html'),
 ('L84-romer-1990','Endogenous Technological Change','Paul M. Romer','10.1086/261725','Journal of Political Economy 98(5, Part 2) (1990),S71-S102','https://paulromer.net/posts/2015/pdf/Endogenous.pdf','pdf'),
]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(s):
 sid,title,author,doi,pub,url,fmt=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/f'original.{fmt}').exists():return {'id':sid,'status':'already_archived'}
 log=[]
 try:
  r=requests.get(url,timeout=35);rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code!=200 or (fmt=='pdf' and not r.content.lstrip().startswith(b'%PDF-')) or (fmt=='html' and 'Wealth of Nations' not in r.text):
   (d/'failed-response.bin').write_bytes(r.content);rec['validation']='failed_http_or_content';log.append(rec);save(d/'acquisition-log.json',log);return {'id':sid,'status':'failed','http':r.status_code}
  (d/f'original.{fmt}').write_bytes(r.content)
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser')
   for t in soup(['script','style','nav']):t.decompose()
   text=soup.get_text('\n',strip=True);pages=None
  (d/'extracted.txt').write_text(text,encoding='utf-8');rec['validation']='Expected format and parse checked';log.append(rec)
  save(d/'acquisition-log.json',log);save(d/'metadata.json',{'id':sid,'title':title,'authors':author,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights and distribution notices retained; see source file.',**rec})
  return {'id':sid,'status':'archived','pages':pages,'text_characters':len(text)}
 except Exception as ex:
  log.append({'url':url,'error':str(ex)});save(d/'acquisition-log.json',log);return {'id':sid,'status':'failed','error':str(ex)}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(run,SOURCES):print(json.dumps(result),flush=True)
