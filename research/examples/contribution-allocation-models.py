"""Exact finite counterexamples and a hypothetical service's residual allocations."""
from fractions import Fraction as F
from itertools import permutations
from pathlib import Path
import json

def average_marginal(players,value):
    orders=list(permutations(players));out={a:F(0) for a in players}
    for order in orders:
        s=frozenset()
        for a in order:
            nxt=s|{a};out[a]+=F(value(nxt)-value(s),len(orders));s=nxt
    return out

def evaluate(players,value):
    allp=frozenset(players)
    return {'full_value':value(allp),'baseline':value(frozenset()),
       'leave_one_out':{a:value(allp)-value(allp-{a}) for a in players},
       'average_marginal':{a:str(x) for a,x in average_marginal(players,value).items()}}

complements=evaluate(('A','B'),lambda s:100 if len(s)==2 else 0)
substitutes=evaluate(('A','B'),lambda s:100 if s else 0)
split=evaluate(('A1','A2','B'),lambda s:100 if s else 0)
split['same_entity_total']=str(sum(average_marginal(('A1','A2','B'),lambda s:100 if s else 0)[a] for a in ('A1','A2')))

coalition_values={frozenset():0,frozenset('A'):10,frozenset('B'):5,frozenset('C'):0,
 frozenset('AB'):25,frozenset('AC'):15,frozenset('BC'):10,frozenset('ABC'):30}
service=evaluate(('A','B','C'),lambda s:coalition_values[s])
service.update({'gross_receipts':100,'committed_service_costs':40,'maintenance_budget':20,'reserve':10,'residual':30,
 'capital_weights':{'A':0,'B':0,'C':1},'labour_hours':{'A':6,'B':3,'C':1},
 'capital_residual_allocation':{'A':'0','B':'0','C':'30'},
 'labour_residual_allocation':{'A':'18','B':'9','C':'3'},
 'coalition_values':{''.join(sorted(s)) or 'empty':v for s,v in coalition_values.items()},
 'scope':'Only allocation of residual30; not total compensation or predicted behavior. Coalition net values are assumed,not observed.'})

result={'status':'illustrations,not empirical estimates or a recommended allocation rule',
 'complementarity':complements,'substitutability':substitutes,'unverified_identity_partition':split,
 'preventive_maintenance':{'before_failure_probability':'3/10','after_failure_probability':'1/20','loss_if_failure':200,'expected_loss_reduction':str((F(3,10)-F(1,20))*200),'scope':'Assumed causal probabilities; expected avoided loss is not cash revenue and not automatically payable.'},
 'service':service}
out=Path(__file__).resolve().parents[1]/'surveys/03-competition-cooperation-distribution/contribution-model-results.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sum(average_marginal(('A','B','C'),lambda s:coalition_values[s]).values())==30
print(json.dumps({'complements':complements,'substitutes':substitutes,'split_entity_total':split['same_entity_total'],'service_average_marginal':service['average_marginal'],'preventive_expected_gain':result['preventive_maintenance']['expected_loss_reduction']},ensure_ascii=False))
