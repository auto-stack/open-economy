"""Economic leadership,advertising,adaptation and firm governance originals."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
s=importlib.util.spec_from_file_location('b',Path(__file__).with_name('acquire-money-cases.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-31'
SOURCES=[
 ('L166-hermalin-1998','Toward an Economic Theory of Leadership: Leading by Example','Benjamin E.Hermalin','AER88(5),1998,1188-1206;university teaching copy','https://people.duke.edu/~qc2/BA532/1998%20AER%20Hermalin.pdf','pdf'),
 ('L167-aghion-tirole-1997','Formal and Real Authority in Organizations','Philippe Aghion; Jean Tirole','JPE105(1),1997,1-29;university teaching copy','https://people.duke.edu/~qc2/BA532/1997%20JPE%20Aghion%20and%20Tirole.pdf','pdf'),
 ('L168-bagwell-2007','The Economic Analysis of Advertising','Kyle Bagwell','HandbookIndustrialOrganization3,Chapter28,2007;actual file extent to inspect','https://felixmunozgarcia.com/wp-content/uploads/2019/09/ch28_econ_analysis_of_advertising_bagwell.pdf','pdf'),
 ('L169-march-1991','Exploration and Exploitation in Organizational Learning','James G.March','OrganizationScience2(1),1991,71-87','https://hiveresearchlab.org/wp-content/uploads/2013/12/march_1991_exploration_and_exploitation_in_organizational_learning.pdf','pdf'),
 ('L170-hansmann-kraakman-squire-2006','Law and the Rise of the Firm','Henry Hansmann; Reinier Kraakman; Richard Squire','HarvardLawReview119,2006,1333-1403;Yale copy extent to inspect','https://law.yale.edu/sites/default/files/documents/pdf/Faculty/Hansmann_Law_and_the_Rise_of_the_Firm.pdf','pdf'),
 ('L171-anderson-2017-record','Private Government: How Employers Rule Our Lives (and Why We Dont Talk about It)','Elizabeth Anderson','PrincetonUniversityPress2017 publisher record;not book body','https://press.princeton.edu/books/hardcover/9780691176512/private-government','html'),
 ('L172-ferreras-2017-record','Firms as Political Entities: Saving Democracy through Economic Bicameralism','Isabelle Ferreras','Author book record2017;not full book','https://isabelleferreras.net/books/firms-as-political-entities/','html'),
 ('L173-jager-schoefer-heining-2020','Labor in the Boardroom','Simon Jager; Benjamin Schoefer; Jorg Heining','NBERWP26519,2019 revisedAugust2020;not2021QJEtypeset','https://www.nber.org/system/files/working_papers/w26519/w26519.pdf','pdf'),
 ('L174-burdin-2013','Are Worker-Managed Firms Really More Likely to Fail?','Gabriel Burdin','IZADP7412,May2013;not2014journaltypeset','https://repec.iza.org/dp7412.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
