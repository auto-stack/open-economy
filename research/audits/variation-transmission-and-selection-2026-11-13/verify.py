"""Current-round provenance/editorial checks, not validation of an evolution theory."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'wiki/raw/round-52'
TOPIC = ROOT / 'research/surveys/06-technological-levers-and-organizational-evolution/variation-transmission-and-selection'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return path.read_text(encoding='utf-8-sig')


def main():
    checks = []

    def check(name, okay, evidence=None):
        checks.append({'check': name, 'passed': bool(okay), 'evidence': evidence})

    before = json.loads(read(HERE / 'before-state.json'))['protected_sha256']
    differences = [p for p, expected in before.items() if sha(ROOT / p) != expected]
    check('All37 protected files unchanged, including14 chapter bodies and14 cards', not differences, differences)
    chapters = list((ROOT / 'book').glob('part-*/*.md'))
    cards = list((ROOT / 'book/argument-cards').glob('*.md'))
    check('Research round does not create a fifteenth chapter/card', len(chapters) == len(cards) == 14,
          {'drafted': len(chapters), 'cards': len(cards), 'undrafted_of_28': 28-len(chapters)})

    expected_pages = {'L229': 19, 'L230': 8, 'L232': 27}
    source_metadata = sorted(RAW.glob('L*/metadata.json'))
    new_ids, upgrades, source_errors = [], [], []
    for path in source_metadata:
        meta = json.loads(read(path))
        (new_ids if meta['new_source_id'] else upgrades).append(meta['source_id'])
        original = path.parent / meta['archived_file']
        if sha(original) != meta['sha256'] or original.stat().st_size != meta['bytes']:
            source_errors.append(str(original))
        if original.suffix == '.pdf':
            if not original.read_bytes().startswith(b'%PDF-') or len(fitz.open(original)) != expected_pages[meta['source_id']]:
                source_errors.append(meta['source_id'] + ': PDF structure/pages')
        else:
            soup = BeautifulSoup(read(original), 'html.parser')
            expected = 'Partial connectivity increases cultural accumulation' if meta['source_id'] == 'L231' else 'The cultural niche'
            if expected not in soup.title.get_text() or not soup.select_one('article'):
                source_errors.append(meta['source_id'] + ': full article identity')
        if not meta.get('read_scope') or not meta.get('reading_limits'):
            source_errors.append(meta['source_id'] + ': reading scope')
    check('3 parsed PDFs and2 full HTML articles;4 new IDs plus existing L179',
          not source_errors and new_ids == ['L229','L230','L231','L232'] and upgrades == ['L179'],
          {'errors': source_errors, 'new': new_ids, 'upgraded': upgrades})

    logs = json.loads(read(RAW / 'download-log.json'))
    classes = json.loads(read(RAW / 'response-classification.json'))
    successful = [a for a in logs if a.get('saved') and a.get('valid_document')]
    failed = [a for a in logs if not a.get('saved')]
    log_errors = []
    for record in successful:
        path = RAW / record['path']
        if sha(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            log_errors.append(record['path'])
    check('9 acquisition attempts:5 adopted documents,2 ancillary XML,2 failures retained',
          len(logs) == len(classes['attempts']) == 9 and len(successful) == 7 and len(failed) == 2 and not log_errors,
          {'success': len(successful), 'failures': len(failed), 'errors': log_errors})
    pubs = {}
    for name in ['pubmed-records.xml','derex-pubmed.xml']:
        for article in ET.parse(RAW / 'discovery' / name).findall('.//PubmedArticle'):
            pubs[article.findtext('.//PMID')] = article
    boyd = pubs['21690340']
    check('Official L179 supplement citation and corrected L231 DOI retained',
          'Suppl 2' in boyd.findtext('.//Journal/JournalIssue/Volume')
          and '10.1073/pnas.1518798113' in ET.tostring(pubs['26929364'], encoding='unicode')
          and '108(26)' in read(RAW / 'read-scope-extension.json'))

    reuse_errors = []
    reuse = json.loads(read(RAW / 'source-reuse.json'))['sources']
    for source in reuse:
        if source['new_download'] or source['new_reading_scope']:
            reuse_errors.append(source['source_id'])
        for artifact in source['artifacts']:
            path = RAW / artifact['path']
            if sha(path) != artifact['sha256']:
                reuse_errors.append(artifact['path'])
    check('L51/L56/L176 originals reused within old scopes',
          not reuse_errors and {s['source_id'] for s in reuse} == {'L51','L56','L176'}, reuse_errors)

    spec = importlib.util.spec_from_file_location('finite_mechanisms', TOPIC / 'mechanism-example.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.construct()
    saved = json.loads(read(TOPIC / 'example-results.json'))
    check('Four distinct stipulated histories reproduce the same endpoint; no empirical calibration',
          result == saved and len(result['histories']) == 4
          and all(h['end_counts'] == {'A':6,'B':2} for h in result['histories'])
          and [h['retained_actor_ids'] for h in result['histories']] == [8,8,6,0])

    claims = read(TOPIC / 'claim-checks.md')
    fields = ['主张与地位','来源及作用','反向材料','适用边界','已查与未知','当前用法与复核']
    groups = re.split(r'^## C\d+ ', claims, flags=re.M)[1:]
    check('Six claim groups each retain all six light-check fields',
          len(groups) == 6 and all(all('**'+f+'：**' in g for f in fields) for g in groups))
    review = read(TOPIC / 'review-2026.md')
    check('Theory types, experimental limits and relational evidence gap explicit',
          all(t in review for t in ['文献论述','条件推论','待验证假说','工作方案','价值主张',
                                    '成员与关系更替','预设','尚缺','没有直接操纵']))

    files = list(TOPIC.glob('*.md')) + [ROOT/'research/reviews/57-variation-transmission-and-organizational-evolution.md', RAW/'README.md']
    nav = ['README.md','research/README.md','book/README.md','book/argument-map.md','book/chapter-interfaces.md',
           'book/outline.md','research/survey-and-paper-program.md','wiki/raw/README.md','wiki/index/SOURCES.md',
           'research/surveys/06-technological-levers-and-organizational-evolution/README.md',
           'research/surveys/06-technological-levers-and-organizational-evolution/research-program.md']
    files += [ROOT/n for n in nav]
    missing = []
    for path in files:
        for target in re.findall(r'\]\(([^)]+)\)', read(path)):
            target = target.strip('<>').split('#')[0]
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target):
                continue
            dest = path.parent / unquote(target)
            if not dest.exists():
                missing.append({'file':str(path.relative_to(ROOT)), 'target':target})
    check('Local links in new material and changed navigation resolve', not missing, missing)

    manifest = json.loads(read(RAW/'manifest.json'))
    listed = {a['path'] for a in manifest['files']}
    present = {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    manifest_errors = [a['path'] for a in manifest['files']
                       if sha(RAW/a['path']) != a['sha256'] or (RAW/a['path']).stat().st_size != a['bytes']]
    check('Round52 manifest covers every retained file except itself', listed == present and not manifest_errors,
          {'files':len(listed), 'errors':manifest_errors})

    ignored = ['wiki/raw/round-52/L229-lewontin-1970/original.pdf',
               'wiki/raw/round-52/L179-boyd-richerson-henrich-2011/original.html',
               'wiki/raw/round-52/discovery/pubmed-records.xml']
    trackable = ['wiki/raw/round-52/README.md','wiki/raw/round-52/manifest.json',
                 'wiki/raw/round-52/L229-lewontin-1970/metadata.json',
                 str((TOPIC/'review-2026.md').relative_to(ROOT))]
    def is_ignored(name):
        return subprocess.run(['git','check-ignore','-q',name],cwd=ROOT).returncode == 0
    check('Existing Git rules keep originals local and reviewed descriptors trackable',
          all(is_ignored(p) for p in ignored) and all(not is_ignored(p) for p in trackable))
    tag = subprocess.check_output(['git','rev-parse','framework-v0.1^{}'],cwd=ROOT,text=True).strip()
    check('Original framework tag unchanged', tag == '40e0f4c5f3ea19d4bdfd9313f1b95192c50c182d', tag)
    tag_differences=[]
    for name in ['docs/charter.md','wiki/archive/source-package-manifest.json']:
        original = subprocess.check_output(['git','show','framework-v0.1:'+name],cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != sha(ROOT/name):
            tag_differences.append(name)
    check('Charter0.4 and original source-package manifest remain tag-identical', not tag_differences,tag_differences)
    check('Official79-entry theory register frozen at known digest',
          sha(ROOT/'shared/theory-register.md') == '1fb0bfa5774904d09011e651f500f85b9ca8c632eeb52b4969a539d910f971e5')
    check('Legacy source ZIP frozen and not extended beyond round37',
          sha(ROOT/'.local-artifacts/open-economy-source-pack-2026-11-12.zip') == 'f0c5d85ff3b17254fca988964c47585a1e5ccd89a1016e30dc35a919b24fa8b6')

    output={'date_local':'2026-11-13','scope':'P1.5 first research round; provenance and editorial consistency',
            'passed':all(c['passed'] for c in checks),'checks':checks,
            'current_output_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files if p.parent == TOPIC or p.name.startswith('57-')},
            'limitations':['No empirical reproduction, systematic review or universal Ordo validation.',
                          'Synthetic histories establish non-identification only; no performance ranking or real parameters.',
                          'Organizational succession, fragmentation and skill-loss process evidence still needed.',
                          'No new chapter/card, formal theory entry, Git commit/tag/push or source-ZIP rebuild.']}
    (HERE/'validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':output['passed'],'checks':len(checks),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False))
    return 0 if output['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
