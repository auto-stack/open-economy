"""Bounded first-pass corpus for unfair competition, open collaboration and allocation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
spec=importlib.util.spec_from_file_location('base_acquirer',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-23'
SOURCES=[
 ('L116-akerlof-1970','The Market for Lemons: Quality Uncertainty and the Market Mechanism','George A.Akerlof','QJE84(3),1970,488-500; actual version to inspect','https://web.pdx.edu/~nwallace/EHP/AkerlofLemons.pdf','pdf'),
 ('L117-gabaix-laibson-2006','Shrouded Attributes,Consumer Myopia,and Information Suppression in Competitive Markets','Xavier Gabaix; David Laibson','QJE121(2),2006,505-540','https://pages.stern.nyu.edu/~xgabaix/papers/shrouded.pdf','pdf'),
 ('L118-stigler-1971','The Theory of Economic Regulation','George J.Stigler','BellJournal2(1),1971,3-21; teaching-hosted copy','https://publics22.classes.ryansafner.com/readings/Stigler-1971.pdf','pdf'),
 ('L119-nobel-tirole-2014','Jean Tirole: Market Power and Regulation','Economic Sciences Prize Committee','Scientific Background,13October2014','https://www.nobelprize.org/uploads/2018/06/advanced-economicsciences2014-1.pdf','pdf'),
 ('L120-fcic-conclusions-2011','Financial Crisis Inquiry Report: Conclusions','Financial Crisis Inquiry Commission','2011 majority conclusions; not entire report or all dissenting statements','https://fcic-static.law.stanford.edu/cdn_media/fcic-reports/fcic_final_report_conclusions.pdf','pdf'),
 ('L121-sec-ponzi','Ponzi Scheme','SEC Investor.gov','Official educational definition; not case-specific legal advice','https://www.investor.gov/protect-your-investments/fraud/types-fraud/ponzi-scheme','html'),
 ('L122-lerner-tirole-2000','The Simple Economics of Open Source','Josh Lerner; Jean Tirole','NBERWP7600,March2000; actual draft version to inspect','https://www.nber.org/system/files/working_papers/w7600/w7600.pdf','pdf'),
 ('L123-hoffmann-nagle-zhou-2024','The Value of Open Source Software','Manuel Hoffmann; Frank Nagle; Yanuo Zhou','HBSWP24-038; actual version to inspect','https://www.hbs.edu/ris/Publication%20Files/24-038_51f8444f-502c-4139-8bf2-56eb4b65c58a.pdf','pdf'),
 ('L124-shapley-1952','A Value for n-Person Games','Lloyd S.Shapley','RANDP295,1952; not1953book version','https://www.rand.org/content/dam/rand/pubs/papers/2021/P295.pdf','pdf'),
 ('L125-holmstrom-milgrom-1991','Multitask Principal-Agent Analyses: Incentive Contracts,Asset Ownership,and Job Design','Bengt Holmstrom; Paul Milgrom','JLEO7SpecialIssue,1991,24-52','https://web.stanford.edu/~milgrom/publishedarticles/Multitask%20Principal%20Agent.pdf','pdf'),
 ('L126-ftc-ai-partnerships-2025','Partnerships Between Cloud Service Providers and AI Developers','FTC Office of Technology staff','January2025report; data as ofSeptember2024 plus public information throughJanuary2025','https://www.ftc.gov/system/files/ftc_gov/pdf/p246201_aipartnerships6breport_redacted.pdf','pdf'),
 ('L127-scheinkman-xiong-2003','Overconfidence and Speculative Bubbles','Jose A.Scheinkman; Wei Xiong','JPE111(6),2003,1183-1219','https://www.princeton.edu/~wxiong/papers/bubble.pdf','pdf'),
 ('L128-fehr-schmidt-1999','A Theory of Fairness,Competition,and Cooperation','Ernst Fehr; Klaus M.Schmidt','ZurichWP4,1999; actual version to inspect,not automaticallyQJEtypeset','https://www.econ.uzh.ch/static/wp/iewwp004.pdf','pdf'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
