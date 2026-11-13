"""Verify round50 sources, examples and preserved book/research baselines."""
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
RAW = ROOT / 'wiki/raw/round-45'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


prior = json.loads((ROOT / 'research/audits/detection-and-learning-2026-11-13/validation.json').read_text())
assert digest(TOPIC / 'review-2026-v0.3.snapshot.md') == prior['review_sha256']
provenance = json.loads((TOPIC / 'version-provenance.json').read_text())
assert provenance['current_version'] == '0.4'
assert provenance['current_review_sha256'] == digest(TOPIC / 'review-2026.md')
for item in provenance['snapshots']:
    assert digest(TOPIC / item['path']) == item['sha256']
review = (TOPIC / 'review-2026.md').read_text(encoding='utf-8')
for term in ['版本0.4', '文献结论', '条件推论', '待验证假说C', '价值主张', 'L221', 'L224']:
    assert term in review, term
assert len(list((ROOT / 'book').glob('part-*/*.md'))) == 12
assert len([p for p in (ROOT / 'book/argument-cards').glob('*.md') if p.name != 'README.md']) == 12
phase_one = json.loads((ROOT / 'research/audits/chapter-and-measurement-2026-11-13/phase-one.json').read_text())
assert digest(ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md') == phase_one['new_chapter_sha256']

files = list(TOPIC.rglob('*.md')) + [RAW / 'README.md', ROOT / 'research/reviews/50-new-explanations-and-safe-tests.md']
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
for number in range(38, 46):
    folder = ROOT / f'wiki/raw/round-{number:02}'
    records = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if isinstance(records, dict):
        records = records.get('files', records.get('entries'))
    for item in records:
        p = folder / item['path']
        assert p.stat().st_size == item['bytes'] and digest(p) == item['sha256'], str(p)
    manifests[f'round-{number}'] = len(records)
records = json.loads((RAW / 'manifest.json').read_text())
assert {r['path'] for r in records} == {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name != 'manifest.json'}

pdf_pages = {}
for folder in ['L221-gershman-blei-niv-2010', 'L222-bongard-lipson-2007', 'L223-schulz-bonawitz-2007', 'L224-sui-et-al-2015']:
    meta = json.loads((RAW / folder / 'metadata.json').read_text())
    p = RAW / folder / meta['adopted_file']
    assert digest(p) == meta['sha256'] and p.stat().st_size == meta['bytes']
    doc = fitz.open(p)
    assert len(doc) == meta['pdf_pages']
    pdf_pages[meta['id']] = len(doc)
    text = ''.join(page.get_text() for page in doc)
    if meta['id'] in ['L221', 'L222']:
        assert meta['doi'].split('/', 1)[1] in text
    if meta['id'] == 'L224':
        extra = meta['additional_pdf']
        q = RAW / folder / extra['file']
        assert digest(q) == extra['sha256'] and q.stat().st_size == extra['bytes']
        assert len(fitz.open(q)) == extra['pdf_pages'] == 12
        pdf_pages['L224-extended-same-family'] = 12
pubmed = ET.parse(RAW / 'discovery/pubmed-records.xml').getroot()
doi_year = {}
for article in pubmed.findall('PubmedArticle'):
    for x in article.findall('./PubmedData/ArticleIdList/ArticleId'):
        if x.get('IdType') == 'doi':
            doi_year[x.text] = article.findtext('./MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
assert doi_year['10.1037/0012-1649.43.4.1045'] == '2007'
assert doi_year['10.1073/pnas.0609476104'] == '2007'
for item in json.loads((RAW / 'source-reuse.json').read_text()):
    assert digest(ROOT / item['original_path']) == item['sha256']
attempts = json.loads((RAW / 'download-log.json').read_text())
assert len(attempts) == 7 and all(a.get('status') == 200 and 'error' not in a for a in attempts)
assert json.loads((RAW / 'response-classification.json').read_text())['new_main_studies'] == 4

result = json.loads((TOPIC / 'structure-and-safe-tests-2026-11-13/model-results.json').read_text())
model = result['structure']
assert len(model['new_observations']) == model['incremental_query_budget'] == 2
assert model['budget_remaining'] == 0
assert all(0 <= x <= 1 for x, y in model['new_observations'])
assert model['generated_features'] == ['1', 'x', 'x*x']
assert model['diagnostic_error'] > model['threshold']
assert model['refitted_affine_max_training_error'] > model['threshold']
assert math.isclose(model['validation_prediction'], model['validation_observed'], abs_tol=1e-10)
assert model['alternate_matches_all_observations']
assert model['alternate_at_unobserved'] != model['expanded_at_unobserved']
safety = result['safety']
assert safety['certified_set'] == [0, 1] and safety['new_queries'] == [1]
assert safety['best_certified_value'] < safety['true_global_max']
assert safety['wrongly_certified_unsafe_points'] == [3]
assert safety['certified_with_additional_externally_verified_seed5'] == [0, 1, 4, 5]
assert result['mean_vs_outcome']['mean'] >= result['mean_vs_outcome']['threshold']
assert min(result['mean_vs_outcome']['outcomes']) < result['mean_vs_outcome']['threshold']

theory = digest(ROOT / 'shared/theory-register.md')
assert theory == '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
tag = git('rev-parse', 'framework-v0.1^{commit}').decode().strip()
assert tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
assert (ROOT / 'docs/charter.md').read_bytes() == git('show', 'framework-v0.1:docs/charter.md')
assert (ROOT / 'wiki/archive/source-package-manifest.json').read_bytes() == git('show', 'framework-v0.1:wiki/archive/source-package-manifest.json')
package_sha = digest(ROOT / '.local-artifacts/open-economy-source-pack-2026-11-12.zip')
assert package_sha == 'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'
for p in [RAW / 'L224-sui-et-al-2015/extended.pdf', RAW / 'L223-schulz-bonawitz-2007/original.txt', RAW / 'inspection/L224-p5.png']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 0
for p in [RAW / 'L224-sui-et-al-2015/metadata.json', RAW / 'manifest.json']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 1
assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0

receipt = dict(date_local='2026-11-13 Asia/Shanghai', status='passed', review_version='0.4',
    review_sha256=digest(TOPIC / 'review-2026.md'), previous_snapshot_matches_prior_receipt=True,
    drafts=12, argument_cards=12, remaining_units=16, checked_markdown_files=len(files), broken_links=broken,
    raw_manifests_verified=manifests, source_ids=['L221', 'L222', 'L223', 'L224'],
    main_pdf_files=4, additional_same_family_pdf_files=1, pdf_pages=pdf_pages,
    publication_record_crosschecks=True, source_and_reuse_hashes_verified=True,
    visual_checks=['L221 PDF3 prior and footnotes', 'L222 PDF4 specified inputs and Table3',
                   'L223 PDF8 causal-learning limitation', 'L224 PDF5 main theorem', 'L224 extendedPDF12 safety lemma'],
    finite_examples_verified=True, formal_register_sha256=theory, charter_equals_tag=True,
    tag_commit=tag, old_source_package_sha256=package_sha, ignore_boundaries_verified=True,
    git_diff_check='passed', no_commit_tag_or_push_performed=True,
    limits=['purposeful synthesis, not exhaustive literature coverage', 'grammar and observables still supplied',
            'informative evidence is distinct from demonstrated correct causal learning',
            'conditional static safety is distinct from per-outcome protection and dynamic recovery',
            'no independent replication of papers or full reproof of SafeOpt'])
(HERE / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert (HERE / 'validation.json').exists()
print(json.dumps(receipt, ensure_ascii=False))
