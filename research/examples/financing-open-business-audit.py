"""Finite examples for reading and institutional accounting, not empirical estimates."""
from pathlib import Path
from fractions import Fraction as Q
import csv
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/surveys/08-price-income-and-reinvestment'

def numeric(value):
    if isinstance(value,Q): return float(value)
    if isinstance(value,dict): return {k:numeric(v) for k,v in value.items()}
    if isinstance(value,list): return [numeric(v) for v in value]
    return value

def cdf_integral(atoms,y):
    # Integral_0^y F(x)dx = E[(y-X)+], for nonnegative X.
    return sum(prob*max(Q(0),y-value) for value,prob in atoms)

def risk_direction():
    spread=[(Q(0),Q(1,2)),(Q(2),Q(1,2))]
    certain=[(Q(1),Q(1))]
    rows=[]
    for y in [Q(0),Q(1,2),Q(1),Q(3,2),Q(2),Q(3)]:
        left=cdf_integral(spread,y);right=cdf_integral(certain,y)
        assert left>=right
        rows.append({'y':y,'integrated_cdf_spread':left,'integrated_cdf_certain':right})
    mean_spread=sum(x*p for x,p in spread);mean_certain=sum(x*p for x,p in certain)
    variance_spread=sum((x-mean_spread)**2*p for x,p in spread)
    assert mean_spread==mean_certain==1 and variance_spread==1
    return {'kind':'own_two_point_example_not_author_erratum', 'rows':rows,
            'equal_mean':mean_spread,'spread_variance':variance_spread,'certain_variance':Q(0)}

def financing():
    I=Q(100);A=Q(20);R=Q(150);pH=Q(4,5);pL=Q(2,5);dp=pH-pL
    B=Q(24);b=Q(8);c=Q(18);gamma=Q(1);beta=Q(11,5)
    direct_pledge=pH*(R-B/dp)
    Abar=I-direct_pledge/gamma
    beta_min=gamma*pH/pL
    Im_min=pH*c/(dp*beta)
    monitored_pledge=pH*(R-(b+c)/dp)
    Aunder=I-Im_min-monitored_pledge/gamma
    # A nearby feasible contract with STRICT effort and monitoring incentives.
    Rf=Q(101,4);Rm=Q(451,10);Ru=R-Rf-Rm
    Im=pH*Rm/beta;Iu=I-A-Im
    checks={'resource_funding':A+Im+Iu==I,
            'payoff_sum':Rf+Rm+Ru==R,
            'firm_effort_strict':dp*Rf>b,
            'monitor_effort_strict':dp*Rm>c,
            'firm_participation_strict':pH*Rf>gamma*A,
            'monitor_participation_strict':pH*Rm-c>gamma*Im,
            'uninformed_participation_strict':pH*Ru>gamma*Iu,
            'monitor_needed_for_chosen_contract':dp*Rf<B,
            'good_viable_before_monitoring':pH*R-gamma*I>0,
            'bad_not_viable_including_private_B':pL*R-gamma*I+B<0,
            'beta_exceeds_minimum':beta>beta_min,
            'section_IV_optional_b_plus_c_exceeds_B':b+c>B,
            'monitor_useful_at_minimum_beta':c*dp<pH*(B-b)}
    assert all(checks.values())
    assert A<Abar and A>=Aunder and monitored_pledge<direct_pledge
    gains={'firm':pH*Rf-gamma*A,'monitor':pH*Rm-c-gamma*Im,
           'uninformed':pH*Ru-gamma*Iu}
    assert sum(gains.values())==pH*R-gamma*I-c==2
    return {'kind':'hypothetical_conditional_contract_not_full_equilibrium',
        'parameters':dict(I=I,A=A,R=R,pH=pH,pL=pL,B=B,b=b,c=c,gamma=gamma,beta_m=beta),
        'direct':dict(pledgeable_income=direct_pledge,external_funding_needed=I-A,Abar=Abar),
        'monitored_binding_bounds':dict(beta_min=beta_min,Im_min=Im_min,pledgeable_uninformed_income=monitored_pledge,Aunder=Aunder),
        'strict_contract':dict(Rf=Rf,Rm=Rm,Ru=Ru,Im=Im,Iu=Iu,gains=gains),
        'checks':checks,
        'printed_equation_3_inconsistency':dict(good_net=pH*R-gamma*I,
            printed_negative_rhs=-pH*B/dp,printed_condition_satisfied=pH*R-gamma*I < -pH*B/dp,
            positive_Abar_condition_satisfied=pH*R-gamma*I < pH*B/dp)}

def simulate(name,inflows,earmarked,repair=False,initial=True):
    due={'maintenance':Q(8),'platform':Q(4),'contributor_contract':Q(2)}
    cash=due.copy() if initial else {k:Q(0) for k in due}
    pooled=sum(cash.values());predicted=cash.copy();predicted_pool=pooled
    rows=[];first_failure=None
    for month,amount in enumerate(inflows,1):
        amount=Q(amount)
        if not earmarked:
            predicted_pool+=amount-sum(due.values())
            available=pooled+amount;gap=max(Q(0),sum(due.values())-available)
            if gap and first_failure is None:first_failure=month
            # Terminate the fixed service upon its first funding failure; negative
            # projections remain a diagnosis, never an executed overdraft.
            executed=first_failure is None
            if executed: pooled=available-sum(due.values())
            rows.append(dict(scenario=name,month=month,regime='pooled',inflow=amount,
                forecast_maintenance='',forecast_platform='',forecast_contributor='',
                forecast_total=predicted_pool,authorized_platform_transfer=Q(0),
                actual_end_maintenance='',actual_end_platform='',actual_end_contributor='',
                actual_end_total=pooled if executed else '',
                fixed_service_executable=executed,shortfall_at_first_failure=gap if month==first_failure else Q(0)))
            continue
        allocations={'maintenance':amount*Q(2,5),'platform':amount*Q(2,5),'contributor_contract':amount*Q(1,5)}
        for k in due: predicted[k]+=allocations[k]-due[k]
        available={k:cash[k]+allocations[k] for k in due}
        transfer=Q(0)
        if repair and first_failure is None:
            missing=max(Q(0),due['maintenance']-available['maintenance'])
            # A prospective, pre-authorized purchase from platform surplus only;
            # preserve its current bill plus one month's platform reserve.
            transferable=max(Q(0),available['platform']-due['platform']-Q(4))
            transfer=min(missing,transferable)
            available['maintenance']+=transfer;available['platform']-=transfer
        gaps={k:max(Q(0),due[k]-available[k]) for k in due}
        if any(gaps.values()) and first_failure is None:first_failure=month
        executed=first_failure is None
        if executed:cash={k:available[k]-due[k] for k in due}
        rows.append(dict(scenario=name,month=month,regime='earmarked_repair' if repair else 'earmarked',
            inflow=amount,forecast_maintenance=predicted['maintenance'],forecast_platform=predicted['platform'],
            forecast_contributor=predicted['contributor_contract'],forecast_total=sum(predicted.values()),
            authorized_platform_transfer=transfer,
            actual_end_maintenance=cash['maintenance'] if executed else '',
            actual_end_platform=cash['platform'] if executed else '',
            actual_end_contributor=cash['contributor_contract'] if executed else '',
            actual_end_total=sum(cash.values()) if executed else '',fixed_service_executable=executed,
            shortfall_at_first_failure=sum(gaps.values()) if month==first_failure else Q(0)))
    return {'scenario':name,'regime':rows[0]['regime'],'first_failure_month':first_failure,
            'forecast_final_total_without_repair':rows[-1]['forecast_total'],
            'actual_total_transferred':sum(r['authorized_platform_transfer'] for r in rows),
            'rows':rows}

def main():
    scenarios={'base':[24]*12,'common_revenue_drop':[24]*3+[9]*6+[24]*3,
               'receipts_delayed':[0]*2+[72]+[24]*9,'no_receipts':[0]*12}
    cash=[]
    for name,inflows in scenarios.items():
        cash.extend([simulate(name,inflows,False),simulate(name,inflows,True),simulate(name,inflows,True,True)])
    assert cash[0]['first_failure_month'] is None and cash[1]['first_failure_month'] is None
    assert cash[3]['first_failure_month'] is None and cash[4]['first_failure_month']==6 and cash[5]['first_failure_month'] is None
    assert all(x['first_failure_month']==2 for x in cash if x['scenario']=='receipts_delayed')
    assert all(x['first_failure_month']==2 for x in cash if x['scenario']=='no_receipts')
    flat=[r for c in cash for r in c['rows']]
    with (OUT/'institution-cash-scenarios.csv').open('w',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(flat[0]));w.writeheader();w.writerows(numeric(flat))
    result={'date':'2026-11-12','empirical_data':False,'parameters_are_policy':False,
        'risk_direction':risk_direction(),'financing':financing(),
        'cash_protocol':{'months':12,'monthly_due':{'maintenance':8,'platform':4,'contributor_contract':2},
            'initial_cash':{'maintenance':8,'platform':4,'contributor_contract':2},
            'public_fee_share':0.6,'maintenance_share_within_public':2/3,
            'earmarked_total_fractions':{'maintenance':0.4,'platform':0.4,'contributor_contract':0.2},
            'pooled_minimum_steady_inflow':14,'earmarked_minimum_steady_inflow':20,
            'legal_responsibility_or_actual_demand_inferred':False},
        'cash_summary':[{k:v for k,v in c.items() if k!='rows'} for c in cash]}
    (OUT/'financing-argument-model-results.json').write_text(json.dumps(numeric(result),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(numeric({'direct':result['financing']['direct'],
        'monitored':result['financing']['monitored_binding_bounds'],'cash':result['cash_summary']}),ensure_ascii=False))

if __name__=='__main__':main()
