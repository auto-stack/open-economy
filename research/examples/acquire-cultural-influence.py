"""Targeted originals for cultural influence; scope and versions finalized separately."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-29'
SOURCES=[
 ('L156-green-brock-2000','The Role of Transportation in the Persuasiveness of Public Narratives','Melanie C.Green; Timothy C.Brock','JPSP79(5),2000,701-721;published article copy','https://weatherhypepodcast.com/uploads/1/0/8/8/10887248/the_role_of_transportation_in_the_persuasiveness_of_public_narratives.pdf','pdf'),
 ('L157-braddock-dillard-2016-record','Meta-analytic evidence for the persuasive effect of narratives on beliefs, attitudes, intentions, and behaviors','Kurt Braddock; James Price Dillard','PennState official research record and abstract;not paper body','https://pure.psu.edu/en/publications/meta-analytic-evidence-for-the-persuasive-effect-of-narratives-on/','html'),
 ('L158-depetris-chauvin-et-al-2020','Building Nations through Shared Experiences: Evidence from African Football','Emilio Depetris-Chauvin; Ruben Durante; Filipe Campante','AER110(5),2020,1572-1602;author-hosted journal copy;2024 correction separate','https://filipecampante.org/wp-content/uploads/2021/07/campante_BuildingNations_May2020.pdf','pdf'),
 ('L159-juslin-vastfjall-2008','Emotional responses to music: The need to consider underlying mechanisms','Patrik N.Juslin; Daniel Vastfjall','BBS31,2008;target article plus possible commentary and response;inspect file','https://www.appstate.edu/~steelekm/classes/psy5150/Documents/Juslin%26Vastfjall2008.pdf','pdf'),
 ('L160-campante-et-al-correction-2024','Correction to Building Nations through Shared Experiences: Evidence from African Football','Filipe Campante; Emilio Depetris-Chauvin; Ruben Durante','November2024 correction;AEA official file','https://www.aeaweb.org/content/file?id=21819','pdf'),
 ('L161-delpeyrou-bertoli-2024','Building Nations through Shared Experiences: Evidence from African Football: a Replication','Leonie Delpeyrou; Simone Bertoli','I4RDiscussionPaper193,2024;repository file','https://www.econstor.eu/bitstream/10419/307961/1/I4R-DP193.pdf','pdf'),
 ('L162-campante-et-al-reply-2024','Building Nations through Shared Experiences: Evidence from African Football: A Reply to Delpeyrou and Bertoli','Filipe Campante; Emilio Depetris-Chauvin; Ruben Durante','I4RDiscussionPaper194,December2024;repository file','https://www.econstor.eu/bitstream/10419/307962/1/I4R-DP194.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
