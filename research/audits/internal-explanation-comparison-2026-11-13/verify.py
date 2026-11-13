"""Verify a scoped synthetic comparison without rewriting prior audit receipts."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import subprocess
from urllib.parse import unquote
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/explanations-memory-and-revision'
COMP = TOPIC / 'internal-comparison-2026-11-13'
RAW = ROOT / 'wiki/raw/round-48'


def sha(p):
    digest = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


spec = importlib.util.spec_from_file_location('internal_record_comparison', COMP / 'compare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
scratch = ROOT / '.local-artifacts/internal-explanation-comparison-verification'
scratch.mkdir(parents=True, exist_ok=True)
module.HERE = scratch
fresh = module.run()
saved = load(COMP / 'results.json')
check('Deterministic rerun in separate scratch directory matches final results', fresh == saved)

comparisons = []
for s in saved['scenarios']:
    noise = s['unrelated_records']
    b = COMP / f'fixtures/noise-{noise}/B/materials.jsonl'
    c = COMP / f'fixtures/noise-{noise}/C/materials.jsonl'
    index = load(c.with_name('index.json'))
    rows = [json.loads(line) for line in b.read_bytes().splitlines()]
    grouped = {}
    for row in rows:
        grouped.setdefault(row['owner'], []).append(row['id'])
    comparisons.append({'noise': noise, 'B_C_byte_equal': b.read_bytes() == c.read_bytes(),
                        'same_semantic_index': index['groups'] == grouped,
                        'auxiliary_records': len(rows), 'record_hash_matches': sha(b) == s['B_C_same_material_sha256']})
check('B/C use identical evidence bytes; index only reorganizes existing owner fields',
      all(x['B_C_byte_equal'] and x['same_semantic_index'] and x['record_hash_matches'] for x in comparisons), comparisons)

claims = load(COMP / 'fixtures/conclusions.json')
gold = load(COMP / 'fixtures/reference-decisions.json')
tree = ast.parse((COMP / 'compare.py').read_text(encoding='utf-8'))
reader_functions = [x for x in tree.body if isinstance(x, ast.FunctionDef)
                    and x.name in ['answer', 'interpret', 'build_index']]
reader_names = {x.id for func in reader_functions for x in ast.walk(func) if isinstance(x, ast.Name)}
check('No oracle labels embedded in conclusions/index or consulted by reader functions',
      not {'gold', 'expected_answers'} & reader_names
      and all('status' not in c and 'locations' not in c for c in claims)
      and all('reference_decisions' not in (COMP / f'fixtures/noise-{n}/C/index.json').read_text()
              for n in [0, 20, 100]),
      {'author_blind': False, 'human_participants': 0, 'reader_uses_reference_answers': False})

base = saved['scenarios'][1]
summaries = {mode: base['unlimited'][mode]['summary'] for mode in ['A', 'B', 'C']}
check('Seven questions: A2 resolved/5 abstentions; B/C7 resolved; exact locations0/3/3',
      [summaries[m]['reference_decisions_resolved'] for m in ['A', 'B', 'C']] == [2, 7, 7]
      and [summaries[m]['exact_error_locations'] for m in ['A', 'B', 'C']] == [0, 3, 3]
      and summaries['A']['abstentions_or_budget_stops'] == 5
      and all(summaries[m]['unsafe_acceptances_in_fixture'] == 0 for m in ['A', 'B', 'C']), summaries)
check('Reported read costs include separate index preparation and initialization',
      [summaries[m]['cost']['evidence_records_read'] for m in ['A', 'B', 'C']] == [0, 250, 22]
      and summaries['C']['cost']['index_lookups'] == 5
      and base['C_index_build']['record_inspections'] == 50
      and base['C_index_build']['index_entries_written'] == 50
      and base['C_initialization']['snapshot_bytes_verified_once'] == 5471
      and base['C_initialization']['index_file_bytes_loaded_once'] == 4405,
      {'preparation': base['C_index_build'], 'initialization': base['C_initialization'],
       'storage': base['storage_bytes']})
check('B can self-organize the same index and achieve the same subsequent costs',
      all(s['B_builds_once']['same_index_as_C']
          and s['B_builds_once']['summary'] == s['unlimited']['C']['summary']
          and s['B_builds_once']['build'] == s['C_index_build'] for s in saved['scenarios']))
check('Read-budget and hypothetical write-cost sensitivity claims match output',
      next(b for b in base['budgets'] if b['auxiliary_record_budget_per_question'] == 4)['conditions']['C']['reference_decisions_resolved'] == 5
      and next(b for b in base['budgets'] if b['auxiliary_record_budget_per_question'] == 5)['conditions']['C']['reference_decisions_resolved'] == 7
      and [x['first_strict_saving_request'] for x in saved['cost_sensitivity']] == [2, 3, 7],
      {'weights_are_assumptions': True, 'human_time_measured': False})

fault = saved['faults']['misassigned_relation']
check('Misassigned relation can hide conflict despite intact files and complete ID coverage',
      fault['all_original_files_unchanged'] and fault['all_ids_still_indexed_once']
      and fault['C05_verdict']['status'] == 'usable-in-finite-task'
      and fault['gold_C05']['status'] == 'conflicting-evidence'
      and fault['after_refresh_C05']['status'] == 'conflicting-evidence'
      and fault['C06_verdict']['status'] == 'index-requires-review',
      {'injected_error': True, 'frequency_estimated': False, 'refresh_cost': fault['full_refresh_cost']})
check('Actual changed snapshot rejected before any indexed application verdict',
      saved['faults']['stale_snapshot']['changed_snapshot_detected']
      and saved['faults']['stale_snapshot']['lookup_not_executed'], saved['faults']['stale_snapshot'])
q = {'claim_id': 'C07', 'request': {'task': 'bounded-curve', 'context': 'A', 'unit': 'U', 'x': .25}}
cpath = COMP / 'fixtures/noise-20/C/materials.jsonl'
verdict = module.answer(claims[6], q, 'C', cpath, load(cpath.with_name('index.json')))
check('Corrected curve check does not extrapolate to an uninspected point',
      verdict['status'] == 'uninspected-point', verdict['status'])

initial = load(COMP / 'initial-run-provenance.json')
old_tree = ast.parse((COMP / 'compare-v0.1.snapshot.py').read_text(encoding='utf-8'))


def function_tree(t, name):
    return ast.dump(next(x for x in t.body if isinstance(x, ast.FunctionDef) and x.name == name))


check('Initial protocol/run preserved; questions and reference decisions not changed after first run',
      sha(COMP / 'protocol.md') == initial['original_protocol_sha256']
      and sha(COMP / 'compare-v0.1.snapshot.py') == initial['initial_script_sha256']
      and sha(COMP / 'initial-run.snapshot.json') == initial['initial_results_sha256']
      and all(function_tree(tree, n) == function_tree(old_tree, n) for n in ['questions', 'expected_answers'])
      and (COMP / 'amendment.md').exists(),
      {'post_run_scope_and_cost_amendment': True, 'amendment_disclosed': True})

manifest = load(RAW / 'manifest.json')
manifest_errors = []
for item in manifest:
    p = RAW / item['path']
    if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
        manifest_errors.append(item['path'])
listed = {x['path'] for x in manifest}
actual = {str(p.relative_to(RAW)).replace('\\', '/') for p in RAW.rglob('*')
          if p.is_file() and p.name != 'manifest.json'}
check('Round48 manifest matches exact archive bytes and complete file coverage',
      not manifest_errors and listed == actual, {'files': len(manifest), 'errors': manifest_errors})
frozen_files = [p for p in (RAW / 'internal-comparison').rglob('*') if p.is_file()]
check('Frozen internal materials match research artifacts exactly',
      all(sha(p) == sha(COMP / p.relative_to(RAW / 'internal-comparison')) for p in frozen_files),
      {'files': len(frozen_files)})
reuse = load(RAW / 'source-reuse.json')
source_errors = []
for src in reuse['sources']:
    for artifact in src['artifacts']:
        p = RAW / artifact['path']
        if not p.exists() or p.stat().st_size != artifact['bytes'] or sha(p) != artifact['sha256']:
            source_errors.append([src['source_id'], artifact['path']])
check('Six existing literature sources / seven originals reused, no new network requests or IDs',
      not source_errors and len(reuse['sources']) == 6
      and sum(len(x['artifacts']) for x in reuse['sources']) == 7
      and load(RAW / 'download-log.json') == [] and load(RAW / 'metadata.json')['new_network_requests'] == 0,
      source_errors)

prior = load(ROOT / 'research/audits/explanation-memory-and-revision-2026-11-13/validation.json')
prior_review = str((TOPIC / 'review-2026.md').relative_to(ROOT)).replace('\\', '/')
version = load(TOPIC / 'version-provenance.json')
check('Review0.1 preserved exactly;0.2 provenance matches current document',
      sha(TOPIC / 'review-2026-v0.1.snapshot.md') == prior['research_outputs_sha256'][prior_review]
      and all(sha(TOPIC / item['file']) == item['sha256'] for item in version['versions']))

changed_md = [ROOT / name for name in [
    'README.md', 'book/README.md', 'book/outline.md', 'book/chapter-interfaces.md', 'book/argument-map.md',
    'research/README.md', 'research/survey-and-paper-program.md',
    'research/reviews/53-internal-comparison-of-explanation-records.md',
    'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-48/README.md']]
changed_md += [TOPIC / n for n in ['README.md', 'review-2026.md', 'chapter-evidence.md']]
changed_md += list(COMP.glob('*.md'))
broken, count = [], 0
for p in changed_md:
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', p.read_text(encoding='utf-8')):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        count += 1
        dest = (p.parent / target).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            broken.append([str(p.relative_to(ROOT)), target])
check('Authored document links resolve; frozen originals retain source-relative context',
      not broken, {'links': count, 'errors': broken})

check('13 drafted units and13 cards; remaining15 unchanged',
      len(list(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))) == 13
      and len(list(ROOT.glob('book/argument-cards/part-??-*.md'))) == 13)
previous_book = load(ROOT / 'research/audits/entropy-information-chapter-2026-11-13/validation.json')
check('Earlier chapter bodies unchanged',
      all(sha(ROOT / name) == digest for name, digest in previous_book['manuscript_file_sha256'].items()
          if name.startswith('book/part-')))
protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6'}
check('Formal79 register, earlier information review and source ZIP preserved',
      all(sha(ROOT / name) == digest for name, digest in protected.items()))
tag_commit = subprocess.check_output(['git', 'rev-list', '-n', '1', 'framework-v0.1'], cwd=ROOT).decode().strip()
check('Framework tag remains unchanged', tag_commit == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag_commit)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    original = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check('Historical baseline preserved: ' + name, original == (ROOT / name).read_bytes())

result = {'date_local': '2026-11-13', 'scope': 'Internal comparison of three structured explanation-recording conditions',
          'passed': all(x['passed'] for x in checks), 'checks': checks,
          'current_output_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in [
              COMP / 'compare.py', COMP / 'results.json', COMP / 'protocol.md', COMP / 'amendment.md',
              TOPIC / 'review-2026.md', TOPIC / 'version-provenance.json', RAW / 'manifest.json']},
          'limitations': ['Synthetic tasks, explicit semantic rules, known reference decisions; no independent human test.',
                         'Record and byte accounting is a conditional model; no measured human labor, fees or productivity.',
                         'Association creation from natural language was not measured; B and C already share owner metadata.',
                         'Old revision-bound audit receipts not rerun or rewritten. No Git commit, tag, push or ZIP rebuild.']}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [x for x in checks if not x['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
