from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-24'
SOURCES=[
 ('L129-grossman-hart-1986','The Costs and Benefits of Ownership: A Theory of Vertical and Lateral Integration','Sanford J.Grossman; Oliver D.Hart','JPE94(4),1986,691-719; researcher-hosted article, identity to inspect','https://www.edegan.com/pdfs/Grossman%20Hart%20%281986%29%20-%20The%20Costs%20and%20Benefits%20of%20Ownership.pdf','pdf'),
 ('L131-marx-gotha-1875','Critique of the Gotha Programme, Part I','Karl Marx','Written1875; mirror of Marxists Internet Archive English translation,selectedPartI','https://www.dhspriory.org/kenny/PhilTexts/Marx/www.marxists.org/archive/marx/works/1875/gotha/ch01.htm','html'),
 ('L136-clark-1899','The Distribution of Wealth: A Theory of Wages, Interest and Profits','John Bates Clark','OLL electronic edition of historic book,actual edition to inspect','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/329/Clark_0190_EBk_v6.0.pdf','pdf'),
 ('L137-ilo-care-2018','Care work and care jobs for the future of decent work: Executive Summary','Laura Addati; Umberto Cattaneo; Valeria Esquivel; Isabel Valarino; ILO','2018 executive summary,mirror of ILO text,not full report','https://www.right-to-education.org/sites/right-to-education.org/files/resource-attachments/ILO_report_Care_work_2018_0.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
