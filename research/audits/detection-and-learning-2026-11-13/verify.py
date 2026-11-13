"""Verify round49 evidence, finite calculations and preserved historical baselines."""
from pathlib import Path
from urllib.parse import unquote
import hashlib
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET
import fitz

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOPIC = ROOT / 'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo'
RAW = ROOT / 'wiki/raw/round-44'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


previous = json.loads((ROOT / 'research/audits/costs-and-adaptation-2026-11-13/validation.json').read_text())
assert digest(TOPIC / 'review-2026-v0.2.snapshot.md') == previous['review_sha256']
assert digest(TOPIC / 'review-2026-v0.1.snapshot.md') == previous['previous_snapshot_sha256']
provenance = json.loads((TOPIC / 'version-provenance.json').read_text())
assert provenance['current_version'] == '0.3'
assert digest(TOPIC / 'review-2026.md') == provenance['current_review_sha256']
for record in provenance['snapshots']:
    assert digest(TOPIC / record['path']) == record['sha256']
review = (TOPIC / 'review-2026.md').read_text(encoding='utf-8')
for term in ['版本0.3', '文献结论', '条件推论', '待验证假说C', '价值主张', 'L217', 'L220']:
    assert term in review, term
assert len(list((ROOT / 'book').glob('part-*/*.md'))) == 12
assert len([p for p in (ROOT / 'book/argument-cards').glob('*.md') if p.name != 'README.md']) == 12
phase_one = json.loads((ROOT / 'research/audits/chapter-and-measurement-2026-11-13/phase-one.json').read_text())
assert digest(ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md') == phase_one['new_chapter_sha256']

files = list(TOPIC.rglob('*.md')) + [RAW / 'README.md', ROOT / 'research/reviews/49-failure-detection-and-affordable-learning.md']
files += [ROOT / p for p in ['README.md', 'research/README.md', 'wiki/raw/README.md', 'wiki/index/SOURCES.md',
          'research/survey-and-paper-program.md', 'research/surveys/04-influence-and-social-equivalence/README.md']]
broken = []
for p in files:
    for target in re.findall(r'\]\(([^\s)]+)\)', p.read_text(encoding='utf-8')):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][\w+.-]*:', target):
            continue
        dest = (p.parent / target).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([p.relative_to(ROOT).as_posix(), target])
assert not broken, broken

manifests = {}
for number in range(38, 45):
    folder = ROOT / f'wiki/raw/round-{number:02}'
    records = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if isinstance(records, dict):
        records = records.get('files', records.get('entries'))
    for record in records:
        p = folder / record['path']
        assert p.stat().st_size == record['bytes'] and digest(p) == record['sha256'], str(p)
    manifests[f'round-{number}'] = len(records)
records = json.loads((RAW / 'manifest.json').read_text())
assert {r['path'] for r in records} == {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name != 'manifest.json'}

pubmed = ET.parse(RAW / 'discovery/pubmed-records.xml').getroot()
years = {a.findtext('./MedlineCitation/PMID'): int(a.findtext('./MedlineCitation/Article/Journal/JournalIssue/PubDate/Year'))
         for a in pubmed.findall('PubmedArticle')}
assert years == {'20844132': 2010, '25347535': 2014}
bio_fields = {}
pdf_pages = {}
for folder in ['L217-adams-mackay-2007', 'L218-nassar-et-al-2010', 'L219-wilson-et-al-2014', 'L220-griffiths-et-al-2015']:
    meta = json.loads((RAW / folder / 'metadata.json').read_text())
    p = RAW / folder / meta['adopted_file']
    assert digest(p) == meta['sha256'] and p.stat().st_size == meta['bytes']
    if p.suffix == '.pdf':
        doc = fitz.open(p)
        assert len(doc) == meta['pdf_pages']
        pdf_pages[meta['id']] = len(doc)
        if meta['doi']:
            assert meta['doi'].split('/', 1)[1] in ''.join(pg.get_text() for pg in doc)
    else:
        xml = ET.parse(p).getroot()
        assert xml.tag == 'collection'
        fields = {x.get('key'): x.text for x in xml.find('.//passage').findall('infon')}
        assert fields['article-id_doi'] == meta['doi']
        assert 'PMC' + fields['article-id_pmc'] == meta['pmcid']
        assert years[fields['article-id_pmid']] == meta['publication_year']
        assert fields['year'] == meta['raw_bioc_year_field']
        bio_fields[meta['id']] = dict(raw_year=fields['year'], publication_year=meta['publication_year'], passages=len(xml.findall('.//passage')))
for item in json.loads((RAW / 'source-reuse.json').read_text()):
    assert digest(ROOT / item['original_path']) == item['sha256']

result = json.loads((TOPIC / 'detection-and-learning-2026-11-13/model-results.json').read_text())
assert result['finite_horizon_cases'][0]['first_action'] == 'act'
assert result['finite_horizon_cases'][6]['first_action'] == 'probe'
assert result['finite_horizon_cases'][-1]['first_action'] == 'act'
changed, unchanged, costly, slower, no_hazard = result['online_cases']
assert changed['mean_net_points'] > 60 > costly['mean_net_points']
assert unchanged['mean_net_points'] < unchanged['fixed_old_rule_points']
assert slower['mean_delay_among_detected'] > changed['mean_delay_among_detected']
assert slower['mean_net_points'] > changed['mean_net_points']
assert no_hazard['detection_path_fraction'] < 1
assert math.isclose(changed['mean_net_points'] - costly['mean_net_points'], 30 * 0.95, abs_tol=1e-10)
assert math.isclose(result['boCPD_constant_hazard_reset_posterior'], 0.02, abs_tol=1e-12)
assert len(result['example_trace']) == 120
assert all(row['observed_match'] is None for row in result['example_trace'] if not row['diagnostic'])

theory = digest(ROOT / 'shared/theory-register.md')
assert theory == '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
tag = git('rev-parse', 'framework-v0.1^{commit}').decode().strip()
assert tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
assert (ROOT / 'docs/charter.md').read_bytes() == git('show', 'framework-v0.1:docs/charter.md')
assert (ROOT / 'wiki/archive/source-package-manifest.json').read_bytes() == git('show', 'framework-v0.1:wiki/archive/source-package-manifest.json')
package_sha = digest(ROOT / '.local-artifacts/open-economy-source-pack-2026-11-12.zip')
assert package_sha == 'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'
for p in [RAW / 'L218-nassar-et-al-2010/bioc.xml', RAW / 'L220-griffiths-et-al-2015/original.pdf', RAW / 'inspection/L217-p3.png']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 0
for p in [RAW / 'L218-nassar-et-al-2010/metadata.json', RAW / 'manifest.json']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 1
assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0

receipt = dict(date_local='2026-11-13 Asia/Shanghai', status='passed', review_version='0.3',
    review_sha256=digest(TOPIC / 'review-2026.md'), previous_review_snapshot_matches_prior_receipt=True,
    drafts=12, argument_cards=12, remaining_units=16, checked_markdown_files=len(files), broken_links=broken,
    raw_manifests_verified=manifests, source_ids=['L217', 'L218', 'L219', 'L220'],
    new_pdfs=2, BioC_fulltext_exports=2, original_JATS=0, pdf_pages=pdf_pages, BioC_fields=bio_fields,
    publication_dates_crosschecked=True, visual_checks=['L217 PDF3 Algorithm1', 'L220 PDF8 resource-rational comparison'],
    model_calculations_checked=True, source_and_reuse_hashes_verified=True,
    formal_register_sha256=theory, charter_equals_tag=True, tag_commit=tag, old_source_package_sha256=package_sha,
    ignore_boundaries_verified=True, git_diff_check='passed', no_commit_tag_or_push_performed=True,
    limits=['purposeful synthesis, not exhaustive coverage', 'BioC math conversion gaps remain',
            'inference in a given model library, not invention of arbitrary rules',
            'finite chosen-parameter models, no empirical calibration or author-study replication',
            'unknown model families, causal diagnosis and safe exploration still require research'])
(HERE / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert (HERE / 'validation.json').exists()
print(json.dumps(receipt, ensure_ascii=False))
