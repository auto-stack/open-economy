"""Finalize actual versions, scoped reading and reproducible archive checks."""
from pathlib import Path
import json,csv,hashlib,re,importlib.util
from urllib.parse import unquote,urlsplit
import fitz

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-27'
SUR=ROOT/'research/surveys/04-influence-and-social-equivalence'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

versions={
 'L152-garicano-2000':dict(actual_version='JPE108(5),2000,874-904;31page university-hosted article',doi='10.1086/317671',read_scope='PDF1-3,5;PDF4intro selections browsed;PDF2 visually checked;not all proofs or extensions',selection_status='targeted_original_pdf_read'),
 'L153-bloom-et-al-2010':dict(actual_version='HBSWorkingPaper11-023;6September2010;58pages;author URL says2014 but file is2010',doi_of_later_journal_version='10.1287/mnsc.2014.2013',read_scope='PDF1-3,7-9;PDF2 visually checked;empirical associations and IV direction from abstract only;not regression tables or identification details',selection_status='targeted_original_working_paper_read',later_journal_scope='2014official abstract in discovery only;2014 original PDF failed'),
 'L154-dellacqua-et-al-2026':dict(actual_version='OrganizationScience37(2),2026,403-423;online11March2026;partial official tool-return only,not2023 working paper',doi='10.1287/orsc.2025.21838',read_scope='Official ePDF text returned in web batch9:PDF1abstract and metadata;PDF2-4intro/context selections;no full methods,tables,appendix or actual visual screenshot reading',selection_status='adopted_partial_official_tool_text',source_pdf_pages_reported_by_tool=21,url='https://pubsonline.informs.org/doi/epdf/10.1287/orsc.2025.21838',original_downloaded=False,download_status='original_requests_failed_partial_tool_text_only',format='partial_tool_return',rights='Official2026 first-page tool text states CCBY4.0;attribute DOI/authors/journal;do not transfer this license to2023 working paper or other sources'),
}
rows=[];pdfs=[]
for sid,extra in versions.items():
 d=RAW/sid;p=d/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'))
 m.update(extra);m['id']=sid;m['reading_notes']='../../../../research/surveys/04-influence-and-social-equivalence/communication-reading-notes.md'
 m['knowledge_base_status']='raw provenance archived;not converted/imported into AutoDown'
 if (d/'original.pdf').exists():
  doc=fitz.open(d/'original.pdf');assert not doc.is_repaired
  m.update(original_downloaded=True,download_status='original_archived_identity_and_internal_version_checked',pages=len(doc))
  pdfs.append(dict(id=sid,pages=len(doc)))
 m['source_files']=[dict(file=q.name,bytes=q.stat().st_size,sha256=digest(q)) for q in sorted(d.iterdir()) if q.name.startswith(('original.','tool-return-'))]
 save(p,m)
 rows.append({k:m.get(k,'') for k in ['id','actual_version','selection_status','download_status','read_scope','url']})
assert [x['pages'] for x in pdfs]==[31,58]

reuse=[
 ('L15','wiki/raw/round-04/L15-shannon-1948/original.pdf','Corrected1948reprint55pages','Prior introduction/section6 PDF1,10-12;current reread PDF1;engineering scope and information definitions'),
 ('L16','wiki/raw/round-04/L16-landauer-1961/original.pdf','2000reprint261-269 of1961article','Prior sections3-4 PDF4-5;current visual reread PDF4-5;reset conditions,bias,correlations;scan text alone inadequate'),
 ('L20','wiki/raw/round-04/L20-kolchinsky-wolpert-2018/original.pdf','InterfaceFocus8,2018,20180041','Prior intro/sections3-5.1.1 PDF5-7;current reread PDF5-6;causal information/viability distinction;no model reproduction'),
 ('L21','wiki/raw/round-04/L21-tong-statphys/original-native.pdf','University statphys chapter;year not verified','Reuse prior sections1.2.1,1.3.3 PDF11,28-30;no new whole-page reading;physical states,Gibbs entropy,units'),
 ('L81','wiki/raw/round-18/L81-brynjolfsson-li-raymond-2025/original.html','QJE140(2),2025,889-942;publisherCDN journal HTML','Prior scope in round18notes;current reread abstract/intro opening;5172agents,15percent average task measure;staggered rollout not wholly randomized'),
]
reused=[]
for sid,path,version,scope in reuse:
 p=ROOT/path;assert p.is_file()
 item=dict(id=sid,path=path,actual_version=version,read_scope=scope,bytes=p.stat().st_size,sha256=digest(p))
 reused.append(item)
 rows.append(dict(id=sid,actual_version=version,selection_status='reused_existing_source',download_status='previous_archive_retained_no_duplicate_download',read_scope=scope,url='see original source metadata'))
save(RAW/'reuse-reading.json',reused)
contexts=['shared/theory-register.md','research/reviews/04-reading-notes.md','research/reviews/04-measures-and-bridges.md','research/reviews/18-reading-notes.md']
save(RAW/'reuse-context.json',[dict(path=p,sha256=digest(ROOT/p),scope='Existing project context,not new original evidence') for p in contexts])
with (SUR/'communication-source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

files=[dict(path=p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(RAW.rglob('*')) if p.is_file() and p.name not in ['manifest.json','checksums.sha256']]
save(RAW/'manifest.json',dict(date='2026-11-12',scope='All round27 files except manifest/checksums;old-source hashes separate',files=files))
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
errors=[]
for x in files:
 p=RAW/x['path']
 if p.stat().st_size!=x['bytes'] or digest(p)!=x['sha256']:errors.append('Archive mismatch '+x['path'])
for x in reused:
 if digest(ROOT/x['path'])!=x['sha256']:errors.append('Reuse mismatch '+x['id'])
checked=0
mdfiles=[SUR/'communication-productivity-and-order.md',SUR/'communication-models.md',SUR/'communication-reading-notes.md',SUR/'communication-search-and-selection.md',ROOT/'research/reviews/27-communication-productivity-and-order.md',RAW/'README.md',SUR/'README.md',ROOT/'README.md',ROOT/'research/README.md',ROOT/'book/README.md',ROOT/'docs/research-dependencies.md',ROOT/'wiki/raw/README.md']
for p in mdfiles:
 txt=re.sub(r'`[^`]*`','',p.read_text(encoding='utf-8'))
 for target in re.findall(r'\]\(([^)]+)\)',txt):
  target=target.strip().strip('<>')
  if re.match(r'^(https?:|chatgpt-conversation:|plugin:|#)',target):continue
  target=unquote(target.split('#')[0])
  if not target:continue
  checked+=1
  if not (p.parent/target).resolve().is_file():errors.append('Missing link '+str(p.relative_to(ROOT))+' '+target)
spec=importlib.util.spec_from_file_location('models',ROOT/'research/examples/communication-organization-models.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
actual=model.calculate();saved=json.loads((SUR/'communication-model-results.json').read_text(encoding='utf-8'))
if actual!=saved:errors.append('Finite model output differs')
result=dict(status='pass' if not errors else 'fail',date='2026-11-12',raw_files_checked=len(files),links_checked=checked,original_pdfs=pdfs,partial_official_tool_sources=1,reused_original_sources=len(reused),finite_examples_checked=3,errors=errors,scope='Archive integrity,internal versions,local links and assumed examples;not empirical validation of Ordo,influence or productivity law')
save(SUR/'communication-verification.json',result)
print(json.dumps(result,ensure_ascii=False));assert not errors
