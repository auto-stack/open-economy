"""Check round48 artifacts and preserved baselines without rewriting old receipts."""
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
RAW = ROOT / 'wiki/raw/round-43'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True,
                          capture_output=True).stdout


assert len(list((ROOT / 'book').glob('part-*/*.md'))) == 12
assert len([p for p in (ROOT / 'book/argument-cards').glob('*.md') if p.name != 'README.md']) == 12
phase_one = json.loads((ROOT / 'research/audits/chapter-and-measurement-2026-11-13/phase-one.json').read_text())
assert digest(ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md') == phase_one['new_chapter_sha256']
review = (TOPIC / 'review-2026.md').read_text(encoding='utf-8')
snapshot = TOPIC / 'review-2026-v0.1.snapshot.md'
assert '版本0.1' in snapshot.read_text(encoding='utf-8')
assert '版本0.2' in review and '2011年更正' in review
for term in ['文献结论', '条件推论', '待验证假说', '价值主张', 'L216']:
    assert term in review, term

files = list(TOPIC.rglob('*.md')) + [ROOT / 'research/reviews/48-controller-costs-net-benefits-and-adaptation.md', RAW / 'README.md']
nav = ['README.md', 'research/README.md', 'wiki/raw/README.md', 'wiki/index/SOURCES.md',
       'research/survey-and-paper-program.md', 'research/surveys/04-influence-and-social-equivalence/README.md']
files += [ROOT / p for p in nav]
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
for number in range(38, 44):
    folder = ROOT / f'wiki/raw/round-{number:02}'
    records = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if isinstance(records, dict):
        records = records.get('files', records.get('entries'))
    for item in records:
        p = folder / item['path']
        assert p.stat().st_size == item['bytes'] and digest(p) == item['sha256'], str(p)
    manifests[f'round-{number}'] = len(records)
records = json.loads((RAW / 'manifest.json').read_text())
actual = {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name != 'manifest.json'}
assert actual == {r['path'] for r in records}

source_pages = {}
for folder in ['L213-sagawa-ueda-2009', 'L214-lan-et-al-2012', 'L215-govern-tenwolde-2014', 'L216-dekel-alon-2005']:
    base = RAW / folder
    meta = json.loads((base / 'metadata.json').read_text())
    p = base / meta['adopted_file']
    assert digest(p) == meta['sha256'] and p.stat().st_size == meta['bytes']
    if p.suffix == '.pdf':
        doc = fitz.open(p)
        assert len(doc) == meta['pdf_pages']
        text = '\n'.join(page.get_text() for page in doc)
        # arXiv paper cites journal DOI in its record rather than PDF text.
        if meta['id'] == 'L213':
            assert meta['doi'] in (base / 'arxiv-record.html').read_text(encoding='utf-8')
        else:
            assert meta['doi'].split('/', 1)[1] in text.replace('\n', '')
        source_pages[meta['id']] = len(doc)
    else:
        xml = ET.parse(p).getroot()
        assert xml.find("./front/article-meta/article-id[@pub-id-type='doi']").text == meta['doi']
        source_pages[meta['id']] = 'complete JATS, no PDF page map'
correction = json.loads((RAW / 'L213-sagawa-ueda-2009/erratum/metadata.json').read_text())
cp = RAW / 'L213-sagawa-ueda-2009/erratum' / correction['adopted_file']
assert digest(cp) == correction['sha256']
assert 'L124@P0' in cp.read_text(encoding='utf-8')
assert correction['original_pdf_downloaded'] is False
for item in json.loads((RAW / 'source-reuse.json').read_text()):
    assert digest(ROOT / item['original_path']) == item['sha256']

result = json.loads((TOPIC / 'costs-and-adaptation-2026-11-13/model-results.json').read_text())
assert result['cost_cases'][1]['net_log_growth'] > 0 > result['cost_cases'][2]['net_log_growth']
assert math.isclose(result['information_before_nats'], result['information_after_nats'], abs_tol=1e-12)
assert result['final_expected_log_size']['frozen'] < 0 < result['final_expected_log_size']['revised_after_delay']
assert result['revision_delay_sensitivity'][-1]['advantage_over_frozen'] == 0
assert all(len(rows) == 60 for rows in result['trajectories'].values())

theory = digest(ROOT / 'shared/theory-register.md')
assert theory == '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
tag = git('rev-parse', 'framework-v0.1^{commit}').decode().strip()
assert tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
assert (ROOT / 'docs/charter.md').read_bytes() == git('show', 'framework-v0.1:docs/charter.md')
assert (ROOT / 'wiki/archive/source-package-manifest.json').read_bytes() == git('show', 'framework-v0.1:wiki/archive/source-package-manifest.json')
package_sha = digest(ROOT / '.local-artifacts/open-economy-source-pack-2026-11-12.zip')
assert package_sha == 'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'
for p in [RAW / 'L216-dekel-alon-2005/original.pdf', RAW / 'L214-lan-et-al-2012/original.xml',
          RAW / 'L213-sagawa-ueda-2009/erratum-tool-text.txt', RAW / 'inspection/L215-p11.png']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 0
for p in [RAW / 'L216-dekel-alon-2005/metadata.json', RAW / 'manifest.json']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 1
whitespace = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True)
assert whitespace.returncode == 0, whitespace.stdout.decode(errors='replace')

receipt = dict(date_local='2026-11-13 Asia/Shanghai', status='passed', review_version='0.2',
    review_sha256=digest(TOPIC / 'review-2026.md'), previous_snapshot_sha256=digest(snapshot),
    drafts=12, argument_cards=12, remaining_units=16, checked_markdown_files=len(files), broken_links=broken,
    raw_manifests_verified=manifests, new_main_source_ids=['L213', 'L214', 'L215', 'L216'],
    new_full_pdfs=3, new_full_jats=1, correction_complete_tool_text=1, correction_original_pdf=0,
    source_pages=source_pages, old_reused_sources_hashes_verified=True,
    visual_checks=['L213 PDF2 Eqs2–5', 'L215 PDF3 Eq4', 'L215 PDF11 SI short-time limit', 'L216 PDF3 Eq4 and Figure4'],
    model_calculations_checked=True, model_scope='finite chosen parameters; no empirical calibration or author simulation replication',
    formal_register_sha256=theory, charter_equals_tag=True, tag_commit=tag,
    old_source_package_sha256=package_sha, git_ignore_boundaries_verified=True,
    git_diff_check='passed', no_commit_tag_or_push_performed=True,
    limits=['purposeful synthesis, not exhaustive literature coverage', 'strategy learning remains to be explained',
            'whole-controller empirical net-benefit account not yet established', 'unified Ordo measure not established'])
(HERE / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert (HERE / 'validation.json').exists()
print(json.dumps(receipt, ensure_ascii=False))
