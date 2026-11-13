"""Verify this chapter/research handoff without rewriting historical receipts."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True,
                          capture_output=True).stdout


drafts = sorted((ROOT / 'book').glob('part-*/*.md'))
cards = sorted((ROOT / 'book/argument-cards').glob('*.md'))
cards = [p for p in cards if p.name != 'README.md']
assert len(drafts) == len(cards) == 12
phase_one = json.loads((HERE / 'phase-one.json').read_text(encoding='utf-8'))
chapter = ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md'
assert digest(chapter) == phase_one['new_chapter_sha256']
for status in ['文献结论', '条件推论', '待验证假说', '价值']:
    assert status in chapter.read_text(encoding='utf-8'), status

topic = ROOT / 'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo'
new_md = list(topic.glob('*.md')) + [chapter,
    ROOT / 'book/argument-cards/part-01-03-inputs-maintenance-and-continuity.md',
    ROOT / 'research/reviews/47-maintenance-draft-and-information-research.md',
    ROOT / 'wiki/raw/round-42/README.md']
navigation = ['README.md', 'research/README.md', 'book/README.md',
    'book/outline.md', 'book/framework-scope.md', 'book/argument-map.md',
    'book/chapter-interfaces.md', 'research/survey-and-paper-program.md',
    'research/surveys/04-influence-and-social-equivalence/README.md',
    'wiki/raw/README.md', 'wiki/index/SOURCES.md']
broken = []
for path in new_md + [ROOT / n for n in navigation]:
    for target in re.findall(r'\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][\w+.-]*:', target):
            continue
        dest = (path.parent / target).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([path.relative_to(ROOT).as_posix(), target])
assert not broken, broken

manifests = {}
for number in range(38, 43):
    folder = ROOT / f'wiki/raw/round-{number:02}'
    records = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if isinstance(records, dict):
        records = records.get('files', records.get('entries'))
    assert isinstance(records, list)
    for item in records:
        p = folder / item['path']
        assert p.stat().st_size == item['bytes'], str(p)
        assert digest(p) == item['sha256'], str(p)
    manifests[f'round-{number}'] = len(records)

reuse = json.loads((ROOT / 'wiki/raw/round-42/source-reuse.json').read_text(encoding='utf-8'))[0]
assert digest(ROOT / reuse['original_path']) == reuse['sha256']
theory = digest(ROOT / 'shared/theory-register.md')
assert theory == '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5'
tag = git('rev-parse', 'framework-v0.1^{commit}').decode().strip()
assert tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d'
assert (ROOT / 'docs/charter.md').read_bytes() == git('show', 'framework-v0.1:docs/charter.md')
assert (ROOT / 'wiki/archive/source-package-manifest.json').read_bytes() == git('show', 'framework-v0.1:wiki/archive/source-package-manifest.json')
package = ROOT / '.local-artifacts/open-economy-source-pack-2026-11-12.zip'
assert package.stat().st_size == 288402894
package_sha = digest(package)
assert package_sha == 'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'

raw = ROOT / 'wiki/raw/round-42'
for p in [raw / 'L211-sagawa-ueda-2010/original.pdf',
          raw / 'L212-sowinski-et-al-2023/original.txt',
          raw / 'inspection/L20-p9.png']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 0
for p in [raw / 'L211-sagawa-ueda-2010/metadata.json', raw / 'manifest.json']:
    assert subprocess.run(['git', 'check-ignore', '-q', str(p)], cwd=ROOT).returncode == 1

receipt = dict(date_local='2026-11-13 Asia/Shanghai', status='passed',
    drafts=12, argument_cards=12, remaining_candidate_units=16,
    chapter_written_before_new_research=True, phase_one_preserved=True,
    checked_markdown_files=len(new_md) + len(navigation), broken_links=broken,
    raw_manifests_verified=manifests, new_source_ids=['L211', 'L212'],
    new_full_pdfs=2, reused_source_ids=['L20'],
    visual_checks=['L211 PDF1 equations3–4', 'L20 PDF9 equations5.11–5.12 and caveats',
                   'L212 PDF5 equations4–5 and Figures2–3'],
    formal_register_sha256=theory, formal_register_unchanged=True,
    charter_equals_tag=True, tag_commit=tag,
    old_package_manifest_equals_tag=True, old_package_sha256=package_sha,
    git_ignore_boundaries_verified=True, no_commit_tag_or_push_performed=True,
    limits=['purposeful synthesis, not exhaustive systematic review',
            'original simulations not rerun', 'unified Ordo measure not established'])
(HERE / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert (HERE / 'validation.json').exists()
print(json.dumps(receipt, ensure_ascii=False))
