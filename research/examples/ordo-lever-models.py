"""Assumed capacity and adoption examples;not a universal Ordo law."""
from pathlib import Path
import json
def capacity(eta,u,delta=.1,k0=10,steps=10):
 k=k0;xs=[k]
 for _ in range(steps):k=(1-delta)*k+eta*u;xs.append(round(k,9))
 return xs
def calculate():
 stocks=dict(no_input=capacity(1,0),baseline=capacity(1,1),improved_conversion=capacity(2,1))
 adoption=[dict(periods=t,baseline_new_units=(10*t-4*t)/2,tool_new_units=(10*t-4*t-2*t-8)/1) for t in [2,5,10]]
 assert stocks['baseline']==[10.0]*11
 assert stocks['no_input'][-1]==3.486784401
 assert stocks['improved_conversion'][-1]==16.513215599
 assert [(r['baseline_new_units'],r['tool_new_units']) for r in adoption]==[(6,0),(15,12),(30,32)]
 return dict(status='assumed examples only;not empirical or thermodynamic validation',capacity_model=stocks,capacity_steady_states=dict(baseline=10,improved_conversion=20),adoption_model=adoption,strict_adoption_advantage_condition='T>8 under fixed stated assumptions')
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'surveys/06-technological-levers-and-organizational-evolution/model-results.json';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(calculate(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Capacity,steady-state and adoption-budget examples checked;all parameters assumed.')
