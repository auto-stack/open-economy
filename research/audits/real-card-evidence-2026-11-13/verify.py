"""Check provenance and scoped repairs; manual source appraisal is not automated proof."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/explanations-memory-and-revision'
AUDIT = TOPIC / 'real-card-audit-2026-11-13'
RAW = ROOT / 'wiki/raw/round-49'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def targets(path):
    result = []
    for item in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', path.read_text(encoding='utf-8')):
        item = unquote(item.strip('<>')).split('#')[0]
        if item and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', item):
            result.append((path.parent / item).resolve())
    return result


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


register = load(AUDIT / 'case-register.json')
cases = register['cases']
check('Purposeful sample fixed to6 claims in3 existing cards',
      len(cases) == 6 and len({c['card'] for c in cases}) == 3
      and [c['case_id'] for c in cases] == ['R01', 'R02', 'R03', 'R04', 'R05', 'R06'],
      {'random_sample': False, 'blind_assessment': False, 'population_rates_estimated': False})

metadata = load(RAW / 'metadata.json')
before = load(RAW / 'before-state.json')
before_lookup = {r['path']: r for r in before['cards']}
card_errors = []
for case in cases:
    old = ROOT / case['before_snapshot']
    current = ROOT / case['card']
    old_lines = old.read_text(encoding='utf-8').splitlines()
    new_lines = current.read_text(encoding='utf-8').splitlines()
    if sha(old) != case['before_card_sha256'] or sha(current) != case['after_card_sha256']:
        card_errors.append([case['case_id'], 'file hash'])
    if case['claim_text'] not in old_lines[case['before_card_line'] - 1] or case['claim_text'] not in new_lines[case['after_card_line'] - 1]:
        card_errors.append([case['case_id'], 'claim locator'])
    for source in case['evidence']:
        p = ROOT / source['path']
        if not p.exists() or sha(p) != source['sha256']:
            card_errors.append([case['case_id'], source['path']])
check('Exact claim wording retained; before/after line locators and source hashes valid', not card_errors, card_errors)

trace_errors = []
for case in cases:
    route = case['before_verified_path']
    for origin, destination in zip(route, route[1:]):
        # Resolve old-card links in their original directory, using the frozen old text.
        source = ROOT / origin
        content = ((RAW / before_lookup[origin]['snapshot']).read_text(encoding='utf-8')
                   if origin in before_lookup else source.read_text(encoding='utf-8'))
        found = []
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', content):
            target = unquote(target.strip('<>')).split('#')[0]
            if target and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                found.append((source.parent / target).resolve())
        if (ROOT / destination).resolve() not in found:
            trace_errors.append([case['case_id'], origin, destination])
check('Reported pre-repair routes really existed; they are not claimed to be shortest', not trace_errors, trace_errors)

kinds = {c['case_id']: c['finding_class'] for c in cases}
check('Case classification distinguishes locator refinements, adequate trace and effect gap',
      list(kinds.values()).count('locator_and_role_clarification') == 4
      and kinds['R03'] == 'trace_already_adequate'
      and kinds['R04'] == 'direct_effect_evidence_still_missing', kinds)
check('Evidence-gap claim remains a hypothesis; source is motivation rather than validation',
      cases[3]['claim_status'] == '待验证假说'
      and cases[3]['direct_effect_evidence_in_reviewed_trace'] is False
      and cases[3]['evidence'][0]['role'] == 'motivation_and_open_question_not_direct_validation'
      and all(c['opposing_material_search_exhaustive'] is False for c in cases))
check('Corrections, theorem limits, alternatives and analytic boundaries kept distinct',
      len({c['boundary_material_kind'] for c in cases}) == 6
      and all(c['scientific_reversal_found'] is False for c in cases),
      {'note': 'Manual appraisal of the six reviewed claims, not a guarantee of truth or exhaustive absence of contrary evidence.'})

source_errors = []
reuse = load(RAW / 'source-reuse.json')
for src in reuse['sources']:
    for item in src['artifacts']:
        p = RAW / item['path']
        if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
            source_errors.append([src['source_id'], item['path']])
check('Four original literature families/six artifacts reused without new acquisition',
      not source_errors and len(reuse['sources']) == 4
      and sum(len(s['artifacts']) for s in reuse['sources']) == 6
      and reuse['new_network_requests'] == 0 and load(RAW / 'download-log.json') == [], source_errors)

snapshot_errors = []
for category, field in [('before_cards', 'path'), ('after_cards', 'path'),
                        ('project_materials', 'path'), ('context_records', 'origin')]:
    for row in metadata[category]:
        p = RAW / row['snapshot']
        if sha(p) != row['sha256']:
            snapshot_errors.append([category, row['snapshot']])
        if category != 'before_cards' and sha(ROOT / row[field]) != row['sha256']:
            snapshot_errors.append([category, row[field], 'current artifact differs'])
for p in (RAW / 'audit-records').iterdir():
    if p.is_file() and sha(p) != sha(AUDIT / p.name):
        snapshot_errors.append(['audit-records', p.name])
check('Before/after cards, project bases, context records and current audit frozen exactly',
      not snapshot_errors, snapshot_errors)

manifest = load(RAW / 'manifest.json')
manifest_errors = []
for item in manifest:
    p = RAW / item['path']
    if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
        manifest_errors.append(item['path'])
actual = {str(p.relative_to(RAW)).replace('\\', '/') for p in RAW.rglob('*')
          if p.is_file() and p.name != 'manifest.json'}
check('Round49 manifest covers every archived file with exact bytes',
      not manifest_errors and actual == {x['path'] for x in manifest},
      {'files': len(manifest), 'errors': manifest_errors})

prior = load(ROOT / 'research/audits/internal-explanation-comparison-2026-11-13/validation.json')
review_path = str((TOPIC / 'review-2026.md').relative_to(ROOT)).replace('\\', '/')
versions = load(TOPIC / 'version-provenance.json')['versions']
check('Review0.2 is preserved exactly;0.1/0.2/0.3 version receipts match',
      sha(TOPIC / 'review-2026-v0.2.snapshot.md') == prior['current_output_sha256'][review_path]
      and [v['version'] for v in versions] == ['0.1', '0.2', '0.3']
      and all(sha(TOPIC / v['file']) == v['sha256'] for v in versions))

changed = [ROOT / n for n in [
    'README.md', 'book/README.md', 'book/outline.md', 'book/chapter-interfaces.md', 'book/argument-map.md',
    'research/README.md', 'research/survey-and-paper-program.md',
    'research/reviews/54-real-card-evidence-and-boundary-audit.md',
    'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-49/README.md']]
changed += [ROOT / n for n in before_lookup]
changed += [TOPIC / n for n in ['README.md', 'chapter-evidence.md', 'review-2026.md']]
changed += list(AUDIT.glob('*.md'))
broken = []
link_count = 0
for p in changed:
    for dest in targets(p):
        link_count += 1
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([str(p.relative_to(ROOT)), str(dest)])
check('Changed authored-document links resolve; copied originals retain origin context',
      not broken, {'links': link_count, 'errors': broken})

anchor_errors = []
for name in before_lookup:
    p = ROOT / name
    for target in re.findall(r'\]\(([^\s)]+)\)', p.read_text(encoding='utf-8')):
        if '#' not in target:
            continue
        path, anchor = unquote(target).split('#', 1)
        dest = (p.parent / path).resolve()
        if dest.suffix != '.md' or not dest.exists():
            continue
        headings = re.findall(r'^#{1,6}\s+(.+)$', dest.read_text(encoding='utf-8'), re.M)
        slugs = {re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings}
        if anchor not in slugs:
            anchor_errors.append([name, target])
check('New card Markdown section anchors match actual headings', not anchor_errors, anchor_errors)

older_book = load(ROOT / 'research/audits/entropy-information-chapter-2026-11-13/validation.json')
check('Manuscript bodies unchanged while three card repairs get new hashes',
      all(sha(ROOT / name) == digest for name, digest in older_book['manuscript_file_sha256'].items()
          if name.startswith('book/part-'))
      and all(sha(ROOT / row['path']) != row['sha256'] for row in before['cards']))
check('Draft/card counts stay13/13, leaving15 candidate units undrafted',
      len(list(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))) == 13
      and len(list(ROOT.glob('book/argument-cards/part-??-*.md'))) == 13)
protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'}
check('Formal79 register, information review and original source ZIP preserved',
      all(sha(ROOT / name) == digest for name, digest in protected.items()))
tag = subprocess.check_output(['git', 'rev-list', '-n', '1', 'framework-v0.1'], cwd=ROOT).decode().strip()
check('Original framework tag unchanged', tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    original = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check('Historical baseline preserved: ' + name, original == (ROOT / name).read_bytes())

result = {'date_local': '2026-11-13', 'scope': 'Six selected real claims in three argument cards',
          'passed': all(c['passed'] for c in checks), 'checks': checks,
          'current_output_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in [
              AUDIT / 'case-register.json', AUDIT / 'reading-notes.md', AUDIT / 'README.md',
              TOPIC / 'review-2026.md', TOPIC / 'version-provenance.json', RAW / 'manifest.json',
              *[ROOT / name for name in before_lookup]]},
          'limitations': ['Human source appraisal by the same author; automated checks cover provenance, links and retained wording only.',
                         'No exhaustive counterevidence search, representative defect rate, reader timing or causal effect estimate.',
                         'Direct-effect evidence remains missing in the reviewed maintenance-hypothesis trace.',
                         'Earlier revision-bound receipts not rerun or rewritten; no Git commit/tag/push or ZIP rebuild.']}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [c for c in checks if not c['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
