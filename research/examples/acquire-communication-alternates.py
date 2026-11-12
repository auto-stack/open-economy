from pathlib import Path
import importlib.util,json
spec=importlib.util.spec_from_file_location('base',Path(__file__).with_name('acquire-money-cases.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=Path(__file__).resolve().parents[2]/'wiki/raw/round-27'
if __name__=='__main__':
 for s in [
 ('L153-bloom-et-al-2010','The Distinct Effects of Information Technology and Communication Technology on Firm Organization','Bloom; Garicano; Sadun; Van Reenen','Author-hosted PDF;actual HBSWorkingPaper11-023,6September2010','https://raffaellasadun.com/papers/bloom-et-al-2014-it-and-ct-firm-organization.pdf','pdf'),
 ('L154-dellacqua-et-al-2026','Navigating the Jagged Technological Frontier','DellAcqua and coauthors','2026 Organization Science37(2):403-423; target publisher PDF; earlier2023 HBS target failed','https://pubsonline.informs.org/doi/pdf/10.1287/orsc.2025.21838','pdf'),
 ]: print(json.dumps(m.acquire(s)),flush=True)
