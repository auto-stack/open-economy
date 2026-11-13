"""Describe adopted full texts and abstracts separately; archive without rewriting old batches."""
from pathlib import Path
import csv,json,hashlib,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-41'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
logs=[]
for p in sorted((RAW/'discovery').glob('download-attempts-*.json')):
 for entry in json.loads(p.read_text(encoding='utf-8')):
  if 'target' not in entry and '/27852/contents' in entry.get('url',''):
   entry={**entry,'target':'L209-development-2026/'+entry.get('file','repository-response.html')}
  logs.append(entry)
specs=[
 ('L204-partridge-1982','The good enough calculi of evolving control systems: evolution is not engineering','L. D. Partridge','10.1152/ajpregu.1982.242.3.R173',1982,'pubmed.xml','original_abstract_only','PubMed original abstract only; journal body unavailable','Abstract on evolved control logic; do not infer full proof or cases','backward seed reference; same abstract payload also archived in round40 discovery'),
 ('L205-moore-ede-1986','Physiology of the circadian timing system: predictive versus reactive homeostasis','M. C. Moore-Ede','10.1152/ajpregu.1986.250.5.R737',1986,'pubmed.xml','original_abstract_only','PubMed original abstract only; original journal body not obtained','Abstract defining reactive/predictive responses and mismatch; no original experiments checked','backward seed reference; publisher and CiteSeer full-text attempts failed'),
 ('L206-romanovsky-2004','Do fever and anapyrexia exist? Analysis of set point-based definitions','Andrej A. Romanovsky','10.1152/ajpregu.00068.2004',2004,'original.pdf','full_text_targeted_reading','Author lab copy of journal4page Report, R992–R995, first published2004-06-24','PDF1–4 body and Figure1; Figure1 PDF2 visually checked; original cited experiments not individually reviewed','backward reference from L196; original conceptual critique plus analysis of earlier empirical reports'),
 ('L207-weinberger-2026','Homeostasis and causal control','Naftali Weinberger','10.1007/s10539-026-10018-8',2026,'original.pdf','full_text_targeted_reading','Publisher30page PDF, Biology & Philosophy41:18, online2026-05-21','PDF1,9–13,22–24,27 selected passages; PDF9,23 formulas visually checked; not complete model reproduction','2026 forward citation candidate, reference to seed checked in acquired PDF'),
 ('L208-beyond-2026','Beyond canonical homeostasis: Dynamic, plastic, and intermittently unregulated physiology as the norm','Warren Burggren; Tobis Wang','10.14814/phy2.71150',2026,'original.xml','full_text_targeted_reading','EuropePMC JATS full text and PMC HTML; PDF not obtained; author names preserved as published','JATS1.2,3.1.2,4.1–4.2,5–6; review and energetic/evolutionary hypotheses separated','2026 forward citation candidate, seed citation checked in JATS reference'),
 ('L209-development-2026','Autonomy and development: distinguishing teleological development from teleological physiology','Tiago Rama','10.1007/s10539-026-10007-x',2026,'original.html','publisher_abstract_preview_only','Publisher subscription preview HTML, not full article; online2026-02-06,41:6','Abstract only; no full developmental argument or figures reviewed','2026 forward citation candidate; index link only, not verified in acquired article body'),
 ('L210-kanosue-2010','Concepts to utilize in describing thermoregulation and neurophysiological evidence for how the system works','Kazuyuki Kanosue; Larry I. Crawshaw; Kei Nagashima; Tamae Yoda','10.1007/s00421-009-1256-6',2010,'original.html','publisher_abstract_preview_only','Publisher subscription preview HTML; online2009, issue2010 109:5–11','Abstract only; no full neurophysiological evidence review','backward seed reference and alternative account to compare with L206')
]
rows=[]
import fitz
for dirname,title,authors,doi,year,filename,status,version,scope,route in specs:
 folder=RAW/dirname;adopted=folder/filename;source_logs=[x for x in logs if x.get('target','').startswith(dirname+'/')]
 success=next(x for x in reversed(source_logs) if x.get('sha256')==sha(adopted))
 meta={'id':dirname.split('-')[0],'title':title,'authors':authors,'doi':doi,'publication_year':year,'adopted_file':filename,'sha256':sha(adopted),'bytes':adopted.stat().st_size,'source_url':success['url'],'final_url':success['final_url'],'retrieved_at_utc':success['time_utc'],'version':version,'content_status':status,'reading_scope':scope,'discovery_route':route,'full_document_read':False,'independent_replication':False,'formal_systematic_inclusion':False,'correction_retraction_search':'not comprehensively completed','old_archives_modified':False}
 if filename.endswith('.pdf'):meta['pdf_pages']=len(fitz.open(adopted))
 if meta['id']=='L208':meta['publication_dates']={'JATS_pub_date':'2026-10-19','OpenAlex_index_publication_date':'2026-10-01','difference_preserved':True}
 if meta['id']=='L210':meta['online_year']=2009
 save(folder/'metadata.json',meta);save(folder/'download-log.json',source_logs);save(folder/'read-scope-extension.json',{'id':meta['id'],'date_local':'2026-11-13','content_status':status,'adopted_file':filename,'sha256':sha(adopted),'scope':scope,'full_document_read':False})
 rows.append({'id':meta['id'],'doi':doi,'content_status':status,'adopted_file':adopted.relative_to(ROOT).as_posix(),'reading_scope':scope,'version':version,'route':route})
with (HERE/'source-status.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save(RAW/'source-reuse.json',{'L204':{'prior_payload':'wiki/raw/round-40/discovery/partridge-pubmed.xml','prior_sha256':sha(ROOT/'wiki/raw/round-40/discovery/partridge-pubmed.xml'),'current_payload':'L204-partridge-1982/pubmed.xml','same_bytes':(ROOT/'wiki/raw/round-40/discovery/partridge-pubmed.xml').read_bytes()==(RAW/'L204-partridge-1982/pubmed.xml').read_bytes(),'meaning':'same original abstract now registered under stable work ID, not a new independent study'},'prior_source_files_modified':False})
save(RAW/'discovery/metadata.json',{'date_local':'2026-11-13','purpose':'targeted original-source follow-up and 2026 candidate retrieval, not systematic search','seed_reference_batch':'round40','work_ids':['L204','L205','L206','L207','L208','L209','L210'],'full_text_work_ids':['L206','L207','L208'],'abstract_preview_work_ids':['L204','L205','L209','L210'],'search_results':['search-01.txt','search-02.txt','search-03.txt','search-04.txt'],'open_results':['open-01.txt'],'retrieval_attempts':['download-attempts-01.json','download-attempts-02.json','download-attempts-03.json','download-attempts-04.json'],'rejected_bioc':'rejected-bioc-error.html'})
manifest=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(RAW.rglob('*')) if p.is_file() and p.name!='manifest.json'];save(RAW/'manifest.json',manifest)
print(json.dumps({'manifest_entries':len(manifest),'work_records':len(rows),'PDFs':len(list(RAW.rglob('*.pdf'))),'fulltexts':3,'abstract_previews':4},ensure_ascii=False))
