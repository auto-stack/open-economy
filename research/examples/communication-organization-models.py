"""Finite assumed examples, not empirical estimates or validation of Ordo."""
from pathlib import Path
import math,json

def entropy(ps):
 return -sum(p*math.log2(p) for p in ps if p)

def mutual(joint):
 px={x:sum(p for (a,b),p in joint.items() if a==x) for x,y in joint}
 py={y:sum(p for (a,b),p in joint.items() if b==y) for x,y in joint}
 return sum(p*math.log2(p/(px[x]*py[y])) for (x,y),p in joint.items() if p)

def calculate():
 old=[5,8]; better=[5,8,11]; unchanged=[5,8,7]
 assert set(old)<=set(better) and set(old)<=set(unchanged)
 cases=[('baseline',10,.8,10),('more_messages',100,.8,10),('noisy_load',100,.1,10),('more_processing',100,.8,40)]
 bottleneck=[dict(case=n,R=r,q=q,B=b,expected_useful=q*min(r,b)) for n,r,q,b in cases]
 independent={(0,0):.25,(0,1):.25,(1,0):.25,(1,1):.25}
 copy={(0,0):.5,(1,1):.5}
 information=dict(message_entropy_bits=entropy([.5,.5]),independent_mutual_bits=mutual(independent),copy_mutual_bits=mutual(copy))
 assert [x['expected_useful'] for x in bottleneck]==[8,8,1,32]
 assert information==dict(message_entropy_bits=1,independent_mutual_bits=0,copy_mutual_bits=1)
 return dict(status='checked finite examples; assumed not measured',feasible_sets=dict(old=old,better=better,non_strict=unchanged,old_optimum=max(old),expanded_optimum=max(better),non_strict_optimum=max(unchanged),possible_realized_choice=5),bottleneck=bottleneck,information=information)

if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'surveys/04-influence-and-social-equivalence/communication-model-results.json'
 p.write_text(json.dumps(calculate(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Three finite examples checked; no real-world parameters estimated.')
