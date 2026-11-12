"""Finalize round25 scopes and provenance without changing old theory records."""
from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-25';SUR=ROOT/'research/surveys/04-influence-and-social-equivalence'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j=json.loads((RAW/'discovery/web-records.json').read_text(encoding='utf-8'))
for sid,batch,needle in [
 ('L139-parsons-1963',2,'ON THE CONCEPT OF INFLUENCE ('),
 ('L142-coleman-1972',2,'Systems of social exchange (')]:
    s=str(j['searches'][batch]['result']);pos=s.find(needle);assert pos>=0
    part=s[pos:].split('--------------------------------------------------------------------------------')[0]
    (RAW/sid/'web-tool-text.partial.txt').write_text('OFFICIAL PUBLISHER ABSTRACT/CATALOGUE AS RETURNED BY SEARCH TOOL,NOT ORIGINAL HTML OR FULL ARTICLE.\n'+part,encoding='utf-8')
save(RAW/'L139-parsons-1963/translation-record-request.json',{
 'url':'https://revistamexicanadesociologia.unam.mx/index.php/rms/article/view/58841',
 'date_local':'2026-11-12','status':'connect_timeout','connect_timeout_seconds':8,
 'scope':'Record-page request failed before any response was archived;Spanish1964article body not obtained or read;web attempts separately recorded.'})
scopes={
 'L138':('adopted_targeted_pdf','PDF1-4,printed201-204;PDF3 visually inspected;not all comparability arguments or Senate analysis.','BehavioralScience2(3),1957,201-215;15page university teaching scan.'),
 'L139':('abstract_only_context','Official publisher abstract and bibliography via search batch3;no body or original HTML;UNAM1964translation not read.','PublicOpinionQuarterly27(1),1963,37-62;DOI10.1086/267148;not full generalized-medium theory reading.'),
 'L140':('adopted_targeted_pdf','PDF1-2,8,11-12;PDF12 visually inspected;PDF9 browsed only;includes explicit universal-labor-time and conservation analogy,not physically validated.','18page English teaching reformat of The Forms of Capital,1986,Richardson-edited handbook;not original page-layout scan.'),
 'L141':('adopted_targeted_pdf','PDF1-5 definitions,conditions and example;PDF1 visually resolves OCR89as39;not independent recomputation of all original normalizers.','Psychometrika18(1),1953,39-43;5page teaching scan.'),
 'L142':('abstract_only_context','Official publisher abstract and bibliography via search batch3;no full model or equilibrium proof.','JournalMathematicalSociology2(2),1972,145-163;DOI10.1080/0022250X.1972.9989811;2010online date not original publication.'),
 'L143':('adopted_targeted_pdf','PDF1,3-4,15;selected threshold/network model and discussion;not all simulation sections or independent reproduction.','JConsumerResearch34(4),2007,441-458;18pages;simulation study not population prevalence evidence.'),
 'L144':('adopted_targeted_pdf','PDF1,6-7 section2.1 and causal-graph argument;not all subsequent examples or simulations.','arXiv1004.4704v3 stamp30Nov2010,lastLATEX1Dec2010,27pages;path2011doesnot make it final journal typeset.'),
 'L145':('adopted_targeted_pdf','PDF1-2 andPDF4discussion;PDF3estimation/discussion browsed,SI not obtained or independently checked;PDF2Figure1 visual inspection.','Nature489,2012,295-298,4pages;study2Nov2010;full randomized users differ from6.3million matched voting subset.'),
 'L146':('adopted_targeted_pdf','PDF1intro selections,PDF2definition and conditioning,PDF4common-driver caveat and conclusion;PDF2visually inspected;not numerical reproduction.','arXivnlin/0001042v1 stamp19Jan2000,4pages;titledate26Nov2024also visible,reason not verified;not downloaded PRL typeset.'),
 'L147':('adopted_targeted_pdf','PDF1-4selected intro,channel,sections2.2-2.3;PDF3visually inspected;not subsequent full evolution experiments.','IEEECEC2005,128-135,8page university-hosted proceedings copy;repository2025/2026timestamps not publication dates.'),
 'L148':('unread_lead_only','Failed teaching-copy acquisition;no substantive original reading or table adopted.','Stevens1946Science103(2684):677-680,measurement-theory lead only.'),
}
rows=[]
for p in sorted(RAW.glob('L*/metadata.json')):
    m=json.loads(p.read_text(encoding='utf-8'));status,scope,version=scopes[m['id'][:4]]
    m.update({'selection_status':status,'read_scope':scope,'actual_version':version,'knowledge_base_status':'raw and provenance archived;not yet converted/imported into AutoDown'})
    if m.get('original_downloaded'):m['download_status']='original_archived_identity_checked'
    elif (p.parent/'web-tool-text.partial.txt').exists():m['download_status']='original_failed_abstract_tool_text_only'
    else:m['download_status']='original_failed_unread_lead'
    m['source_files']=[{'file':q.name,'bytes':q.stat().st_size,'sha256':digest(q)} for q in sorted(p.parent.iterdir()) if q.name.startswith(('original.','web-tool-text.'))]
    save(p,m);rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','download_status','read_scope','url']})
with (SUR/'source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
contexts=[
 ('theory-register','shared/theory-register.md','Working Ordo HYP01 status and definitions;no new stable theory entry in this round.'),
 ('Q3-review','research/reviews/04-measures-and-bridges.md','Prior distinction between entropy,information,task capacity and value;project review,not new physical evidence.'),
 ('H02','wiki/raw/round-09/H02-open-business-dialogue/conversation.md','Historical user design context and prior Q8 reading;not new instructions or operating evidence.'),
]
save(RAW/'reuse-context.json',[{'id':sid,'path':path,'bytes':(ROOT/path).stat().st_size,'sha256':digest(ROOT/path),'scope':scope} for sid,path,scope in contexts])
files=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(RAW.rglob('*')) if p.is_file() and p.name not in ['manifest.json','checksums.sha256']]
save(RAW/'manifest.json',{'date':'2026-11-12','scope':'All round25 files except manifest/checksums;old project-context digests listed separately','files':files})
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
print(json.dumps({'original_pdfs':len(list(RAW.glob('L*/original.pdf'))),'abstract_only_sources':2,'unread_leads':1,'project_context_files':3,'manifest_files':len(files)}))
