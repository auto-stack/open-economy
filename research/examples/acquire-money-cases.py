"""Retrieve actual historical-case sources; preserve errors separately from originals."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-21'
SOURCES=[
 ('L100-met-silver-loan','Cuneiform tablet: loan of silver','Metropolitan Museum of Art','Object66.245.17a; ca20th-19th century BCE','https://www.metmuseum.org/art/collection/search/325858','html'),
 ('L101-met-barley-account','Cuneiform tablet: administrative account with entries concerning malt and barley groats','Metropolitan Museum of Art','Object1988.433.3; date to verify','https://www.metmuseum.org/art/collection/search/327385','html'),
 ('L102-bm-electrum-coin','Electrum coin 1841,B.2203','British Museum','6th century BCE circa; catalogue dating','https://www.britishmuseum.org/collection/object/C_1841-B-2203','html'),
 ('L103-bm-money-gallery','Money Gallery Room68 Large Print Guide','British Museum','2020 guide;2021-hosted PDF, version pending inspection','https://www.britishmuseum.org/sites/default/files/2021-05/Money_Gallery_LPG_2020_Room_68.pdf','pdf'),
 ('L104-kroll-early-coinage','The Monetary Background of Early Coinage — publisher preview','John H. Kroll','Oxford Handbook of Greek and Roman Coinage,2012; preview extent to inspect','https://api.pageplace.de/preview/DT0400.9780199719334_A24395225/preview-9780199719334_A24395225.pdf','pdf'),
 ('L105-songshi-181','Song Shi, Siku Quanshu transcription, volume181','Tuotuo and other Yuan compilers; Wikisource transcription','Retrospective dynastic history; electronic transcription not checked against facsimile','https://zh.wikisource.org/zh/宋史_(四庫全書本)/卷181','html'),
 ('L106-chnmuseum-jiaozi','宋代交子与纸币发行','National Museum of China','2016 Chinese Epic exhibition section; selected text on a large exhibition page','https://en.chnmuseum.cn/Portals/0/web/exhibition/exhibitions/161120Chines-Epic/','html'),
 ('L107-chnmuseum-huizi','会子版','National Museum of China','Collection interpretation; webpage date/version to inspect','https://www.chnmuseum.cn/zp/zpml/201812/t20181218_26121.shtml','html'),
 ('L108-quinn-roberds-2010','How Amsterdam Got Fiat Money','Stephen Quinn; William Roberds','Federal Reserve Bank of Atlanta Working Paper2010-17,December2010; FRASER archival copy','https://fraser.stlouisfed.org/files/docs/historical/frbatl/wp/frbatl_wp_2010-17.pdf','pdf'),
 ('L109-vonglahn-2026-record','The Rise and Demise of Paper Money in Imperial China — publisher record','Richard von Glahn','Cambridge2026; bibliographic page, not full book','https://www.cambridge.org/core/books/the-rise-and-demise-of-paper-money-in-imperial-china/C87055AD79B968129C6534E3679CF631','html'),
]

def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def acquire(s):
 sid,title,authors,publication,url,fmt=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 lp=d/'acquisition-log.json';logs=json.loads(lp.read_text(encoding='utf-8')) if lp.exists() else []
 if (d/f'original.{fmt}').exists():return {'id':sid,'status':'already_archived'}
 meta={'id':sid,'title':title,'authors':authors,'publication':publication,'url':url,'research_date_local':'2026-11-12','read_scope':'Pending targeted reading','selection_status':'pending_inspection','rights':'Original rights retained; local research archive, not blanket redistribution permission.'}
 try:
  r=requests.get(url,timeout=(10,25));rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  valid=r.status_code==200 and ((fmt=='pdf' and r.content.lstrip().startswith(b'%PDF-')) or(fmt=='html' and len(r.content)>1500 and b'<html' in r.content.lower()))
  if not valid:
   fn=f'failed-response-{len(logs)+1}.bin';(d/fn).write_bytes(r.content);rec['validation']='failed_http_or_format';rec['response_file']=fn;meta.update({'download_status':'failed','original_downloaded':False})
  else:
   p=d/f'original.{fmt}';p.write_bytes(r.content)
   if fmt=='pdf':
    doc=fitz.open(p);assert not doc.is_repaired;text='\n\n'.join(f'===== PDF PAGE {i+1} =====\n'+q.get_text() for i,q in enumerate(doc));pages=len(doc)
   else:
    soup=BeautifulSoup(r.content,'html.parser')
    for t in soup(['script','style','nav','footer']):t.decompose()
    main=soup.find('main') or soup;text=main.get_text('\n',strip=True);pages=None
   (d/'extracted.txt').write_text(text,encoding='utf-8')
   meta.update({'format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'archived_file':p.name,'download_status':'downloaded_pending_substantive_validation','original_downloaded':True,**rec});rec['validation']='format parsed; identity and scope pending inspection'
  logs.append(rec)
 except Exception as e:
  logs.append({'url':url,'error':str(e),'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});meta.update({'download_status':'failed','original_downloaded':False})
 save(lp,logs);save(d/'metadata.json',meta)
 return {'id':sid,'status':meta['download_status'],'pages':meta.get('pages'),'bytes':meta.get('bytes')}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for x in pool.map(acquire,SOURCES):print(json.dumps(x),flush=True)
