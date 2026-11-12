"""Two-period assumed task model;not March1991 replication or Ordo estimator."""
from pathlib import Path
import json
def value(k,q,n=10,p=.2):
 current=n-k
 discovery=1-(1-p)**k
 future=n*((1-q)+q*2*discovery)
 return current+future
def calculate():
 rows=[]
 for q in [0,.5,1]:
  scores=[round(value(k,q),8) for k in range(11)];best=max(scores)
  rows.append(dict(change_probability=q,values=scores,best_search_counts=[k for k,v in enumerate(scores) if v==best],best_expected_output=best))
 assert [r['best_search_counts'] for r in rows]==[[0],[4],[7]]
 return dict(status='assumed two-period example,not measured parameters',n=10,individual_search_success=.2,current_production_per_worker=1,future_unchanged_production=1,future_changed_with_discovery=2,future_changed_without_discovery=0,cases=rows)
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'surveys/05-firm-authority-and-democracy/adaptation-model-results.json';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(calculate(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps([(r['change_probability'],r['best_search_counts'],r['best_expected_output']) for r in calculate()['cases']]))
