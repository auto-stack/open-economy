"""Read-only checks of sources, counting, links and protected framework state.
Writes only the current calibration's validation receipt, never old audits.
"""
from pathlib import Path
import csv,hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-39'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
checks={};fail=[]
manifest=json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))
errors=[]
for x in manifest:
 p=RAW/x['path']
 if not p.is_file() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']:errors.append(x['path'])
checks['raw39_manifest']={'entries':len(manifest),'failures':errors}
if errors:fail.append('raw39 manifest')
actual={p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name!='manifest.json'}
listed={x['path'] for x in manifest}
checks['raw39_unlisted_files']=sorted(actual-listed)
checks['raw39_missing_files']=sorted(listed-actual)
if actual!=listed:fail.append('raw39 inventory')
reuse=json.loads((RAW/'source-reuse.json').read_text(encoding='utf-8'))
checks['reused_sources']=[{'id':x['id'],'sha_matches_record':sha(ROOT/x['original_path'])==x['sha256'],'sha_matches_prior_metadata':x['sha256']==x['prior_metadata_sha256']} for x in reuse]
if not all(x['sha_matches_record'] and x['sha_matches_prior_metadata'] for x in checks['reused_sources']):fail.append('old source integrity')
expected_tag='40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
tag=git('rev-parse','framework-v0.1^{}').decode().strip()
checks['framework_tag']={'commit':tag,'unchanged':tag==expected_tag}
if tag!=expected_tag:fail.append('framework tag')
register=ROOT/'shared/theory-register.md';reg_expected='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
checks['theory_register']={'sha256':sha(register),'unchanged':sha(register)==reg_expected}
if sha(register)!=reg_expected:fail.append('theory register')
prior=git('show','framework-v0.1:research/surveys/01-organization-maintenance/protocol.md')
snap=HERE.parent/'protocol-v0.1.snapshot.md'
checks['protocol01_snapshot']={'sha256':sha(snap),'equals_tag_bytes':snap.read_bytes()==prior}
if snap.read_bytes()!=prior:fail.append('protocol snapshot')
package_manifest=ROOT/'wiki/archive/source-package-manifest.json';pm=json.loads(package_manifest.read_text(encoding='utf-8'))
checks['old_source_package']={'manifest_unchanged':package_manifest.read_bytes()==git('show','framework-v0.1:wiki/archive/source-package-manifest.json'),'bytes_match':(ROOT/pm['local_package_path']).stat().st_size==pm['package_bytes'],'sha256_match':sha(ROOT/pm['local_package_path'])==pm['package_sha256'],'new_rounds_not_in_old_package':not any('/round-38/' in x['path'] or '/round-39/' in x['path'] for x in pm['files'])}
if not all(checks['old_source_package'].values()):fail.append('old source package')
oc=list(csv.DictReader((HERE/'retrieval-occurrences.csv').open(encoding='utf-8')));dc=list(csv.DictReader((HERE/'candidate-records.csv').open(encoding='utf-8')));units=list(csv.DictReader((HERE/'extraction-units.csv').open(encoding='utf-8')))
flow=json.loads((HERE/'flow-counts.json').read_text(encoding='utf-8'))
checks['counts']={'occurrences':len(oc),'deduplicated':len(dc),'pilot_units':len(units),'exclusions':sum(x['title_decision']=='exclude_title' for x in dc),'awaiting':sum(x['title_decision']=='await_abstract_or_fulltext' for x in dc),'formal_inclusions':sum(x['formal_inclusion'].lower()=='true' for x in dc)}
if len(oc)!=flow['retrieval_occurrences'] or len(dc)!=flow['doi_or_external_id_deduplicated_candidates'] or len(units)!=6 or checks['counts']['formal_inclusions']!=0:fail.append('counts')
by_id={x['record_id']:x for x in oc}
if len(by_id)!=len(oc):fail.append('duplicate occurrence identifiers')
for x in dc:
 for rid in x['occurrences'].split(';'):
  if rid not in by_id or (by_id[rid]['doi'] or by_id[rid]['external_id'])!=x['identity_key']:fail.append('dedup provenance')

mds=[ROOT/'README.md',ROOT/'research/README.md',ROOT/'research/survey-and-paper-program.md',ROOT/'wiki/raw/README.md',ROOT/'research/reviews/43-maintenance-survey-calibration.md',HERE.parent/'protocol.md',HERE.parent/'protocol-v0.1.snapshot.md',RAW/'README.md',ROOT/'wiki/raw/round-38/README.md',*HERE.glob('*.md')]
broken=[];links=0
for p in mds:
 for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if re.match(r'^[a-zA-Z]+://|^#',target):continue
  target=target.split('#',1)[0].strip('<>')
  dest=(p.parent/target).resolve();links+=1
  if dest==HERE/'validation.json':continue
  if not dest.exists():broken.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
checks['local_links']={'checked':links,'broken':broken}
if broken:fail.append('local links')
pdfs=list(RAW.rglob('*.pdf'))
checks['raw_payload_ignored_by_git']={p.relative_to(ROOT).as_posix():subprocess.run(['git','check-ignore','-q','--',str(p.relative_to(ROOT))],cwd=ROOT).returncode==0 for p in pdfs}
if not all(checks['raw_payload_ignored_by_git'].values()):fail.append('PDF ignore policy')
changed=git('diff','--name-only').decode().splitlines();allowed={'README.md','research/README.md','wiki/raw/README.md','research/surveys/01-organization-maintenance/protocol.md'}
checks['tracked_changes']={'paths':changed,'only_expected':set(changed)<=allowed}
if not set(changed)<=allowed:fail.append('unexpected tracked change')
result={'date_local':'2026-11-13 Asia/Shanghai','status':'pass' if not fail else 'needs_fix','checks':checks,'failures':fail,'scope':'Archive/count/link/version integrity only; not independent scientific review, full eligibility, proof reproduction or novelty certification'}
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(fail))
