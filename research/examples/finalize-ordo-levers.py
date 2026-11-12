"""Check actual archived versions,scoped reading and finite examples."""
from pathlib import Path
import json,csv,hashlib,re,importlib.util
import fitz
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-32';SUR=ROOT/'research/surveys/06-technological-levers-and-organizational-evolution'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scopes={
 'L175':('PNAS8(6),1922,147-151;original request406;tool shows5page copy with next article starting on151','Tool return printed147-150body;no original PDF download or visual inspection;old population/food estimates not independently adopted'),
 'L176':('ResearchPolicy36,2007,274-287;14page author-institute journal copy','PDF1abstract/intro,PDF2selections,PDF11interaction/section7opening;not all cases or priority claims'),
 'L177':('NBERWP4148,August1992,43pages;not1995journaltypeset','PDF1cover,PDF2abstract,PDF3intro opening;no later model,equilibrium,equations or microprocessor-table analysis'),
 'L178':('AER80(2),1990,355-361;7page original article on third-party host','PDF1,3-4electrification/unit-drive/layout passages;PDF4visual;not all measurement discussion or independent historical-data audit'),
 'L179':('PNAS2011author8page EarlyEdition per tool;final citation108(26):10918-25 separately;old/new authorPDFrequestsfailed','Tool-return PDF1abstract/problem framing only;not full article,archaeological dates or all cultural-evolution evidence'),
 'L180':('37page publisher preview;copyright1990firstpublication/1992paperback;mainIntroPDF16printed3,lastPDF37printed24;not full book','PDF4-5title/copyright,PDF12contents,PDF16-18intro selections;PDF17visual;not all preface,ancient technology chapter or later historical comparison'),
}
rows=[];pdfs=[]
for p in sorted(RAW.glob('L*/metadata.json')):
 m=json.loads(p.read_text(encoding='utf-8'));v,s=scopes[m['id'][:4]];m.update(actual_version=v,read_scope=s,reading_notes='../../../../research/surveys/06-technological-levers-and-organizational-evolution/reading-notes.md',knowledge_base_status='raw archived;not converted/imported into AutoDown')
 q=p.parent/'original.pdf'
 if q.exists():
  doc=fitz.open(q);assert not doc.is_repaired;m.update(original_downloaded=True,download_status='original_archived_identity_and_version_checked',selection_status='targeted_original_pdf_read',pages=len(doc));pdfs.append(dict(id=m['id'],pages=len(doc)))
 else:
  q=p.parent/'tool-return-selected.partial.txt';assert q.is_file() and q.stat().st_size>1200
  m.update(original_downloaded=False,download_status='original_requests_failed_primary_tool_passages_only',selection_status='primary_paper_tool_selections_only',format='partial_tool_return')
 m['source_file']=dict(file=q.name,bytes=q.stat().st_size,sha256=sha(q));save(p,m)
 rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','read_scope','url']})
assert [x['pages'] for x in pdfs]==[14,43,7,37]
with (SUR/'source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
reused=[('wiki/raw/round-01/L03-prigogine-1977/original.pdf','Prior lecture scope for nonequilibrium and entropy exchange;no new pages'),('wiki/raw/round-04/L20-kolchinsky-wolpert-2018/original.pdf','PriorPDF5-7functional information/viability;no new pages'),('wiki/raw/round-19/L84-romer-1990/original.pdf','PriorPDF1-4nonrival designs,investment and execution resources;no later model proof'),('wiki/raw/round-28/L155-brynjolfsson-rock-syverson-record/original.html','OfficialNBERrecord abstract only,not full J-curve paper;prior complementary-investment context'),('shared/theory-register.md','Formal79baseline and OrdoHYP01unchanged;project context'),('research/reviews/10-research-synthesis.md','Prior treatment of leverage and bounded mechanisms;project context'),('research/reviews/04-measures-and-bridges.md','Existing physical/functional/valuation boundaries;project context')]
items=[dict(path=p,scope=s,sha256=sha(ROOT/p)) for p,s in reused]
old=Path('D:/Down/Entropy Economy.2026-11-11.md');assert old.is_file();items.append(dict(path=str(old),scope='User historical dialogue around lines150-223;design history only,not current instructions or external scientific evidence',sha256=sha(old)))
save(RAW/'reuse-context.json',items)
files=[dict(path=p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file() and p.name not in ['manifest.json','checksums.sha256','verification.json']]
save(RAW/'manifest.json',dict(date='2026-11-12',scope='All round32 files except manifest,checksums,verification',files=files));(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
errors=[];links=0
for x in files:
 if sha(RAW/x['path'])!=x['sha256']:errors.append('Hash mismatch '+x['path'])
md=list(SUR.glob('*.md'))+[RAW/'README.md',ROOT/'research/reviews/31-inputs-levers-and-organizational-evolution.md',ROOT/'README.md',ROOT/'research/README.md',ROOT/'book/README.md',ROOT/'docs/research-dependencies.md',ROOT/'wiki/raw/README.md']
for p in md:
 txt=re.sub(r'`[^`]*`','',p.read_text(encoding='utf-8'))
 for target in re.findall(r'\]\(([^)]+)\)',txt):
  if re.match(r'^(https?:|#|chatgpt-conversation:|plugin:)',target):continue
  links+=1
  if not (p.parent/target.split('#')[0]).resolve().is_file():errors.append('Missing link '+str(p.relative_to(ROOT))+' '+target)
spec=importlib.util.spec_from_file_location('model',ROOT/'research/examples/ordo-lever-models.py');model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
if model.calculate()!=json.loads((SUR/'model-results.json').read_text(encoding='utf-8')):errors.append('Model mismatch')
r=dict(status='pass' if not errors else 'fail',raw_files_checked=len(files),links_checked=links,original_pdfs=pdfs,primary_tool_only_sources=2,reused_original_or_record_sources=4,finite_examples_checked=2,errors=errors,scope='Archive identity,version/scope,integrity,links,finite arithmetic;not empirical validation of evolution,Ordo or technological returns')
save(RAW/'verification.json',r);print(json.dumps(r));assert not errors
