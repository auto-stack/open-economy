"""Freeze inspected source scopes, case observations, and checksums for round21."""
from pathlib import Path
import hashlib,json,csv,datetime
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-21'
SURVEY=ROOT/'research/surveys/02-wealth-money-history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
SCOPES={
'L100-met-silver-loan':('selected_catalogue_and_partial_interpretation','Official catalogue JSON plus partial curator webpage, not independent ancient-text reading','API identity/date/material/accession and curator paragraph on6minas,deferred repayment,monthly late interest,witnesses; no numerical rate or production outcome','catalogue_and_curatorial_interpretation'),
'L101-met-barley-account':('selected_catalogue_and_partial_interpretation','Official catalogue JSON plus partial curator webpage, no independent transliteration','API identity/date/material and webpage opening description; temple distribution retained as most-likely interpretation','catalogue_and_curatorial_interpretation'),
'L102-bm-electrum-coin':('lead_only','No original retrieved','Discovery snippets only; not substantive evidence','unread_lead'),
'L103-bm-money-gallery':('lead_only','No original retrieved','Discovery snippets only; no complete guide reading','unread_lead'),
'L104-kroll-early-coinage':('selected_target_chapter_complete','71-page publisher preview containing complete target chapter, not complete book','PDF p5 version; pp52-61 = printed33-42, complete target chapter including bibliography; p58 rendered and inspected; other chapters not adopted','historical_scholarly_reconstruction'),
'L105-songshi-181':('selected_partial_transcription','Partial web-tool transcription only; no original HTML/raw or facsimile','Selected beginning hui-zi/jiao-zi discussion: iron coins,16households,default,public office,regional conditions,redemption and backing; not whole volume or quantitative chronology','retrospective_dynastic_history_transcription'),
'L106-chnmuseum-jiaozi':('selected_web_section','Full2016 exhibition HTML; only designated section adopted; not a surviving Song instrument','Song-dynasty jiaozi and paper issuance section: merchant coordination,regulation and separate1023decision/1024issuance dates; other exhibition sections excluded','museum_historical_explanation'),
'L107-chnmuseum-huizi':('selected_object_description','Full official object-description webpage','Title and full short description on huizi printing plate,denominations,official issuance and fiscal explanation; no geographic universality or independent inflation series','museum_object_and_historical_explanation'),
'L108-quinn-roberds-2010':('selected_paper_parts','Complete109-page2010working paper, not2014journal version','PDF pp1-17,49-50,56-57; history,data methods,conclusion,appendix accounting opening; p13 visual check; VAR and full archival series not replicated','archival_historical_research'),
'L109-vonglahn-2026-record':('selected_publisher_summary_only','Full publisher book record and chapter4 summary pages; no book/chapter body','Bibliographic data,contents,and chapter4 summary only; online18September2026,print2026,pp113-146,DOI10.1017/9781009699440.007; not old2005chapter','publisher_record_and_author_abstract'),
}

def metadata():
 for sid,(selection,scope,read,evidence) in SCOPES.items():
  d=RAW/sid;p=d/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'))
  docs=sorted(d.glob('original.*'))
  if sid=='L109-vonglahn-2026-record':docs.append(d/'chapter-4-record.html')
  files=[]
  for q in docs:
   if not q.exists():continue
   source_url=m['url']
   if sid in ['L100-met-silver-loan','L101-met-barley-account']:source_url='https://collectionapi.metmuseum.org/public/collection/v1/objects/'+('325858' if 'L100' in sid else '327385')
   if q.name=='chapter-4-record.html':source_url='https://www.cambridge.org/core/books/rise-and-demise-of-paper-money-in-imperial-china/northern-song-monetary-policy-and-the-invention-of-paper-currency-in-sichuan/8D4E47993802972BFFEE47EC0DF7CD22'
   files.append({'path':q.name,'bytes':q.stat().st_size,'sha256':sha(q),'source_url':source_url,'document_scope':scope})
  partial=d/'partial-web-tool-text.txt'
  m.update({'selection_status':selection,'evidence_type':evidence,'downloaded_document_scope':scope,'read_scope':read,
   'original_downloaded':bool(files),'original_files':files,'partial_tool_text_downloaded':partial.exists(),
   'full_text_of_target_research_work_obtained':sid in ['L104-kroll-early-coinage','L108-quinn-roberds-2010'],
   'download_status':('original_catalogue_plus_partial_webpage' if 'L100' in sid or 'L101' in sid else 'publisher_record_and_summary_only' if sid.startswith('L109') else 'partial_tool_transcription_only' if sid.startswith('L105') else 'failed_lead_only' if selection=='lead_only' else 'downloaded_inspected_scope'),
   'notes':'../../../../research/surveys/02-wealth-money-history/case-reading-notes.md','rights':'Original rights retained; local research archive. Downloaded catalogue/transcription/preview does not imply full work or redistribution permission.'})
  if partial.exists():m['partial_tool_text']={'path':partial.name,'sha256':sha(partial),'is_original_file':False}
  if files:m['format']=files[0]['path'].rsplit('.',1)[-1];m['sha256']=files[0]['sha256']
  if sid=='L101-met-barley-account':m['publication']='Object1988.433.3; catalogue dates ca3100-2900BCE; probable Uruk,temple function is curatorial inference'
  if sid=='L104-kroll-early-coinage':m['publication']='JohnH.Kroll in WilliamE.Metcalf(ed.),OxfordHandbookofGreekandRomanCoinage,2012,33-42; complete chapter within71-page preview'
  if sid=='L109-vonglahn-2026-record':m['publication']='RichardvonGlahn,Cambridge2026; chapter4 online18September2026,113-146,DOI10.1017/9781009699440.007; abstract only'
  save(p,m)
 rows=[]
 for sid in SCOPES:
  m=json.loads((RAW/sid/'metadata.json').read_text(encoding='utf-8'))
  rows.append({k:m.get(k) for k in ['id','title','selection_status','download_status','evidence_type','read_scope','url']})
 with (SURVEY/'case-source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def evidence():
 rows=[
 ('A01','NearEast','ca3100-2900BCE','L101','Commodity administration','Barley account; probable temple distribution','Catalogue and curator interpretation','No general money or private sale established'),
 ('A02','NearEast','ca20th-19thcBCE','L100','Deferred silver obligation','Amount,schedule,late interest and witnesses','Catalogue and curator interpretation','No widespread transferability,production outcome or credit-first genesis established'),
 ('B01','Precoinage and coinage','EarlyIronAge-ArchaicGreece','L104','Unit versus delivery','Value convention differs from actual delivered goods','Historical reconstruction','Ancient testimony partly indirect; original sources not all rechecked'),
 ('B02','Precoinage and coinage','7th-6thcBCE','L104','Certification','Weight,alloy quality and issuer certification jointly matter','Historical mechanism interpretation','Not unique first-coin motivation or global sequence'),
 ('C01','SongChina','10th-11thc','L105;L106;L109','Commercial credit and public takeover','Private issuance,default,public office or takeover','Retrospective history;museum explanation;author abstract','Chronology and original documents require further verification'),
 ('C02','SongChina','11thc','L106','Same-side coordination','Museum explanation describes joint merchant operation','Museum historical explanation','Not independent gain estimates or absence of competition'),
 ('C03','SongChina','Songperiod','L105;L107','Acceptance and maintenance','Regional acceptance,backing,issuance and redemption differ','Partial history transcription and museum account','No complete price or issuance series'),
 ('D01','Amsterdam','1609onwards','L108','Account settlement','Transferable balances settle obligations; not circulating banknotes','Archival historical research','No formal multilateral netting assumed; notes qualify practice'),
 ('D02','Amsterdam','1683-1680s','L108','Payment versus redemption','Balance and negotiable coin-withdrawal receipt separated','Historical institutional reconstruction','Exact abolition date of old withdrawal right unknown'),
 ('D03','Amsterdam','1666-1702studywindow','L108','Credit and distribution','Account lending,metal lending and city capital extraction differ','Partial archival accounting reconstruction','Missing periods and interpolated prices; not full social-welfare identification'),
 ]
 keys=['observation_id','case','period','source_ids','mechanism','observation','evidence_type','inference_limit']
 with (SURVEY/'case-evidence-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(keys);w.writerows(rows)

def manifest():
 files=sorted(p for p in RAW.rglob('*') if p.is_file() and p.name not in ['manifest.json','checksums.sha256'])
 rows=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
 save(RAW/'manifest.json',{'research_date_local':'2026-11-12','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All round21 files except the two checksum manifests; failures and partial source formats distinctly labelled','files':rows})
 (RAW/'checksums.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in rows),encoding='utf-8')
 assert all(sha(RAW/x['path'])==x['sha256'] for x in rows)
 print('Verified archive files:',len(rows))
if __name__=='__main__':metadata();evidence();manifest()
