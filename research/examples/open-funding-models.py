"""Q7: illustrative funding contracts, available margins and recurring liquidity.

Project-created benchmarks, not empirical estimates or actual contract advice.
All money equivalents use the same arbitrary unit; no energy-price conversion.
Run to regenerate the companion results and scientific figures.
"""
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import json


VALUES = (F(6), F(4), F(2))
LABOR = F(6)  # Labor opportunity cost, paid at the assumed reservation amount.
OTHER = F(3)
CORE_COST = LABOR + OTHER
ADMIN = F(3, 5)
REQUIRED = CORE_COST + ADMIN
QUOTES = (F(53, 10), F(33, 10), F(13, 10))
CAMPAIGN_COST = F(1, 5)  # Part of ADMIN; incurred even if the campaign fails.
BONUS = F(1, 10)


def contract_payoffs(acceptance, failure_bonus=F(0), signing_cost=F(0)):
    """Fixed named participants; unanimity required; failed pledges refunded.

    Refusers get zero if the project fails. A failure bonus goes only to signers.
    The guarantor pays the campaign cost in either outcome, and the remaining
    administration cost only on success. Success is assumed verifiable/enforced.
    """
    supplied = all(acceptance)
    users = tuple(
        ((v-p-signing_cost) if supplied else (failure_bonus-signing_cost))
        if accepts else F(0)
        for v, p, accepts in zip(VALUES, QUOTES, acceptance)
    )
    operator = (sum(QUOTES)-REQUIRED if supplied
                else -CAMPAIGN_COST-sum(acceptance)*failure_bonus)
    return users, operator


def enumerate_contract(failure_bonus=F(0), signing_cost=F(0)):
    equilibria = []
    rows = []
    gains = [[] for _ in VALUES]
    for action in product((False, True), repeat=3):
        payoffs, operator = contract_payoffs(action, failure_bonus, signing_cost)
        stable = True
        for i in range(3):
            changed = list(action)
            changed[i] = not changed[i]
            alternative = contract_payoffs(changed, failure_bonus, signing_cost)[0][i]
            if alternative > payoffs[i]:
                stable = False
        if stable:
            equilibria.append([int(x) for x in action])
        rows.append(dict(acceptance=[int(x) for x in action],
                         user_payoffs=[float(x) for x in payoffs],
                         operator_payoff=float(operator)))
    for i in range(3):
        for others in product((False, True), repeat=2):
            refuse = list(others)
            refuse.insert(i, False)
            accept = list(refuse)
            accept[i] = True
            gains[i].append(contract_payoffs(accept, failure_bonus, signing_cost)[0][i]
                            - contract_payoffs(refuse, failure_bonus, signing_cost)[0][i])
    return dict(failure_bonus=float(failure_bonus),signing_cost=float(signing_cost),
                pure_equilibria=equilibria,
                strictly_dominant_acceptance=all(min(g)>0 for g in gains),
                minimum_acceptance_gain=[float(min(g)) for g in gains],profiles=rows)


refund = enumerate_contract()
bonus = enumerate_contract(BONUS)
friction = enumerate_contract(BONUS, F(3, 20))
assert len(refund['pure_equilibria']) == 5
assert bonus['pure_equilibria'] == [[1, 1, 1]]
assert bonus['strictly_dominant_acceptance']
assert friction['pure_equilibria'] == [[0, 0, 0], [1, 1, 1]]
success_profit = sum(QUOTES)-REQUIRED
max_failed_signers = len(VALUES)-1
max_failure_liability = CAMPAIGN_COST+max_failed_signers*BONUS
break_even_success_probability = max_failure_liability/(success_profit+max_failure_liability)
assert success_profit == F(3,10) and max_failure_liability == F(2,5)

# Service demand is conditional on an already financed core, not a solved joint
# public-funding game. These are incremental private values above open access.
SERVICE_VALUES = (F(5), F(4), F(2))
SERVICE_UNIT_COST = F(1)
service_options=[]
for price in sorted(set(SERVICE_VALUES)):
    buyers=sum(v>=price for v in SERVICE_VALUES)  # Indifferent buyers buy.
    revenue=price*buyers
    delivery=SERVICE_UNIT_COST*buyers
    margin=revenue-delivery
    service_options.append(dict(price=float(price),buyers=buyers,
                                gross_revenue=float(revenue),delivery_cost=float(delivery),
                                available_margin=float(margin),core_gap=float(REQUIRED-margin)))
best=max(service_options,key=lambda x:x['available_margin'])
assert best['available_margin']==6 and best['core_gap']==float(F(18,5))
SPONSOR = F(4)
MARGIN = F(6)
minimum_allocation=(REQUIRED-SPONSOR)/MARGIN
assert minimum_allocation==F(14,15)
allocation_rows=[]
for alpha in (F(0),F(1,2),minimum_allocation,F(1)):
    available=SPONSOR+alpha*MARGIN
    allocation_rows.append(dict(maintenance_allocation=float(alpha),
                                maintenance_receipts=float(available),
                                cash_after_required_cost=float(available-REQUIRED)))

# A matching budget is a real external input, not newly created value.
matching_cap = F(3)
minimum_unmatched_donation=REQUIRED-matching_cap
assert minimum_unmatched_donation>=matching_cap
assert minimum_unmatched_donation+min(minimum_unmatched_donation,matching_cap)==REQUIRED


def receipts_distribution(n, common_shock=False):
    """Each period: total promised receipts 12, active probability 4/5.

    One unit below equals 0.6 money units; core obligation is 16 units.
    Independent sources each pay 12/n when active; common shocks synchronize all.
    Source states are independent over time; no new borrowing or rescue funding.
    """
    if common_shock or n==1:
        return {0:F(1,5),20:F(4,5)}
    assert 20 % n==0
    return {k*(20//n):F(comb(n,k))*F(4,5)**k*F(1,5)**(n-k)
            for k in range(n+1)}


def liquidity_path(n, common_shock=False, periods=12, reserve_units=16):
    dist=receipts_distribution(n,common_shock)
    assert sum(dist.values())==1
    mean=sum(F(x)*p for x,p in dist.items())
    var=sum((x-mean)**2*p for x,p in dist.items())
    assert mean==16
    alive={reserve_units:F(1)}
    failed=F(0)
    path=[dict(period=0,probability_all_obligations_met=1.0,cumulative_failure=0.0)]
    for t in range(1,periods+1):
        updated={}
        for balance,mass in alive.items():
            for income,p in dist.items():
                after=balance+income-16
                probability=mass*p
                if after<0:
                    failed+=probability
                else:
                    updated[after]=updated.get(after,F(0))+probability
        alive=updated
        assert sum(alive.values())+failed==1
        path.append(dict(period=t,probability_all_obligations_met=float(1-failed),
                         cumulative_failure=float(failed)))
    return dict(sources=n,common_shock=common_shock,periods=periods,
                initial_reserve=float(F(reserve_units)*F(3,5)),
                expected_period_receipts=float(mean*F(3,5)),
                variance_period_receipts=float(var*F(3,5)**2),
                probability_failure_within_horizon=float(failed),
                exact_failure_probability=str(failed),path=path)


concentrated=liquidity_path(1)
diversified=liquidity_path(4)
correlated=liquidity_path(4,True)
assert concentrated['path']==correlated['path']
assert diversified['variance_period_receipts'] < concentrated['variance_period_receipts']
assert diversified['probability_failure_within_horizon'] < concentrated['probability_failure_within_horizon']
reserves=[dict(reserve=float(F(r)*F(3,5)),
               concentrated_failure=liquidity_path(1,reserve_units=r)['probability_failure_within_horizon'],
               diversified_failure=liquidity_path(4,reserve_units=r)['probability_failure_within_horizon'])
          for r in (0,8,16,32)]

result=dict(scope='Project-created illustrative benchmarks, no empirical estimates',
            common_target=dict(core_labor_opportunity_cost=float(LABOR),
                               core_other_inputs=float(OTHER),administration=float(ADMIN),
                               required_cash_per_period=float(REQUIRED),
                               open_core_values=[float(x) for x in VALUES]),
            assurance=dict(quotes=[float(x) for x in QUOTES],refund=refund,
                           failure_bonus=bonus,bonus_with_signing_friction=friction,
                           operator_success_profit=float(success_profit),
                           maximum_campaign_and_failure_bonus_liability=float(max_failure_liability),
                           worst_failure_mix_break_even_success_probability=float(break_even_success_probability)),
            complements=dict(incremental_service_values=[float(x) for x in SERVICE_VALUES],
                             options=service_options,best_conditional_margin=best,
                             committed_sponsorship=float(SPONSOR),
                             minimum_core_allocation=float(minimum_allocation),
                             allocation_examples=allocation_rows),
            matching=dict(multiplier=1,external_cap=float(matching_cap),
                          uncapped_donation_threshold=float(REQUIRED/2),
                          capped_donation_threshold=float(minimum_unmatched_donation)),
            recurring=dict(concentrated=concentrated,independent_four=diversified,
                           perfectly_correlated_four=correlated,reserve_sensitivity=reserves),
            verification=['enumerated every acceptance profile and unilateral deviation',
                          'verified strict-dominance gains for the fixed unanimity bonus game',
                          'exact service-margin and allocation accounting',
                          'exact finite-horizon liquidity state propagation with probability conservation'])
out=Path(__file__).parent
(out/'open-funding-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(dict(assurance_equilibria={k:result['assurance'][k]['pure_equilibria']
                                          for k in ['refund','failure_bonus','bonus_with_signing_friction']},
                      service_margin=best,minimum_allocation=float(minimum_allocation),
                      liquidity_failure={k:result['recurring'][k]['probability_failure_within_horizon']
                                         for k in ['concentrated','independent_four','perfectly_correlated_four']},
                      reserves=reserves),indent=2))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14,4.2),constrained_layout=True)
axes[0].bar(['Service sales\n(gross)','After service\ncost','Plus committed\nsponsorship'],[8,6,10],color=['#8196ac','#3478af','#359b72'])
axes[0].axhline(float(REQUIRED),color='black',linestyle=':',label='Core + administration = 9.6')
axes[0].set(ylabel='Money-equivalent units',title='A  Available funds require cost accounting')
axes[0].legend(fontsize=7,loc='lower left')
for data,label,color in [(concentrated,'One source / four fully correlated','#c56831'),
                          (diversified,'Four independent sources','#3478af')]:
    axes[1].plot([x['period'] for x in data['path']],
                 [x['probability_all_obligations_met'] for x in data['path']],
                 marker='o',label=label,color=color)
axes[1].set(xlabel='Periods elapsed',ylabel='Probability every obligation was met',
            ylim=(0,1.03),title='B  Same mean receipts, different liquidity risk')
axes[1].legend(fontsize=7)
alphas=[i/100 for i in range(101)]
axes[2].plot(alphas,[float(SPONSOR)+float(MARGIN)*a for a in alphas],label='4 sponsorship + allocated service margin')
axes[2].axhline(float(REQUIRED),color='black',linestyle=':',label='Required funding = 9.6')
axes[2].axvline(float(minimum_allocation),color='#c56831',linestyle='--',label='Minimum allocation = 14/15')
axes[2].set(xlabel='Fraction of service margin allocated to core',ylabel='Funds available for maintenance',
            title='C  Revenue needs a credible return path')
axes[2].legend(fontsize=7,loc='lower right')
fig.savefig(out/'open-funding-tradeoffs.png',dpi=180)
fig.savefig(out/'open-funding-tradeoffs.svg')
plt.close(fig)
