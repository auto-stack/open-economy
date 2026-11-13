"""Validate a small format pilot and its provenance, not the disputed research conclusions."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/explanations-memory-and-revision'
TRIAL = TOPIC / 'disputed-sources-2026-11-13'
RAW = ROOT / 'wiki/raw/round-50'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


data = load(TRIAL / 'cases.json')
expected = {'claim', 'sources', 'opposing', 'boundaries', 'coverage', 'use'}
check('Two filled pilots retain six core fields without a truth score',
      len(data['cases']) == 2 and set(data['required_fields']) == expected
      and all(expected <= set(c) and all(c[k] for k in expected) and 'score' not in c
              for c in data['cases']), {'format_version': data['format_version'], 'cases': 2})
source_errors = []
for case in data['cases']:
    for s in case['sources']:
        p = ROOT / s['path']
        if not p.exists() or sha(p) != s['sha256']:
            source_errors.append([case['case_id'], s['path']])
        if not all(s[k] for k in ['speaker', 'role', 'target', 'locator']):
            source_errors.append([case['case_id'], 'missing source identity/role/target/locator'])
check('All case sources resolve with exact bytes and distinguish speaker/role/target/locator',
      not source_errors, source_errors)

first, second = data['cases']
check('One L58 PDF retains target, independent commentator and reply as different voices',
      len(first['sources']) == 3 and len({s['path'] for s in first['sources']}) == 1
      and len({s['speaker'] for s in first['sources']}) == 3
      and {s['role'] for s in first['sources']} == {
          'original_empirical_report', 'methodological_critique', 'author_reply'},
      {'independent_data_count_not_inferred': True})
check('Football identity/trust and national conflict have separate use decisions',
      len(second['use']['outcomes']) == 2
      and second['use']['numerical_estimate_adopted_as_book_parameter'] is False
      and '保留争议' in second['use']['outcomes'][1]['decision']
      and {s['role'] for s in second['sources']} >= {
          'author_correction', 'replication_and_identification_critique', 'author_reply', 'publication_version_context'})
check('Both pilots explicitly retain unverified work and review triggers',
      all(c['coverage']['unverified'] and c['use']['review_trigger']
          and c['opposing']['exhaustive_search'] is False for c in data['cases']))

reuse = load(RAW / 'source-reuse.json')
reuse_errors = []
for r in reuse['sources']:
    p = RAW / r['original']
    if not p.exists() or p.stat().st_size != r['bytes'] or sha(p) != r['sha256']:
        reuse_errors.append(r['source_id'])
check('Five existing PDF containers reused; no new source IDs or primary PDF acquisition',
      not reuse_errors and {s['source_id'] for s in reuse['sources']} == {'L58', 'L158', 'L160', 'L161', 'L162'}
      and reuse['new_literature_ids'] == reuse['new_primary_pdf_downloads'] == 0, reuse_errors)
extension = load(RAW / 'read-scope-extension.json')
check('New page scopes recorded separately from old metadata',
      {s['source_id'] for s in extension['extensions']} == {'L160', 'L161', 'L162'}
      and all(not s['old_metadata_modified'] and not s['full_proofs_or_data_replication']
              for s in extension['extensions']), extension['extensions'])

classification = load(RAW / 'response-classification.json')
responses = classification['responses']
check('Three saved HTTP200 responses: one real publication record, two noncontent checks',
      len(load(RAW / 'download-log.json')) == 3 and len(responses) == 3
      and sum(r['adopted'] for r in responses) == 1
      and sum('bot' in r['title'].lower() and not r['adopted'] for r in responses) == 2
      and all(sha(RAW / r['path']) == r['sha256'] for r in responses), responses)
publisher = (RAW / 'records/aea-article.html').read_text(encoding='utf-8')
check('Adopted publisher record contains original abstract and2024 correction entry',
      '37 percent' in publisher and 'Online Corrigendum' in publisher and '2024' in publisher,
      {'role': 'version context only, not independent effect verification'})

before = load(RAW / 'before-state.json')
metadata = load(RAW / 'metadata.json')
context_errors = []
for original, current in zip(before['documents'], metadata['after_documents']):
    old_p, new_p, live_p = RAW / original['snapshot'], RAW / current['snapshot'], ROOT / current['path']
    if sha(old_p) != original['sha256'] or sha(new_p) != current['sha256'] or sha(live_p) != current['sha256']:
        context_errors.append(original['path'])
    if not live_p.read_bytes().startswith(old_p.read_bytes()):
        context_errors.append([original['path'], 'prior reading note changed rather than appended'])
check('Three source-context updates append scope/role notes and preserve prior text',
      not context_errors, context_errors)
freeze_errors = []
for p in (RAW / 'trial-records').iterdir():
    if p.is_file() and sha(p) != sha(TRIAL / p.name):
        freeze_errors.append(p.name)
check('Format and case snapshots match authored records',
      not freeze_errors and sha(ROOT / metadata['format_path']) == metadata['format_sha256']
      and sha(RAW / metadata['format_snapshot']) == metadata['format_sha256'], freeze_errors)

manifest = load(RAW / 'manifest.json')
manifest_errors = []
for r in manifest:
    p = RAW / r['path']
    if not p.exists() or p.stat().st_size != r['bytes'] or sha(p) != r['sha256']:
        manifest_errors.append(r['path'])
actual = {str(p.relative_to(RAW)).replace('\\', '/') for p in RAW.rglob('*')
          if p.is_file() and p.name != 'manifest.json'}
check('Round50 manifest covers all archived bytes',
      not manifest_errors and actual == {r['path'] for r in manifest},
      {'files': len(manifest), 'errors': manifest_errors})

prior = load(ROOT / 'research/audits/real-card-evidence-2026-11-13/validation.json')
review_name = str((TOPIC / 'review-2026.md').relative_to(ROOT)).replace('\\', '/')
versions = load(TOPIC / 'version-provenance.json')['versions']
check('Review0.3 retained byte-for-byte and current0.4 version bound to content',
      sha(TOPIC / 'review-2026-v0.3.snapshot.md') == prior['current_output_sha256'][review_name]
      and [v['version'] for v in versions] == ['0.1', '0.2', '0.3', '0.4']
      and all(sha(TOPIC / v['file']) == v['sha256'] for v in versions))

changed = [ROOT / p for p in [
    'README.md', 'shared/source-check-format.md', 'book/README.md', 'book/outline.md',
    'book/chapter-interfaces.md', 'book/argument-map.md', 'research/README.md',
    'research/survey-and-paper-program.md', 'research/reviews/55-lightweight-source-check-and-disputed-cases.md',
    'research/reviews/12-reading-notes.md',
    'research/surveys/04-influence-and-social-equivalence/README.md',
    'research/surveys/04-influence-and-social-equivalence/cultural-reading-notes.md',
    'research/surveys/04-influence-and-social-equivalence/art-sport-and-cultural-influence.md',
    'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-50/README.md']]
changed += list(TRIAL.glob('*.md'))
changed += [TOPIC / name for name in ['README.md', 'chapter-evidence.md', 'review-2026.md']]
broken = []
count = 0
for p in changed:
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', p.read_text(encoding='utf-8')):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        count += 1
        dest = (p.parent / target).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([str(p.relative_to(ROOT)), target])
check('Authored-document local links resolve; snapshots retain source-relative context',
      not broken, {'links': count, 'errors': broken})

old_book = load(ROOT / 'research/audits/entropy-information-chapter-2026-11-13/validation.json')
check('Existing chapter bodies and last-round repaired cards untouched',
      all(sha(ROOT / name) == digest for name, digest in old_book['manuscript_file_sha256'].items()
          if name.startswith('book/part-'))
      and all(sha(ROOT / name) == digest for name, digest in prior['current_output_sha256'].items()
              if name.startswith('book/argument-cards/')))
check('Still13 drafted units/13 cards; no bulk empty-card rollout',
      len(list(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))) == 13
      and len(list(ROOT.glob('book/argument-cards/part-??-*.md'))) == 13)
protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'}
check('Formal79 register, earlier information review and source ZIP unchanged',
      all(sha(ROOT / n) == h for n, h in protected.items()))
tag = subprocess.check_output(['git', 'rev-list', '-n', '1', 'framework-v0.1'], cwd=ROOT).decode().strip()
check('Historical tag unchanged', tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    old = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check('Historical baseline preserved: ' + name, old == (ROOT / name).read_bytes())

output_files = [ROOT / 'shared/source-check-format.md', TRIAL / 'cases.json',
                TRIAL / 'README.md', TOPIC / 'review-2026.md', TOPIC / 'version-provenance.json', RAW / 'manifest.json']
result = {'date_local': '2026-11-13', 'scope': 'Six-field format pilot in two substantive source disputes',
          'passed': all(c['passed'] for c in checks), 'checks': checks,
          'current_output_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in output_files},
          'limitations': ['Same-author targeted appraisal; no blinded adjudication, reader timing or measured maintenance benefit.',
                         'Partial original/commentary/correction/reply reading; no full data or code replication.',
                         'Two cases show representational coverage, not proof of truth or the efficiency of the format.',
                         'Prior revision-bound audit receipts not overwritten or rerun; no Git commit/tag/push or ZIP regeneration.']}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [c for c in checks if not c['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
