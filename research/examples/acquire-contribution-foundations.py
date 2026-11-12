"""Acquire a bounded primary-source corpus on contribution and distribution."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-24'
SOURCES=[
 ('L129-grossman-hart-1986','The Costs and Benefits of Ownership: A Theory of Vertical and Lateral Integration','Sanford J.Grossman; Oliver D.Hart','JPE94(4),1986,691-719; university-hosted article','https://faculty.washington.edu/mfan/is582/articles/GH1986.pdf','pdf'),
 ('L130-alchian-demsetz-1972','Production, Information Costs, and Economic Organization','Armen A.Alchian; Harold Demsetz','AER62(5),1972,777-795; university-hosted article','https://homepage.villanova.edu/peter.zaleski/alchian.pdf','pdf'),
 ('L131-marx-gotha-1875','Critique of the Gotha Programme, Part I','Karl Marx','Written1875; online English translation, edition to inspect','https://www.marxists.org/archive/marx/works/1875/gotha/ch01.htm','html'),
 ('L132-shapley-1953','A Value for n-Person Games','Lloyd S.Shapley','Contributions to the Theory of Games II,1953,307-317; target publisher chapter','https://www.degruyterbrill.com/document/doi/10.1515/9781400881970-018/pdf','pdf'),
 ('L133-ghorbani-zou-2019','Data Shapley: Equitable Valuation of Data for Machine Learning','Amirata Ghorbani; James Zou','ICML2019,PMLR97:2242-2251','https://proceedings.mlr.press/v97/ghorbani19c/ghorbani19c.pdf','pdf'),
 ('L134-niso-credit','Contributor Roles','NISO CRediT','Official role taxonomy and implementation explanation, retrieved2026-11-12','https://credit.niso.org/contributor-roles/','html'),
 ('L135-lazear-1996','Performance Pay and Productivity','Edward P.Lazear','NBERWP5672,July1996; not automatically2000AERversion','https://www.nber.org/system/files/working_papers/w5672/w5672.pdf','pdf'),
 ('L136-clark-1899','The Distribution of Wealth: A Theory of Wages, Interest and Profits','John Bates Clark','Firstpublished1899; online1908edition, selected reading only','https://www.econlib.org/library/Clark/clkDW.html?to_print=true','html'),
 ('L137-ilo-care-2018','Care work and care jobs for the future of decent work: Executive Summary','Laura Addati; Umberto Cattaneo; Valeria Esquivel; Isabel Valarino; ILO','2018 executive summary, not full report','https://www.ilo.org/sites/default/files/wcmsp5/groups/public/%40dgreports/%40dcomm/%40publ/documents/publication/wcms_633166.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
