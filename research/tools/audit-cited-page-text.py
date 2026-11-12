"""Check cited-page transcription artifacts; keep historic baseline outputs intact."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'wiki/derived/cited-page-text-2026-11-12'
AUDIT=ROOT/'research/audits/cited-page-ocr-2026-11-12'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    AUDIT.mkdir(parents=True,exist_ok=True)
    provenance=json.loads((OUT/'provenance.json').read_text(encoding='utf-8'))
    # Formula statements are keyed to actual source locations, not project examples.
    formulas=[]
    def add(work,page,printed,label,tex,needle,note=''):
        file=f'{work}/pdf-{page:02d}-print-{printed}.verified.md'
        text=(OUT/file).read_text(encoding='utf-8')
        if needle not in text:
            raise AssertionError((work,page,label,needle))
        formulas.append(dict(id=f'{work}-F{1+sum(f["work_id"]==work for f in formulas):02d}',
            work_id=work,pdf_page=page,printed_page=printed,source_label=label,latex=tex,
            verified_text=file,visible_in_scan=True,visual_review='single_assistant_against_saved_scan',
            note=note))
    add('L185',4,157,'unnumbered: affine scale',r'au+b,\quad a>0','au + b, provided a > 0')
    add('L185',4,157,'property (a)',r'u(A)>u(B)','u(A) > u(B)')
    add('L185',4,157,'property (b)',r'0\le p\le1;\quad u[pA+(1-p)B]=p u(A)+(1-p)u(B)',r'u[pA+(1-p)B]=p\,u(A)+(1-p)\,u(B)')
    add('L185',4,157,'unnumbered: two displayed definitions',r'p[A,B]+(1-p)[C,D];\quad[pA+(1-p)C,pB+(1-p)D]',r'p[A,B]+(1-p)[C,D]', 'Original prints two expressions with “will be defined as”, not one numbered equality.')
    add('L185',6,159,'assumption 6',r'u_1(\beta)>u_1(\alpha),\ u_2(\beta)>u_2(\alpha)\Rightarrow\alpha\ne c(S)',r'u_2(\beta)>u_2(\alpha)', 'Implication sign is a compact transcription of the sentence; both original inequalities are strict.')
    add('L185',6,159,'assumption 7',r'S\subseteq T,\ c(T)\in S\Rightarrow c(T)=c(S)','If the set T contains the set S and c(T) is in S, then c(T) = c(S).','Set notation and implication abbreviate the printed sentence.')
    add('L185',6,159,'symmetry and assumption 8',r'(a,b)\leftrightarrow(b,a);\quad c(S)=(a,a),\ u_1=u_2',r'the line $u_1=u_2$', 'Arrow abbreviates the printed symmetry definition.')
    add('L185',6,159,'unnumbered: product criterion',r'u_1u_2',r'first quadrant where $u_1u_2$ is maximized', 'Text says maximum in first quadrant; no printed argmax expression is invented here.')
    add('L185',6,159,'unnumbered: rescaling and contradiction',r'(1,1);\quad u_1+u_2>2',r'with $u_1+u_2>2$')
    add('L185',6,159,'unnumbered: square region',r'u_1+u_2\le2;\quad u_1+u_2=2',r'the region $u_1+u_2\le 2$')
    add('L189',3,394,'Figure 1 and text',r'\hat r^{*}',r'\hat r^{*}', 'Both hat and star checked; figure is schematic, not numeric evidence.')
    add('L189',4,395,'unnumbered: risk parameter ordering',r'\theta_1>\theta_2;\quad y\ge0',r'\theta_1>\theta_2', 'Printed body and footnote 5 project-number directions conflict; preserved without emendation.')
    add('L189',4,395,'equation (1)',r'\int_0^\infty Rf(R,\theta_1)dR=\int_0^\infty Rf(R,\theta_2)dR',r'\tag{1} \int_0^\infty Rf(R,\theta_1)')
    add('L189',4,395,'equation (2)',r'\int_0^y F(R,\theta_1)dR\ge\int_0^y F(R,\theta_2)dR',r'dR\ge\int_0^y F(R,\theta_2)', 'The scan prints >=, not <=; uppercase F differs from density f in equation (1).')
    add('L189',4,395,'equation (3)',r'C+R\le B(1+\hat r)',r'C+R\le B(1+\hat r)', 'B denotes amount borrowed; <= boundary is retained.')
    add('L189',4,395,'footnote 6: alternative default definition',r'R<B(1+\hat r)',r'R<B(1+\hat r)', 'No C, strict <; not identical to equation (3).')
    add('L190',6,667,'unnumbered: aggregate firm capital',r'K_f=\int A\,dG(A)',r'K_f=\int A\,dG(A)', 'No integration bounds printed.')
    add('L190',6,667,'unnumbered: investment and financing gap',r'I>0;\quad A<I;\quad I-A','If A < I, a firm needs at least I — A')
    add('L190',6,667,'unnumbered: success probability difference',r'\Delta p=p_H-p_L>0',r'\Delta p=p_H-p_L>0')
    add('L190',7,668,'Figure I: table entries',r'(0,p_H),\ (b,p_L),\ (B,p_L)',r'| Probability of success | $p_H$ | $p_L$ | $p_L$ |','Pairs summarize original table rows; Figure I is distinct from equation (1).')
    add('L190',7,668,'equation (1)',r'p_HR-\gamma I>0>p_LR-\gamma I+B',r'p_HR-\gamma I>0>p_LR-\gamma I+B', 'gamma denotes return on investor capital; B is a private benefit, unlike L189.')
    add('L190',7,668,'unnumbered: private benefits',r'B>b>0','B > b > 0')
    dump(OUT/'formula-register.json',dict(date='2026-11-12',entries=formulas,
         purpose='source transcription and page lookup, not a scientific model validation'))
    expected={
        'L185':([2,4,5,6],[155,157,158,159],'2819cd077194ff30af0852b78fdf0b085f08a972cc100b5152af20f8470ccfa5'),
        'L189':([2,3,4],[393,394,395],'6cc8accd21859d3dfb5ec4091bf0f80f2c12e603b840239b34f747e9a6c142bf'),
        'L190':([2,3,4,5,6,7],[663,664,665,666,667,668],'6db56bda95911484f48e631a82bc1e4443c6e7c2ec144454d76755793570686b')}
    phrases={('L185',2):'highly rational',('L185',4):'probability combination',
             ('L185',5):'compact and convex',('L185',6):r'u_1u_2',
             ('L189',2):'adverse selection effect',('L189',3):'bank-optimal',('L189',4):r'\tag{2}',
             ('L190',2):'capital constrained',('L190',3):'flight-to-quality',
             ('L190',4):'credible monitors',('L190',5):'Another implication',
             ('L190',6):r'\Delta p',('L190',7):r'\gamma I'}
    catalogue=[]; page_checks=[]
    for source in provenance['sources']:
        work=source['work_id']; pdfs,prints,expected_sha=expected[work]
        assert [p['pdf_page'] for p in source['page_scope']]==pdfs
        assert [p['printed_page'] for p in source['page_scope']]==prints
        assert sha(ROOT/source['source'])==source['source_sha256']==expected_sha
        for p in source['page_scope']:
            text=(OUT/p['verified_text']).read_text(encoding='utf-8')
            raw=json.loads((OUT/p['raw_ocr_json']).read_text(encoding='utf-8-sig'))
            assert (OUT/p['raw_text']).read_text(encoding='utf-8').rstrip('\n')==raw['text']
            assert phrases[(work,p['pdf_page'])].lower() in text.lower()
            assert text.count('$$')%2==0
            assert raw['width']<=raw['max_image_dimension'] and raw['height']<=raw['max_image_dimension']
            page_checks.append(dict(work_id=work,pdf_page=p['pdf_page'],printed_page=p['printed_page'],
                printed_page_basis='visible numeral' if p['printed_page_visible'] else 'cover pp663–691 plus following visible664',
                searchable_phrase=phrases[(work,p['pdf_page'])],phrase_found=True,
                raw_engine_text_preserved=True,visual_review_record=p['visual_review']))
        catalogue.append(dict(work_id=work,source=source['source'],source_sha256=source['source_sha256'],
            derived_on='2026-11-12',text_status='partial_cited_pages_ocr_visually_corrected',
            pdf_pages=pdfs,printed_pages=prints,whole_work_ocr=False,
            text=(OUT/source['verified_text']).relative_to(ROOT).as_posix(),
            provenance=(OUT/'provenance.json').relative_to(ROOT).as_posix(),
            formula_checks=(OUT/'formula-and-page-checks.md').relative_to(ROOT).as_posix(),
            original_pdf_text_layer_changed=False,independent_double_entry=False))
    (ROOT/'wiki/index/derived-text-catalog.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in catalogue),encoding='utf-8')
    # This is a new receipt, not a rerun or overwrite of baseline v0.2.
    receipt=json.loads((ROOT/'research/audits/internal-baseline-2026-11-12/artifact-receipt.json').read_text(encoding='utf-8'))
    frozen=[r for r in receipt['artifacts'] if r['path'].startswith('research/baselines/')]
    assert frozen and all(sha(ROOT/r['path'])==r['sha256'] for r in frozen)
    raw_rows=list(csv.DictReader((ROOT/'research/baselines/internal-knowledge-2026-11-12/archive-integrity.csv').open(encoding='utf-8-sig',newline='')))
    assert len(raw_rows)==1117
    for r in raw_rows:
        path=ROOT/Path(r['manifest']).parent/r['path']
        assert sha(path)==r['expected_sha256'],str(path)
    assert sha(ROOT/'shared/theory-register.md')=='1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
    # Hash all derived payloads. Manifest intentionally excludes itself.
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest-sha256.json']
    dump(OUT/'manifest-sha256.json',dict(date='2026-11-12',self_excluded=True,
        files=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]))
    changed_docs=[ROOT/p for p in ['README.md','research/README.md','wiki/index/README.md','wiki/index/SOURCES.md',
        'wiki/index/source-annotations.json','wiki/index/derived-text-catalog.jsonl',
        'research/reviews/38-cited-page-ocr-and-formula-checks.md',
        'research/surveys/08-price-income-and-reinvestment/reading-notes.md',
        'research/surveys/08-price-income-and-reinvestment/credit-reading-notes.md']]
    broken=[]; link_count=0; local_targets=[]
    pending_outputs={(AUDIT/'verification.json').resolve(),(AUDIT/'artifact-receipt.json').resolve()}
    for path in files+changed_docs:
        if path.suffix!='.md': continue
        for match in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)',path.read_text(encoding='utf-8')):
            dest=match.group(1).split('#')[0].strip('<>')
            if not dest or re.match(r'\w+://',dest): continue
            link_count+=1
            target=(path.parent/dest).resolve()
            local_targets.append(target)
            if not target.exists() and target not in pending_outputs: broken.append(dict(file=str(path),link=dest))
    assert not broken,broken
    verification=dict(date_local='2026-11-12',status='pass',page_count=len(page_checks),
        source_count=len(catalogue),formula_entries=len(formulas),page_checks=page_checks,
        original_pdf_hashes_match=True,previous_manifest_entries_matching=len(raw_rows),
        historical_baseline_artifacts_matching=len(frozen),historical_baseline_rerun=False,
        formal_register_unchanged=True,raw_sources_modified=False,new_network_sources=0,new_raw_batch=False,
        local_links_checked=link_count,broken_links=broken,
        independent_human_review=False,full_work_ocr=False,searchable_pdf_created=False,
        AutoDown_import_executed=False,
        source_issue='L189 printed395 body/footnote5 project-number direction discrepancy retained, not resolved.',
        checks_meaning='File integrity, scope, traceability and fixed-string search; visual fidelity is the documented single-assistant review, not proved by these automated checks.')
    dump(AUDIT/'verification.json',verification)
    artifacts=files+[OUT/'manifest-sha256.json']+changed_docs+[
        ROOT/'research/tools/ocr-cited-pages.ps1',ROOT/'research/tools/prepare-cited-page-ocr.py',
        ROOT/'research/tools/verify-cited-page-text.py',Path(__file__),AUDIT/'verification.json']
    dump(AUDIT/'artifact-receipt.json',dict(date_local='2026-11-12',self_excluded=True,artifacts=[
        dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(artifacts))]))
    assert all(p.exists() for p in local_targets), 'A final local link did not resolve after receipt creation'
    print(json.dumps({k:verification[k] for k in ['status','page_count','formula_entries',
        'previous_manifest_entries_matching','historical_baseline_artifacts_matching','local_links_checked']},ensure_ascii=False))

if __name__=='__main__': main()
