"""Describe the current source batch, retaining prior source states and stable IDs."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-40'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
attempts=[]
for p in sorted((RAW/'discovery').glob('acquisition-attempts*.json')):attempts.extend(json.loads(p.read_text(encoding='utf-8')))
specs=[
 ('L196-bechtel-bich-2024','Situating homeostasis in organisms: maintaining organization through time','William Bechtel; Leonardo Bich','10.1113/JP286883',2024,'2024-10-09',2024,'complete author-hosted online typeset version, J.Physiol.0.0 pp1–18; journal6003–6020 not page-mapped','Main text manuscript2–16 targeted reading; figures2(p8),3(p12), network argument14–15 visually checked; references exported rather than all originals read','backward/forward seed; same work as prior L196'),
 ('L199-billman-2020','Homeostasis: The Underappreciated and Far Too Often Ignored Central Organizing Principle of Physiology','George E. Billman','10.3389/fphys.2020.00200',2020,'2020-03-10',2020,'publisher12page review','PDF2 definition/introduction and PDF11 Summary selected passages','backward reference DOI in L196 publisher export'),
 ('L200-bich-menatti-health','Homeostasis and Health: From Balance to Change','Leonardo Bich; Laura Menatti','10.1007/s13752-025-00510-x',2025,'2025-10-14',2026,'author-hosted13page online typeset version; issue2026 21(2):174–186; cite PDF page not inferred print page','PDF1 abstract,7–8 and10 selected passages; reference to L196 PDF11; footnote7 temperature wording held for original-source check','forward citation confirmed in PDF; shares an author/theoretical lineage with seed'),
 ('L201-horseman-2025','Kinorhesis: A physiological principle of transformation that is complementary with homeostatic stability','Nelson D. Horseman','10.3389/fphys.2025.1633607',2025,'2025-10-10',2025,'publisher15page Hypothesis and Theory','PDF2–3 definitions/contrast and13 conclusion/figure8 caption selected passages; L196 reference PDF14','forward citation confirmed in PDF; new theoretical proposal not independent empirical replication'),
 ('L202-farnsworth-2025','Homeostatic set-points are physical and foundational to organism autonomy','Keith D. Farnsworth','10.1016/j.biosystems.2025.105634',2025,'2025-10-30',2025,'university repository18page PDF incl cover; file declares publisher version, OpenAlex location says submittedVersion; record discrepancy','PDF2–3 abstract/introduction/1.1 and12–13 conclusion selected passages; hypothesis PDF3 visually checked; L196 reference PDF15; no mathematical reproduction','forward citation confirmed in PDF; alternative physical account of set-points'),
 ('L203-bechtel-bich-history','Rediscovering Bernard and Cannon: Restoring the Broader Vision of Homeostasis Eclipsed by the Cyberneticists','William Bechtel; Leonardo Bich','10.1017/psa.2024.72',2024,'2024-12-12',2025,'author-hosted22page journal PDF, Philosophy of Science2025 92:584–605','First PDF page abstract,identity,online date and issue; remaining body not read; citation relation to L196 remains index-only','related history paper by same authors, separate work not a seed version')
]
import fitz
for dirname,title,authors,doi,online_year,online_date,issue_year,version,scope,route in specs:
 folder=RAW/dirname;p=folder/'original.pdf';doc=fitz.open(p)
 logs=[x for x in attempts if x['target'].startswith(dirname+'/')]
 success=next(x for x in reversed(logs) if x.get('sha256')==sha(p))
 meta={'id':dirname.split('-')[0],'title':title,'authors':authors,'doi':doi,'first_online_year':online_year,'first_online_date':online_date,'issue_year':issue_year,'version':version,'original_file':'original.pdf','bytes':p.stat().st_size,'sha256':sha(p),'pdf_pages':len(doc),'source_url':success['url'],'final_url':success['final_url'],'retrieved_at_utc':success['time_utc'],'reading_status':'targeted_passages_read' if dirname.split('-')[0]!='L203' else 'first_page_identity_and_abstract_only','reading_scope':scope,'discovery_route':route,'full_document_read':False,'formal_systematic_review_inclusion':False,'independent_experiment_or_proof_reproduction':False,'retraction_correction_status':'No complete dedicated correction/retraction search performed; discovered withdrawn candidate excluded from evidence','raw_prior_archives_modified':False}
 save(folder/'metadata.json',meta);save(folder/'download-log.json',logs)
 save(folder/'read-scope-extension.json',{'id':meta['id'],'date_local':'2026-11-13','version':version,'sha256':sha(p),'scope':scope,'prior_reading_preserved':True})
old=ROOT/'wiki/raw/round-11/L61-ramsay-woods-2014/original.xml'
seed_old=ROOT/'wiki/raw/round-39/L196-bechtel-bich-2024/metadata.json'
save(RAW/'source-reuse.json',[
 {'id':'L61','path':old.relative_to(ROOT).as_posix(),'sha256':sha(old),'read_scope':'Reuse previous read scope only; no new XML passages read','new_download':False,'original_modified':False},
 {'id':'L196','prior_metadata':seed_old.relative_to(ROOT).as_posix(),'prior_metadata_sha256':sha(seed_old),'new_original':'wiki/raw/round-40/L196-bechtel-bich-2024/original.pdf','new_original_sha256':sha(RAW/'L196-bechtel-bich-2024/original.pdf'),'identity':'Same DOI and authors; new complete copy does not overwrite earlier partial tool text/failures','new_work':False}
])
save(RAW/'discovery/metadata.json',{'date_local':'2026-11-13','role':'Search/query responses and discovery, not all adopted full texts','seed_doi':'10.1113/JP286883','seed_openalex_id':'W4403274118','backward_reference_export':{'file':'L196-crossref.json','record_count':88,'type':'publisher-deposited references, not originals read'},'forward_citation_export':{'file':'L196-citing-openalex.json','cutoff':'2026-11-13','returned':34,'display_count':34,'per_page':100,'page':1,'sort':'publication_date:asc','query':'filter=cites:W4403274118,to_publication_date:2026-11-13','limitations':'single-index snapshot; versions/withdrawals/citation links need validation'},'author_catalog':'bich-publications.html','initial_web_capture_gap':'See initial-query-notes.json; first web response not saved verbatim'})
manifest=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(RAW.rglob('*')) if p.is_file() and p.name!='manifest.json']
save(RAW/'manifest.json',manifest)
print(json.dumps({'manifest_entries':len(manifest),'PDFs':len(list(RAW.rglob('*.pdf'))),'new_work_ids':['L199','L200','L201','L202','L203'],'seed_id_preserved':'L196'},ensure_ascii=False))
