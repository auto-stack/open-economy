"""Scoped sources on energetic support,technological leverage and cultural accumulation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
s=importlib.util.spec_from_file_location('b',Path(__file__).with_name('acquire-money-cases.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-32'
SOURCES=[
 ('L175-lotka-1922','Contribution to the Energetics of Evolution','Alfred J.Lotka','PNAS8,1922,147-151;actual file extent to inspect;historic hypothesis not physical axiom','https://www.sustainable.soltechdesigns.com/lotka1922.pdf','pdf'),
 ('L176-arthur-2007','The Structure of Invention','W.Brian Arthur','ResearchPolicy36,2007,274-287;author institute copy','https://sites.santafe.edu/~wbarthur/Papers/Invention-Arthur.pdf','pdf'),
 ('L177-bresnahan-trajtenberg-1992','General Purpose Technologies: Engines of Growth?','Timothy F.Bresnahan; Manuel Trajtenberg','NBERWP4148,August1992;not1995journalversion','https://www.nber.org/system/files/working_papers/w4148/w4148.pdf','pdf'),
 ('L178-david-1990','The Dynamo and the Computer: An Historical Perspective on the Modern Productivity Paradox','Paul A.David','AER80(2),1990,355-361;third-party copy of original article','https://gwern.net/doc/economics/automation/1990-david.pdf','pdf'),
 ('L179-boyd-richerson-henrich-2011','The Cultural Niche: Why Social Learning Is Essential for Human Adaptation','Robert Boyd; Peter J.Richerson; Joseph Henrich','PNAS2011;author hosted version extent/page numbers to inspect','https://scholar.harvard.edu/files/henrich/files/boyd_richerson_henrich_2011-2.pdf','pdf'),
 ('L180-mokyr-lever-of-riches-preview','The Lever of Riches: Technological Creativity and Economic Progress: publisher preview','Joel Mokyr','1990firstpublication,1992paperback;preview not full book','https://api.pageplace.de/preview/DT0400.9780199762712_A23609510/preview-9780199762712_A23609510.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
