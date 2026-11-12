"""Bounded source acquisition and six-page extension of an existing local scan."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import subprocess
import urllib.request
import fitz

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'wiki/raw/round-37'
DERIVED=ROOT/'wiki/derived/financing-followup-2026-11-12/L190'

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def download(url,target):
    target=RAW/target
    target.parent.mkdir(parents=True,exist_ok=True)
    entry={'url':url,'attempted_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (research archive)'})
        with urllib.request.urlopen(req,timeout=35) as response:
            body=response.read()
            entry.update(final_url=response.url,status=response.status,content_type=response.headers.get('Content-Type'),bytes=len(body))
        target.write_bytes(body)
        entry.update(file=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(body).hexdigest())
    except Exception as e:
        entry.update(error=str(e),status='not_downloaded')
    print(json.dumps(entry,ensure_ascii=False),flush=True)
    return entry

def main():
    logs=[]
    logs.append(download('https://doi.org/10.7916/D8V12FT1','L189-crosscheck/columbia-record.html'))
    logs.append(download('https://www.jstor.org/stable/1802787','L189-crosscheck/jstor-record.html'))
    dump(RAW/'acquisition-attempts.json',logs)
    source=ROOT/'wiki/raw/round-36/L190-holmstrom-tirole-1997/original.pdf'
    DERIVED.mkdir(parents=True,exist_ok=True)
    records=[]
    with fitz.open(source) as doc:
        for number in range(8,14):
            printed=number+661
            stem=f'pdf-{number:02d}-print-{printed}'
            pic=DERIVED/(stem+'.png')
            doc[number-1].get_pixmap(dpi=220,alpha=False).save(pic)
            target=DERIVED/(stem+'.ocr.json')
            subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',
                str(ROOT/'research/tools/ocr-cited-pages.ps1'),'-ImagePath',str(pic),'-OutputPath',str(target)],check=True)
            ocr=json.loads(target.read_text(encoding='utf-8-sig'))
            (DERIVED/(stem+'.raw.txt')).write_text(ocr['text']+'\n',encoding='utf-8')
            records.append({'pdf_page':number,'printed_page':printed,'image':pic.relative_to(ROOT).as_posix(),
                            'ocr':target.relative_to(ROOT).as_posix(),'raw_text':(DERIVED/(stem+'.raw.txt')).relative_to(ROOT).as_posix()})
            print('L190 extension:',number,printed,len(ocr['text']),flush=True)
    dump(RAW/'L190-extension/read-scope-extension.json',{'work_id':'L190','source':source.relative_to(ROOT).as_posix(),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'copied_original':False,
        'new_pages':records,'previous_read_scope':'PDF2–7, printed663–668',
        'new_scope_status':'rendered_and_ocr_completed_visual_review_pending','whole_work_read':False})

if __name__=='__main__': main()
