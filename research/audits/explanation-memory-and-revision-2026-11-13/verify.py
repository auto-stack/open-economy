"""Check source acquisition, reading scope, finite example and book research handoff."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'wiki/raw/round-47'
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/explanations-memory-and-revision'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


checks = []


def check(name, passed, evidence=None):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


manifest = read_json(RAW / 'manifest.json')
errors = []
for item in manifest:
    p = RAW / item['path']
    if not p.exists() or p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
        errors.append(item['path'])
actual_files = {str(p.relative_to(RAW)).replace('\\', '/') for p in RAW.rglob('*')
                if p.is_file() and p.name != 'manifest.json'}
check('Round47 manifest covers all archived files and exact bytes',
      not errors and {x['path'] for x in manifest} == actual_files,
      {'files': len(manifest), 'errors': errors})

log = read_json(RAW / 'download-log.json')
classification = read_json(RAW / 'response-classification.json')
failed = [r for r in log if not r.get('classified_as_expected')]
check('13 acquisition requests; 10 expected responses; 3 failures retained and not adopted',
      len(log) == 13 and len(failed) == 3
      and sum(bool(r.get('classified_as_expected')) for r in log) == 10
      and len(classification['unadopted_attempts']) == 3,
      [{'path': r['path'], 'http_status': r.get('status_code'),
        'expected_content': r.get('classified_as_expected', False)} for r in failed])

adopted = []
source_errors = []
for sid in ['L225', 'L226', 'L227', 'L228']:
    d = next(RAW.glob(sid + '-*'))
    m = read_json(d / 'metadata.json')
    p = d / m['adopted_file']
    if p.stat().st_size != m['bytes'] or sha(p) != m['sha256']:
        source_errors.append(sid)
    adopted.append({'source_id': sid, 'material': m['adopted_file'],
                    'sha256': sha(p), 'read_scope': m['reading_scope']})
check('Four adopted primary documents match metadata and targeted reading scopes', not source_errors, adopted)

import fitz
pdf_counts = {}
for relative in ['L225-sandve-et-al-2013/original.pdf',
                 'L226-wilkinson-et-al-2016/original.pdf',
                 'L226-wilkinson-et-al-2016/addendum.pdf']:
    p = RAW / relative
    pdf_counts[relative] = len(fitz.open(p)) if p.read_bytes().startswith(b'%PDF-') else None
check('Two primary PDFs and one same-family addendum have correct page counts',
      list(pdf_counts.values()) == [4, 9, 2], pdf_counts)
bioc = ET.parse(RAW / 'L227-hardwicke-et-al-2018/bioc.xml')
passages = bioc.findall('.//passage')
html = (RAW / 'L228-nosek-et-al-2018/original.html').read_text(encoding='utf-8')
check('BioC and HTML are article bodies; failed BioC not counted as a full text',
      len(passages) == 184 and all(x in html for x in ['The preregistration revolution', 'id="s3"', 'id="s14"'])
      and not read_json(RAW / 'L228-nosek-et-al-2018/metadata.json')['bioc_response_adopted'],
      {'hardwicke_passages': len(passages), 'nosek_adopted': 'PMC HTML'})

publication = ET.parse(RAW / 'discovery/pubmed-records.xml')
linked = ET.parse(RAW / 'discovery/linked-publication-records.xml')
main_pmids = {a.findtext('.//PMID') for a in publication.findall('.//PubmedArticle')}
linked_pmids = {a.findtext('.//PMID') for a in linked.findall('.//PubmedArticle')}
nosek_record = next(a for a in publication.findall('.//PubmedArticle') if a.findtext('.//PMID') == '29531091')
comments = {x.findtext('PMID'): x.attrib['RefType'] for x in nosek_record.findall('.//CommentsCorrections')}
check('Publication records distinguish FAIR addendum from Nosek comments/reply',
      main_pmids == {'24204232', '26978244', '30225032', '29531091'}
      and linked_pmids == {'30890711', '30341224', '30341225'}
      and all(comments.get(x) == 'CommentIn' for x in ['30341224', '30341225']),
      {'nosek_link_types': comments})

reuse = read_json(RAW / 'source-reuse.json')
reuse_errors = []
for item in reuse['sources']:
    p = RAW / item['original']
    if p.stat().st_size != item['bytes'] or sha(p) != item['sha256']:
        reuse_errors.append(item['source_id'])
    original_metadata = read_json(RAW / item['source_metadata'])
    if original_metadata.get('sha256') != item['sha256']:
        reuse_errors.append([item['source_id'], 'old metadata integrity'])
check('L23/L47 reuse preserves originals and records L47 reading extension separately',
      not reuse_errors and {i['source_id'] for i in reuse['sources']} == {'L23', 'L47'}
      and (RAW / 'read-scope-extension.json').exists(), reuse_errors)

spec = importlib.util.spec_from_file_location('explanation_memory_example', TOPIC / 'examples.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
saved_example = read_json(TOPIC / 'example-results.json')
fresh = module.run()
check('Finite example output reproducible and demonstrates the stated distinction',
      fresh == saved_example and fresh['v1']['matches_recorded_result']
      and not fresh['v1']['matches_intended_sample_mean']
      and fresh['v2']['sample_mean'] == 4
      and fresh['v2']['old_record_still_unchanged']
      and fresh['dependency_review']['flag_for_review'] == ['mean-claim-v1', 'threshold-decision-v1']
      and fresh['dependency_review']['independent_count_not_flagged'],
      {'saved_result_sha256': sha(TOPIC / 'example-results.json'), 'empirical_data': False})

changed_md = [ROOT / p for p in [
    'README.md', 'research/README.md', 'research/survey-and-paper-program.md',
    'research/reviews/52-explanation-memory-interfaces-and-revision.md',
    'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
    'book/README.md', 'book/outline.md', 'book/chapter-interfaces.md', 'book/argument-map.md',
    'wiki/index/SOURCES.md', 'wiki/raw/README.md', 'wiki/raw/round-47/README.md',
]] + list(TOPIC.glob('*.md'))
link_errors, link_count = [], 0
for p in changed_md:
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', p.read_text(encoding='utf-8')):
        target = unquote(target.strip('<>')).split('#')[0]
        if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        link_count += 1
        dest = (p.parent / target).resolve()
        if not dest.exists() and dest != HERE / 'validation.json':
            link_errors.append([str(p.relative_to(ROOT)), target])
check('Changed research/book navigation and reading-note links resolve', not link_errors,
      {'links': link_count, 'errors': link_errors})

drafts = list(ROOT.glob('book/part-??/[0-9][0-9]-*.md'))
cards = list(ROOT.glob('book/argument-cards/part-??-*.md'))
check('Research adds no complete manuscript or argument-card unit', len(drafts) == len(cards) == 13,
      {'drafts': len(drafts), 'cards': len(cards), 'not_drafted': 15})
previous = read_json(ROOT / 'research/audits/entropy-information-chapter-2026-11-13/validation.json')
book_body_files = [n for n in previous['manuscript_file_sha256'] if n.startswith('book/part-')]
body_hashes = {n: sha(ROOT / n) for n in book_body_files}
check('Prior drafted chapters unchanged by this research round',
      all(body_hashes[n] == previous['manuscript_file_sha256'][n] for n in book_body_files), body_hashes)

protected = {
    'shared/theory-register.md': '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5',
    'research/surveys/04-influence-and-social-equivalence/entropy-information-ordo/review-2026.md':
        'eda4f4053413f6956c46f21559e93c99a5b9fa70864e84db92d84d7aaccd35af',
    '.local-artifacts/open-economy-source-pack-2026-11-12.zip':
        'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6',
}
protected_actual = {n: sha(ROOT / n) for n in protected}
check('Formal register, prior0.4 review and source package unchanged',
      all(protected_actual[n] == h for n, h in protected.items()), protected_actual)
tag_commit = subprocess.check_output(['git', 'rev-list', '-n', '1', 'framework-v0.1'], cwd=ROOT).decode().strip()
check('Historical framework tag unchanged', tag_commit == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag_commit)
for name in ['docs/charter.md', 'wiki/archive/source-package-manifest.json']:
    original = subprocess.check_output(['git', 'show', f'framework-v0.1:{name}'], cwd=ROOT)
    check('Historical baseline unchanged: ' + name, original == (ROOT / name).read_bytes())

descriptor_paths = [RAW / 'README.md', RAW / 'manifest.json', RAW / 'download-log.json',
                    RAW / 'response-classification.json', RAW / 'source-reuse.json',
                    RAW / 'read-scope-extension.json', *RAW.glob('L*/metadata.json')]
check('Archive descriptors trackable; original full texts and inspection images ignored',
      all(subprocess.run(['git', 'check-ignore', '--quiet', str(p.relative_to(ROOT))],
                         cwd=ROOT).returncode == 1 for p in descriptor_paths)
      and all(subprocess.run(['git', 'check-ignore', '--quiet', name], cwd=ROOT).returncode == 0
              for name in ['wiki/raw/round-47/L225-sandve-et-al-2013/original.pdf',
                           'wiki/raw/round-47/L228-nosek-et-al-2018/original.html',
                           'wiki/raw/round-47/inspection/L226-pdf4.png']))

result = {'date_local': '2026-11-13', 'scope': 'First research round for manuscript unitP1.4',
          'passed': all(c['passed'] for c in checks), 'checks': checks,
          'research_outputs_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                                      for p in sorted(TOPIC.glob('*')) if p.is_file()},
          'limitations': ['Targeted literature reading, not an exhaustive systematic survey or2026 publication review.',
                         'Finite synthetic example, not independent replication of the cited empirical study.',
                         'Record structure and revision process remain project proposals; net benefit and governance effects untested.',
                         'Prior audit receipts preserved as revision-bound historical records; no old receipt rerun or rewritten.']}
(HERE / 'validation.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps({'passed': result['passed'], 'checks': len(checks),
                  'failed': [c for c in checks if not c['passed']]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] else 1)
