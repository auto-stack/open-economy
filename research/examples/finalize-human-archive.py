"""Finalize the round-11 provenance manifest without changing downloaded originals."""
from pathlib import Path
import datetime, hashlib, json

ROOT=Path(__file__).resolve().parents[2]/'wiki'/'raw'/'round-11'
DETAILS={
 'L54-sterling-2012':('ResearchGate cover plus journal typeset article; Physiology & Behavior 106 (2012) 5-15; received/accepted 2011.', 'PDF pp.2-4 (journal pp.5-7): abstract, introduction, feedback critique and predictive regulation. Later clinical claims not adopted.', 'theoretical review/essay'),
 'L55-deci-ryan-2000':('42-page journal target article, Psychological Inquiry 11(4), 227-268, from SDT website.', 'PDF pp.1,4,10,12,24-26; partial passages on pp.21-22,27. Targeted needs/internalization/evolution reading, not entire article.', 'theoretical framework and research synthesis'),
 'L56-west-et-al-2015':('8-page PNAS Early Edition, university author copy; final citation 112(33),10112-10119.', 'PDF pp.1-3,6-7: definitions, steps, Table 1, benefits/return paths, interdependence, maximizing-agent limits and future directions.', 'comparative theoretical review'),
 'L57-tomasello-et-al-2005':('42-page accepted copyedited prepublication manuscript, cover copyright 2004/in press; published article 2005, BBS 28,675-691. Not final typeset version.', 'PDF pp.1,3-4,11-12,16-17,24; partial p.15. Intentional action, shared goals/roles and cultural hypotheses; species/clinical generalizations not adopted.', 'theoretical proposal and developmental/comparative research synthesis'),
 'L58-henrich-et-al-2005':('62-page author proof with editorial queries and placeholder pagination; includes target, commentaries and reply. Final target 795-815; discussion 815-855.', 'PDF pp.1,5,9,11-14; main p.20 passages; Binmore commentary on p.23 plus p.24 ending; reply sections R1.1-R1.2 on pp.45-46 and adjacent passages. Not all commentaries or data read.', 'cross-cultural experiments with commentary and author reply'),
 'L59-fehr-gaechter-2002':('4-page Nature typeset article 415,137-140 (2002), LMU EconWPA deposit identifier dated 2003.', 'PDF p.1 and Methods on pp.3-4, selected results/discussion passages on pp.2-3. No raw-data reanalysis.', 'primary experimental study'),
 'L60-herrmann-et-al-2008':('6-page Science typeset copy 319,1362-1367; first/last pages include fragments of adjacent unrelated articles, not adopted.', 'This article on PDF p.1; design/definitions p.2; results/context-variable construction p.4; results and part discussion p.5; article ending p.6. Online supplement not read.', 'primary cross-participant-pool experimental study'),
 'L61-ramsay-woods-2014':('PMC author manuscript via public NCBI BioC full-text XML; journal 2014, manuscript release 2015. No typeset PDF obtained; some cross-reference text simplified in BioC.', 'Abstract/introduction; Anticipatory control and Scope of Homeostasis passages; first part of Physiological Regulation vs. Physiological Control; beginning of central-integrator section; Concluding Thoughts. Robustness section located, not fully assessed.', 'critical theoretical review'),
}

def dump(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for sid,(version,scope,kind) in DETAILS.items():
    d=ROOT/sid; mp=d/'metadata.json'; meta=json.loads(mp.read_text(encoding='utf-8'))
    original=d/('original.xml' if sid.startswith('L61') else 'original.pdf')
    assert original.exists() and meta['sha256']==sha(original)
    meta.update(version=version,read_scope=scope,source_type=kind,
                reading_method='Targeted full-text passages; extraction alone does not count as reading.',
                reading_notes='../../../research/reviews/12-reading-notes.md',
                local_research_archive=True)
    # metadata.json is inside the source directory: use four upward hops.
    meta['reading_notes']='../../../../research/reviews/12-reading-notes.md'
    if sid.startswith('L57'):
        meta['author_index_url']='https://miketomasello.com/sample-page/theory-papers/'
    attempts=[]
    for p in sorted(d.glob('attempt*.json')):
        item=json.loads(p.read_text(encoding='utf-8'))
        attempts.extend(item if isinstance(item,list) else [item])
    attempts.extend(meta.get('attempts',[]))
    if sid.startswith('L57'):
        attempts.append({'url':'https://www.eva.mpg.de/documents/Cambridge/Tomasello_Understanding_BehBrainSci_2005_1555292.pdf','status_code':404,'response_file':'failed-response-initial.bin','record_origin':'Reconstructed from actual round-11 acquisition tool result; response preserved unchanged.'})
    if sid.startswith('L61'):
        attempts.append({'url':meta['source_url'],'status_code':200,'validation':'XML parsed; full-text title and body validated','response_file':'original.xml'})
    unique=[]; seen=set()
    for a in attempts:
        key=json.dumps(a,sort_keys=True,ensure_ascii=False)
        if key not in seen:
            unique.append(a);seen.add(key)
    dump(d/'acquisition-log.json',{'source_id':sid,'attempts':unique})
    dump(mp,meta)

files=[]; originals=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:
        continue
    entry={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
    files.append(entry)
    if p.name in ('original.pdf','original.xml'):
        originals.append({'id':p.parent.name,**entry})
assert len(originals)==8
dump(ROOT/'manifest.json',{'research_date_local':'2026-11-12','timezone':'Asia/Shanghai',
     'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'source_count':len(originals),'originals':originals,'files':files,
     'excludes':['manifest.json itself','__pycache__ contents']})
print(json.dumps({'sources':len(originals),'pdf':sum(x['path'].endswith('.pdf') for x in originals),
                  'xml':sum(x['path'].endswith('.xml') for x in originals),'manifest_files':len(files)},ensure_ascii=False))
