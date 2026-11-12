"""Record source boundaries and archive checksums for the bounded AI context audit."""
from pathlib import Path
import json,hashlib,datetime

root=Path(__file__).resolve().parents[2]/'wiki/raw/round-18'
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
updates={
 'L79-acemoglu-restrepo-2019':{'version':'28-page typeset 2019 journal PDF from MIT author site','source_type':'task-based theoretical framework with empirical interpretation','read_scope':'PDF pp.1-2,6-10. p.8 wage-bill identity and effects decomposition rendered and visually checked. Empirical decomposition and appendices not reconstructed.'},
 'L81-brynjolfsson-li-raymond-2025':{'source_type':'primary workplace study of staggered AI assistance deployment','read_scope':'Abstract, selected Introduction, end of III describing assistance and human discretion, IV.A AI Rollout, RCT Analysis and opening Robustness paragraphs, opening VIII Conclusion and generalization caveat. No reanalysis of estimates or all robustness checks.'},
 'L82-ifr-2026':{'version':'Official press release dated September 24, 2026, describing 2025 industrial robot statistics; not the full paid World Robotics report','source_type':'official statistical release','observation_year':2025,'release_date':'2026-09-24','read_scope':'Overview, regional sections and Outlook. Used only for deployment background; forecasts are not observations, and industrial robots are not general-purpose humanoids.'},
}
for sid,fields in updates.items():
 p=root/sid/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'));m.update(fields);m['reading_notes']='../../../../research/reviews/18-reading-notes.md';save(p,m)
save(root/'L80-ilo-2025/metadata.json',{'id':'L80-ilo-2025','title':'Generative AI and Jobs: A Refined Global Index of Occupational Exposure','authors':'Pawel Gmyrek; Janine Berg; Karol Kaminski; Filip Konopczynski; Agnieszka Ladna; Balint Nafradi; Konrad Roslaniec; Marek Troszynski','publication':'ILO Working Paper 140, May 2025; official publication page dated May 20, 2025','research_date_local':'2026-11-12','source_url':'https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure','pdf_url':'https://www.ilo.org/sites/default/files/2025-05/WP140_web.pdf','format':'partial_web_tool_text','original_pdf_downloaded':False,'full_report_archived':False,'version':'Official publication-page description and initial PDF tool excerpt; local page/PDF requests returned 403. Tool record also retains separately identified other opened sources.','read_scope':'Official publication-page research description and author/date fields; only initial PDF cover/licence excerpt. Full methods, tables and appendix not read. Used to distinguish potential task exposure from realized adoption or employment change.','reading_notes':'../../../../research/reviews/18-reading-notes.md','rights':'Original rights retained; the report PDF identifies CC BY 4.0 subject to attribution and third-party terms. This archive contains tool excerpts, not the original PDF.'})
files=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:continue
 data=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
save(root/'manifest.json',{'research_date_local':'2026-11-12','timezone':'Asia/Shanghai','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_original_files':3,'full_pdf_originals':1,'full_html_originals':2,'partial_tool_text_sources':1,'originals':[x for x in files if x['path'].endswith('/original.pdf') or x['path'].endswith('/original.html')],'files':files})
print(json.dumps({'files':len(files),'full_original_files':3,'partial_tool_text_sources':1}))
