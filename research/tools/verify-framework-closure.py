"""Verify framework artifact structure, exact cash accounts and unchanged evidence.

This checks files and finite arithmetic, not scientific validity or peer review.
It never stages, commits, tags or pushes, and never rewrites raw archives.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'research/audits/framework-closure-2026-11-12'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],text=True,encoding='utf-8').strip()

def main():
    AUDIT.mkdir(parents=True,exist_ok=True)
    outline=(ROOT/'book/outline.md').read_text(encoding='utf-8')
    interfaces=(ROOT/'book/chapter-interfaces.md').read_text(encoding='utf-8')
    rows=[line for line in interfaces.splitlines() if re.match(r'^\| P\d\.\d ',line)]
    keys=[re.match(r'^\| P(\d)\.(\d) ',line).groups() for line in rows]
    expected=[(str(part),str(n)) for part,count in enumerate([5,4,4,4,7,4],1) for n in range(1,count+1)]
    assert keys==expected and len(set(keys))==28
    chinese='一二三四五六'
    outline_keys=[(str(chinese.index(m.group(1))+1),m.group(2)) for m in re.finditer(r'^\| ([一二三四五六])(\d) ',outline,re.M)]
    assert outline_keys==expected
    assert all(len([s.strip() for s in line.split('|')[1:-1]])==4 for line in rows)
    # Narrow table checks cannot verify the truth of its prose; that is recorded separately.
    assert len(list((ROOT/'book').glob('part-*/*.md')))==11
    assert len(list((ROOT/'book/argument-cards').glob('part-*.md')))==11
    register=ROOT/'shared/theory-register.md'
    assert sha(register)=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
    inputs=json.loads((AUDIT/'input-receipt.json').read_text(encoding='utf-8'))
    old_charter=next(x for x in inputs['files'] if x['path']=='docs/charter.md')
    preserved=ROOT/'docs/history/charter-v0.3-2026-11-12.original.md'
    assert sha(preserved)==old_charter['sha256']
    assert '版本：0.4' in (ROOT/'docs/charter.md').read_text(encoding='utf-8')
    # Independently check saved cash ledger rather than merely checking model flags.
    example=ROOT/'research/surveys/08-price-income-and-reinvestment'
    result=json.loads((example/'ai-income-account-results.json').read_text(encoding='utf-8'))
    ledger=list(csv.DictReader((example/'ai-income-cash-ledger.csv').open(encoding='utf-8-sig',newline='')))
    assert len(ledger)==19
    for case in result['cases']:
        cash={k:float(v) for k,v in result['initial_cash'].items()}
        transactions=[r for r in ledger if r['scenario']==case['scenario']]
        assert len(transactions)>=4
        for row in transactions:
            amount=float(row['amount']);cash[row['sender']]-=amount;cash[row['receiver']]+=amount
            assert min(cash.values())>=-1e-8 and abs(sum(cash.values())-200)<1e-8
            assert all(abs(cash[k]-float(row['cash_'+k]))<1e-8 for k in cash)
        assert cash==case['final_cash']
        assert case['actual_sales']<=case['service_capacity']
        assert case['maintenance_inside_wages']==8
    assert [x['actual_sales'] for x in result['cases']]==[92,68,80,78]
    raw_rows=list(csv.DictReader((ROOT/'research/baselines/internal-knowledge-2026-11-12/archive-integrity.csv').open(encoding='utf-8-sig',newline='')))
    assert len(raw_rows)==1117
    for row in raw_rows:assert sha(ROOT/Path(row['manifest']).parent/row['path'])==row['expected_sha256']
    raw37=json.loads((ROOT/'wiki/raw/round-37/manifest.json').read_text(encoding='utf-8'))
    for row in raw37:assert sha(ROOT/'wiki/raw/round-37'/row['path'])==row['sha256']
    old_receipt=json.loads((ROOT/'research/audits/internal-baseline-2026-11-12/artifact-receipt.json').read_text(encoding='utf-8'))
    frozen=[r for r in old_receipt['artifacts'] if r['path'].startswith('research/baselines/')]
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in frozen)
    # Primary sources and earlier readings are unchanged; record actual reused project analyses.
    reused=[ROOT/p for p in ['shared/theory-register.md','shared/concept-interfaces.md',
        'research/reviews/02-organization-criteria.md','research/reviews/03-maintenance-model.md',
        'research/reviews/04-measures-and-bridges.md','research/reviews/05-modularity-models.md',
        'research/reviews/06-memory-reuse-models.md','research/reviews/07-economic-bridge.md',
        'research/reviews/33-organization-and-economic-interfaces.md',
        'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
        'research/surveys/05-firm-authority-and-democracy/firm-power-and-democratic-governance.md',
        'research/surveys/08-price-income-and-reinvestment/financing-argument-map.md']]
    dump(AUDIT/'source-reuse.json',dict(date='2026-11-12',new_external_read_pages=0,new_literature_ids=0,
        source_type='existing_project_analyses_reused_with_original_scopes_not_primary_sources_reread',
        files=[dict(path=rel(p),sha256=sha(p)) for p in reused]))
    artifacts=[ROOT/p for p in ['README.md','research/README.md','book/README.md','book/outline.md','book/argument-map.md',
        'book/chapter-interfaces.md','book/framework-scope.md','shared/minimal-theory-core.md',
        'docs/charter.md','docs/history/charter-v0.3-2026-11-12.md',
        'docs/history/charter-v0.3-2026-11-12.original.md','docs/history/charter-v0.3-2026-11-12.provenance.json',
        'docs/framework-baseline-readiness.md','docs/research-dependencies.md',
        'research/reviews/41-framework-closure.md',
        'research/surveys/07-organization-formation/README.md',
        'research/surveys/07-organization-formation/organization-comparison-and-boundaries.md',
        'research/surveys/08-price-income-and-reinvestment/README.md',
        'research/surveys/08-price-income-and-reinvestment/ai-production-income-and-maintenance-loop.md',
        'research/surveys/08-price-income-and-reinvestment/ai-income-cash-ledger.csv',
        'research/surveys/08-price-income-and-reinvestment/ai-income-account-results.json',
        'research/examples/ai-income-feedback-accounts.py']]
    artifacts +=[Path(__file__),AUDIT/'input-receipt.json',AUDIT/'source-reuse.json']
    pending={(AUDIT/'verification.json').resolve(),(AUDIT/'artifact-receipt.json').resolve()}
    broken=[];targets=[]
    for p in artifacts:
        if p.suffix!='.md':continue
        for m in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',p.read_text(encoding='utf-8')):
            dest=m.group(1).split('#')[0].strip('<>')
            if not dest or re.match(r'\w+://',dest):continue
            # Byte-preserved source snapshots retain their documented original base;
            # the separate readable history view has normally resolving links.
            base=ROOT/'docs' if p==preserved else p.parent
            target=(base/dest).resolve();targets.append(target)
            if not target.exists() and target not in pending:broken.append(dict(file=rel(p),link=dest))
    assert not broken,broken
    # The user authorized framework closure; versioning is a separate remaining stage.
    assert git('rev-parse','HEAD')=='afc8e0517b5df4e0e932d1d4a50a5379cf19d247'
    assert git('ls-files').splitlines()==['README.md']
    assert not git('tag','--list') and not git('diff','--cached','--name-only')
    verification=dict(date_local='2026-11-12',status='framework_content_checks_pass_version_gate_pending',
        parts=6,candidate_units=28,part_counts=dict(sorted(Counter(a for a,b in keys).items())),
        chapter_drafts=11,argument_cards=11,charter_version='0.4',charter_0_3_preserved_exactly=True,
        historical_original_link_base='docs/charter.md',historical_readable_view_links_rebased=True,
        formal_79_register_unchanged=True,three_framework_dossiers_present=True,
        source_scope_expanded=False,new_raw_batch=False,new_external_literature=0,
        ledger_scenarios=4,ledger_transactions=19,cash_conservation_every_step=True,
        actual_AI_or_policy_effect_estimated=False,full_macroeconomic_equilibrium_solved=False,
        old_raw_entries_matching=len(raw_rows),round37_payloads_matching=len(raw37),
        frozen_baseline_artifacts_unchanged=len(frozen),local_links_checked=len(targets),broken_links=broken,
        gates={'1_chapter_mapping':'content_pass','2_three_bridges':'content_pass',
               '3_claim_status_and_open_hypotheses':'internal_content_review_pass',
               '4_scope_and_remaining_research':'internal_content_review_pass',
               '5_git_source_package_and_clone_checks':'not_implemented'},
        independent_peer_review=False,git_index_modified=False,commit_created=False,tag_created=False,push_executed=False,
        limits='Framework responsibility and file/account checks; not scientific proof, empirical institutional validation, or permission to publish third-party archives.')
    dump(AUDIT/'verification.json',verification)
    artifacts.append(AUDIT/'verification.json')
    dump(AUDIT/'artifact-receipt.json',dict(date='2026-11-12',self_excluded=True,
        artifacts=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(artifacts))]))
    assert all(p.exists() for p in targets)
    print(json.dumps({k:verification[k] for k in ['status','parts','candidate_units','chapter_drafts',
        'charter_version','ledger_transactions','old_raw_entries_matching','round37_payloads_matching','local_links_checked']},ensure_ascii=False))

if __name__=='__main__':main()
