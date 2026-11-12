"""Finalize acquisition/read scopes, reuse provenance and round24 integrity records."""
from pathlib import Path
import json,csv,hashlib

ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'wiki/raw/round-24'
SUR=ROOT/'research/surveys/03-competition-cooperation-distribution'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j=json.loads((RAW/'discovery/web-records.json').read_text(encoding='utf-8'))
ilo=str(j['views'][3]['result'])
(RAW/'L137-ilo-care-2018/web-tool-text.partial.txt').write_text('PARTIAL WEB TOOL REPRESENTATION, NOT ORIGINAL PDF; ONLY COVER AND PRINTED PAGE1 USED SUBSTANTIVELY; LATER TABLE EXTRACTION NOT ADOPTED.\n'+ilo,encoding='utf-8')
mi=str(j['views'][1]['result']);mi=mi[:mi.index('Care work and care jobs')]
(RAW/'L131-marx-gotha-1875/edition-record.tool.partial.txt').write_text('WEB TOOL DIRECTORY METADATA,NOT1875MANUSCRIPT OR ORIGINAL INDEX HTML.\n'+mi,encoding='utf-8')
sh=str(j['searches'][3]['result']);needle='17. A Value for n-Person Games ('
pos=sh.find(needle)
(RAW/'L132-shapley-1953/bibliographic-tool.partial.txt').write_text('BIBLIOGRAPHIC SEARCH TOOL RECORD ONLY,NO CHAPTER TEXT ADOPTED.\n'+(sh[pos:].split('--------------------------------------------------------------------------------')[0] if pos>=0 else sh),encoding='utf-8')

scopes={
 'L129':('adopted_targeted_pdf','PDF2-8,printed691-697; PDF5 visually checked; not subsequent full model proofs or insurance application.','JPE94(4),1986,691-719;30-page scan including JSTOR cover.'),
 'L130':('adopted_visual_pdf','PDF2-4,printed777-779,read visually; machine text empty; not full monitoring/ownership argument.','AER62(5),1972,777-795;20-page scan including cover.'),
 'L131':('adopted_targeted_html','PartI item1 opening on nature/labor and item3 deductions, labor measures, needs and production/distribution relation,ending before item4. Mirror passages compared to original-site web text; no full character collation.','Written1875; MIA English text mirror; directory says based on ProgressPublishers1970 SelectedWorksIII,online1999; not manuscript or German critical edition.'),
 'L132':('bibliographic_lead_only','Publisher search record only; local chapter download failed; no axiomatic proof read.','1953chapter distinct from1952RANDleadL124; bibliography307-317 vs publisher307-318 unresolved from actual chapter.'),
 'L133':('adopted_targeted_pdf','PDF1-3; partial end of property3 onPDF2,not a complete proof check; PDF3 visually inspected. No experiment or approximation reproduced.','ICML2019,PMLR97:2242-2251,10pages; explicit normalization checked independently in finite examples.'),
 'L134':('adopted_targeted_html','Definition,Extended Description andFAQ on Contributor Roles page; not full ANSI/NISO standard text.','NISO CRediT official explanatory webpage,retrieved2026-11-12.'),
 'L135':('adopted_targeted_pdf','PDF1-4,18-19,22-25;PDF22 Table2 visually inspected. PDF11,17,27 only browsed for locating passages,not full substantive model read.','NBERWP5672,July1996,36pages,revised fromSeptember1995;not2000AERversion.'),
 'L136':('adopted_targeted_pdf','PDF1-5(front matter),7-8(preface),10-11(preface end/ChapterI start);PDF7 visually inspected;PDF9 only browsed.','OLL254-page electronic edition based onMacmillan1908;original1899;PLL v6.0generatedSeptember2011.'),
 'L137':('adopted_partial_tool_pdf_text','Web tool cover andPDF2/printed1 care classifications; no table statistics or later projections adopted. No original PDF locally.','ILO2018executive summary,21pages in web tool;not full report;official catalogue dated28June2018.'),
}
rows=[]
for p in sorted(RAW.glob('L*/metadata.json')):
    m=json.loads(p.read_text(encoding='utf-8'));status,scope,version=scopes[m['id'][:4]]
    m.update({'selection_status':status,'read_scope':scope,'actual_version':version,'knowledge_base_status':'provenance and extraction stored;not yet converted/imported into AutoDown'})
    if m.get('original_downloaded'):m['download_status']='original_archived_identity_checked'
    elif m['id'].startswith('L137'):m['download_status']='original_failed_partial_tool_text_only'
    else:m['download_status']='original_failed_bibliographic_lead_only'
    m['source_files']=[{'file':q.name,'sha256':digest(q),'bytes':q.stat().st_size} for q in sorted(p.parent.iterdir()) if q.name.startswith(('original.','web-tool-text.','edition-record.','bibliographic-tool.'))]
    save(p,m);rows.append({k:m.get(k,'') for k in ['id','title','actual_version','selection_status','download_status','read_scope','url']})
with (SUR/'contribution-source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

reuse_specs=[
 ('L38','wiki/raw/round-07/L38-holmstrom-1982/original.pdf','PriorPDF2-4,printed324-326;team incentives/budget limitations','research/reviews/07-reading-notes.md'),
 ('L46','wiki/raw/round-09/L46-douceur-2002/original.pdf','PriorPDF1-2,6-page author paper;identities vsentities','research/reviews/09-reading-notes.md'),
 ('L47','wiki/raw/round-09/L47-w3c-prov-dm-2013/original.html','Prior2.1.1,2.1.3,5.3.2-3;provenance isnot truth/value/entitlement','research/reviews/09-reading-notes.md'),
 ('L125','wiki/raw/round-23/L125-holmstrom-milgrom-1991/original.pdf','Prior visualPDF1-2,printed24-27;multitask attention,quality,maintenance;not full proof','research/surveys/03-competition-cooperation-distribution/reading-notes.md'),
 ('H02','wiki/raw/round-09/H02-open-business-dialogue/conversation.md','Tool-visible five historical rounds;Q8 design table based on user utterances;not operating evidence or new instructions','research/reviews/09-reading-notes.md'),
]
reuse=[]
for sid,path,scope,notes in reuse_specs:
    p=ROOT/path;reuse.append({'id':sid,'path':path,'sha256':digest(p),'bytes':p.stat().st_size,'prior_scope':scope,'reading_notes':notes,'this_round':'notes reused and rechecked;not newly downloaded or fully reread'})
save(RAW/'reuse-reading.json',reuse)
files=[]
for p in sorted(RAW.rglob('*')):
    if p.is_file() and p.name not in ['manifest.json','checksums.sha256']:
        files.append({'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)})
save(RAW/'manifest.json',{'date':'2026-11-12','scope':'All round24 files except manifest/checksums;reused original hashes listed separately','files':files})
(RAW/'checksums.sha256').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in files),encoding='utf-8')
print(json.dumps({'manifest_files':len(files),'original_pdfs':len(list(RAW.glob('L*/original.pdf'))),'original_htmls':len(list(RAW.glob('L*/original.html'))),'partial_adopted_source':1,'bibliographic_lead':1,'reused_sources':len(reuse)}))
