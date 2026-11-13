"""Write this batch's descriptive provenance and manifest; never rebuild old ZIPs."""
from pathlib import Path
import csv,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RAW=ROOT/'wiki/raw/round-39'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reuse_specs=[
 ('L03','wiki/raw/round-01/L03-prigogine-1977/original.pdf','PDF2–4 = printed264–266; entropy production and restrictions; previous PDF1–10 reading preserved'),
 ('L05','wiki/raw/round-01/L05-dipaolo-2005/original.pdf','PDF6–8 = printed434–436; conservation and active maintenance critique; previous PDF6–12 reading preserved'),
 ('L06','wiki/raw/round-01/L06-montevil-mossio-2015/original.html','Author HTML sections3–5, dependence/closure definitions; previous sections1–6.1 reading preserved'),
 ('L14','wiki/raw/round-03/L14-bich-et-al/original.pdf','Author manuscript PDF15–18 = manuscript15–18, section5; journal2016 pagination not mapped'),
]
reuse=[]
for sid,path,scope in reuse_specs:
 p=ROOT/path;old=json.loads((p.parent/'metadata.json').read_text(encoding='utf-8'))
 reuse.append({'id':sid,'original_path':path,'sha256':sha(p),'prior_metadata_sha256':old.get('sha256'),'this_round_read_scope':scope,'original_and_prior_metadata_modified':False,'reading_type':'selected passages rechecked; no claim of complete rereading'})
save(RAW/'source-reuse.json',reuse)
specs=[
 ('L195-conant-ashby-1970','Every good regulator of a system must be a model of that system','Roger C. Conant; W. Ross Ashby',
  'journal-scan.pdf','Journal pages90–91,95–96 = PDF3–4,8–9; theorem/conditions visually checked on PDF8–9; university retype used as auxiliary text only',
  'journal scan with publisher cover; original1970, online posting2007 is not original year','downloaded_selected_passages'),
 ('L196-bechtel-bich-2024','Situating homeostasis in organisms: maintaining organization through time','William Bechtel; Leonardo Bich',
  'partial-tool-text.txt','Publisher abstract/abstract-figure text and repository tool excerpts labelled author-copy pages13,15; original PDF unavailable; journal page mapping unverified',
  'tool text only; repository advance-layout pagination differs from final journal6003–6020','partial_tool_text_only'),
 ('L197-cross-hohenberg-1993','Pattern formation outside of equilibrium','M. C. Cross; P. C. Hohenberg',
  'original.pdf','Abstract; I.A opening854; I.D selected858–859; II.A at859; PDF1,4,8–9 selected passages; equation2.1 visually checked PDF9; remaining11 final PDF pages unexamined',
  'University-hosted journal copy273 PDFpages, journal851–1112 maps to first262; not full reading','downloaded_selected_passages'),
 ('L198-eykhoff-1994','Every good regulator of a system must be a model of that system','Pieter Eykhoff',
  'original.pdf','Publisher abstract and visual first page135; authorship/title/original1970 reference checked; other4pages not reviewed; extracted text has DOI only',
  'Publisher5page scanned journal article135–139; separate work, not L195 reprint','downloaded_identity_check_only'),
]
follow=json.loads((RAW/'discovery/followup-retrieval-log.json').read_text(encoding='utf-8'))
for dirname,title,authors,adopted,scope,version,state in specs:
 dest=RAW/dirname;meta=json.loads((dest/'metadata.json').read_text(encoding='utf-8'))
 meta.update(title=title,authors=authors,reading_status=state,reading_scope=scope,adopted_file=adopted,actual_version=version,role='purposive calibration; not formal included study',retraction_or_correction_check='not systematically completed')
 if 'read_scope' in meta:meta.pop('read_scope')
 file=dest/adopted;meta['adopted_file_sha256']=sha(file)
 if file.suffix=='.pdf':
  import fitz
  meta.update(adopted_pdf_pages=len(fitz.open(file)),adopted_bytes=file.stat().st_size)
 if dirname.startswith('L196'):
  meta.update(download_status='original_PDF_not_obtained',pmid='39383321',pmcid='not established; wrong PMC11613639 rejected',provenance_note='EuropePMC known-DOI response says not inPMC; discovery-profile identifiers were not reliable')
 elif dirname.startswith('L195'):
  meta.update(download_status='two_PDF_presentations_obtained',auxiliary_file='original.pdf',auxiliary_version='10-page university retype, NOT publisher page layout',adopted_url='https://theisticscience.com/papers/tree/BioRegulation/Conant-IJSS1970.pdf')
 elif dirname.startswith('L197'):
  meta.update(download_status='downloaded',adopted_url='https://moodle.uni-saarland.de/pluginfile.php/784115/mod_page/content/37/CRO93.pdf',sha256=sha(file),pdf_pages=273,bytes=file.stat().st_size)
 save(dest/'metadata.json',meta)
 save(dest/'read-scope-extension.json',{'id':meta['id'],'date_local':'2026-11-13','status':state,'adopted_file':adopted,'sha256':sha(file),'read_scope':scope,'full_work_read':False,'formal_inclusion':False,'page_render_location':'../inspection (local only)'})
 if dirname.startswith('L198'):
  save(dest/'download-log.json',[{'url':meta['url'],'time_utc':meta['time_utc'],'status':meta.get('status'),'bytes':meta.get('bytes'),'sha256':meta.get('sha256')}])
 extra=[x for x in follow if x.get('source')==dirname]
 if extra:
  logs=json.loads((dest/'download-log.json').read_text(encoding='utf-8')) if (dest/'download-log.json').exists() else []
  # Keep original acquisition records intact; append only once.
  for x in extra:
   if x not in logs:logs.append(x)
  save(dest/'download-log.json',logs)

units=[
 {'id':'L03','type':'lecture/theoretical account','object':'entropy balance and physical stability','support':'boundary exchanges given','maintainer_update':'not explained in selected passages','scope':reuse[0]['this_round_read_scope']},
 {'id':'L197','type':'review/ideal mechanism example','object':'convection pattern','support':'plate geometry and temperature difference imposed','maintainer_update':'apparatus renewal not modeled in selected example','scope':specs[2][4]},
 {'id':'L195','type':'conditional mathematical argument','object':'outcome-distribution entropy','support':'given event sets/map and distribution; admissible conditional distributions','maintainer_update':'regulator production/repair not modeled in proof','scope':specs[0][4]},
 {'id':'L06','type':'conceptual/formal characterization','object':'constraints mutually maintained across scales','support':'open material/energy flows and external constraints retained','maintainer_update':'explicit dependency relations, not measured renewal rates','scope':reuse[2]['this_round_read_scope']},
 {'id':'L14','type':'conceptual mechanism/checklist','object':'endogenous regulatory changes to constitutive regimes','support':'constitutive network produces regulatory subsystem','maintainer_update':'explicit endogenous production; cases not independently tested','scope':reuse[3]['this_round_read_scope']},
 {'id':'L05','type':'conceptual critique','object':'organization conservation vs active viability response','support':'material/energetic openness; no numerical model reconstructed','maintainer_update':'retrospective persistence does not establish adaptive response','scope':reuse[1]['this_round_read_scope']},
]
for x in units:x.update(formal_inclusion=False,full_work_read=False,independent_proof_or_experiment_reproduction=False)
with (HERE/'extraction-units.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(units[0]));w.writeheader();w.writerows(units)

manifest=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(RAW.rglob('*')) if p.is_file() and p.name!='manifest.json']
save(RAW/'manifest.json',manifest)
print(json.dumps({'raw_manifest_entries':len(manifest),'downloaded_PDF_files':len(list(RAW.rglob('*.pdf'))),'extraction_units':len(units),'old_sources_reused':len(reuse)},ensure_ascii=False))
