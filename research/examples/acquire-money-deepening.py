"""Acquire targeted Chinese paper-money and Athenian coinage evidence."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('money_cases_acquirer',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=ROOT/'wiki/raw/round-22'
SOURCES=[
 ('L110-songchaoshishi-15','宋朝事實 卷15 四库本电子转录','李攸；Wikisource transcription','Song-period compilation, actual transcription/version to inspect','https://zh.wikisource.org/zh-hant/宋朝事實_(四庫全書本)/卷15','html'),
 ('L111-guan-palma-wu-yuan','The rise and fall of paper money in Yuan China,1260-1368','Hanhui Guan; Nuno Palma; Meng Wu','Economic History Review DOI10.1111/ehr.13305; actual accepted manuscript with appendix','https://pure.manchester.ac.uk/ws/portalfiles/portal/282385467/Paper_money_in_Yuan_China_withappendix.pdf','pdf'),
 ('L112-kroll-agora-1993','The Greek Coins,The Athenian Agora XXVI','John H.Kroll; contributions Alan S.Walker','American School of Classical Studies at Athens,1993','https://www.ascsa.edu.gr/uploads/media/oa_ebooks/oa_agora/Agora_XXVI.pdf','pdf'),
 ('L113-stroud-silver-law-1974','An Athenian Law on Silver Coinage','Ronald S.Stroud','Hesperia43(2),1974,157-188; JSTOR147454','https://www.ascsa.edu.gr/uploads/media/hesperia/147454.pdf','pdf'),
 ('L114-thucydides-2-13','History of the Peloponnesian War 2.13','Thucydides; Charles Foster Smith translation','1919-1923 translation; Perseus First1KGreek electronic edition','https://beta.perseus.tufts.edu/urn:cts:greekLit:tlg0003.tlg001.1st1K-eng1/chapter:2.13/','html'),
 ('L115-jianyan-zaji-16','建炎以來朝野雜記 甲集卷16','李心传；识典古籍电子转录','Southern Song compilation; electronic edition/version pending inspection','https://www.shidianguji.com/zh/book/NGJ89241199902323041725/chapter/1lq15sq2irrxi','html'),
]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(m.acquire,SOURCES):print(json.dumps(r),flush=True)
