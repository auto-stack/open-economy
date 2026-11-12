"""Bounded primary-source corpus for influence, conversion and information theory."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-25'
SOURCES=[
 ('L138-dahl-1957','The Concept of Power','Robert A.Dahl','BehavioralScience2(3),1957,201-215;university teaching copy,target identity to inspect','https://www.unc.edu/~fbaum/teaching/articles/Dahl_Power_1957.pdf','pdf'),
 ('L139-parsons-1963','On the Concept of Influence','Talcott Parsons','PublicOpinionQuarterly27(1),1963,37-62;publisher record,not assumed full text','https://academic.oup.com/poq/article-abstract/27/1/37/1816851','html'),
 ('L140-bourdieu-1986','The Forms of Capital','Pierre Bourdieu','1986book chapter,English teaching transcription;actual scope to inspect','https://web.stanford.edu/~eckert/Courses/ParisPapers/Bourdieu1986.pdf','pdf'),
 ('L141-katz-1953','A New Status Index Derived from Sociometric Analysis','Leo Katz','Psychometrika18(1),1953,39-43;verify actual journal pages','https://www.cs.cornell.edu/courses/cs6241/2019sp/readings/Katz-1953-status.pdf','pdf'),
 ('L142-coleman-1972','Systems of Social Exchange','James S.Coleman','JournalMathematicalSociology2(2),1972,145-163;publisher abstract only unless full text obtained','https://www.tandfonline.com/doi/abs/10.1080/0022250X.1972.9989811','html'),
 ('L143-watts-dodds-2007','Influentials, Networks, and Public Opinion Formation','Duncan J.Watts; Peter Sheridan Dodds','JConsumerResearch34(4),2007,441-458','https://pdodds.w3.uvm.edu/research/papers/others/2007/watts2007a.pdf','pdf'),
 ('L144-shalizi-thomas-2010','Homophily and Contagion Are Generically Confounded in Observational Social Network Studies','Cosma Rohilla Shalizi; Andrew C.Thomas','arXiv1004.4704v3,Nov30-Dec1 2010 draft;not automatically2011published version','https://www.stat.cmu.edu/~brian/780/bibliography/01%20homophily%20and%20contagion/shalizi-thomas-homophily-contagion-2011-SMR.pdf','pdf'),
 ('L145-bond-et-al-2012','A 61-million-person experiment in social influence and political mobilization','Robert M.Bond and coauthors','Nature489,2012,295-298;university-hosted article','https://sparq.stanford.edu/sites/g/files/sbiybj19021/files/media/file/bond_et_al._2012_-_a_61-million-person_experiment_in_social_influence_political_mobilization.pdf','pdf'),
 ('L146-schreiber-2000','Measuring Information Transfer','Thomas Schreiber','PhysicalReviewLetters85,2000,461-464;publisher-hosted fulltext','https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.85.461/fulltext','pdf'),
 ('L147-klyubin-polani-nehaniv-2005','Empowerment: A Universal Agent-Centric Measure of Control','Alexander S.Klyubin; Daniel Polani; Chrystopher L.Nehaniv','IEEECEC2005,128-135;author manuscript,actual version to inspect','https://citeseerx.ist.psu.edu/document?doi=ce54273b7e5403bfd71433ac064e66a91acc822c&repid=rep1&type=pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
