"""Check this book-writing revision; do not rewrite older revision-bound receipts."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def text(path):
    return path.read_text(encoding='utf-8-sig')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


before = json.loads(text(HERE / 'before-state.json'))
chapter = ROOT / 'book/part-01/02-entropy-information-and-ordo.md'
card = ROOT / 'book/argument-cards/part-01-02-entropy-information-and-ordo.md'
ct = text(chapter)
drafts = sorted(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))
cards = sorted(ROOT.glob('book/argument-cards/part-??-*.md'))
draft_keys = {f'{p.parent.name}-{p.name[:2]}' for p in drafts}
card_keys = {p.name[:10] for p in cards}
check('13 manuscript units and matching argument cards; 15 of 28 not drafted',
      len(drafts) == len(cards) == 13 and draft_keys == card_keys,
      {'drafts': len(drafts), 'cards': len(cards), 'remaining': 28 - len(drafts)})
check('Claim status and limits explicit in chapter', all(x in ct for x in [
    '文献结论', '条件推论', '待验证假说', '价值问题', '工作机制',
    '不是由热力学定律直接推出', '不把这些性质压缩成已经成立的统一标量',
    '不等于每次带噪声的观测都达到阈值', '另一个函数仍可能穿过全部已知点',
]))

modified_md = [
    'README.md', 'book/README.md', 'book/outline.md', 'book/chapter-interfaces.md',
    'book/framework-scope.md', 'book/argument-map.md',
    'book/part-01/02-entropy-information-and-ordo.md',
    'book/part-01/03-inputs-maintenance-and-continuity.md',
    'book/part-02/01-human-as-organization.md',
    'book/part-02/04-goal-conflict-and-revision.md',
    'book/part-03/02-revisable-shared-commitments.md',
    'book/argument-cards/part-01-02-entropy-information-and-ordo.md',
    'book/argument-cards/part-01-03-inputs-maintenance-and-continuity.md',
    'book/argument-cards/part-02-01-human-as-organization.md',
    'book/argument-cards/part-02-04-goal-conflict-and-revision.md',
    'book/argument-cards/part-03-02-revisable-shared-commitments.md',
    'research/README.md', 'research/survey-and-paper-program.md',
    'research/reviews/51-information-ordo-chapter-and-handoffs.md',
    'research/surveys/04-influence-and-social-equivalence/README.md',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/README.md',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/chapter-evidence.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-46/README.md',
]
broken = []
link_count = 0
for name in modified_md:
    p = ROOT / name
    body = text(p)
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', body):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        link_count += 1
        destination = (p.parent / target).resolve()
        # This check itself writes validation.json; other targets must already exist.
        if not destination.exists() and destination != HERE / 'validation.json':
            broken.append({'file': name, 'target': target})
check('Local links in changed/new navigation and manuscripts resolve', not broken,
      {'links': link_count, 'broken': broken})
foot_defs = re.findall(r'^\[\^([^\]]+)\]:', ct, re.M)
foot_refs = re.findall(r'\[\^([^\]]+)\](?!:)', ct)
check('Chapter footnotes defined, used and unique',
      set(foot_refs) == set(foot_defs) and len(foot_defs) == len(set(foot_defs)),
      {'definitions': len(foot_defs), 'references': len(foot_refs)})

nav_errors = []
for name in ['book/README.md', 'book/outline.md', 'book/chapter-interfaces.md',
             'book/framework-scope.md', 'book/argument-map.md']:
    body = text(ROOT / name)
    if re.search(r'当前.{0,4}12章|共十二章|现有十二张|其余16|16单元待起草', body):
        nav_errors.append(name)
check('Current book navigation uses 13/15, leaving historical baseline intact',
      not nav_errors, nav_errors)

reuse_dir = ROOT / 'wiki/raw/round-46'
reuse = json.loads(text(reuse_dir / 'source-reuse.json'))
expected_ids = {'L15', 'L16', 'L17', 'L20', 'L21', 'L211', 'L212', 'L213',
                'L215', 'L217', 'L218', 'L219', 'L220', 'L221', 'L222', 'L223', 'L224'}
artifact_count = 0
reuse_errors = []
for entry in reuse['sources']:
    for field in ['source_metadata', 'reading_notes']:
        if not (reuse_dir / entry[field]).exists():
            reuse_errors.append([entry['source_id'], field])
    for item in entry['artifacts']:
        p = (reuse_dir / item['path']).resolve()
        artifact_count += 1
        if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
            reuse_errors.append([entry['source_id'], item['path'], 'integrity'])
        if item['new_download_this_round'] or item['new_primary_reading_this_round']:
            reuse_errors.append([entry['source_id'], 'reuse incorrectly counted as new'])
check('17 study families / 19 prior artifacts, metadata and reading notes resolve',
      not reuse_errors and {e['source_id'] for e in reuse['sources']} == expected_ids
      and artifact_count == 19 and reuse['new_downloads'] == 0,
      {'families': len(reuse['sources']), 'artifacts': artifact_count, 'errors': reuse_errors})
check('New archive descriptors eligible for Git; full originals stay ignored',
      all(subprocess.run(['git', 'check-ignore', '--quiet', str(p.relative_to(ROOT))],
                         cwd=ROOT).returncode == 1
          for p in reuse_dir.glob('*') if p.is_file())
      and subprocess.run(['git', 'check-ignore', '--quiet',
                          'wiki/raw/round-45/L224-sui-et-al-2015/original.pdf'],
                         cwd=ROOT).returncode == 0)

manifest_errors = []
manifest_files = 0
for round_number in range(38, 47):
    base = ROOT / f'wiki/raw/round-{round_number}'
    data = json.loads(text(base / 'manifest.json'))
    entries = data if isinstance(data, list) else data.get('files', data.get('entries', []))
    for item in entries:
        manifest_files += 1
        p = base / item['path']
        if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
            manifest_errors.append([round_number, item['path']])
check('Source manifests rounds38–46 still match archived bytes', not manifest_errors,
      {'checked_files': manifest_files, 'errors': manifest_errors})

p = ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md'
mt = text(p)
core = mt[mt.index('## 输入怎样成为可用支持'):mt.index('## 从维护进入改变与发展')]
core_hash = hashlib.sha256(core.encode()).hexdigest()
check('Maintenance scientific sections unchanged; authorized handoff prose updated',
      core_hash == before['maintenance_scientific_sections_normalized_sha256']
      and sha(p) != before['files'][str(p.relative_to(ROOT)).replace('\\', '/')],
      {'before_file_sha256': before['files']['book/part-01/03-inputs-maintenance-and-continuity.md'],
       'after_file_sha256': sha(p), 'scientific_sections_sha256': core_hash,
       'note': 'Prior receipts remain tied to their original revisions and were not rerun/overwritten.'})

protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6',
}
protected_results = {n: sha(ROOT / n) for n in protected}
check('Formal79 register, annual-review0.4 and old source ZIP preserved',
      all(protected_results[n] == h for n, h in protected.items()), protected_results)
tag_commit = git('rev-list', '-n', '1', 'framework-v0.1')
check('Framework tag unchanged', tag_commit == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag_commit)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    old = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check(f'Historical tag file unchanged: {name}', (ROOT / name).read_bytes() == old)

result = {
    'date_local': '2026-11-13', 'scope': 'Book chapter synthesis and authorized chapter handoffs',
    'passed': all(c['passed'] for c in checks), 'checks': checks,
    'manuscript_file_sha256': {n: sha(ROOT / n) for n in modified_md},
    'limitations': [
        'Editorial and provenance checks; not empirical validation of hypotheses or universal Ordo.',
        'Existing models and scientific review unchanged; no new model execution claimed.',
        'Previous receipts are historical, revision-bound and not rewritten to match current draft count.',
        'No Git commit/tag/push or source-package regeneration performed.',
    ],
}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [c for c in checks if not c['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
