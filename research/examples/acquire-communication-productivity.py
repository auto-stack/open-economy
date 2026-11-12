"""Targeted organizational knowledge and AI evidence; physics sources reused."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-27'
SOURCES=[
 ('L152-garicano-2000','Hierarchies and the Organization of Knowledge in Production','Luis Garicano','JPE108(5),2000,874-904;university-hosted article','https://pdodds.w3.uvm.edu/files/papers/others/2000/garicano2000a.pdf','pdf'),
 ('L153-bloom-et-al-2010','The Distinct Effects of Information Technology and Communication Technology on Firm Organization','Nicholas Bloom; Luis Garicano; Raffaella Sadun; John Van Reenen','Initial target ManagementScience2014;actual retrieved author version2010;see final metadata','https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.2014.2013','pdf'),
 ('L154-dellacqua-et-al-2026','Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of AI on Knowledge Worker Productivity and Quality','Fabrizio DellAcqua and coauthors','Initial target HBSWorkingPaper24-013;later official2026partial text;see final metadata','https://www.hbs.edu/ris/Publication%20Files/24-013_d9b45b68-9e74-42d6-a1c6-c72fb70c7282.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
