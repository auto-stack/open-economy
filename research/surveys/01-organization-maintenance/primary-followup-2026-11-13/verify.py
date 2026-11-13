"""Check new source states and book references without changing previous receipts."""
from pathlib import Path
import csv,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-41'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
checks={};fail=[]
for n in [38,39,40,41]:
 raw=ROOT/f'wiki/raw/round-{n}';m=json.loads((raw/'manifest.json').read_text(encoding='utf-8'));bad=[x['path'] for x in m if not (raw/x['path']).is_file() or sha(raw/x['path'])!=x['sha256'] or (raw/x['path']).stat().st_size!=x['bytes']]
 checks[f'raw{n}_manifest']={'entries':len(m),'failures':bad}
 if bad:fail.append(f'raw{n}')
listed={x['path'] for x in json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))};actual={p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name!='manifest.json'}
checks['raw41_inventory_exact']=listed==actual
if listed!=actual:fail.append('inventory')
rows=list(csv.DictReader((HERE/'source-status.csv').open(encoding='utf-8')))
checks['source_counts']={'records':len(rows),'complete_documents_obtained':sum(x['content_status']=='full_text_targeted_reading' for x in rows),'abstract_or_preview':sum(x['content_status']!='full_text_targeted_reading' for x in rows),'pdf_files':len(list(RAW.rglob('*.pdf')))}
if checks['source_counts']!={'records':7,'complete_documents_obtained':3,'abstract_or_preview':4,'pdf_files':2}:fail.append('counts')
import fitz
sources=[]
for p in sorted(RAW.glob('L*/metadata.json')):
 m=json.loads(p.read_text(encoding='utf-8'));f=p.parent/m['adopted_file'];b=f.read_bytes()
 if f.suffix=='.pdf':
  d=fitz.open(f);text=''.join(x.get_text() for x in d);pages=len(d)==m['pdf_pages']
 else:text=b.decode('utf-8');pages=True
 identity=m['doi'].lower() in re.sub(r'\s+','',text).lower()
 sources.append({'id':m['id'],'hash_matches':sha(f)==m['sha256'],'doi_in_payload':identity,'page_count_matches':pages,'content_state':m['content_status'],'ignored_original':subprocess.run(['git','check-ignore','-q','--',str(f.relative_to(ROOT))],cwd=ROOT).returncode==0})
checks['source_integrity']=sources
if len(sources)!=7 or not all(all(x[k] for k in ['hash_matches','doi_in_payload','page_count_matches','ignored_original']) for x in sources):fail.append('source integrity')
x=ET.parse(RAW/'L208-beyond-2026/original.xml').getroot()
checks['JATS_identity']={'article_root':x.tag=='article','doi':any(z.text=='10.14814/phy2.71150' for z in x.findall('.//article-id')),'body_present':x.find('body') is not None,'not_bioc_error':not (RAW/'L208-beyond-2026/original.xml').read_text(encoding='utf-8').startswith('[Error]')}
if not all(checks['JATS_identity'].values()):fail.append('JATS')
ref207=fitz.open(RAW/'L207-weinberger-2026/original.pdf')[27].get_text()
ref208=' '.join(' '.join(z.itertext()) for z in x.findall('.//ref'))
checks['2026_seed_citation_checks']={'L207_PDF28':'Situating homeostasis' in ref207,'L208_JATS_references':'Situating homeostasis' in ref208}
if not all(checks['2026_seed_citation_checks'].values()):fail.append('seed citations')
prov=json.loads((HERE/'provenance.json').read_text(encoding='utf-8'))
checks['review02_snapshot']=sha((HERE/prov['previous_review']).resolve())==prov['previous_sha256']
checks['formal_register_unchanged']=sha(ROOT/'shared/theory-register.md')=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
checks['framework_tag_unchanged']=git('rev-parse','framework-v0.1^{}').decode().strip()=='40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
checks['charter04_unchanged']=(ROOT/'docs/charter.md').read_bytes()==git('show','framework-v0.1:docs/charter.md')
pm_file=ROOT/'wiki/archive/source-package-manifest.json';pm=json.loads(pm_file.read_text(encoding='utf-8'))
checks['old_source_package']={'manifest_unchanged':pm_file.read_bytes()==git('show','framework-v0.1:wiki/archive/source-package-manifest.json'),'zip_unchanged':sha(ROOT/pm['local_package_path'])==pm['package_sha256'],'new_batch_absent':not any('/round-41/' in z['path'] for z in pm['files'])}
for k in ['review02_snapshot','formal_register_unchanged','framework_tag_unchanged','charter04_unchanged']:
 if not checks[k]:fail.append(k)
if not all(checks['old_source_package'].values()):fail.append('old source package')
files=[ROOT/'README.md',ROOT/'research/README.md',ROOT/'book/README.md',ROOT/'wiki/raw/README.md',ROOT/'research/survey-and-paper-program.md',ROOT/'research/reviews/46-primary-regulation-and-2026.md',HERE.parent/'protocol.md',HERE.parent/'review-2026.md',HERE.parent/'review-2026-v0.2.snapshot.md',ROOT/'book/part-02/01-human-as-organization.md',ROOT/'book/part-02/02-maintenance-and-development.md',ROOT/'book/argument-cards/part-02-01-human-as-organization.md',ROOT/'book/argument-cards/part-02-02-maintenance-and-development.md',RAW/'README.md',*HERE.glob('*.md')]
broken=[];footnotes=[];count=0
for p in files:
 text=p.read_text(encoding='utf-8')
 for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',text):
  if re.match(r'^[a-zA-Z]+://|^#',target):continue
  count+=1;dest=(p.parent/target.split('#',1)[0].strip('<>')).resolve()
  if dest!=HERE/'validation.json' and not dest.exists():broken.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
 if p.parent.name=='part-02':
  defs=re.findall(r'^\[\^([^\]]+)\]:',text,re.M);refs=re.findall(r'\[\^([^\]]+)\](?!:)',text)
  if len(defs)!=len(set(defs)) or not set(refs)<=set(defs):footnotes.append(p.name)
checks['links']={'checked':count,'broken':broken};checks['footnote_failures']=footnotes
if broken or footnotes:fail.append('document links/notes')
checks['book_draft_count']=len(list((ROOT/'book').glob('part-*/*.md')))
if checks['book_draft_count']!=11:fail.append('draft count')
result={'date_local':'2026-11-13 Asia/Shanghai','status':'pass' if not fail else 'needs_fix','checks':checks,'failures':fail,'scope':'Payload states, hashes, IDs, citations, counts, links and protected framework; not independent scientific review, model reproduction or complete literature coverage'}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(fail))
