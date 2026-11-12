"""Finalize provenance for the bounded wealth-emergence reading."""
from pathlib import Path
import json,hashlib,datetime

root=Path(__file__).resolve().parents[2]/'wiki/raw/round-19'
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
updates={
 'L83-smith-1776':{'version':'Project Gutenberg ebook 3300 English transcription of a later text edition; first publication 1776, not a first-edition facsimile.','source_type':'historical primary economic text','read_scope':'Book I Chapter I opening through the paragraph listing dexterity, time saved switching tasks, and machinery as three mechanisms. Not the complete chapter or book; historical quantitative and cross-country claims not adopted.'},
 'L84-romer-1990':{'version':'32-page journal typeset PDF from author site; 1990 JPE article, not 1989 NBER working paper.','source_type':'formal endogenous-growth model','read_scope':'PDF pp.1-4 / journal S71-S74. p.4 rivalry/excludability visually checked. No reconstruction of later equilibrium, welfare or trade proofs; no claim all execution costs are zero or private provision of public goods is universally impossible.'},
}
for sid,fields in updates.items():
 p=root/sid/'metadata.json';m=json.loads(p.read_text(encoding='utf-8'));m.update(fields);m['reading_notes']='../../../../research/reviews/19-reading-notes.md';save(p,m)
files=[]
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:continue
 data=p.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
save(root/'manifest.json',{'date_local':'2026-11-12','timezone':'Asia/Shanghai','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'full_originals':2,'pdf_originals':1,'html_originals':1,'originals':[x for x in files if x['path'].endswith('/original.pdf') or x['path'].endswith('/original.html')],'files':files})
print(json.dumps({'files':len(files),'full_originals':2}))
