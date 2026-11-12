"""Acquire a bounded, competing-traditions corpus for a historical literature survey."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,fitz,json,hashlib,datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-20'
SOURCES=[
 ('L85-aristotle-politics','Politics Book I','Aristotle; Benjamin Jowett translation','Ancient text; English translation edition supplied by Internet Classics Archive','https://classics.mit.edu/Aristotle/politics.1.one.html','html'),
 ('L86-marx-capital-1867','Capital Volume I Chapter 1','Karl Marx','First published 1867; Marxists Internet Archive English text, edition to be checked','https://www.marxists.org/archive/marx/works/1867-c1/ch01.htm','html'),
 ('L87-jevons-political-economy','The Theory of Political Economy','W. Stanley Jevons','First published 1871; Econlib electronic edition, version to be checked','https://www.econlib.org/library/YPDBooks/Jevons/jvnPE.html?chapter_num=7','html'),
 ('L88-menger-1892','On the Origin of Money','Carl Menger; Caroline A. Foley translation','The Economic Journal 2(6) (1892),239-255','https://is.muni.cz/el/econ/podzim2021/BPE_SMOE/um/Menger1892_On_the_Origin_of_Money.pdf','pdf'),
 ('L89-innes-1913','What is Money?','A. Mitchell Innes','The Banking Law Journal, May 1913; online transcription','https://www.community-exchange.org/docs/what%20is%20money.htm','html'),
 ('L90-knapp-1924','The State Theory of Money','Georg Friedrich Knapp','1924 English translation of 1905 German work','https://ia801900.us.archive.org/35/items/in.ernet.dli.2015.224223/2015.224223.The-State.pdf','pdf'),
 ('L91-humphrey-1985','Barter and Economic Disintegration','Caroline Humphrey','Man, New Series 20(1) (1985),48-72; DOI 10.2307/2802221','https://voidnetwork.gr/wp-content/uploads/2016/09/Barter-and-economic-disintegration-by-Caroline-Humphrey.pdf','pdf'),
 ('L92-grierson-origins','The Origins of Money','Philip Grierson','Lecture/reprint; dates and version pending source inspection','https://elaineou.com/wp-content/uploads/2017/01/Grierson-The-Origins-of-Money.pdf','pdf'),
 ('L93-schmandt-besserat-accounting','From Accounting to Writing','Denise Schmandt-Besserat','Author research webpage; undated, version to be checked','https://sites.utexas.edu/dsb/tokens/from-accounting-to-writing/','html'),
 ('L94-boe-money-2014','Money Creation in the Modern Economy','Michael McLeay; Amar Radia; Ryland Thomas','Bank of England Quarterly Bulletin 2014 Q1','https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2014/money-creation-in-the-modern-economy.pdf','pdf'),
 ('L95-loc-cuneiform','About this Collection: Cuneiform Tablets','Library of Congress','Official collection description and catalogue context','https://www.loc.gov/collections/cuneiform-tablets/about-this-collection/','html'),
 ('L96-von-glahn-2005','The Origins of Paper Money in China','Richard von Glahn','The Origins of Value, chapter 4 (2005),65-89; circulated chapter PDF','https://glia.ca/2014/money-art/pdfs/2_ORIGINS_GE1127_2014.pdf','pdf'),
 ('L97-cantillon-1755','Essay on the Nature of Trade in General','Richard Cantillon','First published 1755; English electronic edition, translation/version to be checked','https://davidmhart.com/liberty/FrenchClassicalLiberals/Cantillon/1755-Commerce/index-eng.html','html'),
]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def acquire(s):
 sid,title,author,publication,url,fmt=s;d=ROOT/sid;d.mkdir(parents=True,exist_ok=True)
 if (d/f'original.{fmt}').exists():return {'id':sid,'status':'already_archived'}
 lp=d/'acquisition-log.json';logs=json.loads(lp.read_text(encoding='utf-8')) if lp.exists() else []
 try:
  r=requests.get(url,timeout=40);rec={'url':url,'final_url':r.url,'status_code':r.status_code,'bytes':len(r.content),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  valid=r.status_code==200 and ((fmt=='pdf' and r.content.lstrip().startswith(b'%PDF-')) or (fmt=='html' and len(r.content)>1500))
  if not valid:
   (d/f'failed-response-{len(logs)+1}.bin').write_bytes(r.content);rec['validation']='failed_http_or_format';logs.append(rec);save(lp,logs);return {'id':sid,'status':'failed','http':r.status_code}
  if fmt=='pdf':
   doc=fitz.open(stream=r.content,filetype='pdf');text='\n\n'.join(f'===== PDF PAGE {p.number+1} =====\n'+p.get_text() for p in doc);pages=len(doc)
  else:
   soup=BeautifulSoup(r.content,'html.parser')
   for t in soup(['script','style','nav']):t.decompose()
   main=soup.find('main') or soup;text=main.get_text('\n',strip=True);pages=None
  (d/f'original.{fmt}').write_bytes(r.content);(d/'extracted.txt').write_text(text,encoding='utf-8');rec['validation']='Format parsed; substantive content and source version pending inspection';logs.append(rec);save(lp,logs)
  save(d/'metadata.json',{'id':sid,'title':title,'authors':author,'publication':publication,'research_date_local':'2026-11-12','format':fmt,'pages':pages,'sha256':hashlib.sha256(r.content).hexdigest(),'read_scope':'Pending targeted reading','rights':'Original rights and distribution notices retained; local research archive, not blanket redistribution permission.',**rec})
  return {'id':sid,'status':'archived','pages':pages,'text_characters':len(text)}
 except Exception as ex:
  logs.append({'url':url,'error':str(ex)});save(lp,logs);return {'id':sid,'status':'failed','error':str(ex)}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(acquire,SOURCES):print(json.dumps(result),flush=True)
