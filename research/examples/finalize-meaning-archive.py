"""Record actual reading scopes and version boundaries for the meaning research."""
from pathlib import Path
import json,hashlib,datetime

root=Path(__file__).resolve().parents[2]/'wiki/raw/round-16'
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tyler={'id':'L75-tyler-2006','title':'Psychological Perspectives on Legitimacy and Legitimation','authors':'Tom R. Tyler','doi':'10.1146/annurev.psych.57.102904.190038','publication':'Annual Review of Psychology 57 (2006),375-400; first online July 8, 2005','research_date_local':'2026-11-12','format':'partial_web_tool_text','original_pdf_downloaded':False,'full_article_archived':False,'source_url':'https://law.huji.ac.il/sites/default/files/law/files/tyler_2006_psychological_perspectives_on_legit_1.pdf','version':'Tool identifies 27-page journal PDF; local requests returned HTML check pages with HTTP 200. Saved tool text is partial, not the PDF.','read_scope':'Web-tool excerpts: PDF pp.1-4 definitions and introduction, relevant parts of pp.16-18 on legitimacy vs morality and normative status. Not the complete review or individual cited experiments.','reading_notes':'../../../../research/reviews/17-reading-notes.md','rights':'Original rights retained; local research archive, not redistribution permission.'}
save(root/'L75-tyler-2006/metadata.json',tyler)
updates={
 'L76-wolf-2007':{'version':'Official HTML transcript of 2007 Tanner lectures; not the 2010 book or its commentaries.','source_type':'philosophical argument','read_scope':'Lecture I opening A False Dichotomy, A Conception of Meaningfulness in Life and subjective/objective elements, Larger-than-Oneself discussion and Lecture I conclusion; final Lecture II paragraphs on objective value and epistemic humility. Not a full reconstruction of Lecture II.'},
 'L77-martela-steger-2016':{'version':'16-page journal typeset PDF including a download cover; article pp.531-545.','source_type':'conceptual theoretical review','read_scope':'PDF pp.2,5-6,8,12. Table 1 on p.5 rendered and visually checked; other sections only located; clinical claims and cited studies not adopted.'},
 'L78-martela-riekki-2018':{'version':'Full publisher HTML of 2018 article, not a later longitudinal study.','source_type':'cross-sectional self-report research on meaningful work','read_scope':'Abstract; Study 1 and 2 Participants and Procedure; Study 2 Work Meaningfulness measure and Interpretation; opening Discussion; causal limitation in contributions section and full Limitations. No regression/SEM reanalysis. Reported sample sizes and exclusion narratives retained without resolving all denominator arithmetic.'},
}
for sid,fields in updates.items():
 p=root/sid/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'));m.update(fields);m['reading_notes']='../../../../research/reviews/17-reading-notes.md';save(p,m)
files=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:continue
 data=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
save(root/'manifest.json',{'research_date_local':'2026-11-12','timezone':'Asia/Shanghai','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_full_originals':3,'full_pdf_originals':1,'full_html_originals':2,'partial_tool_text_sources':1,'originals':[x for x in files if x['path'].endswith('/original.pdf') or x['path'].endswith('/original.html')],'files':files})
print(json.dumps({'files':len(files),'full_originals':3,'partial_tool_text_sources':1}))
