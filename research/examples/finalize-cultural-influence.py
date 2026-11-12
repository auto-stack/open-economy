"""Archive identity and scoped reading checks; no empirical replication claimed."""
from pathlib import Path
import json,csv,hashlib,re
import fitz

ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-29';SUR=ROOT/'research/surveys/04-influence-and-social-equivalence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scopes={
 'L156':('JPSP79(5),2000,701-721;21page journal scan;third-party host','PDF1,14-15,16main text/table7;PDF17discussion opening selections;PDF16 visually checked;not all methods or data reanalysis','targeted_original_read'),
 'L157':('PennState original record HTML and abstract of2016CommunicationMonographs83(4):446-467;not paper body','Title,abstract,bibliography;no full meta-analysis methods,bias analysis or recalculation','official_record_abstract_only'),
 'L158':('AER110(5),2020,1572-1602;32page author file with31page article plus cited-by list','PDF1-2,28conclusions;PDF32identified as appended citation list;not all regressions;read with2024correction and replication debate','targeted_original_read_with_correction_context'),
 'L159':('BBS31,2008,target559-575;63page file559-621includes commentaries and response','PDF1-3,5target article only;PDF3definitions visually checked;other target pages/commentaries/reply not read','targeted_theoretical_framework_read'),
 'L160':('AEA official18page correction;coverNovember2024,publisherlisting3December2024','PDF1-3abstract,intro,data errors,interpretation and sampling clarification;no recalculation of updated tables','targeted_correction_read'),
 'L161':('I4RDP193,December2024;EconStor77pages,first3repository/series covers','PDF4-6abstract/introduction;first3version/rights only;no full appendix or code rerun;additional reply mentioned but not all exchanges read','targeted_replication_critique_read'),
 'L162':('I4RDP194;seriescoverDecember2024,bodytitlepageAugust2024;40page repository file;chronology not inferred','PDF4-6abstract,intro,individual-level response opening;first3version/rights;not all country analysis or tables','targeted_author_reply_read'),
}
rows=[];pdfs=[]
for p in sorted(RAW.glob('L*/metadata.json')):
 m=json.loads(p.read_text(encoding='utf-8'));version,scope,status=scopes[m['id'][:4]]
 m.update(actual_version=version,read_scope=scope,selection_status=status,download_status='original_source_file_archived_identity_checked',reading_notes='../../../../research/surveys/04-influence-and-social-equivalence/cultural-reading-notes.md',knowledge_base_status='raw archived;not converted/imported into AutoDown')
 original=p.parent/('original.html' if m['id'].startswith('L157') else 'original.pdf');assert original.is_file()
 if original.suffix=='.pdf':
  d=fitz.open(original);assert not d.is_repaired;pdfs.append(dict(id=m['id'],pages=len(d)))
 m['source_file']=dict(file=original.name,bytes=original.stat().st_size,sha256=sha(original));save(p,m)
 rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','read_scope','url']})
assert [x['pages'] for x in pdfs]==[21,32,63,18,77,40]
with (SUR/'cultural-source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
context=['shared/theory-register.md','research/reviews/14-needs-feelings-and-goals.md','research/reviews/17-commitment-authority-and-meaning.md','research/surveys/04-influence-and-social-equivalence/mobilization-definition.md']
save(RAW/'reuse-context.json',[dict(path=p,sha256=sha(ROOT/p),scope='Existing project context only;underlying other originals not newly read') for p in context])
files=[dict(path=p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file() and p.name not in ['manifest.json','checksums.sha256','verification.json']]
save(RAW/'manifest.json',dict(date='2026-11-12',scope='All round29 files except manifest,checksums,verification receipt',files=files))
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
errors=[];links=0
for x in files:
 if sha(RAW/x['path'])!=x['sha256']:errors.append('Hash mismatch '+x['path'])
md=[SUR/'art-sport-and-cultural-influence.md',SUR/'cultural-reading-notes.md',SUR/'README.md',SUR/'mobilization-definition.md',ROOT/'research/reviews/28-art-sport-and-cultural-influence.md',RAW/'README.md',ROOT/'README.md',ROOT/'research/README.md',ROOT/'book/README.md',ROOT/'docs/research-dependencies.md',ROOT/'wiki/raw/README.md']
for p in md:
 txt=re.sub(r'`[^`]*`','',p.read_text(encoding='utf-8'))
 for target in re.findall(r'\]\(([^)]+)\)',txt):
  if re.match(r'^(https?:|#|chatgpt-conversation:|plugin:)',target):continue
  links+=1
  if not (p.parent/target.split('#')[0]).resolve().is_file():errors.append('Missing link '+str(p.relative_to(ROOT))+' '+target)
result=dict(status='pass' if not errors else 'fail',raw_files_checked=len(files),links_checked=links,original_pdfs=pdfs,original_record_html=1,empirical_reanalysis=False,errors=errors,scope='Original identity,versions,integrity and local links;not validation of long-term cultural effects or Ordo')
save(RAW/'verification.json',result);print(json.dumps(result));assert not errors
