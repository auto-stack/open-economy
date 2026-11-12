"""Archive primary-source PDFs for the needs, feelings and goals discussion."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-13'
SOURCES=[
 ('L63-garfinkel-et-al-2015','Knowing Your Own Heart: Distinguishing Interoceptive Accuracy from Interoceptive Awareness','Sarah N. Garfinkel; Anil K. Seth; Adam B. Barrett; Keisuke Suzuki; Hugo D. Critchley','10.1016/j.biopsycho.2014.11.004','Biological Psychology 104 (2015),65-74','https://scienceofbehaviorchange.org/wp-content/uploads/2017/11/Garfinkel-et-al.-2015-Knowing-your-own-heart-Distinguishing-interoceptive-accuracy-from-interoceptive-awareness.pdf'),
 ('L64-berridge-robinson-2016','Liking, Wanting, and the Incentive-Sensitization Theory of Addiction','Kent C. Berridge; Terry E. Robinson','10.1037/amp0000059','American Psychologist 71(8) (2016),670-679','https://sites.lsa.umich.edu/berridge-lab/wp-content/uploads/sites/743/2019/10/2016-Berridge-Robinson-Liking-wanting-IS-theory-of-addiction-Am-Psychol.pdf'),
 ('L65-schultz-dayan-montague-1997','A Neural Substrate of Prediction and Reward','Wolfram Schultz; Peter Dayan; P. Read Montague','10.1126/science.275.5306.1593','Science 275(5306) (1997),1593-1599','https://www.gatsby.ucl.ac.uk/~dayan/papers/sdm97.pdf'),
 ('L66-desmedt-et-al-2018','The Heartbeat Counting Task Largely Involves Non-Interoceptive Processes: Evidence from Both the Original and an Adapted Counting Task','Olivier Desmedt; Olivier Luminet; Olivier Corneille','10.1016/j.biopsycho.2018.09.004','Biological Psychology 138 (2018),185-188','https://www.uclep.be/labs/ARL/publications/Desmedt%20et%20al._2018.pdf'),
]

def acquire(s):
 sid,title,authors,doi,publication,url=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/'metadata.json').exists():return {'id':sid,'status':'already_archived'}
 try:
  r=requests.get(url,timeout=55)
  record={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code!=200 or not r.content.lstrip().startswith(b'%PDF-'):
   (d/'failed-response.bin').write_bytes(r.content);record['validation']='failed_pdf_or_http_validation'
   (d/'acquisition-log.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed',**record}
  doc=fitz.open(stream=r.content,filetype='pdf')
  (d/'original.pdf').write_bytes(r.content)
  (d/'extracted.txt').write_text('\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc),encoding='utf-8')
  record['validation']='PDF header and parser passed'
  meta={'id':sid,'title':title,'authors':authors,'doi':doi,'publication':publication,'research_date_local':'2026-11-12','source_url':url,'format':'pdf','pages':len(doc),'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading; extraction is not reading.','rights':'Original rights retained; local research archive, not redistribution permission.',**record}
  (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  (d/'acquisition-log.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
  return {'id':sid,'status':'archived','pages':len(doc),'bytes':len(r.content)}
 except Exception as ex:
  record={'url':url,'error':str(ex)};(d/'acquisition-log.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed',**record}

if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
