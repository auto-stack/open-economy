"""Distinguish increasing success from exponential and bounded feedback growth."""
from fractions import Fraction as F
from pathlib import Path
import json

success=[{'capacity':i,'success_probability':str(F(i,10+i))} for i in range(1,7)]
increments=[str(F(i+1,11+i)-F(i,10+i)) for i in range(1,6)]
unbounded=bounded=2.0;trajectory=[]
for t in range(13):
    trajectory.append({'period':t,'constant_proportional_reinvestment':unbounded,'capacity_limited_feedback':bounded})
    unbounded*=1.5;bounded+=0.5*bounded*(1-bounded/10)
result={'status':'assumed illustrative models,not empirical influence scales',
 'increasing_but_saturating_success':{'rule':'p(I)=I/(10+I)','points':success,'unit_capacity_increments':increments,
   'derivatives':'p_prime=10/(10+I)^2>0;p_second=-20/(10+I)^3<0 for I>=0'},
 'feedback':{'initial_capacity':2,'proportional_rate':0.5,'bounded_capacity_parameter':10,
   'unbounded_rule':'I[t+1]=1.5*I[t]','bounded_rule':'I[t+1]=I[t]+0.5*I[t]*(1-I[t]/10)',
   'trajectory':trajectory,'scope':'Both formulas stipulated;feedback alone does not select a unique empirical growth law.'}}
out=Path(__file__).resolve().parents[1]/'surveys/04-influence-and-social-equivalence/mobilization-model-results.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(F(success[i+1]['success_probability'])>F(success[i]['success_probability']) for i in range(len(success)-1))
assert all(F(increments[i+1])<F(increments[i]) for i in range(len(increments)-1))
assert all(0<x['capacity_limited_feedback']<10 for x in trajectory)
print(json.dumps({'success_points':success,'period12':trajectory[-1]},ensure_ascii=False))
