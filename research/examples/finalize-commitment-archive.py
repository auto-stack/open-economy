"""Record actual source versions, reading scope, failures and checksums for round 15."""
from pathlib import Path
import json,hashlib,datetime

root=Path(__file__).resolve().parents[2]/'wiki/raw/round-15'
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
leads=[
 ('L71-bratman-1992','Shared Cooperative Activity','Michael E. Bratman','10.2307/2185537','The Philosophical Review 101(2) (1992),327-341','Course PDF requests failed; web tool returned 401. Search cover/bibliographic material only; no article body read.'),
 ('L72-ostrom-walker-gardner-1992','Covenants With and Without a Sword: Self-Governance Is Possible','Elinor Ostrom; James Walker; Roy Gardner','10.2307/1964229','American Political Science Review 86(2) (1992),404-417','Local PDF requests returned 406. Web tool text contains cover and appended linked citations, not the scanned body. The distinct 1991 draft also failed to download; no experiment results adopted.'),
]
for sid,title,authors,doi,pub,scope in leads:
 save(root/sid/'metadata.json',{'id':sid,'title':title,'authors':authors,'doi':doi,'publication':pub,'research_date_local':'2026-11-12','format':'bibliographic_lead_with_failed_acquisition','original_article_downloaded':False,'article_body_read':False,'adopted_for_substantive_claims':False,'read_scope':scope,'acquisition_log':'acquisition-log.json','search_records':'../search-*.json','web_tool_record':'../web-views.json','reading_notes':'../../../../research/reviews/16-reading-notes.md'})
updates={
 'L73-hart-moore-1988':{'version':'32-page scan of 1988 journal article including one JSTOR cover; not 1985 MIT working paper.','source_type':'formal theoretical model','read_scope':'PDF pp.2-6, Conclusions p.23 and opening p.24. Article pp.755-759,776-777; full proofs not reconstructed. p.6 visually checked.'},
 'L74-hamann-et-al-2012':{'version':'9-page 2012 journal typeset PDF from Duke author lab; copyright 2011.','source_type':'developmental experiments; age is not randomized','read_scope':'PDF pp.1-3, procedure/coding parts of p.4, p.5, pp.7-8. p.6 only located; references not read as separate sources. Main result figure and trial-level denominators visually checked on p.5.'},
}
for sid,fields in updates.items():
 p=root/sid/'metadata.json';obj=json.loads(p.read_text(encoding='utf-8'));obj.update(fields);obj['reading_notes']='../../../../research/reviews/16-reading-notes.md';save(p,obj)
files=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:continue
 data=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
save(root/'manifest.json',{'research_date_local':'2026-11-12','timezone':'Asia/Shanghai','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_full_originals':2,'bibliographic_leads_without_article':2,'originals':[x for x in files if x['path'].endswith('/original.pdf')],'files':files})
print(json.dumps({'files':len(files),'new_full_originals':2,'leads_without_article':2}))
