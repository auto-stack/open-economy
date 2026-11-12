"""Preserve first acquisition failures and try ordinary alternate public copies."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
import importlib.util

spec=importlib.util.spec_from_file_location('acquire',Path(__file__).with_name('acquire-shared-commitment-sources.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
alternates={
 'L71-bratman-1992':['https://danielwharris.com/teaching/2020/303/readings/Bratman.pdf'],
 'L72-ostrom-walker-gardner-1992':['https://wtf.tw/ref/ostrom_1992.pdf'],
 'L74-hamann-et-al-2012':['https://sites.duke.edu/tomasellolabduke/files/2016/09/Hamann_etal_2012.x.pdf'],
}
def run(s):
 sid,title,authors,doi,pub,_=s;d=mod.ROOT/sid
 if (d/'metadata.json').exists() and (d/'original.pdf').exists():return {'id':sid,'status':'already_archived'}
 logpath=d/'acquisition-log.json';logs=json.loads(logpath.read_text())
 for url in alternates.get(sid,[]):
  try:
   r=requests.get(url,timeout=30);log={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   if r.status_code!=200 or not r.content.lstrip().startswith(b'%PDF-'):
    (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);log['validation']='failed_http_or_pdf_validation';logs.append(log);continue
   doc=fitz.open(stream=r.content,filetype='pdf');(d/'original.pdf').write_bytes(r.content)
   (d/'extracted.txt').write_text('\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc),encoding='utf-8')
   log['validation']='PDF header and parser passed';logs.append(log)
   meta={'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':'pdf','source_url':url,'pages':len(doc),'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights retained; local research archive, not redistribution permission.',**log}
   (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');logpath.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8')
   return {'id':sid,'status':'archived','pages':len(doc)}
  except Exception as ex:logs.append({'url':url,'error':str(ex)})
 logpath.write_text(json.dumps(logs,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed'}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(run,mod.SOURCES):print(json.dumps(result))
