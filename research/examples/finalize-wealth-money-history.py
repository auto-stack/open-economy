"""Describe actual versions and reading scope; retain failed and wrong-match files."""
from pathlib import Path
import json, hashlib, csv, datetime
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-20'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

DATA={
'L85-aristotle-politics':('Politics Book I','Aristotle; Benjamin Jowett translation','Ancient work; Internet Classics Archive English translation; underlying edition not fully verified','https://classics.mit.edu/Aristotle/politics.1.one.html','original_selected','Parts VIII-X, especially household provision, use/exchange, coinage and acquisition; not a verified chronology','historical_theory'),
'L86-marx-capital-1867':('Capital Volume I Chapter I excerpt','Karl Marx','First published 1867; 43-page English chapter excerpt hosted by MIT, publication imprint unverified','https://www.mit.edu/~allanmc/marx.capital.1.pdf','original_selected','PDF pp2-3,7-8,27; not the whole volume or a reconstruction of all value forms','conceptual_theory'),
'L87-jevons-political-economy':('The Theory of Political Economy','William Stanley Jevons','First published 1871; Macmillan 1888 third edition; OLL electronic PDF generated September 2011','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/625/Jevons_0237_EBk_v6.0.pdf','original_selected','PDF pp2,46,49,94,108; selected definitions, competition and gains from exchange; not all mathematical derivations','theoretical_model'),
'L88-menger-1892':('On the Origin of Money','Carl Menger; Caroline A. Foley translation','Economic Journal 2(6),239-255 (1892), DOI10.2307/2956146; actual file 2009 Mises reprint, 56 pages','https://cdn.nakamotoinstitute.org/docs/on-the-origins-of-money.pdf','original_selected','PDF pp12,20,24,34-37,52-53; p35 visually inspected; 2009 French foreword excluded','historical_mechanism_theory'),
'L89-innes-1913':('What is Money?','A. Mitchell Innes','Banking Law Journal May 1913; Mosler HTML transcription, not original journal scan','https://moslereconomics.com/mandatory-readings/what-is-money/','original_selected','Opening critique, butcher/baker acknowledgements, debt-credit and clearing passages; historical examples not independently verified','historical_theory'),
'L90-knapp-1924':('The State Theory of Money','Georg Friedrich Knapp','German original 1905; English translation 1924, printed pp1-2 only via Wikisource proofread but not validated transcription','https://en.wikisource.org/wiki/Page:Georg_Freidrich_Knapp_-_The_State_Theory_of_Money_(1924_translation).pdf/18','partial_selected','Wikisource scan pages18-19 = printed pp1-2; no complete PDF or book read','legal_monetary_theory'),
'L91-humphrey-1985':('Barter and Economic Disintegration','Caroline Humphrey','Man New Series20(1):48-72 (1985), DOI10.2307/2802221; 26-page JSTOR copy including cover','https://voidnetwork.gr/wp-content/uploads/2016/09/Barter-and-economic-disintegration-by-Caroline-Humphrey.pdf','original_selected','PDF pp1-4,20-24 = cover and journal pp48-50,66-70; p2 visually inspected; middle fieldwork sections not fully read','ethnographic_research'),
'L92-grierson-origins':('The Origins of Money','Philip Grierson','Lecture and publication dates require edition inspection; search points to 1970 lecture printed1976 and separate catalogue records','https://elaineou.com/wp-content/uploads/2017/01/Grierson-The-Origins-of-Money.pdf','lead_only','No original text read; bibliographic lead only','unread_lead'),
'L93-schmandt-besserat-accounting':('From Accounting to Writing','Denise Schmandt-Besserat','Undated author research webpage; not an original excavation catalogue','https://sites.utexas.edu/dsb/tokens/from-accounting-to-writing/','original_selected','Tokens, Birth of Writing and opening Incised Logographic Tablets passages; accounting interpretation, not proof tokens were money','author_archaeological_synthesis'),
'L94-boe-money-2014':('Money Creation in the Modern Economy','Michael McLeay; Amar Radia; Ryland Thomas','Bank of England Quarterly Bulletin 2014 Q1; local original PDF unavailable','https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2014/money-creation-in-the-modern-economy.pdf','partial_selected','Official summary and PDF tool excerpts opening and pp2-4; balance-sheet explanation and constraints, not full QE analysis','official_institutional_explanation'),
'L95-loc-cuneiform':('About this Collection: Cuneiform Tablets','Library of Congress','Official collection page not obtained','https://www.loc.gov/collections/cuneiform-tablets/about-this-collection/','lead_only','Only discovery snippet; not used as inspected tablet evidence','unread_lead'),
'L96-von-glahn-2005':('The Origins of Paper Money in China — intended chapter not obtained','Richard von Glahn — intended author','Intended The Origins of Value (2005), chapter4 pp65-89; actual downloaded file is a 169-page Money & Art lecture by David Jhave Johnston','https://glia.ca/2014/money-art/pdfs/2_ORIGINS_GE1127_2014.pdf','wrong_match_excluded','Inspected lecture cover and slides109-113 to identify embedded chapter quotes; original chapter not read','excluded_course_slides'),
'L97-cantillon-1755':('Essai sur la nature du commerce en general / Essay on the Nature of Trade in General','Richard Cantillon; Henry Higgs translation','First published1755; actual Higgs translation and other material, Frank Cass1959 reissue; OLL September2011 electronic PDF','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/285/Cantillon_0039_EBk_v6.0.pdf','original_selected','PDF p2 version; p9 Part I Chapter I Of Wealth; appended commentators excluded','historical_theory'),
'L98-khm-ming-banknote':('Banknote — Ming Hongwu, PG25732','Kunsthistorisches Museum Wien, Munzkabinett','Official German collection catalogue; date label ab1374 retained as catalogue claim, not verified first issuance','https://www.khm.at/kunstwerke/banknote-1031339','original_selected','Object title, material, denomination, inventory and inscription transcription; no claim to establish paper money genesis','museum_object_catalogue'),
'L99-vogel-currencies-preview':('Chapter Two — publisher preview, identity not fully verified','Not verified; do not infer from directory name','Brill book identifier9789004236981, chapter003; no readable original acquired','https://brill.com/previewpdf/book/9789004236981/B9789004236981_003.xml','lead_only','Search snippet only; authorship and edition not verified; excluded from substantive claims','unread_lead'),
}

def finalize_metadata():
 p=RAW/'L96-von-glahn-2005/download-response.bin'
 if p.exists():
  d=fitz.open(p)
  assert len(d)==169 and not d.is_repaired
  d.close()
  p.rename(p.with_name('wrong-match-lecture.pdf'))
 p=RAW/'L98-khm-ming-banknote/download-response.bin'
 if p.exists():
  assert b'PG 25732' in p.read_bytes()
  p.rename(p.with_name('original.html'))
 for sid,(title,authors,publication,url,status,scope,evidence) in DATA.items():
  d=RAW/sid;d.mkdir(exist_ok=True)
  mp=d/'metadata.json';old=json.loads(mp.read_text(encoding='utf-8')) if mp.exists() else {}
  originals=list(d.glob('original.*'))
  for p in originals:
   if p.suffix=='.pdf':
    doc=fitz.open(p);assert not doc.is_repaired
    old['pages']=len(doc)
    if not (d/'extracted.txt').exists():
     (d/'extracted.txt').write_text('\n\n'.join(f'===== PDF PAGE {i+1} =====\n'+q.get_text() for i,q in enumerate(doc)),encoding='utf-8')
   elif p.suffix=='.html':
    soup=BeautifulSoup(p.read_bytes(),'html.parser')
    for t in soup(['script','style','nav','footer']):t.decompose()
    if not (d/'extracted.txt').exists(): (d/'extracted.txt').write_text(soup.get_text('\n',strip=True),encoding='utf-8')
  actual=originals[0] if originals else (d/'wrong-match-lecture.pdf' if status=='wrong_match_excluded' else None)
  old.update({'id':sid,'title':title,'authors':authors,'publication':publication,'url':url,
   'research_date_local':'2026-11-12','selection_status':status,'evidence_type':evidence,'read_scope':scope,
   'is_original_of_cited_work':bool(originals),'original_downloaded':bool(originals),
   'download_status':'downloaded_original' if originals else ('partial_tool_text_only' if status=='partial_selected' else ('wrong_document_downloaded' if status=='wrong_match_excluded' else 'failed_or_unread_lead')),
   'format':actual.suffix[1:] if actual else ('partial_web_tool_text' if status=='partial_selected' else 'none'),
   'archived_file':actual.name if actual else ('partial-web-tool-text.txt' if status=='partial_selected' else None),
   'sha256':sha(actual) if actual else (sha(d/'partial-web-tool-text.txt') if status=='partial_selected' else None),
   'version_and_reading_notes':'../../../../research/surveys/02-wealth-money-history/reading-notes.md',
   'rights':'Original rights retained. Local research archive; download does not grant blanket redistribution permission.'})
  if status=='wrong_match_excluded':
   old['actual_download_title']='GE1127 Money & Art: Lecture Origins'
   old['actual_download_author']='David Jhave Johnston'
   old['pages']=169
   doc=fitz.open(actual)
   (d/'extracted-wrong-match.txt').write_text('\n\n'.join(f'===== LECTURE PDF PAGE {i+1} =====\n'+q.get_text() for i,q in enumerate(doc)),encoding='utf-8')
  save(mp,old)
  if not (d/'acquisition-log.json').exists():
   observation={'L96-von-glahn-2005':'Earlier Python requests did not produce complete file. Native curl resumed incomplete ranges; final validated size32587875 bytes,169 unrepaired PDF pages. Actual document is lecture, not intended chapter.',
    'L98-khm-ming-banknote':'Direct request returned200,123466 bytes; HTML includes object PG25732. Browser tool separately returned403.',
    'L99-vogel-currencies-preview':'Web view403; direct requests connect timeout20 seconds; no original file.'}.get(sid,'See discovery tool records.')
   save(d/'acquisition-log.json',[{'research_date_local':'2026-11-12','url':url,'record_type':'reconstructed_observation_from_tool_output','observation':observation}])
 # Reuse keeps prior archives and manifests immutable.
 reused=[]
 for sid,scope in [('L83-smith-1776','New selected reading: BookI II-III openings, IV first4 paragraphs; BookII III first2 paragraphs. Prior BookI I reading retained. No full capital theory read.'),('L84-romer-1990','No new reading; reuse prior PDF pp1-4 and p4 visual check. Not historical-origin evidence.')]:
  d=ROOT/'wiki/raw/round-19'/sid;p=next(d.glob('original.*'))
  reused.append({'id':sid,'original_path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'read_scope_this_round':scope,'research_date_local':'2026-11-12','original_archive_unchanged':True})
 save(RAW/'reuse-reading.json',reused)
 rows=[]
 for sid in DATA:
  m=json.loads((RAW/sid/'metadata.json').read_text(encoding='utf-8'))
  rows.append({k:m.get(k) for k in ['id','title','selection_status','download_status','evidence_type','publication','read_scope','url','sha256']})
 with (ROOT/'research/surveys/02-wealth-money-history/source-matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({'selected_new_originals':sum(v[4]=='original_selected' for v in DATA.values()),'selected_partial':sum(v[4]=='partial_selected' for v in DATA.values()),'excluded_wrong_match':1,'unread_leads':sum(v[4]=='lead_only' for v in DATA.values()),'reused':len(reused)}))

def manifest():
 paths=sorted(p for p in RAW.rglob('*') if p.is_file() and p.name not in ['manifest.json','checksums.sha256'])
 entries=[{'path':p.relative_to(RAW).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
 save(RAW/'manifest.json',{'research_date_local':'2026-11-12','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All files in round-20 except manifest.json and checksums.sha256; includes failures, excluded lecture and partial tool text distinctly labelled','files':entries})
 (RAW/'checksums.sha256').write_text(''.join(f"{e['sha256']}  {e['path']}\n" for e in entries),encoding='utf-8')
 assert all(sha(RAW/e['path'])==e['sha256'] for e in entries)
 print('Manifest verified:',len(entries),'files')

if __name__=='__main__':
 finalize_metadata();manifest()
