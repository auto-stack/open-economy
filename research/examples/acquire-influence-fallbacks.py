from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-25'
SOURCES=[
 ('L138-dahl-1957','The Concept of Power','Robert A.Dahl','BehavioralScience2(3),1957,201-215;university teaching copy','https://fbaum.unc.edu/teaching/articles/Dahl_Power_1957.pdf','pdf'),
 ('L146-schreiber-2000','Measuring Information Transfer','Thomas Schreiber','arXivnlin/0001042;actual version to inspect;publisher target failed','https://arxiv.org/pdf/nlin/0001042','pdf'),
 ('L147-klyubin-polani-nehaniv-2005','Empowerment: A Universal Agent-Centric Measure of Control','Alexander S.Klyubin; Daniel Polani; Chrystopher L.Nehaniv','IEEECEC2005,128-135;university archive PDF','https://uhra.herts.ac.uk/id/eprint/282/1/901241.pdf','pdf'),
 ('L148-stevens-1946','On the Theory of Scales of Measurement','S.S.Stevens','Science103(2684),1946,677-680;teaching copy,target identity to inspect','https://marces.org/EDMS623/Stevens%20SS%20(1946)%20On%20the%20Theory%20of%20Scales%20of%20Measurement.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
