"""Write explicit followup provenance, preserve old archives and audit new artifacts."""
from pathlib import Path
import csv
import hashlib
import json
import re
import fitz

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-37'
DER=ROOT/'wiki/derived/financing-followup-2026-11-12'
AUDIT=ROOT/'research/audits/financing-argument-2026-11-12'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def jl(p,rows):p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

def main():
    AUDIT.mkdir(parents=True,exist_ok=True)
    # A2xx status is a transport outcome, not proof that the requested article was served.
    logs=json.loads((RAW/'acquisition-attempts.json').read_text(encoding='utf-8'))
    classifications=[]
    for e in logs:
        file=ROOT/e['file'] if e.get('file') else None
        is_pdf=bool(file and file.read_bytes().startswith(b'%PDF-'))
        html=file.read_text(encoding='utf-8',errors='replace') if file and not is_pdf else ''
        challenge=bool(re.search(r'not a bot|fs-ch-|verify|verification',html,re.I)) and 'mit-publications' not in str(file)
        e['content_classification']='article_pdf' if is_pdf else 'verification_or_challenge_html' if challenge else 'author_bibliography_html'
        e['requested_article_obtained']=is_pdf
        classifications.append({k:e.get(k) for k in ['url','status','file','content_classification','requested_article_obtained']})
    dump(RAW/'acquisition-attempts.json',logs)
    dump(RAW/'response-classification.json',classifications)
    assert sum(e['requested_article_obtained'] for e in logs)==2
    assert sum(e['content_classification']=='verification_or_challenge_html' for e in logs)==3
    old=ROOT/'wiki/raw/round-36/L190-holmstrom-tirole-1997/original.pdf'
    assert sha(old)=='6db56bda95911484f48e631a82bc1e4443c6e7c2ec144454d76755793570686b'
    pages=[]
    for n in range(8,14):
        stem=f'pdf-{n:02d}-print-{n+661}'
        p=DER/'L190'/(stem+'.ocr.json')
        ocr=json.loads(p.read_text(encoding='utf-8-sig'))
        assert (DER/'L190'/(stem+'.raw.txt')).read_text(encoding='utf-8').rstrip('\n')==ocr['text']
        pages.append(dict(pdf_page=n,printed_page=n+661,printed_numeral_visually_checked=True,
            image=rel(DER/'L190'/(stem+'.png')),raw_ocr_json=rel(p),raw_text=rel(DER/'L190'/(stem+'.raw.txt')),
            engine=ocr['engine'],language=ocr['language'],body_ocr_word_for_word_checked=False,
            formula_and_key_passage_review='single_assistant_visual',verified_notes=rel(DER/'verified-formulas.md')))
    dump(RAW/'L190-extension/read-scope-extension.json',dict(work_id='L190',date='2026-11-12',
        source=rel(old),source_sha256=sha(old),copied_original=False,previous_read_scope='PDF2–7,printed663–668',
        new_pages=pages,cumulative_read_scope='PDF2–13,printed663–674',whole_work_read=False,
        source_issue='Printed671 equation(3) negative RHS conflicts with printed668 positive good-project surplus; retained, not used as model premise.'))
    sw=RAW/'L189-crosscheck/ucsd-copy.pdf';ht=RAW/'L190-crosscheck/stanford-copy.pdf'
    assert fitz.open(sw).page_count==19 and fitz.open(ht).page_count==30
    dump(RAW/'L189-crosscheck/crosscheck-metadata.json',dict(work_id='L189',date='2026-11-12',
        title='Credit Rationing in Markets with Imperfect Information',authors=['Joseph E. Stiglitz','Andrew Weiss'],year=1981,
        original_source='wiki/raw/round-36/L189-stiglitz-weiss-1981/original.pdf',
        mirror_url='https://pages.ucsd.edu/~aronatas/project/academic/Stiglitz%20credit.pdf',
        mirror_file=rel(sw),mirror_sha256=sha(sw),pdf_pages=19,read_scope='Visual PDF4,printed395 only',
        result='same visible theta1>theta2, equation(2)>= and footnote5 project-number discrepancy',
        formal_erratum_obtained=False,whole_work_read=False,original_scan_replaced=False))
    dump(RAW/'L190-crosscheck/crosscheck-metadata.json',dict(work_id='L190',date='2026-11-12',
        title='Financial Intermediation, Loanable Funds, and the Real Sector',authors=['Bengt Holmstrom','Jean Tirole'],year=1997,
        original_source=rel(old),mirror_url='https://web.stanford.edu/~piazzesi/Reading/Holmstrom%26Tirole%20QJE%201997.pdf',
        mirror_file=rel(ht),mirror_sha256=sha(ht),pdf_pages=30,
        actual_version='Text-bearing university mirror of1997journal layout; first PDFpage is article663; not compared whole-file with publisher',
        read_scope='Visual PDF9,printed671 only; first-page bibliographic placement checked; PDF10,printed672 was a mechanical locating preview only',
        result='equation(3) negative RHS also visible in this copy',
        author_bibliography=dict(file='mit-publications.html',url='https://economics.mit.edu/people/faculty/bengt-holmstrom/publications',
            read_scope='Only the1997 article listing and JSTOR link',journal='QJE112(3):663–691',
            jstor_url='http://www.jstor.org/stable/2951252'),
        formal_erratum_obtained=False,whole_work_read=False,original_scan_replaced=False))
    queries=[
        'Stiglitz Weiss 1981 Credit Rationing corrigendum footnote 5 theta1 theta2 equation 2',
        'Holmstrom Tirole 1997 Financial Intermediation Loanable Funds Real Sector pdf 669 670 incentive',
        '"Credit Rationing" "Stiglitz" "Weiss" "erratum"',
        '"Credit Rationing" "Stiglitz" "Weiss" "corrigendum"',
        'site.academiccommons.columbia.edu "Credit Rationing in Markets with Imperfect Information"',
        '"Holmstrom" "Tirole" "1997" "errata"',
        '"Holmstrom" "Tirole" "1997" "Condition (3)"',
        '"Credit Rationing" "footnote 5" "Stiglitz"',
        '"Holmstrom Tirole" "typo" "1997"',
        '"Holmström" "Tirole" "erratum" 1997',
        '"Stiglitz Weiss" "typo" 1981',
        'site.aeaweb.org "Credit Rationing in Markets with Imperfect Information" correction',
        'site.academic.oup.com/qje "Financial Intermediation" "Correction"']
    dump(RAW/'discovery/search-log.json',dict(date='2026-11-12',query_count=len(queries),queries=queries,
        initial_two_queries_repeated_and_saved=True,
        selection='Only the original papers, alternative university copies and author bibliography used; unrelated hits remain discovery only.',
        finding='No formal correction obtained within these bounded searches and accessible endpoints; does not prove none exists.',
        new_literature_ids=0,archived_pdf_copies=2))
    dump(RAW/'source-reuse.json',dict(date='2026-11-12',sources=[
        dict(work_id='L185',metadata='wiki/raw/round-35/L185-nash-1950/metadata.json',
             read_scope='Previously read155,157–159; no new pages this round'),
        dict(work_id='L190',metadata='wiki/raw/round-36/L190-holmstrom-tirole-1997/metadata.json',
             read_scope='Extension specified separately; old source and metadata unchanged'),
        dict(work_id='L42',metadata='wiki/raw/round-08/L42-vonhippel-vonkrogh-2002/metadata.json',
             read_scope='Reused previous2002draft cover and16–18 only; no new reading'),
        dict(work_id='L43',metadata='wiki/raw/round-08/L43-riehle-2012/metadata.json',
             read_scope='Reused previous author-copy1,3–6 only; no new reading')]))
    followups=[dict(work_id='L189',stage='round37_crosscheck',source='wiki/raw/round-36/L189-stiglitz-weiss-1981/original.pdf',
        crosscheck=rel(RAW/'L189-crosscheck/crosscheck-metadata.json'),new_read_scope='Same printed395 in alternative copy; no additional article pages',
        formal_erratum_obtained=False),
        dict(work_id='L190',stage='round37_extension_and_crosscheck',source=rel(old),source_sha256=sha(old),
        scope_record=rel(RAW/'L190-extension/read-scope-extension.json'),crosscheck=rel(RAW/'L190-crosscheck/crosscheck-metadata.json'),
        new_read_scope='PDF8–13,printed669–674',cumulative_read_scope='PDF2–13,printed663–674',formal_erratum_obtained=False)]
    jl(ROOT/'wiki/index/source-followups.jsonl',followups)
    cat=ROOT/'wiki/index/derived-text-catalog.jsonl'
    records=[json.loads(line) for line in cat.read_text(encoding='utf-8').splitlines() if line]
    records=[r for r in records if r.get('stage')!='round37_formula_extension']
    records.append(dict(work_id='L190',stage='round37_formula_extension',source=rel(old),source_sha256=sha(old),
        derived_on='2026-11-12',text_status='formula_and_key_passage_notes_checked_body_ocr_unverified',
        pdf_pages=list(range(8,14)),printed_pages=list(range(669,675)),whole_work_ocr=False,
        text=rel(DER/'verified-formulas.md'),provenance=rel(RAW/'L190-extension/read-scope-extension.json'),
        original_pdf_text_layer_changed=False,independent_double_entry=False))
    jl(cat,records)
    ann=ROOT/'wiki/index/source-annotations.json'
    annotations=json.loads(ann.read_text(encoding='utf-8'))
    annotations=[x for x in annotations if x.get('kind')!='financing_argument_followup_round37']
    annotations.append(dict(work_ids=['L189','L190'],kind='financing_argument_followup_round37',date='2026-11-12',
        observation='Alternative copies reproduce two printed inconsistencies; no formal erratum obtained. L190 extension669–674 read visually; formulas checked, body OCR unverified.',
        use='See wiki/index/source-followups.jsonl and new formula notes; do not rewrite older snapshots or infer whole-paper reading.',
        raw_metadata_changed=False))
    dump(ann,annotations)
    # Freeze this batch only after writing its scope and acquisition records.
    raw_files=[p for p in RAW.rglob('*') if p.is_file() and p.name!='manifest.json']
    dump(RAW/'manifest.json',[dict(path=p.relative_to(RAW).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(raw_files)])
    assert sha(ROOT/'shared/theory-register.md')=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
    old_receipt=json.loads((ROOT/'research/audits/internal-baseline-2026-11-12/artifact-receipt.json').read_text(encoding='utf-8'))
    frozen=[r for r in old_receipt['artifacts'] if r['path'].startswith('research/baselines/')]
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in frozen)
    ocr_manifest=json.loads((ROOT/'wiki/derived/cited-page-text-2026-11-12/manifest-sha256.json').read_text(encoding='utf-8'))
    assert all(sha(ROOT/'wiki/derived/cited-page-text-2026-11-12'/r['path'])==r['sha256'] for r in ocr_manifest['files'])
    original_rows=list(csv.DictReader((ROOT/'research/baselines/internal-knowledge-2026-11-12/archive-integrity.csv').open(encoding='utf-8-sig',newline='')))
    assert all(sha(ROOT/Path(r['manifest']).parent/r['path'])==r['expected_sha256'] for r in original_rows)
    results=json.loads((ROOT/'research/surveys/08-price-income-and-reinvestment/financing-argument-model-results.json').read_text(encoding='utf-8'))
    assert all(results['financing']['checks'].values())
    assert results['financing']['strict_contract']['Im']+results['financing']['strict_contract']['Iu']+20==100
    cash=list(csv.DictReader((ROOT/'research/surveys/08-price-income-and-reinvestment/institution-cash-scenarios.csv').open(encoding='utf-8-sig',newline='')))
    assert len(cash)==144
    cash_groups={}
    for row in cash:cash_groups.setdefault((row['scenario'],row['regime']),[]).append(row)
    for group in cash_groups.values():
        prior=14.0;failed=False
        for row in group:
            executable=row['fixed_service_executable']=='True'
            if executable:
                assert not failed
                end=float(row['actual_end_total'])
                assert abs(end-(prior+float(row['inflow'])-14.0))<1e-8
                assert end>=0
                if row['regime']!='pooled':
                    balances=[float(row[k]) for k in ['actual_end_maintenance','actual_end_platform','actual_end_contributor']]
                    assert min(balances)>=-1e-8 and abs(sum(balances)-end)<1e-8
                    if float(row['authorized_platform_transfer'])>0:assert float(row['actual_end_platform'])>=4.0-1e-8
                prior=end
            else:
                failed=True
                assert row['actual_end_total']==''
    assert len(cash_groups)==12
    # Only changed/new documents are checked; historic round labels and old counts remain intact.
    changed=[ROOT/p for p in ['README.md','research/README.md','wiki/index/README.md','wiki/index/SOURCES.md','wiki/raw/README.md',
        'book/part-05/06-investment-income-and-reinvestment.md','book/argument-cards/part-05-06-investment-income-and-reinvestment.md',
        'research/reviews/39-financing-open-business-argument-audit.md',
        'research/surveys/08-price-income-and-reinvestment/README.md',
        'research/surveys/08-price-income-and-reinvestment/credit-reading-notes.md',
        'research/surveys/08-price-income-and-reinvestment/financing-argument-map.md',
        'research/surveys/08-price-income-and-reinvestment/financing-argument-models.md',
        'research/surveys/03-competition-cooperation-distribution/institutional-financing-comparison.md',
        'research/surveys/03-competition-cooperation-distribution/shared-service-institution-protocol.md',
        'research/surveys/03-competition-cooperation-distribution/open-business-finance-and-maintenance.md']]
    payload=[p for p in list(RAW.rglob('*'))+list(DER.rglob('*')) if p.is_file()]
    pending={(AUDIT/'verification.json').resolve(),(AUDIT/'artifact-receipt.json').resolve()}
    targets=[];broken=[]
    for p in changed+payload:
        if p.suffix!='.md':continue
        for m in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',p.read_text(encoding='utf-8')):
            dest=m.group(1).split('#')[0].strip('<>')
            if not dest or re.match(r'\w+://',dest):continue
            target=(p.parent/dest).resolve();targets.append(target)
            if not target.exists() and target not in pending:broken.append({'file':rel(p),'link':dest})
    assert not broken,broken
    ver=dict(date_local='2026-11-12',status='pass',new_raw_batch=37,new_literature_ids=0,
        acquired_alternative_pdfs=2,author_bibliographies=1,challenge_responses_not_papers=3,
        L190_new_pages=6,L190_cumulative_printed_scope='663–674',L190_stanford_print671_pdf_page=9,
        visual_review='single_assistant',new_body_ocr_word_for_word_verified=False,formal_errata_obtained=0,
        original_archive_entries_matching=len(original_rows),historical_baseline_artifacts_unchanged=len(frozen),
        prior_cited_page_payloads_unchanged=len(ocr_manifest['files']),formal_register_unchanged=True,
        original_pdfs_and_metadata_changed=False,cash_scenario_records=144,conditional_contract_checks=results['financing']['checks'],
        cash_conservation_and_nonnegative_actual_balances=True,failed_service_balances_not_fabricated=True,
        maintenance_transfer_preserves_platform_reserve=True,
        local_links_checked=len(targets),broken_links=broken,actual_users_or_budgets_available=False,
        actual_demand_estimated=False,full_general_equilibrium_reproduced=False,AutoDown_imported=False,
        scope='Source fidelity, conditional arithmetic and local artifact integrity; no empirical institutional ranking or unique necessity proof.')
    dump(AUDIT/'verification.json',ver)
    artifacts=payload+changed+[ROOT/'research/tools/financing-followup-acquire.py',Path(__file__),
        ROOT/'research/examples/financing-open-business-audit.py',
        ROOT/'research/surveys/08-price-income-and-reinvestment/financing-argument-model-results.json',
        ROOT/'research/surveys/08-price-income-and-reinvestment/institution-cash-scenarios.csv',
        ROOT/'wiki/index/source-followups.jsonl',cat,ann,AUDIT/'verification.json']
    dump(AUDIT/'artifact-receipt.json',dict(date_local='2026-11-12',self_excluded=True,artifacts=[
        dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(artifacts))]))
    assert all(p.exists() for p in targets)
    print(json.dumps({k:ver[k] for k in ['status','new_literature_ids','L190_new_pages','cash_scenario_records',
        'original_archive_entries_matching','historical_baseline_artifacts_unchanged','prior_cited_page_payloads_unchanged','local_links_checked']},ensure_ascii=False))

if __name__=='__main__':main()
