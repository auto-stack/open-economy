from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-30'
SOURCES=[
 ('L163-couzin-et-al-2005','Effective leadership and decision-making in animal groups on the move','Iain D.Couzin; Jens Krause; Nigel R.Franks; Simon A.Levin','Nature433,2005,513-516;university-hosted article','https://hal.elte.hu/~vicsek/downloads/papers/Couzinetal2005.pdf','pdf'),
 ('L164-lorenz-et-al-2011','How social influence can undermine the wisdom of crowd effect','Jan Lorenz; Heiko Rauhut; Frank Schweitzer; Dirk Helbing','PNAS108(22),2011,9020-9025;ETH-hosted article','https://www.sg.ethz.ch/publications/2011/lorenz2011how-social-influence/PNAS-2011-Lorenz-9020-5.pdf','pdf'),
 ('L165-list-elsholtz-seeley-2009','Independence and interdependence in collective decision making: an agent-based model of nest-site choice by honeybee swarms','Christian List; Christian Elsholtz; Thomas D.Seeley','PhilTransRSocB364,2009,755-762;repository copy;inspect actual file','https://citeseerx.ist.psu.edu/document?doi=c1e65d684ae1c179e447dac17bfc981aa53eef97&repid=rep1&type=pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
