"""Assemble archived exports with explicit, human-reviewed title decisions below.
No keyword classifier and no automatic full-text eligibility decisions.
"""
from pathlib import Path
import collections, csv, hashlib, json, shutil

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; RAW=ROOT/'wiki/raw/round-39'; DISC=RAW/'discovery'
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csvwrite(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

# Decisions refer only to the titles actually inspected in this calibration.
exclusions={
 'P-broad':{8:'Book review; retain bibliographic trail, not mechanism evidence'},
 'C-broad':{1:'Binge-eating self-regulation; outside biophysical/abstract-control scope',2:'Health-behavior self-regulation',3:'Illness self-regulation behavioral model',4:'Self-esteem attribution',5:'Health-behavior change',7:'Relaxation-practice intervention',8:'Macroeconomic governmental regulation',9:'Personality/emotional coping'},
 'C-title':{1:'Professional/nursing regulator',3:'Economic-system application',4:'Social policy cybernetics',7:'Computational medical applications; no maintenance object in title'},
 'B-broad':{8:'Professional autonomy'},
 'B-title':{4:'Computing constraint-closure operation',8:'AI constraint consistency operation'},
 'C-author':{3:'Literary teaching item; not regulator theory'},
 'C-viability':{5:'Book review, not primary mechanism'},
 'C-homeostasis':{4:'Governmentality interpretation; social-theory scope'},
 'OA-C':{2:'Ayllu social organization',4:'Tourism service system',8:'Organizational assessment application',10:'Governance/technology convergence'},
}
notes={
 ('C-seed',1):'Title collision: Eykhoff1994, NOT Conant/Ashby1970 and NOT a duplicate version',
 ('C-author',1):'Book chapter candidate: possible reprint family; author/title/DOI alone do not verify identical text',
 ('C-author',2):'Correct L195 DOI; title+author relevance request still returns unrelated items',
 ('B-title',3):'Keep critical boundary argument: biological constraints do not entail cognitive closure',
 ('B-broad',1):'Planetary extension is boundary candidate, not established biological mapping',
 ('B-title',2):'Planetary extension is boundary candidate; publication/version status pending',
 ('OA-C',9):'Broad universal claim and repository version require verification; title not evidence',
}
logs=json.loads((DISC/'query-log.json').read_text(encoding='utf-8'))
retry=json.loads((DISC/'followup-retrieval-log.json').read_text(encoding='utf-8'))
retry_by={x['id']:x for x in retry if x.get('id')}
logs+=json.loads((DISC/'adaptive-query-log.json').read_text(encoding='utf-8'))
occ=[];qsummary=[]
for q in logs:
    chosen=q if q.get('status')==200 else retry_by.get(q['id'],q)
    if chosen.get('status')!=200:continue
    response=chosen['response'];m=json.loads((DISC/response).read_text(encoding='utf-8'))['message']
    qsummary.append({'id':q['id'],'platform':'Crossref','returned':len(m['items']),'display_total':m['total-results'],'response':response,'query':q['params'],'interpretation':'relevance search; not Boolean conjunction or title equality'})
    for rank,x in enumerate(m['items'],1):
        doi=x.get('DOI','').lower();reason=exclusions.get(q['id'],{}).get(rank)
        occ.append({'record_id':q['id']+'-'+str(rank).zfill(2),'query_id':q['id'],'platform':'Crossref','rank':rank,'doi':doi,'external_id':doi,'title':'; '.join(x.get('title',[])),'authors':'; '.join(' '.join([a.get('given',''),a.get('family','')]).strip() for a in x.get('author',[])),'type':x.get('type',''),'date':json.dumps(x.get('published',{}).get('date-parts',[])),'abstract_in_export':bool(x.get('abstract')),'title_decision':'exclude_title' if reason else 'await_abstract_or_fulltext','reason':reason or notes.get((q['id'],rank),'Potential mechanism/background/boundary candidate; title insufficient for eligibility'),'formal_inclusion':False,'raw_response':response})
oa_log=json.loads((DISC/'openalex-control-query-log.json').read_text(encoding='utf-8'))
if oa_log.get('status')==200:
    d=json.loads((DISC/oa_log['response']).read_text(encoding='utf-8'))
    qsummary.append({'id':'OA-C','platform':'OpenAlex','returned':len(d['results']),'display_total':d['meta']['count'],'response':oa_log['response'],'query':oa_log['params'],'interpretation':'relevance search; first page only'})
    for rank,x in enumerate(d['results'],1):
        doi=(x.get('doi') or '').removeprefix('https://doi.org/').lower();reason=exclusions['OA-C'].get(rank)
        occ.append({'record_id':'OA-C-'+str(rank).zfill(2),'query_id':'OA-C','platform':'OpenAlex','rank':rank,'doi':doi,'external_id':x['id'],'title':x['title'],'authors':'; '.join(a['author']['display_name'] for a in x.get('authorships',[])),'type':x.get('type',''),'date':x.get('publication_date',''),'abstract_in_export':bool(x.get('abstract_inverted_index')),'title_decision':'exclude_title' if reason else 'await_abstract_or_fulltext','reason':reason or notes.get(('OA-C',rank),'Scope or mechanism requires abstract/full text; no eligibility inferred from title'),'formal_inclusion':False,'raw_response':oa_log['response']})
csvwrite(HERE/'retrieval-occurrences.csv',occ)
groups=collections.defaultdict(list)
for x in occ:groups[x['doi'] or x['external_id']].append(x)
dedup=[]
for n,(key,rs) in enumerate(groups.items(),1):
    decisions=set(x['title_decision'] for x in rs)
    # A less restrictive decision wins a conflict, preserving the record for examination.
    state='await_abstract_or_fulltext' if 'await_abstract_or_fulltext' in decisions else 'exclude_title'
    dedup.append({'candidate_id':'CAL-'+str(n).zfill(3),'identity_key':key,'doi':rs[0]['doi'],'title':rs[0]['title'],'authors':rs[0]['authors'],'occurrences':';'.join(x['record_id'] for x in rs),'title_decision':state,'decision_conflict':len(decisions)>1,'formal_inclusion':False,'note':'DOI-level dedup only; related versions are not automatically merged'})
csvwrite(HERE/'candidate-records.csv',dedup)
old=list(csv.DictReader((HERE.parent/'presearch-2026-11-12/candidate-records.csv').open(encoding='utf-8-sig')))
old_dois={x['doi'].lower() for x in old if x.get('doi')};new_dois={x['doi'] for x in dedup if x['doi']}
save(HERE/'query-summary.json',qsummary)
counts={'stage':'calibration only; NOT PRISMA formal flow','date_local':'2026-11-13 Asia/Shanghai','successful_distinct_calibration_requests':len(qsummary),'crossref_records':sum(x['platform']=='Crossref' for x in occ),'openalex_records':sum(x['platform']=='OpenAlex' for x in occ),'retrieval_occurrences':len(occ),'doi_or_external_id_deduplicated_candidates':len(dedup),'duplicate_occurrences_removed':len(occ)-len(dedup),'unique_title_decisions':dict(collections.Counter(x['title_decision'] for x in dedup)),'occurrence_title_decisions':dict(collections.Counter(x['title_decision'] for x in occ)),'prior_pilot_records':len(old),'overlap_dois_with_prior_pilot':len(old_dois & new_dois),'formal_fulltext_included':0,'note':'Availability probes, web discoveries and six purposive extraction units are separate pools. Do not add these counts as included studies.'}
save(HERE/'flow-counts.json',counts)

# Freeze the previous protocol exactly, in the same directory so links still resolve.
protocol=HERE.parent/'protocol.md';snap=HERE.parent/'protocol-v0.1.snapshot.md'
if not snap.exists():shutil.copyfile(protocol,snap)
save(HERE/'protocol-provenance.json',{'previous_protocol':'../protocol-v0.1.snapshot.md','sha256':hashlib.sha256(snap.read_bytes()).hexdigest(),'same_directory_reason':'Preserve bytes and relative links; current protocol will become0.2','formal_preregistration':False})
print(json.dumps(counts,ensure_ascii=False,indent=2))
