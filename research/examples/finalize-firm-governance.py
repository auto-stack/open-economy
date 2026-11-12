"""Finalize scoped sources and archive/model checks,not causal validation."""
from pathlib import Path
import json,csv,hashlib,re,importlib.util
import fitz
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-31';SUR=ROOT/'research/surveys/05-firm-authority-and-democracy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scopes={
 'L166':('AER88(5),1998,1188-1206;20pages includingJSTORcover','PDF2-4abstract/introduction;not model proofs or optimal shares'),
 'L167':('JPE105(1),1997,1-29;30pages includingJSTORcover','PDF2-4abstract/introduction;not all model conditions or comparative statics'),
 'L168':('HandbookIndustrialOrganization3,ch28,2007,1701-1844;145page file,last page no extracted body','PDF1-2contents,4intro,8views,10persuasion opening,16information opening,20complementary,23limits/summary opening;PDF20visual;not full section2 or later models/evidence'),
 'L169':('OrganizationScience2(1),1991,71-87;18pages includingJSTORcover','PDF2-4abstract,intro,exploration/exploitation tradeoff and vulnerability;PDF4visual;not later two models'),
 'L170':('HarvardLawReview119,2006,bibliography1333-1403;69page Yale file actually1335-1403;2013postingstamp not publication','PDF1-2abstract/introduction;PDF1visual;not detailed historical chapters or current legal requirements'),
 'L171':('Princeton2017publisher record only via tool;not book or originalHTML','Official publisher bibliography and Overview from web batch5;no survey number or global legal claim adopted'),
 'L172':('Author record of2017Cambridge book;originalHTML only,not book body','Bibliography and author overview of economic bicameralism;endorsements and reviews not evidence'),
 'L173':('NBERWP26519,November2019 revisedAugust2020;body25August2020;77pages,not2021QJEtypeset','PDF1-4abstract and intro/design opening;not all tables,identification checks,capital analysis or replication'),
 'L174':('IZADP7412,May2013;official record says2014journal separately;tool abstract only','Official IZA bibliography/abstract in web batch5;PDF requests failed,tool recognized48page PDF but no body reading;no causal interpretation of panel comparison'),
}
rows=[];pdfs=[]
for p in sorted(RAW.glob('L*/metadata.json')):
 m=json.loads(p.read_text(encoding='utf-8'));v,s=scopes[m['id'][:4]];m.update(actual_version=v,read_scope=s,reading_notes='../../../../research/surveys/05-firm-authority-and-democracy/reading-notes.md',knowledge_base_status='raw archived;not converted/imported into AutoDown')
 d=p.parent
 if (d/'original.pdf').exists():
  q=d/'original.pdf';doc=fitz.open(q);assert not doc.is_repaired;m.update(selection_status='targeted_original_pdf_read',download_status='original_archived_identity_and_version_checked',original_downloaded=True,pages=len(doc));pdfs.append(dict(id=m['id'],pages=len(doc)))
 elif (d/'original.html').exists():
  q=d/'original.html';m.update(selection_status='author_record_only_not_book_read',download_status='original_record_html_archived',original_downloaded=True)
 else:
  q=d/'tool-return-record.partial.txt';assert q.exists();m.update(selection_status='official_record_partial_tool_text_only',download_status='original_requests_failed_official_record_tool_text_only',original_downloaded=False,format='partial_tool_return')
 m['source_file']=dict(file=q.name,bytes=q.stat().st_size,sha256=sha(q));save(p,m)
 rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','read_scope','url']})
assert [x['pages'] for x in pdfs]==[20,30,145,18,69,77]
with (SUR/'source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
reused=[('wiki/raw/round-01/L07-coase-1937/original.pdf','Enterprise boundary;prior PDF3-10 visual scope only'),('wiki/raw/round-07/L37-ostrom-2010/original-university.pdf','Polycentric framework;prior PDF1-2,4-7,19-21;54page file32article plus citations'),('wiki/raw/round-18/L79-acemoglu-restrepo-2019/original.pdf','2019task automation model;priorPDF1-2,6-10;no new reading'),('wiki/raw/round-18/L81-brynjolfsson-li-raymond-2025/original.html','2025journal AIwork study;prior scoped abstract,intro,rollout,robustness/conclusion passages;no new reading'),('wiki/raw/round-23/L126-ftc-ai-partnerships-2025/original.pdf','January2025FTCstaff report;priorPDF1,4-6executive summary;no new reading'),('shared/theory-register.md','Formal79baseline context;unchanged,not new evidence')]
save(RAW/'reuse-context.json',[dict(path=p,scope=s,sha256=sha(ROOT/p)) for p,s in reused])
files=[dict(path=p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file() and p.name not in ['manifest.json','checksums.sha256','verification.json']]
save(RAW/'manifest.json',dict(date='2026-11-12',scope='All round31 files except manifest,checksums,verification',files=files))
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
errors=[];links=0
for x in files:
 if sha(RAW/x['path'])!=x['sha256']:errors.append('Hash mismatch '+x['path'])
md=list(SUR.glob('*.md'))+[RAW/'README.md',ROOT/'research/reviews/30-firm-leadership-adaptation-and-democracy.md',ROOT/'research/surveys/04-influence-and-social-equivalence/README.md',ROOT/'README.md',ROOT/'research/README.md',ROOT/'book/README.md',ROOT/'docs/research-dependencies.md',ROOT/'wiki/raw/README.md']
for p in md:
 txt=re.sub(r'`[^`]*`','',p.read_text(encoding='utf-8'))
 for target in re.findall(r'\]\(([^)]+)\)',txt):
  if re.match(r'^(https?:|#|chatgpt-conversation:|plugin:)',target):continue
  links+=1
  if not (p.parent/target.split('#')[0]).resolve().is_file():errors.append('Missing link '+str(p.relative_to(ROOT))+' '+target)
spec=importlib.util.spec_from_file_location('model',ROOT/'research/examples/coordination-adaptation-model.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
if model.calculate()!=json.loads((SUR/'adaptation-model-results.json').read_text(encoding='utf-8')):errors.append('Model mismatch')
r=dict(status='pass' if not errors else 'fail',raw_files_checked=len(files),links_checked=links,original_pdfs=pdfs,original_author_html=1,official_record_tool_sources=2,reused_original_sources=5,finite_model_checked=True,errors=errors,scope='Archive identity,scope,versions,integrity,local links and assumed arithmetic;not empirical validation or democracy forecast')
save(RAW/'verification.json',r);print(json.dumps(r));assert not errors
