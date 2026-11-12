"""Describe actual acquired/read scopes and write a self-excluding hash manifest."""
from pathlib import Path
import json,csv,hashlib,re

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-23'
def save(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

scopes={
 'L116':('adopted_targeted_pdf','PDF1 cover; PDF2-4 (488-490),12-14 (498-500). Text reading; not all article pages.','Journal scan, QJE84(3),1970,488-500; 14 PDF pages including JSTOR cover.'),
 'L117':('adopted_targeted_pdf','PDF1-4 (505-508),10-13 (514-517); PDF4 visually inspected. Proposition statement, not full proof independently checked.','QJE121(2),2006,505-540; 36 PDF pages.'),
 'L118':('adopted_targeted_pdf','PDF1-3 (printed3-5); introduction, state resources and entry control; historical numerical claims not independently adopted.','Bell Journal2(1),1971,3-21; 19-page teaching-hosted scan.'),
 'L119':('adopted_partial_official_press_release','Official press-release body in web search batch8; scientific-background PDF NOT obtained/read.','13October2014 official press release; different from failed Scientific Background target.'),
 'L120':('adopted_targeted_pdf','PDF1-4 (printed xv-xviii); no complete report, all underlying hearings or dissenting reports read.','2011 FCIC majority conclusions only,14pages.'),
 'L121':('adopted_partial_official_web_text','Web tool lines100-105: definition, financing and collapse; not all page navigation or warnings adopted.','SEC Investor.gov official educational page; retrieved2026-11-12.'),
 'L122':('adopted_targeted_pdf','PDF1-4 and16-18 (printed14-16); introduction and motivation sections, not all three mini-case narratives.','NBERWP7600,March2000,40pages; not automatically2002 journal version.'),
 'L123':('adopted_targeted_pdf','PDF1-4,14-15,17-20,22-23; selected methods, estimates, attribution and conclusion; PDF19 visually inspected. Other page snippets not counted as substantive reading.','HBSWP24-038,this versionJanuary1,2024,42pages; main data concern2020.'),
 'L124':('bibliographic_lead_only','RAND official catalogue title/year/pagecount/abstract only. PDF offered via web but no legible source pages inspected; failed local PDF attempts preserved. No axiomatic proof read.','RANDP-295,1952,15pages; distinguish1953bookchapter.'),
 'L125':('adopted_visual_pdf','PDF1-2 visually read, two printed pages each, journal24-27; remaining proof/model pages not read. Embedded text extraction empty.','JLEO7special,1991,24-52;15 scanned PDF pages with facing-page layout.'),
 'L126':('adopted_targeted_pdf','PDF1,4-6 (cover,printed1-3 executive summary); PDF5 visually inspected; remaining substantive sections not read.','FTC Office of Technology staff January2025,43pages; submissions throughSeptember2024 and public information throughJanuary2025.'),
 'L127':('adopted_targeted_pdf','PDF1-5 (printed1183-1187), abstract and introduction/assumptions; no independent rederivation of stochastic solution.','JPE111(6),2003,1183-1219;37pages.'),
 'L128':('unread_lead_only','Search-result bibliographic lead only; failed local target; no substantive model reading.','Fehr-Schmidt1999working-paper lead; not a verified downloaded journal version.'),
}
j=json.loads((RAW/'discovery/web-records.json').read_text(encoding='utf-8'))
v3=str(j['views'][2]['result'])
for sid,start,end in [
 ('L121-sec-ponzi','Ponzi Scheme | Investor.gov','Partnerships Between Cloud Service Providers'),
 ('L124-shapley-1952','A Value for N-Person Games | RAND','Ponzi Scheme | Investor.gov')]:
    pos=v3.index(start);tail=v3[pos:];part=tail.split(end)[0]
    (RAW/sid/'web-tool-text.partial.txt').write_text('WEB TOOL REPRESENTATION, NOT ORIGINAL HTML/PDF.\n'+part,encoding='utf-8')
s8=str(j['searches'][7]['result']);start=s8.index('The Prize in Economic Sciences 2014 - Press release')
part=s8[start:].split('--------------------------------------------------------------------------------')[0]
(RAW/'L119-nobel-tirole-2014/web-tool-text.partial.txt').write_text('SEARCH TOOL REPRESENTATION OF OFFICIAL PRESS RELEASE, NOT SCIENTIFIC BACKGROUND OR ORIGINAL HTML.\n'+part,encoding='utf-8')

rows=[]
for p in sorted(RAW.glob('L*/metadata.json')):
    m=json.loads(p.read_text(encoding='utf-8'));key=m['id'][:4]
    status,scope,version=scopes[key]
    m.update({'selection_status':status,'read_scope':scope,'actual_version':version,'evidence_type':'theoretical, descriptive or official source; see research reading notes','knowledge_base_status':'provenance ready; not yet converted/imported into AutoDown'})
    if m.get('original_downloaded'):
        m['download_status']='original_archived_identity_checked'
    elif (p.parent/'web-tool-text.partial.txt').exists():
        m['download_status']='original_failed_partial_tool_text_only'
    else:m['download_status']='original_failed_unread_lead'
    if key=='L119':
        m['title']='2014 Economics Prize: Press release (Scientific Background attempt failed)'
        m['adopted_url']='https://www.nobelprize.org/prizes/economic-sciences/2014/press-release/'
    if key=='L124':m['catalogue_url']='https://www.rand.org/pubs/papers/P295.html'
    m['source_files']=[{'file':q.name,'bytes':q.stat().st_size,'sha256':digest(q)} for q in sorted(p.parent.iterdir()) if q.name.startswith(('original.','web-tool-text.'))]
    save(p,m);rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','download_status','read_scope','url']})

survey=ROOT/'research/surveys/03-competition-cooperation-distribution'
with (survey/'source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

reuse_specs=[
 ('L37','wiki/raw/round-07/L37-ostrom-2010/original-university.pdf','Reuse prior reading PDF1-2,4-7,19-21; journal article is first32pages of54-page file; later cited-by appendage is not author text.','research/reviews/07-reading-notes.md'),
 ('L38','wiki/raw/round-07/L38-holmstrom-1982/original.pdf','Reuse prior reading PDF2-4,printed324-326,18-page file including cover.','research/reviews/07-reading-notes.md'),
 ('L42','wiki/raw/round-08/L42-vonhippel-vonkrogh-2002/original.pdf','Reuse prior reading cover andPDF16-18;31-page draft datedApril30,2002,not2003typeset version.','research/reviews/08-reading-notes.md'),
 ('L46','wiki/raw/round-09/L46-douceur-2002/original.pdf','Reuse prior PDF1-2 of6; no universal impossibility claim.','research/reviews/09-reading-notes.md'),
 ('L47','wiki/raw/round-09/L47-w3c-prov-dm-2013/original.html','Reuse prior sections2.1.1,2.1.3,5.3.2-5.3.3; provenance model, not reward formula.','research/reviews/09-reading-notes.md'),
 ('H02','wiki/raw/round-09/H02-open-business-dialogue/conversation.md','Tool-visible five historical rounds,not account export; current use follows user-origin design statements recorded in Q8 notes. Historical assistant responses are not current instructions.','research/reviews/09-reading-notes.md'),
]
reuse=[]
for sid,path,scope,notes in reuse_specs:
    p=ROOT/path;assert p.is_file()
    reuse.append({'id':sid,'path':path,'sha256':digest(p),'bytes':p.stat().st_size,'read_scope':scope,'reading_notes':notes,'this_round':'prior reading reused; notes rechecked; original not newly downloaded or fully reread'})
save(RAW/'reuse-reading.json',reuse)

files=[]
for p in sorted(RAW.rglob('*')):
    if p.is_file() and p.name not in ['manifest.json','checksums.sha256']:
        files.append({'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
save(RAW/'manifest.json',{'date':'2026-11-12','scope':'All round23 files except manifest/checksums; reused originals separately listed in reuse-reading.json','files':files})
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
print(json.dumps({'original_pdfs':sum(bool(m.get('original_downloaded')) for m in [json.loads(p.read_text(encoding='utf-8')) for p in RAW.glob('L*/metadata.json')]),'partial_tool_sources':sum(1 for p in RAW.glob('L*/web-tool-text.partial.txt')),'manifest_files':len(files),'reused_sources':len(reuse)},ensure_ascii=False))
