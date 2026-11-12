"""Finite illustrative calculations; no empirical parameter estimates."""
from fractions import Fraction
from itertools import permutations, combinations
import json
from pathlib import Path

agents=('A','B','C')
def value(s):
    return 100 if len(s)>=2 else 0

allocation={a:Fraction(0) for a in agents}
orders=[]
for order in permutations(agents):
    coalition=set();increments={}
    for a in order:
        before=value(coalition);coalition.add(a)
        increments[a]=value(coalition)-before
        allocation[a]+=Fraction(increments[a],6)
    orders.append({'order':order,'marginal_increments':increments})

results={
 'status':'illustrative models, not empirical evidence',
 'unfair_strategy':{'extra_receipts_plus_avoided_cost':12,'additional_other_cost':2,
   'conditional_loss_if_detected':50,'cases':[
      {'detection_probability':p,'incremental_expected_payoff':12-2-p*50}
      for p in (0.1,0.2,0.3)],'break_even_probability':0.2},
 'coalition_example':{'value_rule':'0 for empty/singleton; 100 for any pair or all three',
   'orders':orders,'mean_marginal_allocation':{a:str(x) for a,x in allocation.items()},
   'total_allocation':str(sum(allocation.values())),
   'pair_allocations':{'-'.join(pair):str(sum(allocation[a] for a in pair)) for pair in combinations(agents,2)},
   'blocking_pair_value':100,
   'empty_core_reason':'Adding all three pair stability constraints requires 2*(xA+xB+xC)>=300, contradicting total=100.'}
}
out=Path(__file__).resolve().parents[1]/'surveys/03-competition-cooperation-distribution/model-results.json'
out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'incremental_payoffs':[x['incremental_expected_payoff'] for x in results['unfair_strategy']['cases']],
 'allocation':results['coalition_example']['mean_marginal_allocation'], 'budget':str(sum(allocation.values()))},ensure_ascii=False))
