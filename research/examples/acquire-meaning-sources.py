"""Archive bounded primary scholarship on authority, meaning and meaningful work."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-16'
SOURCES=[
 ('L75-tyler-2006','Psychological Perspectives on Legitimacy and Legitimation','Tom R. Tyler','10.1146/annurev.psych.57.102904.190038','Annual Review of Psychology 57 (2006),375-400','https://openscholar.huji.ac.il/sites/default/files/law/files/tyler_2006_psychological_perspectives_on_legit_1.pdf','pdf'),
 ('L76-wolf-2007','Meaning in Life and Why It Matters, Lectures I and II','Susan Wolf',None,'Tanner Lectures, Princeton University, November 7-8, 2007; official transcript, distinct from 2010 book','https://tannerlectures.org/documents/meaning-in-life-and-why-it-matters/','html'),
 ('L77-martela-steger-2016','The Three Meanings of Meaning in Life: Distinguishing Coherence, Purpose, and Significance','Frank Martela; Michael F. Steger','10.1080/17439760.2015.1137623','The Journal of Positive Psychology 11(5) (2016),531-545','https://www.its.caltech.edu/~squartz/Martela-Steger-JOPP.pdf','pdf'),
 ('L78-martela-riekki-2018','Autonomy, Competence, Relatedness, and Beneficence: A Multicultural Comparison of the Four Pathways to Meaningful Work','Frank Martela; Tapani J. J. Riekki','10.3389/fpsyg.2018.01157','Frontiers in Psychology 9 (2018),1157','https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.01157/full','html'),
]
def acquire(s):
 sid,title,authors,doi,pub,url,fmt=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True);logpath=d/'acquisition-log.json'
 if (d/f'original.{fmt}').exists():return {'id':sid,'status':'already_archived'}
 logs=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
 try:
  r=requests.get(url,timeout=35);log={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  valid=r.status_code==200 and ((fmt=='pdf' and r.content.lstrip().startswith(b'%PDF-')) or (fmt=='html' and title.split(',')[0].lower() in r.text.lower()))
  if not valid:
   (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);log['validation']='failed_http_or_content_validation';logs.append(log);save(logpath,logs);return {'id':sid,'status':'failed','http':r.status_code}
  (d/f'original.{fmt}').write_bytes(r.content)
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');extracted='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser');main=soup.find('main') or soup
   for tag in main(['script','style','nav']):tag.decompose()
   extracted=main.get_text('\n',strip=True);pages=None
  (d/'extracted.txt').write_text(extracted,encoding='utf-8');log['validation']='Expected content checked; PDF parser or HTML text extraction passed';logs.append(log);save(logpath,logs)
  meta={'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights retained; local research archive, not redistribution permission.',**log};save(d/'metadata.json',meta)
  return {'id':sid,'status':'archived','pages':pages,'text_characters':len(extracted)}
 except Exception as ex:
  logs.append({'url':url,'error':str(ex)});save(logpath,logs);return {'id':sid,'status':'failed','error':str(ex)}
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
