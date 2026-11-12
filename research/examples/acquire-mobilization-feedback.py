"""Targeted supplement on mobilization mechanisms and cumulative advantage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-26'
SOURCES=[
 ('L149-french-raven-1959','The Bases of Social Power','John R.P.French Jr.; Bertram H.Raven','1959original work;target appears a chapter20 reprint,actual edition/pages to inspect','https://gcsetime.com/wp-content/uploads/2023/03/French-Raven-1959-Pdf-As-Psychology.pdf','pdf'),
 ('L150-merton-1968','The Matthew Effect in Science','Robert K.Merton','Science159,1968,56-63;university-hosted copy,target to inspect','https://garfield.library.upenn.edu/merton/matthew1.pdf','pdf'),
 ('L151-salganik-dodds-watts-2006','Experimental Study of Inequality and Unpredictability in an Artificial Cultural Market','Matthew J.Salganik; Peter Sheridan Dodds; Duncan J.Watts','Science311,2006,854-856;author-hosted full file may contain supplement','https://www.princeton.edu/~mjs3/salganik_dodds_watts06_full.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
