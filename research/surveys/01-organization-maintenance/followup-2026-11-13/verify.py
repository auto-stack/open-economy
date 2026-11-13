"""Check this follow-up without mutating earlier research receipts or archives."""
from pathlib import Path
import csv,hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-40'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
checks={};errors=[]
for n in [38,39,40]:
 raw=ROOT/f'wiki/raw/round-{n}';manifest=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
 bad=[x['path'] for x in manifest if not (raw/x['path']).is_file() or sha(raw/x['path'])!=x['sha256'] or (raw/x['path']).stat().st_size!=x['bytes']]
 checks[f'raw{n}']={'entries':len(manifest),'failures':bad}
 if bad:errors.append(f'raw{n}')
inventory={p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name!='manifest.json'}
listed={x['path'] for x in json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))}
checks['raw40_inventory_exact']=inventory==listed
if inventory!=listed:errors.append('raw40 inventory')
records=list(csv.DictReader((HERE/'backward-reference-register.csv').open(encoding='utf-8')));forward=list(csv.DictReader((HERE/'forward-candidates.csv').open(encoding='utf-8')))
ref=json.loads((RAW/'discovery/L196-crossref.json').read_text(encoding='utf-8'))['message']['reference'];fwd=json.loads((RAW/'discovery/L196-citing-openalex.json').read_text(encoding='utf-8'))
checks['record_counts']={'backward':len(records),'forward':len(forward),'backward_matches_export':len(records)==len(ref)==88,'forward_matches_snapshot':len(forward)==len(fwd['results'])==fwd['meta']['count']==34,'new_pdf_files':len(list(RAW.rglob('*.pdf'))),'new_work_ids':['L199','L200','L201','L202','L203'],'not_inclusion_counts':True}
if not checks['record_counts']['backward_matches_export'] or not checks['record_counts']['forward_matches_snapshot'] or checks['record_counts']['new_pdf_files']!=6:errors.append('counts')
import fitz
source_checks=[]
for p in sorted(RAW.glob('L*/metadata.json')):
 m=json.loads(p.read_text(encoding='utf-8'));original=p.parent/m['original_file'];d=fitz.open(original)
 source_checks.append({'id':m['id'],'sha_match':sha(original)==m['sha256'],'pages_match':len(d)==m['pdf_pages'],'ignored_original':subprocess.run(['git','check-ignore','-q','--',str(original.relative_to(ROOT))],cwd=ROOT).returncode==0,'scope_record_exists':(p.parent/'read-scope-extension.json').is_file()})
checks['sources']=source_checks
if len(source_checks)!=6 or not all(all(x[k] for k in ['sha_match','pages_match','ignored_original','scope_record_exists']) for x in source_checks):errors.append('sources')
# Confirm the three adopted forward relationships in the acquired reference pages.
positions={'L200-bich-menatti-health':(11,'Situating homeostasis'),'L201-horseman-2025':(14,'JP286883'),'L202-farnsworth-2025':(15,'JP286883')}
checks['forward_reference_checks']={sid:term.lower() in fitz.open(RAW/sid/'original.pdf')[pn-1].get_text().lower() for sid,(pn,term) in positions.items()}
if not all(checks['forward_reference_checks'].values()):errors.append('citation links')
checks['withdrawn_candidate_not_adopted']=all(not x['source_id'] and x['status']=='withdrawn_title_do_not_use_as_evidence' for x in forward if x['title'].upper()=='WITHDRAWN')
prov=json.loads((HERE/'provenance.json').read_text(encoding='utf-8'));snap=(HERE/prov['previous_review']).resolve()
checks['review01_snapshot_unchanged']=sha(snap)==prov['previous_review_sha256']
checks['theory_register_unchanged']=sha(ROOT/'shared/theory-register.md')=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
checks['framework_tag_unchanged']=git('rev-parse','framework-v0.1^{}').decode().strip()=='40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
checks['charter04_unchanged']=(ROOT/'docs/charter.md').read_bytes()==git('show','framework-v0.1:docs/charter.md')
pm_path=ROOT/'wiki/archive/source-package-manifest.json';pm=json.loads(pm_path.read_text(encoding='utf-8'))
checks['old_source_package']={'manifest_unchanged':pm_path.read_bytes()==git('show','framework-v0.1:wiki/archive/source-package-manifest.json'),'zip_sha_match':sha(ROOT/pm['local_package_path'])==pm['package_sha256'],'new_batch_absent':not any('/round-40/' in x['path'] for x in pm['files'])}
for k in ['withdrawn_candidate_not_adopted','review01_snapshot_unchanged','theory_register_unchanged','framework_tag_unchanged','charter04_unchanged']:
 if not checks[k]:errors.append(k)
if not all(checks['old_source_package'].values()):errors.append('old package')
files=[ROOT/'README.md',ROOT/'book/README.md',ROOT/'research/README.md',ROOT/'wiki/raw/README.md',ROOT/'research/survey-and-paper-program.md',ROOT/'research/reviews/45-homeostasis-review-followup.md',HERE.parent/'protocol.md',HERE.parent/'review-2026.md',HERE.parent/'review-2026-v0.1.snapshot.md',ROOT/'book/part-02/01-human-as-organization.md',ROOT/'book/part-02/02-maintenance-and-development.md',ROOT/'book/argument-cards/part-02-01-human-as-organization.md',ROOT/'book/argument-cards/part-02-02-maintenance-and-development.md',RAW/'README.md',*HERE.glob('*.md')]
broken=[];count=0;footnote_errors=[]
for p in files:
 text=p.read_text(encoding='utf-8')
 for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',text):
  if re.match(r'^[a-zA-Z]+://|^#',target):continue
  count+=1;target=target.split('#',1)[0].strip('<>');dest=(p.parent/target).resolve()
  if dest==HERE/'validation.json':continue
  if not dest.exists():broken.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
 if p.parent.name=='part-02':
  definitions=re.findall(r'^\[\^([^\]]+)\]:',text,re.M);refs=re.findall(r'\[\^([^\]]+)\](?!:)',text)
  if len(definitions)!=len(set(definitions)) or not set(refs)<=set(definitions):footnote_errors.append(p.name)
checks['local_links']={'checked':count,'broken':broken};checks['chapter_footnotes']={'failures':footnote_errors}
if broken:errors.append('links')
if footnote_errors:errors.append('footnotes')
checks['chapter_draft_count']=len(list((ROOT/'book').glob('part-*/*.md')))
result={'date_local':'2026-11-13 Asia/Shanghai','status':'pass' if not errors else 'needs_fix','checks':checks,'failures':errors,'scope':'Sources, hashes, reference relationships, counts, local links, footnotes and protected baseline; not a scientific replication or independent full review'}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
