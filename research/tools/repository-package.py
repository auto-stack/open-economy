"""Inventory, archive and validate the manuscript/source split without changing Git.

prepare: create an ignored local ZIP and versioned source-package manifest.
check: validate a Git index/tree, its links and available archive payloads.
No command stages, commits, tags or pushes. No original source is modified.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import os
import re
import subprocess
import urllib.parse
import zipfile
from datetime import date

ROOT=Path(__file__).resolve().parents[2]
MANIFEST='wiki/archive/source-package-manifest.json'
RECEIPTS='.local-artifacts/versioning'

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args,input=None):
    return subprocess.check_output(['git','-c','core.quotepath=false',*args],cwd=ROOT,input=input)
def paths(mode,revision):
    args=['ls-files','-z'] if mode=='index' else ['ls-tree','-r','--name-only','-z',revision]
    return [x.decode('utf-8') for x in git(*args).split(b'\0') if x]
def get_blob(path,mode,revision):return git('show',(':'+path) if mode=='index' else revision+':'+path)
def all_blobs(selected,mode,revision):
    # Use one Git process rather than one per file, including byte-exact blobs.
    data=git('ls-files','--stage','-z') if mode=='index' else git('ls-tree','-r','-z',revision)
    objects={}
    for record in data.split(b'\0'):
        if not record:continue
        header,path=record.split(b'\t',1)
        parts=header.split();objects[path.decode('utf-8')]=parts[1] if mode=='index' else parts[2]
    query=b''.join(objects[p]+b'\n' for p in selected)
    raw=git('cat-file','--batch',input=query);offset=0;result={}
    for p in selected:
        end=raw.index(b'\n',offset);size=int(raw[offset:end].split()[-1]);offset=end+1
        result[p]=raw[offset:offset+size];offset+=size+1
    return result
def clean_relative(base,dest):
    return os.path.normpath(str(PurePosixPath(base)/dest)).replace('\\','/')

def prepare():
    files=[]
    for folder in ['wiki/raw','wiki/derived']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    files.extend(p for p in (ROOT/'research').rglob('*') if p.is_file() and 'inspection' in p.relative_to(ROOT).parts)
    files=sorted(set(files))
    out=ROOT/'.local-artifacts/open-economy-source-pack-2026-11-12.zip'
    out.parent.mkdir(exist_ok=True)
    # Overwriting this task-owned ZIP does not touch any original source file.
    records=[]
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:
            relative=p.relative_to(ROOT).as_posix()
            z.write(p,relative)
            records.append(dict(path=relative,bytes=p.stat().st_size,sha256=sha(p)))
    dump(ROOT/MANIFEST,dict(version='1',date_local='2026-11-12',
        package_name=out.name,local_package_path=out.relative_to(ROOT).as_posix(),
        package_bytes=out.stat().st_size,package_sha256=sha(out),
        published_to_remote=False,source_redistribution_reviewed=False,
        contents='Raw and derived archives plus research inspection images; caches excluded. Originals retained in place.',
        file_count=len(records),files=records))
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={r['path'] for r in records}
        assert all(sha_bytes(z.read(r['path']))==r['sha256'] for r in records)
    print(json.dumps(dict(source_package_files=len(records),bytes=out.stat().st_size,zip_checked=True)))

def check(mode,revision,output,root=None):
    selected=paths(mode,revision);selected_set=set(selected)
    payloads=all_blobs(selected,mode,revision)
    package=json.loads(payloads[MANIFEST])
    optional={r['path']:r for r in package['files']}
    zip_members=set(optional)
    # Later batches have their own manifests and need not be in the original ZIP.
    for name in selected:
        if name in optional or not re.fullmatch(r'wiki/raw/round-\d+/manifest\.json',name):
            continue
        batch=json.loads(payloads[name])
        records=batch if isinstance(batch,list) else batch['files']
        for record in records:
            target=clean_relative(str(PurePosixPath(name).parent),record['path'])
            assert target.startswith(str(PurePosixPath(name).parent)+'/'),target
            optional[target]=record
    statuses=collections.Counter();mismatches=[]
    material_root=Path(root).resolve() if root else ROOT
    if root:
        # A pre-commit export must actually contain the exact selected Git bytes.
        wrong=[p for p,b in payloads.items() if not (material_root/p).is_file() or sha(material_root/p)!=sha_bytes(b)]
        assert not wrong,{'repository_export_missing_or_different':wrong}
    archive_zip=material_root/package['local_package_path']
    zip_verified=False
    if archive_zip.exists():
        assert sha(archive_zip)==package['package_sha256'],'Source ZIP checksum mismatch'
        zip_verified=True
    for name,record in optional.items():
        p=material_root/name
        if name in zip_members and name in payloads and sha_bytes(payloads[name])!=record['sha256']:
            # The live Git document may have evolved since the dated ZIP.
            statuses['versioned_document_with_new_revision']+=1
            continue
        if not p.exists():statuses['optional_source_not_installed']+=1
        elif sha(p)==record['sha256']:statuses['available_source_hash_matches']+=1
        else:mismatches.append(name)
    if mismatches:raise AssertionError({'archive_hash_mismatches':mismatches})
    forbidden=[]
    raw_records={'README.md','metadata.json','attempt-metadata.json','manifest.json',
        'crosscheck-metadata.json','read-scope-extension.json','source-reuse.json',
        'download-log.json','acquisition-attempts.json','response-classification.json'}
    derived_records={'README.md','formula-and-page-checks.md','verified-formulas.md',
        'formula-register.json','provenance.json','manifest-sha256.json'}
    for name in selected:
        p=PurePosixPath(name)
        if '__pycache__' in p.parts or p.suffix in {'.pyc','.pdf','.bin','.html','.empty-response'} or 'inspection' in p.parts or name.startswith('.local-artifacts/'):
            forbidden.append(name)
        if name.startswith('wiki/raw/') and p.name not in raw_records and p.suffix!='.sha256':forbidden.append(name)
        if name.startswith('wiki/derived/') and p.name not in derived_records:forbidden.append(name)
    assert not forbidden,forbidden
    # Historical byte snapshots retain their original relative-link context.
    contexts={
        'docs/history/charter-v0.1-2026-11-11.md':'docs',
        'docs/history/charter-v0.2-2026-11-12.md':'docs',
        'docs/history/charter-v0.3-2026-11-12.original.md':'docs',
        'book/history/part-02-01-human-as-organization-before-restructure-2026-11-12.md':'book/part-02'}
    for folder,origin_field in [
        ('wiki/raw/round-48/internal-comparison','origin'),
        ('wiki/raw/round-49/audit-records','audit_record_origin'),
        ('wiki/raw/round-50/trial-records','trial_origin')]:
        frozen=folder+'/README.md'
        if frozen in payloads:
            batch=str(PurePosixPath(folder).parent)
            origin=json.loads(payloads[batch+'/metadata.json'])[origin_field]
            contexts[frozen]=clean_relative(batch,origin)
    links=collections.Counter();broken=[];historical=[]
    for name,body in payloads.items():
        if not name.endswith('.md'):continue
        text=body.decode('utf-8-sig')
        text=re.sub(r'```[\s\S]*?```','',text)
        text=re.sub(r'`[^`\n]*`','',text)
        for m in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',text):
            dest=urllib.parse.unquote(m.group(1).strip('<>').split('#')[0])
            if not dest or re.match(r'[a-zA-Z][\w+.-]*:',dest):continue
            base=contexts.get(name,str(PurePosixPath(name).parent))
            target=clean_relative(base,dest)
            if target in selected_set:links['required_repository_target']+=1
            elif target in optional:links['optional_source_package_target']+=1
            elif any(x.startswith(target.rstrip('/')+'/') for x in optional):links['optional_source_package_directory']+=1
            elif any(x.startswith(target.rstrip('/')+'/') for x in selected):links['repository_directory']+=1
            else:
                item=dict(file=name,target=target,link=dest)
                if name.startswith('wiki/raw/') or name in contexts:historical.append(item)
                else:broken.append(item)
    # Detect secret-shaped material without exposing matching values in logs.
    secret_patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        r'\bgh[pousr]_[A-Za-z0-9]{30,}\b',r'\bgithub_pat_[A-Za-z0-9_]{40,}\b',
        r'\bsk-proj-[A-Za-z0-9_-]{30,}\b',r'(?i)(?:access_token|api_key|client_secret)\s*[=:]\s*[\"\x27]?[A-Za-z0-9_\-]{24,}']
    findings=[]
    for name,body in payloads.items():
        if b'\0' in body[:2048]:continue
        text=body.decode('utf-8',errors='replace')
        if any(re.search(p,text) for p in secret_patterns):findings.append(name)
    assert not findings,{'secret_shaped_values_in':findings}
    # Check the release's actual framework and finite accounting artifacts.
    outline=payloads['book/outline.md'].decode('utf-8')
    interfaces=payloads['book/chapter-interfaces.md'].decode('utf-8')
    keys=[m.groups() for m in re.finditer(r'^\| P(\d)\.(\d) ',interfaces,re.M)]
    expected=[(str(p),str(n)) for p,count in enumerate([5,4,4,4,7,4],1) for n in range(1,count+1)]
    assert keys==expected
    assert len(re.findall(r'^\| [一二三四五六]\d ',outline,re.M))==28
    drafts=[p for p in selected if re.match(r'^book/part-\d+/[^/]+\.md$',p)]
    cards=[p for p in selected if re.match(r'^book/argument-cards/part-.*\.md$',p)]
    listed_drafts={'book/'+p for p in re.findall(r'\]\((part-\d+/[^)\s#]+\.md)\)',outline)}
    assert set(drafts)==listed_drafts,{'drafts_missing_or_unlisted':sorted(set(drafts)^listed_drafts)}
    expected_cards={f'book/argument-cards/{p.parent.name}-{p.name}' for p in map(PurePosixPath,drafts)}
    assert set(cards)==expected_cards,{'cards_missing_or_unpaired':sorted(set(cards)^expected_cards)}
    assert '版本：0.4' in payloads['docs/charter.md'].decode('utf-8')
    assert sha_bytes(payloads['shared/theory-register.md'])=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
    import csv,io
    ledger=list(csv.DictReader(io.StringIO(payloads['research/surveys/08-price-income-and-reinvestment/ai-income-cash-ledger.csv'].decode('utf-8-sig'))))
    assert len(ledger)==19
    groups=collections.defaultdict(list)
    for r in ledger:groups[r['scenario']].append(r)
    for group in groups.values():
        balances={'A':40.,'B':40.,'firm':100.,'public':20.}
        for row in group:
            amount=float(row['amount']);balances[row['sender']]-=amount;balances[row['receiver']]+=amount
            assert min(balances.values())>=0 and abs(sum(balances.values())-200)<1e-8
            assert all(abs(balances[k]-float(row['cash_'+k]))<1e-8 for k in balances)
    result=dict(date_local=date.today().isoformat(),mode=mode,revision=revision if mode=='tree' else 'staged-index',
        status='pass' if not broken and not historical else 'needs_link_review',
        selected_files=len(selected),selected_bytes=sum(len(b) for b in payloads.values()),
        source_package_file_count=package['file_count'],archive_status=dict(statuses),
        source_zip_installed=archive_zip.exists(),source_zip_checksum_verified=zip_verified,
        available_source_integrity_verified=not mismatches,
        all_sources_installed=statuses.get('optional_source_not_installed',0)==0,
        all_source_hashes_verified=not mismatches and statuses.get('optional_source_not_installed',0)==0 and not statuses.get('versioned_document_with_new_revision',0),
        repository_export_bytes_verified=bool(root),link_counts=dict(links),broken_required_links=broken,
        historical_link_issues=historical,forbidden_payloads=forbidden,secret_shaped_values_found=len(findings),
        source_redistribution_reviewed=False,scientific_claims_validated=False,
        framework_checks=dict(candidate_units=28,parts=6,chapter_drafts=len(drafts),argument_cards=len(cards),
            charter_version='0.4',formal79_register_unchanged=True,accounting_rows=19,
            every_transaction_conserves_cash=True))
    dump(ROOT/output,result)
    print(json.dumps({k:result[k] for k in ['status','selected_files','selected_bytes','archive_status','link_counts']},ensure_ascii=False))
    if broken or historical:print(json.dumps({'broken':broken[:25],'historical':historical[:25],'counts':[len(broken),len(historical)]},ensure_ascii=False))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','check'])
    parser.add_argument('--mode',choices=['index','tree'],default='index')
    parser.add_argument('--revision',default='HEAD')
    parser.add_argument('--source-root')
    parser.add_argument('--output',default=RECEIPTS+'/precommit-check.json')
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    else:
        result=check(args.mode,args.revision,args.output,args.source_root)
        raise SystemExit(0 if result['status']=='pass' else 1)
