"""Record actual acquired editions/read scopes and archive checksums for round22."""
from pathlib import Path
import json,hashlib,csv,datetime,re
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-22';SURVEY=ROOT/'research/surveys/02-wealth-money-history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
DATA={
'L110-songchaoshishi-15':('complete_connector_transcription_selected_parts','Song-era compilation surviving in Qing Siku reconstructed WYG edition; Kanripo electronic text, not facsimile','Volume15 pages015-5b through8b jiaozi passage; preface000-1a through4a on transmission; other volume contents not fully read','historical_compilation_electronic_transcription',['connector-volume.txt','connector-preface.txt']),
'L111-guan-palma-wu-yuan':('complete_accepted_manuscript_selected_parts','85-page Manchester author accepted manuscript with appendix; cover links2024publication,DOI10.1111/ehr.13305; not publisher typeset article','PDF pp1-3,7-14,17-18,20-29,39-42,44-49,57-58; p48 table4 visual check; no full replication or all85pages reading','historical_econometric_research_accepted_manuscript',['original.pdf']),
'L112-kroll-agora-1993':('complete_book_selected_parts','JohnH.Kroll with AlanS.Walker,TheGreekCoins,AgoraXXVI,ASCSA1993;433-page PDF including plates','PDF pp1-2 version,4-6 prefatory locators,24-25 introduction,27-32 silver coins; p32 visual check; not complete book reading','excavation_catalogue_and_numismatic_analysis',['original.pdf']),
'L113-stroud-silver-law-1974':('complete_article_selected_parts','RonaldS.Stroud,Hesperia43(2),1974,157-188;35-page PDF incl3plates,stable147454','PDF1 discovery;3-4 translation;5-6 selected dating/epigraphy;15-17 and21 selected commentary;33 plate25; p3 and33 visually inspected; no independent Greek decipherment','inscription_edition_translation_and_archaeological_commentary',['original.pdf']),
'L114-thucydides-2-13':('complete_selected_passage_html','Thucydides2.13; CharlesFosterSmith1919-1923 translation,First1KGreek/Perseus; not complete History','2.13.2-6 fiscal and war preparation narrative; translator modern sterling/dollar equivalents not adopted','ancient_historiographical_text_translated_excerpt',['original.html']),
'L115-jianyan-zaji-16':('complete_connector_transcription_selected_parts','LiXinchuan,JianyanYilaiChaoyeZaji,Jia16;KanripoWYG transcription; distinct from initially located Cuiguzhai copy','WYG016-20b through23b DongnanHuizi;23b through27b selected regional,Sichuan and renewal discussion; digital transcription not checked to facsimile','historical_compilation_electronic_transcription',['connector-volume.txt']),
}
def metadata():
 for sid,(selection,edition,scope,evidence,names) in DATA.items():
  d=RAW/sid;p=d/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'))
  docs=[]
  for name in names:
   q=d/name;assert q.exists(),q
   source=m['url']
   if name.startswith('connector-'):
    repo='KR2m0004' if sid.startswith('L110') else 'KR2m0005';n='000' if name=='connector-preface.txt' else '015' if sid.startswith('L110') else '016';source=f'https://github.com/kanripo/{repo}/blob/master/{repo}_{n}.txt'
   docs.append({'path':name,'bytes':q.stat().st_size,'sha256':sha(q),'source_url':source,'transport':'full UTF-8 text returned by repository connector; not byte-identity verified against raw transport' if name.startswith('connector-') else 'direct file download'})
  m.update({'selection_status':selection,'publication':edition,'read_scope':scope,'evidence_type':evidence,'archived_documents':docs,'research_date_local':'2026-11-12','facsimile_read':False if sid in ['L110-songchaoshishi-15','L115-jianyan-zaji-16'] else None,
   'download_status':'complete_connector_text_and_response' if 'connector' in selection else 'downloaded_identity_and_scope_checked','original_downloaded':not ('connector' in selection),'complete_connector_text_obtained':'connector' in selection,'notes':'../../../../research/surveys/02-wealth-money-history/deepening-reading-notes.md',
   'rights':'Source rights and licence notices retained; local research archive, not blanket redistribution permission.'})
  if 'connector' in selection:
   m['format']='connector_utf8_text';m['original_byte_identity_verified']=False;m['complete_book_obtained']=False
   m['url']=docs[0]['source_url'];m['sha256']=docs[0]['sha256']
   t=(d/'connector-volume.txt').read_text(encoding='utf-8');(d/'extracted.txt').write_text(re.sub(r'<pb:[^>]+>','',t).replace('¶',''),encoding='utf-8')
  save(p,m)
 rows=[]
 for sid in DATA:
  m=json.loads((RAW/sid/'metadata.json').read_text(encoding='utf-8'));rows.append({k:m.get(k) for k in ['id','title','publication','selection_status','download_status','evidence_type','read_scope','url']})
 with (SURVEY/'deepening-source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 rows=[
 ('C01','Song jiaozi','L110','015-5b-6b','Private issue and redemption','Merchant signs,usage and failed redemptions described','Historical account in reconstructed edition','No exact issuer count,full balance sheet or joint-liability contract'),
 ('C02','Song jiaozi','L110','015-7a-8b','Issuance maintenance and fiscal diversion','Registration,coin custody,returned-note cancellation,official procurement problem','Recorded rules and policy criticism','Normative rule differs from audited compliance'),
 ('C03','Southern Song huizi','L115','016-20b-23b','Fiscal acceptance and implementation','Public payment arrangements,regional acceptance and local demands for cash','Historical compilation text','Digital variants; no unverified amount series'),
 ('C04','Yuan paper money','L111','PDF20-29','Measurement','Issuance,official exchange ratios,stock assumptions and sparse price interpolation','Research data construction','Issuance not observed stock; prices not complete annual measurements'),
 ('C05','Yuan paper money','L111','PDF44-49;table4','War and issuance','Nominal and real specifications differ;94 observations;limited disaster significance','Historical statistical association','No universal causal identification or inevitable fiat failure'),
 ('A01','Athenian silver','L112','PDF24-25,27-32','Excavation and circulation','Loss,fill,forgery and hoard selection affect finds','Excavation catalogue','Find count not circulation share or total mint output'),
 ('A02','Athenian silver','L112;L113','PDF32;PDF3-4,21,33','Verification and retirement','Cut plated coins considered alongside inscription procedure','Artifact plus inscription interpretation','Not every enforcement event observed;origin not established'),
 ('A03','Athenian silver','L113','PDF1,3-6','Public service and authority','375/4BCE law assigns testing,official duties,pay and sanctions','Inscription edition and translation','Restorations and foreign-coin interpretation not settled'),
 ('A04','Athenian public finance','L114','2.13.2-6','Revenue,stored coin and expenditure','Tribute,coined stock,building and war costs distinguished','Ancient historiographical narrative','No audited full fiscal ledger or modern purchasing-power conversion'),
 ]
 with (SURVEY/'deepening-evidence-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['observation_id','case','source_ids','read_locator','mechanism','observation','evidence_type','limit']);w.writerows(rows)
def manifest():
 ps=sorted(p for p in RAW.rglob('*') if p.is_file() and p.name not in ['manifest.json','checksums.sha256']);rows=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in ps]
 save(RAW/'manifest.json',{'research_date_local':'2026-11-12','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All round22 files except manifest.json and checksums.sha256,including connector responses,failures and text copies distinguished','files':rows})
 (RAW/'checksums.sha256').write_text(''.join(f"{v['sha256']}  {v['path']}\n" for v in rows),encoding='utf-8')
 assert all(sha(RAW/v['path'])==v['sha256'] for v in rows);print('Verified archive files',len(rows))
if __name__=='__main__':metadata();manifest()
