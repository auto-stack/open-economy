"""Render only the 13 already cited pages; run local OCR without changing raw files."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import fitz

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'wiki/derived/cited-page-text-2026-11-12'
SOURCES = [
    ('L185', 'wiki/raw/round-35/L185-nash-1950/original.pdf', [2,4,5,6], 153),
    ('L189', 'wiki/raw/round-36/L189-stiglitz-weiss-1981/original.pdf', [2,3,4], 391),
    ('L190', 'wiki/raw/round-36/L190-holmstrom-tirole-1997/original.pdf', [2,3,4,5,6,7], 661),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for work, source, pages, offset in SOURCES:
        doc = fitz.open(ROOT/source)
        target = OUT/work
        target.mkdir(exist_ok=True)
        record = dict(work_id=work, source=source, source_sha256=sha(ROOT/source),
                      source_pdf_pages=len(doc), page_scope=[], whole_work_ocr=False)
        for number in pages:
            page = doc[number-1]
            stem = f'pdf-{number:02d}-print-{number+offset}'
            pic = target/(stem+'.png')
            # 220 dpi renders remain within Windows OCR's maximum dimensions.
            pix = page.get_pixmap(dpi=220, alpha=False)
            pix.save(pic)
            raw_json = target/(stem+'.ocr.json')
            subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',
                            str(ROOT/'research/tools/ocr-cited-pages.ps1'),
                            '-ImagePath',str(pic),'-OutputPath',str(raw_json)], check=True,
                           stdout=subprocess.DEVNULL)
            raw = json.loads(raw_json.read_text(encoding='utf-8-sig'))
            # Preserve the recognizer's exact text; corrected reading order is a separate artifact.
            (target/(stem+'.raw.txt')).write_text(raw['text']+'\n',encoding='utf-8')
            record['page_scope'].append(dict(pdf_page=number, printed_page=number+offset,
                image=pic.relative_to(OUT).as_posix(), image_width=pix.width,image_height=pix.height,
                raw_ocr_json=raw_json.relative_to(OUT).as_posix(),
                raw_text=(target/(stem+'.raw.txt')).relative_to(OUT).as_posix(),
                engine=raw['engine'],language=raw['language']))
            print(work, number, number+offset, len(raw['text']), flush=True)
        doc.close()
        records.append(record)
    manifest=dict(created='2026-11-12',status='ocr_completed_visual_verification_pending',
                  engine='Windows.Media.Ocr',os=platform.platform(),render_library=fitz.VersionBind,
                  render_dpi=220,sources=records,originals_modified=False,
                  original_metadata_modified=False,prior_baseline_modified=False)
    (OUT/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()
