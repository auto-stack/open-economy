"""Check chapter synthesis, six-field claims and authorized handoffs; not empirical validation."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/explanations-memory-and-revision'
RAW = ROOT / 'wiki/raw/round-51'
CHAPTER = ROOT / 'book/part-01/04-interfaces-memory-and-technological-levers.md'
CARD = ROOT / 'book/argument-cards/part-01-04-interfaces-memory-and-technological-levers.md'
CLAIMS = TOPIC / 'chapter-claims-2026-11-13.md'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def text(path):
    return path.read_text(encoding='utf-8-sig')


def load(path):
    return json.loads(text(path))


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


drafts = list(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))
cards = list(ROOT.glob('book/argument-cards/part-??-*.md'))
check('14 drafted units and matching14 cards;14 of28 remain',
      len(drafts) == len(cards) == 14
      and {p.parent.name + '-' + p.name[:2] for p in drafts} == {p.name[:10] for p in cards},
      {'drafted': len(drafts), 'cards': len(cards), 'remaining': 28 - len(drafts)})
body = text(CHAPTER)
check('Claim categories, experiment limits, costs and institutional boundary explicit',
      all(s in body for s in ['文献结论', '条件推论', '待验证假说', '工作程序', '价值与制度问题',
                              '完整材料自行建立相同索引', '不是许多次独立检验',
                              '没有测量真实读者时间', '当前可将它作为有限研究入口',
                              '本章没有唯一指定其制度答案']))
definitions = re.findall(r'^\[\^([^\]]+)\]:', body, re.M)
references = re.findall(r'\[\^([^\]]+)\](?!:)', body)
check('Footnotes all defined, used and uniquely identified',
      set(definitions) == set(references) and len(definitions) == len(set(definitions)),
      {'definitions': len(definitions), 'references': len(references)})

sections = re.split(r'^## (C\d+[^\n]*)\n', text(CLAIMS), flags=re.M)
required = {'主张与地位', '来源及作用', '反向材料', '适用边界', '已查与未知', '当前用法与复核'}
claim_checks = []
for i in range(1, len(sections), 2):
    fields = re.findall(r'^- \*\*([^*]+)：\*\*', sections[i + 1], re.M)
    claim_checks.append({'claim': sections[i].split()[0], 'six_fields': set(fields) == required and len(fields) == 6})
check('Eight key claim groups each use the six-field light format',
      len(claim_checks) == 8 and all(x['six_fields'] for x in claim_checks), claim_checks)
check('Quoted project arithmetic matches its specified conditions',
      abs((1 + (1 - 2 * .1) ** 5) / 2 - .66384) < 1e-10
      and all((4 * T - 8 > 3 * T) == (T > 8) for T in [2, 5, 8, 9, 10]),
      {'scope': 'Arithmetic only; no new empirical model or external replication.'})

reuse = load(RAW / 'source-reuse.json')
source_errors = []
for s in reuse['sources']:
    if not (RAW / s['source_metadata']).exists():
        source_errors.append([s['source_id'], 'metadata missing'])
    for a in s['artifacts']:
        p = RAW / a['path']
        if not p.exists() or p.stat().st_size != a['bytes'] or sha(p) != a['sha256']:
            source_errors.append([s['source_id'], a['path']])
check('12 prior sources/14 files resolve without new acquisition or reading scope',
      not source_errors and len(reuse['sources']) == 12
      and sum(len(s['artifacts']) for s in reuse['sources']) == 14
      and reuse['new_network_requests'] == 0 and load(RAW / 'download-log.json') == [], source_errors)

meta = load(RAW / 'metadata.json')
frozen_errors = []
for row in meta['project_bases'] + meta['chapter_artifacts']:
    if sha(ROOT / row['origin']) != row['sha256'] or sha(RAW / row['snapshot']) != row['sha256']:
        frozen_errors.append(row['origin'])
for row in meta['transition_versions']:
    if sha(RAW / row['before_snapshot']) != row['before_sha256']:
        frozen_errors.append([row['origin'], 'before'])
    if sha(ROOT / row['origin']) != row['after_sha256'] or sha(RAW / row['after_snapshot']) != row['after_sha256']:
        frozen_errors.append([row['origin'], 'after'])
check('Project bases, chapter outputs and eight handoff versions frozen exactly',
      not frozen_errors, {'project_bases': len(meta['project_bases']), 'handoffs': len(meta['transition_versions']), 'errors': frozen_errors})
manifest = load(RAW / 'manifest.json')
manifest_errors = []
for item in manifest:
    p = RAW / item['path']
    if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
        manifest_errors.append(item['path'])
actual = {str(p.relative_to(RAW)).replace('\\', '/') for p in RAW.rglob('*')
          if p.is_file() and p.name != 'manifest.json'}
check('Round51 manifest covers exact archived content',
      not manifest_errors and {x['path'] for x in manifest} == actual,
      {'files': len(manifest), 'errors': manifest_errors})

before = load(HERE / 'before-state.json')
maintenance = text(ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md')
core = maintenance[maintenance.index('## 输入怎样成为可用支持'):maintenance.index('## 从维护进入改变与发展')]
check('Maintenance scientific core unchanged despite authorized forward-transition edit',
      hashlib.sha256(core.encode()).hexdigest() == before['maintenance_scientific_core_sha256'],
      {'before_file': before['files']['book/part-01/03-inputs-maintenance-and-continuity.md'],
       'after_file': sha(ROOT / 'book/part-01/03-inputs-maintenance-and-continuity.md')})
info_name = 'book/part-01/02-entropy-information-and-ordo.md'
info_old, info_new = text(RAW / 'before' / info_name), text(ROOT / info_name)
check('Information chapter scientific sections preserved; closing handoff changed',
      info_old.split('## 从可修订的解释进入可持续的组织')[0]
      == info_new.split('## 从可修订的解释进入可持续的组织')[0]
      and sha(ROOT / info_name) != before['files'][info_name])
other_body_errors = []
for name in ['book/part-02/01-human-as-organization.md', 'book/part-03/02-revisable-shared-commitments.md']:
    old, new = text(RAW / 'before' / name), text(ROOT / name)
    if old[old.index('\n## '):] != new[new.index('\n## '):]:
        other_body_errors.append(name)
check('Human and commitment chapters only change introductory handoff', not other_body_errors, other_body_errors)

changed_md = [ROOT / name for name in [
    'README.md', 'book/README.md', 'book/outline.md', 'book/chapter-interfaces.md', 'book/framework-scope.md',
    'book/argument-map.md', 'research/README.md', 'research/survey-and-paper-program.md',
    'research/reviews/56-interfaces-memory-and-levers-chapter.md',
    'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-51/README.md',
    *before['files'].keys()]] + [CHAPTER, CARD, CLAIMS, TOPIC / 'README.md', TOPIC / 'chapter-evidence.md']
broken, anchor_errors, count = [], [], 0
for p in changed_md:
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text(p)):
        target = unquote(target.strip('<>'))
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        relative, _, fragment = target.partition('#')
        if not relative:
            continue
        count += 1
        dest = (p.parent / relative).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([str(p.relative_to(ROOT)), target])
        if p in [CHAPTER, CARD, CLAIMS] and dest.exists() and fragment and dest.suffix == '.md':
            headings = re.findall(r'^#{1,6}\s+(.+)$', text(dest), re.M)
            slugs = {re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings}
            if fragment not in slugs:
                anchor_errors.append([str(p.relative_to(ROOT)), target])
check('Authored local links resolve', not broken, {'links': count, 'errors': broken})
check('New chapter/card/check-file section anchors resolve', not anchor_errors, anchor_errors)
check('Current outline/interfaces reflect14/14 and preserve28 candidates',
      '共十四章；其余14' in text(ROOT / 'book/outline.md')
      and '现有十四张卡' in text(ROOT / 'book/outline.md')
      and '当前14章稿、其余14' in text(ROOT / 'book/chapter-interfaces.md'))

previous = load(ROOT / 'research/audits/lightweight-source-check-2026-11-13/validation.json')
preserved_names = [str((TOPIC / 'review-2026.md').relative_to(ROOT)).replace('\\', '/'),
                   'shared/source-check-format.md']
check('Existing review0.4 scientific text and light format unchanged by writing handoff',
      all(sha(ROOT / name) == previous['current_output_sha256'][name] for name in preserved_names))
protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'}
check('Formal79 register, earlier information review and old source package unchanged',
      all(sha(ROOT / name) == value for name, value in protected.items()))
tag = subprocess.check_output(['git', 'rev-list', '-n', '1', 'framework-v0.1'], cwd=ROOT).decode().strip()
check('Historical framework tag unchanged', tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    old = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check('Historical baseline preserved: ' + name, old == (ROOT / name).read_bytes())

result = {'date_local': '2026-11-13', 'scope': 'P1.4 discussion draft and authorized chapter/card handoffs',
          'passed': all(x['passed'] for x in checks), 'checks': checks,
          'current_output_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in [
              CHAPTER, CARD, CLAIMS, TOPIC / 'chapter-evidence.md', RAW / 'manifest.json',
              *[ROOT / name for name in before['files']]]},
          'limitations': ['Editorial/provenance checks; not verification of universal Ordo or empirical net benefits.',
                         'Models and research conclusions reused in prior conditions; no new empirical experiment.',
                         'Old chapter/card hashes may change because transitions were authorized; prior receipts retain their original revisions.',
                         'No Git commit/tag/push or source ZIP regeneration.']}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [x for x in checks if not x['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
