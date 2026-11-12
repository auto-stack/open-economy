from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-23'
SOURCES=[
 ('L119-nobel-tirole-2014','2014 Economics Prize: Press release','Royal Swedish Academy of Sciences','13 October 2014 press release; different from attempted scientific background','https://www.nobelprize.org/prizes/economic-sciences/2014/press-release/','html'),
 ('L121-sec-ponzi','Ponzi Scheme','SEC Investor.gov','Official educational webpage, retrieved 2026-11-12','https://www.investor.gov/protect-your-investments/fraud/types-fraud/ponzi-scheme?research=1','html'),
 ('L124-shapley-1952','A Value for n-Person Games','Lloyd S.Shapley','RANDP295,1952; not1953book version','https://www.rand.org/content/dam/rand/pubs/papers/2021/P295.pdf?download=1','pdf'),
 ('L126-ftc-ai-partnerships-2025','Partnerships Between Cloud Service Providers and AI Developers','FTC Office of Technology staff','January2025report,43pages','https://search.ftc.gov/system/files/ftc_gov/pdf/p246201_aipartnerships6breport_redacted.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
