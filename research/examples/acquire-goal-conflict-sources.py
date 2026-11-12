"""Acquire primary studies and a theoretical review for goal conflict research."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-14'
SOURCES=[
 ('L67-shenhav-et-al-2013','The Expected Value of Control: An Integrative Theory of Anterior Cingulate Cortex Function','Amitai Shenhav; Matthew M. Botvinick; Jonathan D. Cohen','10.1016/j.neuron.2013.07.007','Neuron 79(2) (2013),217-240','https://www.princeton.edu/~ashenhav/Publications_Presentations_files/Neuron%202013%20Shenhav.pdf'),
 ('L69-wrosch-et-al-2003','Adaptive Self-Regulation of Unattainable Goals: Goal Disengagement, Goal Reengagement, and Subjective Well-Being','Carsten Wrosch; Michael F. Scheier; Gregory E. Miller; Richard Schulz; Charles S. Carver','10.1177/0146167203256921','Personality and Social Psychology Bulletin 29(12) (2003),1494-1508','https://www.cmu.edu/dietrich/psychology/pdf/scales/GAS_article.pdf'),
 ('L70-gollwitzer-brandstaetter-1997','Implementation Intentions and Effective Goal Pursuit','Peter M. Gollwitzer; Veronika Brandstaetter','10.1037/0022-3514.73.1.186','Journal of Personality and Social Psychology 73(1) (1997),186-199','https://www.socmot.uni-konstanz.de/sites/default/files/97_Gollwitzer_Brandst%C3%A4tter_Imp_IntentEffect_Goal_Pursui.pdf'),
]

def acquire(s):
 sid,title,authors,doi,pub,url=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/'metadata.json').exists():return {'id':sid,'status':'already_archived'}
 try:
  r=requests.get(url,timeout=40)
  log={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  if r.status_code!=200 or not r.content.lstrip().startswith(b'%PDF-'):
   (d/'failed-response.bin').write_bytes(r.content);log['validation']='failed_http_or_pdf_validation';(d/'acquisition-log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed',**log}
  doc=fitz.open(stream=r.content,filetype='pdf');(d/'original.pdf').write_bytes(r.content)
  (d/'extracted.txt').write_text('\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc),encoding='utf-8')
  log['validation']='PDF header and parser passed'
  meta={'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':'pdf','source_url':url,'pages':len(doc),'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights retained; local research archive, not redistribution permission.',**log}
  (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(d/'acquisition-log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8')
  return {'id':sid,'status':'archived','pages':len(doc),'bytes':len(r.content)}
 except Exception as ex:
  log={'url':url,'error':str(ex)};(d/'acquisition-log.json').write_text(json.dumps(log,indent=2)+'\n',encoding='utf-8');return {'id':sid,'status':'failed',**log}

if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
