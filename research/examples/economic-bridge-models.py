"""Q6: project-created models separating feasibility, participation and incentives.

Illustrative, dimensionless effort and quasi-linear monetary-equivalent payoffs.
No empirical estimates, actual contract advice or physical-price conversion.
Run this file to regenerate the companion JSON and scientific figure.
"""
from fractions import Fraction as F
from itertools import product
import json
import math
from pathlib import Path


def bisect_increasing(f):
    lo, hi = 0.0, 1.0
    while f(hi) < 0:
        hi *= 2
    for _ in range(100):
        mid = (lo+hi)/2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def maintenance(n, benefit=4.0, concern=0.0):
    effective_b = benefit*(1+concern*(n-1))
    effort = bisect_increasing(lambda e: e*(1+n*e)**2-effective_b)
    total = n*effort
    quality = total/(1+total)
    assert math.isclose(total*(1-quality)-quality,0,abs_tol=1e-12)
    assert math.isclose(effort,effective_b/(1+total)**2,abs_tol=1e-12)
    private_payoff = benefit*quality-effort**2/2
    return dict(n=n,benefit_per_person=benefit,concern_for_others=concern,
                effort_per_person=effort,total_effort=total,stationary_quality=quality,
                material_payoff_per_person=private_payoff,
                aggregate_material_surplus=n*private_payoff)


nash = maintenance(4)
planner = maintenance(4,concern=1)
others = 3*planner['effort_per_person']
deviation = bisect_increasing(lambda e: e*(1+others+e)**2-4)
deviation_payoff = 4*(others+deviation)/(1+others+deviation)-deviation**2/2
assert deviation_payoff > planner['material_payoff_per_person']
assert planner['stationary_quality'] > nash['stationary_quality']

values = (F(6),F(4),F(2))
cost = F(9)


def public_payoffs(payments):
    provided = sum(payments)>=cost
    return tuple((v if provided else F(0))-p for v,p in zip(values,payments))


# Exact enumeration of a finite contribution game; non-refunded contributions.
equilibria=[]
for payments in product(range(10),repeat=3):
    original = public_payoffs(payments)
    stable=True
    for i in range(3):
        for alternative in range(10):
            changed=list(payments);changed[i]=alternative
            if public_payoffs(changed)[i] > original[i]:
                stable=False;break
        if not stable:break
    if stable:equilibria.append(payments)
assert (0,0,0) in equilibria and (5,3,1) in equilibria
for e in equilibria:
    assert e==(0,0,0) or (sum(e)==cost and all(p<=v for p,v in zip(e,values)))


def transfer_accounting(payments,real_cost,administration):
    payments=tuple(F(p) for p in payments)
    user=[v-p for v,p in zip(values,payments)]
    provider=sum(payments)-real_cost-administration
    surplus=sum(user)+provider
    assert surplus==sum(values)-real_cost-administration
    return dict(payments=[float(p) for p in payments],user_surpluses=[float(x) for x in user],
                provider_surplus=float(provider),aggregate_surplus=float(surplus),
                all_users_individually_willing_if_pivotal=all(x>=0 for x in user),
                provider_budget_nonnegative=provider>=0)


funded=transfer_accounting((5,3,1),F(9),F(0))
with_administration=transfer_accounting((F(11,2),F(7,2),F(3,2)),F(9),F(3,2))
equal_split=transfer_accounting((3,3,3),F(9),F(0))
# Equal split describes hypothetical provision; unanimity fails for the third user.
assert not equal_split['all_users_individually_willing_if_pivotal']


def proportional_charge(reports):
    assert sum(reports)>=cost
    return tuple(cost*r/sum(reports) for r in reports)


truthful=proportional_charge(values)
underreport=proportional_charge((F(4),F(4),F(2)))
assert values[0]-underreport[0] > values[0]-truthful[0]
assert all(v-p>=0 for v,p in zip(values,underreport))


def posted_prices(real_cost):
    options=[]
    for price in sorted(set(values)):
        served=[v>=price for v in values]  # Indifferent users buy by assumption.
        revenue=price*sum(served)
        options.append(dict(price=float(price),served=served,revenue=float(revenue),
                            provider_surplus=float(revenue-real_cost),
                            aggregate_surplus_if_provided=float(sum(v for v,s in zip(values,served) if s)-real_cost)))
    best=max(options,key=lambda x:x['provider_surplus'])
    return dict(real_cost=float(real_cost),options=options,best_posted_price_if_operating=best,
                can_finance_without_subsidy=best['provider_surplus']>=0,
                open_access_aggregate_surplus_if_financed=float(sum(values)-real_cost))


p_h,p_l,c_h,c_l,value=F(9,10),F(2,5),F(4),F(0),F(10)
threshold=(c_h-c_l)/(p_h-p_l)
assert threshold==8
contracts=[]
for kind,amount in [('fixed',F(4)),('success_bonus',F(8)),('success_bonus',F(41,5))]:
    if kind=='fixed':
        high=amount-c_h;low=amount-c_l
        pay_h=pay_l=amount
    else:
        high=p_h*amount-c_h;low=p_l*amount-c_l
        pay_h=p_h*amount;pay_l=p_l*amount
    for administration in (F(0),F(2)):
        contracts.append(dict(kind=kind,payment_parameter=float(amount),administration=float(administration),
                              provider_high_payoff=float(high),provider_low_payoff=float(low),
                              high_weakly_incentivized=high>=low,high_strictly_incentivized=high>low,
                              provider_participation_if_high=high>=0,
                              expected_payment_if_high=float(pay_h),
                              payer_surplus_if_high=float(p_h*value-pay_h-administration),
                              payer_surplus_if_low=float(p_l*value-pay_l-administration),
                              statewise_maximum_payment=float(amount)))
assert p_h*value-p_h*threshold==F(9,5)
feasibility=[]
for g in (F(0),F(1),F(9,5),F(2)):
    max_bonus=value-g/p_h
    feasibility.append(dict(administration=float(g),minimum_bonus_IC=float(threshold),
                             maximum_bonus_payer_IR=float(max_bonus),
                             weakly_feasible=max_bonus>=threshold,
                             strictly_incentivized_and_payer_nonnegative_possible=max_bonus>threshold))

output=Path(__file__).parent
result=dict(scope='illustrative economic bridge models; no empirical estimates',
            maintenance=dict(self_regarding_equilibrium=nash,equal_weight_planner=planner,
                             best_unilateral_deviation_from_planner=deviation,
                             deviation_payoff=deviation_payoff,
                             concern_sensitivity=[maintenance(4,concern=x) for x in (0,0.25,0.5,1)]),
            threshold_public_good=dict(values=[float(v) for v in values],real_cost=float(cost),
                                       contribution_grid=list(range(10)),pure_equilibria=equilibria,
                                       funded=funded,with_administration=with_administration,
                                       equal_split_hypothetical_provision=equal_split,
                                       aggregate_surplus_with_admin_4=float(sum(values)-cost-4)),
            reporting=dict(truthful_reports=[6,4,2],truthful_payments=[float(x) for x in truthful],
                           deviating_reports=[4,4,2],deviating_payments=[float(x) for x in underreport],
                           true_payoffs_after_deviation=[float(v-p) for v,p in zip(values,underreport)]),
            exclusion=[posted_prices(F(9)),posted_prices(F(7))],
            hidden_effort=dict(success_probabilities=[float(p_h),float(p_l)],costs=[float(c_h),float(c_l)],
                               payoff_per_success=float(value),bonus_threshold=float(threshold),
                               cases=contracts,feasible_bonus_intervals=feasibility),
            verification=['stationary maintenance balance','symmetric first order conditions',
                          'profitable unilateral deviation at planner allocation',
                          'all pure equilibria of stated finite contribution game',
                          'transfers cancel in aggregate accounting',
                          'profitable value underreporting example',
                          'exact rational incentive and participation inequalities'])
(output/'economic-bridge-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'maintenance':result['maintenance'],'equilibria':equilibria,
                  'funded':funded,'with_administration':with_administration,
                  'reporting':result['reporting'],'bonus_intervals':feasibility},indent=2))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14,4.2),constrained_layout=True)
ns=list(range(1,13))
axes[0].plot(ns,[maintenance(n)['stationary_quality'] for n in ns],marker='o',label='Self-regarding Nash')
axes[0].plot(ns,[maintenance(n,concern=1)['stationary_quality'] for n in ns],marker='s',label='Equal-weight planner')
axes[0].set(xlabel='Number of symmetric beneficiaries',ylabel='Stationary maintained capability q',title='A  Physical response fixed, choices differ')
axes[0].legend(fontsize=8)
indices=list(range(3));width=0.24
for offset,payments,label in [(-width,[3,3,3],'Equal split'),(0,[5,3,1],'Differentiated payments'),
                              (width,[5.5,3.5,1.5],'With administration cost')]:
    axes[1].bar([i+offset for i in indices],[float(v)-p for v,p in zip(values,payments)],width,label=label)
axes[1].axhline(0,color='black',linewidth=0.8)
axes[1].set(xticks=indices,xticklabels=['User 1','User 2','User 3'],ylabel='Individual surplus if provided',
            title='B  Same public benefit, different consent')
axes[1].legend(fontsize=7)
gs=[i/100 for i in range(301)]
axes[2].plot(gs,[float(value)-g/float(p_h) for g in gs],label='Maximum bonus allowed by payer IR')
axes[2].axhline(float(threshold),color='black',linestyle=':',label='Minimum bonus for weak high-effort IC')
axes[2].axvspan(0,1.8,color='green',alpha=0.12)
axes[2].set(xlabel='Administration cost g',ylabel='Success-contingent bonus',title='C  Funding does not guarantee effort')
axes[2].legend(fontsize=7)
fig.savefig(output/'economic-bridge-tradeoffs.png',dpi=180)
fig.savefig(output/'economic-bridge-tradeoffs.svg')
plt.close(fig)
