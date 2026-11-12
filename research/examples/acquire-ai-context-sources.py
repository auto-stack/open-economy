"""Archive primary sources for a bounded framework and AI/robotics evidence audit."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-18'
SOURCES=[
 ('L79-acemoglu-restrepo-2019','Automation and New Tasks: How Technology Displaces and Reinstates Labor','Daron Acemoglu; Pascual Restrepo','10.1257/jep.33.2.3','Journal of Economic Perspectives 33(2) (2019),3-30','https://economics.mit.edu/sites/default/files/publications/Automation%20and%20New%20Tasks%20-%20How%20Technology%20Displace.pdf','pdf','Automation'),
 ('L80-ilo-2025','Generative AI and Jobs: A Refined Global Index of Occupational Exposure','International Labour Organization research team',None,'ILO Working Paper 140; May 20, 2025','https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure','html','Generative AI and Jobs'),
 ('L81-brynjolfsson-li-raymond-2025','Generative AI at Work','Erik Brynjolfsson; Danielle Li; Lindsey R. Raymond','10.1093/qje/qjae044','The Quarterly Journal of Economics 140(2) (2025),889-942','https://academic.oup.com/qje/article/140/2/889/7990658','html','Generative AI at Work'),
 ('L82-ifr-2026','Five Million Robots now Operate in Factories Globally','International Federation of Robotics',None,'World Robotics 2026 official release; September 24, 2026; observations for 2025','https://ifr.org/ifr-press-releases/news/five-million-robots-now-operate-in-factories-globally','html','Five Million Robots'),
]
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def acquire(s):
 sid,title,authors,doi,pub,url,fmt,needle=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/f'original.{fmt}').exists():return {'id':sid,'status':'already_archived'}
 logpath=d/'acquisition-log.json';logs=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
 try:
  r=requests.get(url,timeout=35);rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  valid=r.status_code==200 and ((fmt=='pdf' and r.content.lstrip().startswith(b'%PDF-')) or (fmt=='html' and needle.lower() in r.text.lower() and len(r.content)>3000))
  if not valid:
   (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);rec['validation']='failed_http_or_expected_content';logs.append(rec);save(logpath,logs);return {'id':sid,'status':'failed','http':r.status_code}
  (d/f'original.{fmt}').write_bytes(r.content)
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser');main=soup.find('main') or soup
   for tag in main(['script','style','nav']):tag.decompose()
   text=main.get_text('\n',strip=True);pages=None
  (d/'extracted.txt').write_text(text,encoding='utf-8');rec['validation']='Expected content matched; parse completed';logs.append(rec);save(logpath,logs)
  save(d/'metadata.json',{'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights retained; local research archive, not redistribution permission.',**rec})
  return {'id':sid,'status':'archived','pages':pages,'text_characters':len(text)}
 except Exception as ex:
  logs.append({'url':url,'error':str(ex)});save(logpath,logs);return {'id':sid,'status':'failed','error':str(ex)}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
