"""A closed cash ledger for four hypothetical one-period counterfactuals.

Not a general equilibrium, an AI impact estimate, a tax recommendation, or a
resource-production proof. All scenarios restart from the same cash balances.
"""
from pathlib import Path
from fractions import Fraction as Q
import csv
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/surveys/08-price-income-and-reinvestment'

def run(name,wages,asset_services,capacity,redistribution=0,public_purchase=0):
    initial={'A':Q(40),'B':Q(40),'firm':Q(100),'public':Q(20)}
    cash=initial.copy();rows=[]
    def pay(sender,receiver,amount,purpose):
        amount=Q(amount)
        assert cash[sender]>=amount and amount>=0
        cash[sender]-=amount;cash[receiver]+=amount
        assert min(cash.values())>=0 and sum(cash.values())==200
        rows.append(dict(scenario=name,step=len(rows)+1,sender=sender,receiver=receiver,
            amount=float(amount),purpose=purpose,**{f'cash_{k}':float(v) for k,v in cash.items()}))
    assert wages+asset_services==80 and wages>=8
    pay('firm','A',wages,'current_labor_including_8_maintenance')
    pay('firm','B',asset_services,'asset_and_service_payment_no_further_supplier_cost_in_model')
    if redistribution:
        pay('B','public',redistribution,'hypothetical_authorized_collection')
        pay('public','A',redistribution,'hypothetical_transfer_not_new_resources')
    available={'A':cash['A'],'B':cash['B']}
    spend_A=Q(4,5)*cash['A'];spend_B=Q(1,5)*cash['B']
    pay('A','firm',spend_A,'purchase_at_unit_price_1')
    pay('B','firm',spend_B,'purchase_at_unit_price_1')
    if public_purchase:pay('public','firm',public_purchase,'purchase_of_extra_in_scope_service')
    sales=spend_A+spend_B+public_purchase
    assert sales<=capacity
    assert cash['firm']==100-80+sales
    return dict(scenario=name,wage_payment=wages,asset_service_payment=asset_services,
        maintenance_inside_wages=8,service_capacity=capacity,available_before_purchases={k:float(v) for k,v in available.items()},
        group_A_purchase=float(spend_A),group_B_purchase=float(spend_B),public_purchase=public_purchase,
        redistribution=redistribution,actual_sales=float(sales),unused_capacity=float(capacity-sales),
        firm_cash_change=float(cash['firm']-100),final_cash={k:float(v) for k,v in cash.items()},
        cash_total=float(sum(cash.values())),steps=rows)

def main():
    cases=[run('reference',60,20,100),run('higher_capacity_changed_payments',20,60,140),
           run('higher_capacity_with_transfer',20,60,140,redistribution=20),
           run('higher_capacity_with_public_purchase',20,60,140,public_purchase=10)]
    assert [x['actual_sales'] for x in cases]==[92,68,80,78]
    assert all(x['cash_total']==200 for x in cases)
    assert cases[2]['final_cash']['public']==20 and cases[3]['final_cash']['public']==10
    rows=[r for c in cases for r in c['steps']]
    with (OUT/'ai-income-cash-ledger.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result=dict(date='2026-11-12',status='exact_rational_accounting_checks_pass',empirical_parameters=False,
        policy_recommendation=False,periods=1,cases_restart_from_same_initial_state=True,
        initial_cash={'A':40,'B':40,'firm':100,'public':20},total_initial_cash=200,
        purchase_rules={'A_fraction_of_available_cash':0.8,'B_fraction_of_available_cash':0.2},
        assumptions=['fixed_cash_input80','maintenance8_already_inside_wages_not_added_again',
            'unit_service_price1','no_extra_marginal_cash_cost_below_capacity',
            'B_has_no_further_supplier_cost_in_this_aggregation','existing_assets_and_resource_capacity_are_given',
            'no_bank_money_creation_or_debt','no_next_period_behavior_equation'],
        scientific_limit='Cash closure and one counterexample to capacity implying sales; not proof of resource feasibility, endogenous income equilibrium, or actual AI distribution.',
        cases=[{k:v for k,v in c.items() if k!='steps'} for c in cases],ledger_rows=len(rows))
    (OUT/'ai-income-account-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'actual_sales':[c['actual_sales'] for c in cases],
                      'cash_totals':[c['cash_total'] for c in cases],'ledger_rows':len(rows)}))

if __name__=='__main__':main()
