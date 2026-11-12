"""Finite illustrations of context dependence and information/causal distinctions."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from math import log2
from pathlib import Path
import json

def cmi(joint):
    # Tuples are (X,Y,conditioning state); exact probabilities, floating logarithms.
    pxz=defaultdict(F);pyz=defaultdict(F);pz=defaultdict(F)
    for (x,y,z),p in joint.items():pxz[x,z]+=p;pyz[y,z]+=p;pz[z]+=p
    return sum(float(p)*log2(float(p*pz[z]/(pxz[x,z]*pyz[y,z]))) for (x,y,z),p in joint.items() if p)

observed=defaultdict(F);conditioned=defaultdict(F)
for previous,current in product((0,1),repeat=2):
    observed[current,current,previous]+=F(1,4)
    conditioned[current,current,(previous,current)]+=F(1,4)
te=cmi(observed);te_with_driver=cmi(conditioned)

channels={}
for name,rule in [('copy',lambda a:a),('invert',lambda a:1-a)]:
    joint={(a,rule(a),None):F(1,2) for a in (0,1)}
    channels[name]={'mutual_information_at_uniform_input_bits':cmi(joint),
       'capacity_bits':1,'p_target1_do_action1':rule(1),'p_target1_do_action0':rule(0),
       'target1_causal_difference':rule(1)-rule(0)}

profiles={'A':(F(4,5),F(1,10)),'B':(F(1,10),F(4,5))}
rankings={}
for name,weights in [('task1_priority',(F(9,10),F(1,10))),('task2_priority',(F(1,10),F(9,10)))]:
    rankings[name]={a:str(sum(w*x for w,x in zip(weights,xs))) for a,xs in profiles.items()}

result={'status':'assumed finite models,not empirical social measurements',
 'context_rank_reversal':{'actor_effect_vectors':{a:[str(v) for v in xs] for a,xs in profiles.items()},'weighted_scores':rankings},
 'common_cause':{'structural_model':'Z_t iid fair bits; X_t=Z_t; Y_(t+1)=Z_t; Y_t=Z_(t-1)',
   'observed_te_bits':te,'te_conditioned_on_current_Z_bits':te_with_driver,
   'p_Yfuture1_do_X1':'1/2','p_Yfuture1_do_X0':'1/2','causal_difference':0,
   'observationally_equivalent_alternative':'X_t iid fair bits; Y_(t+1)=X_t; same observed process,causal difference1',
   'observed_joint':[{ 'Yfuture':x,'X':y,'Ypast':z,'probability':str(p)} for (x,y,z),p in observed.items()]},
 'same_capacity_different_goal_effects':channels,
 'local_resource_conversion':{'assumed_response_functions':['I_1(m,r)=m+4r','I_2(m,r)=m+r/2'],
    'money_equivalent_per_reputation_unit_for_same_target':['4','1/2'],
    'scope':'Local stipulated task-response comparisons,not observed prices or trade rights; does not rule out flexible/context-specific numeraire models.'}}
out=Path(__file__).resolve().parents[1]/'surveys/04-influence-and-social-equivalence/model-results.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert abs(te-1)<1e-12 and abs(te_with_driver)<1e-12
assert rankings['task1_priority']['A']=='73/100' and rankings['task2_priority']['B']=='73/100'
print(json.dumps({'te_bits':te,'conditioned_te_bits':te_with_driver,'context_scores':rankings,'target_differences':{k:v['target1_causal_difference'] for k,v in channels.items()}},ensure_ascii=False))
