"""Three assumed examples; not an estimate of leaders or political systems."""
from pathlib import Path
from math import comb
import json
def majority(n,p):
 return sum(comb(n,k)*p**k*(1-p)**(n-k) for k in range(n//2+1,n+1))
def calculate():
 results=dict(status='finite assumed examples only',matching=dict(independent_equal_choice=.5,shared_convention=1),judgment=dict(n=5,individual_correct=.6,independent_majority=round(majority(5,.6),8),individual_wrong_bias=.4,wrong_biased_majority=round(majority(5,.4),8),perfectly_correlated_majority=.6),direction=[dict(A=a,B=10-a,alignment=abs(a-(10-a))/10,total_result=-10*a+(10-a)) for a in [5,10,0]])
 assert results['judgment']['independent_majority']==.68256
 assert results['judgment']['wrong_biased_majority']==.31744
 assert [x['total_result'] for x in results['direction']]==[-45,-100,10]
 return results
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'surveys/04-influence-and-social-equivalence/leadership-model-results.json'
 p.write_text(json.dumps(calculate(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Three assumed examples checked;no empirical parameters estimated.')
