"""Q8: research-only AutoOS Open Business accounting and incentive examples.

Historical candidate rates are scenarios, not adopted policy. All other cost,
demand and scoring parameters are invented for transparent sensitivity analysis.
No live payment integration, business forecast, or identity-defense implementation.
"""
from fractions import Fraction as F
from pathlib import Path
import json

TAU = F(1,20)
BETA = F(1,2)
BASES = {'preservation':F(1000),'promotion':F(2000),'sales_and_tips':F(7000)}
TOTAL = sum(BASES.values())
VARIABLE_RATE = F(1,100)  # Hypothetical; not a payment-provider quotation.
FIXED_COST = F(180)
RESERVE_TARGET = F(20)   # Cash accumulation target, not an operating expense.


def budget(eligible_fraction, volume=TOTAL, beta=BETA, variable_rate=VARIABLE_RATE):
    eligible=eligible_fraction*volume
    fee=TAU*eligible
    public=beta*fee
    retained=fee-public
    variable=variable_rate*volume  # Includes processed exempt principal as well.
    operating=retained-variable-FIXED_COST
    margin_rate=(1-beta)*TAU*eligible_fraction-variable_rate
    threshold=(FIXED_COST+RESERVE_TARGET)/margin_rate if margin_rate>0 else None
    return dict(processed_principal=float(volume),eligible_fraction=float(eligible_fraction),
                eligible_principal=float(eligible),service_fee=float(fee),
                payer_total_excluding_external_extras=float(volume+fee),
                public_allocation=float(public),platform_retained=float(retained),
                hypothetical_variable_cost=float(variable),fixed_cost=float(FIXED_COST),
                operating_cash_surplus=float(operating),reserve_target=float(RESERVE_TARGET),
                cash_after_reserve_target=float(operating-RESERVE_TARGET),
                positive_scale_margin=margin_rate>0,
                break_even_volume_including_reserve=float(threshold) if threshold is not None else None)


scopes={
    'all_principal':budget(F(1)),
    'promotion_sales_tips':budget(F(9,10)),
    'sales_tips_only':budget(F(7,10)),
}
assert scopes['all_principal']['platform_retained']==250
assert scopes['all_principal']['cash_after_reserve_target']==-50
assert scopes['promotion_sales_tips']['cash_after_reserve_target']==-75
assert scopes['sales_tips_only']['cash_after_reserve_target']==-125
assert F(1)-(VARIABLE_RATE*TOTAL+FIXED_COST+RESERVE_TARGET)/(TAU*TOTAL)==F(2,5)

# Explicit once-per-underlying-settlement fee: internal book transfers do not
# constitute new service settlements. This toy identifier rule is not anti-fraud.
seen=set();settlements=[]
for event,principal in [('storage-period-1',F(1000)),('promotion-round-1',F(2000)),
                        ('sale-order-1',F(7000)),('sale-order-1',F(7000))]:
    accepted=event not in seen
    if accepted:seen.add(event)
    settlements.append(dict(event=event,accepted_new_settlement=accepted,
                            charged_fee=float(TAU*principal if accepted else 0)))
assert sum(F(str(x['charged_fee'])) for x in settlements)==500
assert sum(BASES.values())+TAU*TOTAL==F(10500)
assert F(3000)+F(7000)+BETA*TAU*TOTAL+(1-BETA)*TAU*TOTAL==F(10500)


def refund_case(release_early, vendor_recovered=False, public_recovered=False):
    """Full principal+service-fee refund by assumed policy, processing cost lost.

    Initial reserve 40. Capture 1050; processor cost 10; vendor principal 1000;
    public allocation 25. No other spending. Recovery precedes customer refund.
    These are assumed cash flows, not provider policy or legal classifications.
    """
    events=[('initial_reserve',F(40)),('capture',F(1050)),('processing',F(-10))]
    if release_early:
        events.extend([('vendor_payout',F(-1000)),('public_award_payout',F(-25))])
        if vendor_recovered:events.append(('recover_vendor',F(1000)))
        if public_recovered:events.append(('recover_public_award',F(25)))
    events.append(('refund_customer',F(-1050)))
    balance=F(0);rows=[]
    for label,delta in events:
        balance+=delta
        rows.append(dict(event=label,delta=float(delta),cash_balance=float(balance)))
    return dict(released_early=release_early,vendor_recovered=vendor_recovered,
                public_recovered=public_recovered,ending_reserve=float(balance),
                reserve_consumed=float(F(40)-balance),
                additional_funding_if_negative=float(max(F(0),-balance)),events=rows)


refund_cases=[refund_case(False),refund_case(True,True,False),
              refund_case(True,True,True),refund_case(True,False,False)]
assert [x['reserve_consumed'] for x in refund_cases]==[10,35,10,1035]

# Deliberately unsafe metric: information-size proxy times collection count.
# The attacker creates no additional modeled public value but adds identities
# and a claimed content item; cost is fully nonrecoverable in this example.
pool=F(250);honest_weights=(F(80),F(20));attack_weight=F(100)
attack_resource_cost=F(1)
attack_fee=TAU*attack_resource_cost
added_pool=BETA*attack_fee
new_pool=pool+added_pool
new_weights=(*honest_weights,attack_weight)
awards=[new_pool*w/sum(new_weights) for w in new_weights]
outlay=attack_resource_cost+attack_fee
assert sum(awards)==new_pool
assert awards[-1]-outlay==F(9917,80)
reward_case=dict(initial_public_pool=float(pool),honest_weights=[80,20],
                 honest_awards_before=[float(pool*w/sum(honest_weights)) for w in honest_weights],
                 fabricated_weight=float(attack_weight),
                 attacker_nonrecoverable_resource_cost=float(attack_resource_cost),
                 attacker_service_fee=float(attack_fee),self_added_public_pool=float(added_pool),
                 total_pool_after=float(new_pool),awards_after=[float(x) for x in awards],
                 attacker_total_outlay=float(outlay),attacker_net=float(awards[-1]-outlay))

# Aggregate means are not promised individual awards. A minimum promise is an
# extra funding obligation, not implied by positive weights in a finite pool.
reward_scale=[dict(eligible_contributors=n,average_if_pool_250=250/n,
                   minimum_principal_to_fund_one_unit_each=float(F(n)/(BETA*TAU)))
              for n in [100,250,1000]]


def preservation(n):
    fixed=F(12);usage=F(3,10)*n;cost=fixed+usage
    return dict(supporters=n,total_resource_cost=float(cost),equal_share=float(cost/n))


preservation_cases=[preservation(n) for n in [2,4,40,400]]
remaining_cap=F(33,10)
renewal_gap=F(12)+F(3,10)*2-2*remaining_cap
assert renewal_gap==6

promotion=[]
for recipients,consenting_budget in [(100,F(3)),(1000,F(12)),(10000,F(0))]:
    principal_cost=F(1)+F(1,50)*recipients
    required_debit=(1+TAU)*principal_cost
    promotion.append(dict(recipients=recipients,resource_quote=float(principal_cost),
                          fee=float(TAU*principal_cost),total_quote=float(required_debit),
                          explicitly_authorized_budget=float(consenting_budget),
                          executable=consenting_budget>=required_debit))
# First round principal is covered by 3, but fee-inclusive debit 3.15 is not.
assert not promotion[0]['executable']
funded_first_round=dict(principal=3.0,fee=0.15,authorized_budget=3.15,executable=True)
assert F(63,20)==(1+TAU)*F(3)

output=Path(__file__).parent
result=dict(scope='Illustrative Q8 design scenarios, no empirical or production claims',
            conventions=dict(service_fee_rate=float(TAU),public_fee_share=float(BETA),
                             fee_is_additive_to_principal=True,
                             costs_and_currency_units='Hypothetical money equivalents; real settlement precision must be specified'),
            fee_scope=scopes,settlements=settlements,
            beta_feasible_at_volume_10000_with_reserve=0.4,
            volume_20000_all_scope=budget(F(1),F(20000)),
            nonpositive_scale_margin_examples=[budget(F(1),variable_rate=v) for v in (F(1,40),F(3,100))],
            refunds=refund_cases,contribution_metric_counterexample=reward_case,
            finite_pool=reward_scale,preservation=preservation_cases,
            renewal_with_two_remaining_at_old_cap=dict(total_cost=12.6,authorized_budget=6.6,gap=float(renewal_gap)),
            promotion_quotes=promotion,first_round_after_explicit_budget_adjustment=funded_first_round,
            verification=['fee allocation and principal conservation',
                          'same settlement not charged twice',
                          'cash-event refund reconciliation',
                          'reward pool conserves funds but admits profitable fabricated scores',
                          'resource renewal and fee-inclusive promotion authorization'])
(output/'autoos-business-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps(dict(fee_scope=scopes,refund_reserve_consumed=[x['reserve_consumed'] for x in refund_cases],
                      reward_case=reward_case,renewal_gap=float(renewal_gap),promotion=promotion),indent=2))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14,4.2),constrained_layout=True)
volumes=list(range(0,30001,500))
for fraction,label in [(F(1),'All principal'),(F(9,10),'Promotion + sales'),(F(7,10),'Sales only')]:
    axes[0].plot(volumes,[budget(fraction,F(v))['cash_after_reserve_target'] for v in volumes],label=label)
axes[0].axhline(0,color='black',linewidth=0.8)
axes[0].set(xlabel='Processed principal per period',ylabel='Cash after costs and reserve target',title='A  Fee base changes the funding threshold')
axes[0].legend(fontsize=8)
labels=['Held until\nrefund','Early payout;\nvendor recovered','Early payout;\nno recovery']
axes[1].bar(labels,[10,35,1035],color=['#359b72','#d89738','#c46751'])
axes[1].set(ylabel='Refund loss / reserve consumed',title='B  Payout timing changes refund exposure')
for i,v in enumerate([10,35,1035]):axes[1].text(i,v+15,str(v),ha='center',fontsize=8)
counts=[100,250,500,750,1000]
axes[2].plot(counts,[250/n for n in counts],marker='o')
axes[2].set(xlabel='Eligible contributors',ylabel='Mean award from a fixed pool of 250',
            title='C  A return channel is not a fixed income')
fig.savefig(output/'autoos-business-tradeoffs.png',dpi=180)
fig.savefig(output/'autoos-business-tradeoffs.svg')
plt.close(fig)
