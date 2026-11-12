"""Q5 finite models of predictive memory, decision calibration and reuse.

All parameters are illustrative. These models do not estimate real biological,
economic or AutoOS performance, and do not simulate a physical memory device.
Run this file to regenerate the companion JSON and static research figure.
"""
from fractions import Fraction
import json
import math
from pathlib import Path


def entropy_bits(p):
    return -sum(x*math.log2(x) for x in p if x > 0)


def kl_nats(p, q):
    return sum(x*math.log(x/y) for x, y in zip(p, q) if x > 0)


def aged_memory(flip, age):
    match = (1 + (1 - 2*flip)**age)/2
    # Independently propagate the binary transition matrix from a known state.
    state = [1.0, 0.0]
    for _ in range(age):
        state = [state[0]*(1-flip)+state[1]*flip,
                 state[0]*flip+state[1]*(1-flip)]
    assert math.isclose(state[0], match, abs_tol=1e-12)
    return dict(flip_probability=flip, age=age, memory_entropy_bits=1.0,
                predictive_mutual_information_bits=1-entropy_bits([match,1-match]),
                copy_success=match, best_binary_decoding_success=max(match,1-match))


memory = [aged_memory(flip, age) for flip in (0.0,0.1,0.25,0.5,0.9)
          for age in (1,2,5,10,20)]


def growth_advantage(reliability, allocation):
    return reliability*math.log(2*allocation)+(1-reliability)*math.log(2*(1-allocation))


reliability = 0.8
information_nats = math.log(2)-entropy_bits([reliability,1-reliability])*math.log(2)
calibration = []
for allocation in (0.5,0.6,0.8,0.95,0.99):
    gain = growth_advantage(reliability,allocation)
    regret = kl_nats([reliability,1-reliability],[allocation,1-allocation])
    assert math.isclose(information_nats-gain,regret,abs_tol=1e-12)
    calibration.append(dict(true_signal_reliability=reliability,
                            allocation_to_signalled_type=allocation,
                            information_nats=information_nats,
                            gross_log_growth_advantage_per_round=gain,
                            mismatch_regret_nats=regret))


F = Fraction
costs = dict(build=F(12), execution=F(1), whole_setup=F(4),
             whole_maintenance=F(1,5), whole_validation=F(4,5),
             modular_setup=F(7), modular_maintenance=F(2,5),
             modular_validation_total=F(6,5), assembly_per_task=F(3,10),
             wrong_output_penalty=F(20))


def lifecycle(horizon, change):
    c = costs
    survival = (1-change)**2  # Two independently changing reusable sub-results.
    scratch = horizon*(c['build']+c['execution'])
    common = c['build']+horizon*c['execution']
    wrong = sum(1-survival**k for k in range(horizon))
    naive_cost = common+c['whole_setup']+(horizon-1)*c['whole_maintenance']
    naive = naive_cost+c['wrong_output_penalty']*wrong
    whole = common+c['whole_setup']+(horizon-1)*(c['whole_maintenance']+
              c['whole_validation']+c['build']*(1-survival))
    modular = common+c['modular_setup']+horizon*c['assembly_per_task']+(horizon-1)*(
              c['modular_maintenance']+c['modular_validation_total']+c['build']*change)
    # Exact enumeration of the four possible changes during one interval.
    events = [(mask,change**mask.bit_count()*(1-change)**(2-mask.bit_count())) for mask in range(4)]
    assert sum(prob for _,prob in events)==1
    assert sum(prob*c['build']*(mask!=0) for mask,prob in events)==c['build']*(1-survival)
    assert sum(prob*c['build']/2*mask.bit_count() for mask,prob in events)==c['build']*change
    # Independent absorbing-invalidity recursion for the unvalidated cache.
    states = {0:F(1)}
    wrong_dp = F(0)
    for step in range(horizon):
        wrong_dp += sum(prob for mask,prob in states.items() if mask)
        if step < horizon-1:
            nxt = {}
            for old,p_old in states.items():
                for new,p_new in events:
                    mask = old|new
                    nxt[mask]=nxt.get(mask,F(0))+p_old*p_new
            states=nxt
    assert wrong==wrong_dp
    assert whole-scratch == c['whole_setup']-(horizon-1)*(
        c['build']*survival-c['whole_maintenance']-c['whole_validation'])
    qualified = {'from_scratch':scratch,'validated_whole':whole,'validated_modular':modular}
    best = min(qualified.values())
    return dict(horizon=horizon,per_module_change_probability=float(change),
                from_scratch_cost=float(scratch),unvalidated_cost_before_error_penalty=float(naive_cost),
                unvalidated_expected_wrong_outputs=float(wrong),
                unvalidated_penalized_cost=float(naive),validated_whole_cost=float(whole),
                validated_modular_cost=float(modular),
                best_among_three_verified_policies=[k for k,v in qualified.items() if v==best],
                expected_wrong_outputs_for_qualified_policies=0.0)


reuse = [lifecycle(horizon,change) for horizon in (1,2,5,20,100)
         for change in (F(0),F(1,100),F(1,10),F(3,10),F(4,5),F(1))]
retrieval = []
for library_size in (1,10,100):
    search = F(1,5)*F(library_size+1,2)
    saving = costs['build']*F(9,10)**2-costs['whole_maintenance']-costs['whole_validation']-search
    retrieval.append(dict(candidate_count=library_size,expected_linear_search_cost=float(search),
                          per_reuse_saving_margin=float(saving),
                          assumptions='one relevant item uniformly located; fixed cost per inspected candidate; other costs unchanged'))

n_users=10
error_rate=F(1,100)
independent_distribution={k:F(math.comb(n_users,k))*error_rate**k*(1-error_rate)**(n_users-k)
                          for k in range(n_users+1)}
shared_distribution={0:1-error_rate,n_users:error_rate}
def moments(distribution):
    mean=sum(F(k)*p for k,p in distribution.items())
    variance=sum((F(k)-mean)**2*p for k,p in distribution.items())
    return dict(mean_affected=float(mean),variance_affected=float(variance),
                probability_all_affected=float(distribution.get(n_users,F(0))))
independent,shared=moments(independent_distribution),moments(shared_distribution)
assert independent['mean_affected']==shared['mean_affected']
assert math.isclose(shared['variance_affected'],n_users*independent['variance_affected'])
result = dict(scope='project-created finite models; no physical energy or market-price mapping',
              memory=memory,calibration=calibration,
              irrelevant_prediction=dict(environment_components='independent U and V; U is iid fair; V has flip probability 0.1',
                  remembered_component='previous V',task='predict current U',
                  memory_entropy_bits=1.0,information_about_full_next_environment_bits=1-entropy_bits([0.1,0.9]),
                  information_about_task_target_bits=0.0,best_task_success=0.5),
              reuse_cost_parameters={k:float(v) for k,v in costs.items()},reuse=reuse,retrieval=retrieval,
              switching_cases=[dict(remaining_uses=r,avoidable_old_cost_per_use=5,
                                    new_cost_per_use=3,switching_cost=5,already_paid_setup=f,
                                    future_keep_cost=5*r,future_switch_cost=5+3*r,
                                    switch_cheaper=(5+3*r<5*r))
                               for r in (1,10) for f in (0,100)],
              shared_error=dict(users=n_users,marginal_error_probability=float(error_rate),
                                independent_versions=independent,one_shared_error=shared),
              verification=['binary transition matrix vs closed form','log-growth/KL identity',
                            'exact rational enumeration of change events','invalidity recursion vs geometric sum',
                            'whole-cache break-even identity','common-error vs independent-error moments'])
output=Path(__file__).parent
(output/'memory-reuse-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'calibration':calibration,'reuse_horizon_20':[c for c in reuse if c['horizon']==20],
                  'retrieval':retrieval,'checks':result['verification']},indent=2))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(14,4.2),constrained_layout=True)
ages=list(range(1,21))
for flip in (0.1,0.25,0.5):
    axes[0].plot(ages,[aged_memory(flip,k)['predictive_mutual_information_bits'] for k in ages],label=f'Flip probability {flip}')
axes[0].axhline(1,color='black',linestyle=':',label='Stored marginal entropy')
axes[0].set(xlabel='Age of retained state (steps)',ylabel='Information (bits)',title='A  Perfect retention, changing environment',ylim=(-0.03,1.05))
axes[0].legend(fontsize=8)
qs=[0.5+i*0.499/300 for i in range(301)]
axes[1].plot(qs,[growth_advantage(reliability,q) for q in qs],label='Gross advantage')
axes[1].axhline(0,color='black',linestyle=':')
axes[1].axvline(reliability,color='green',linestyle='--',label='True reliability 0.8')
axes[1].set(xlabel='Allocation to signalled type',ylabel='Log-growth advantage (nats / round)',title='B  Same signal, different decisions')
axes[1].legend(fontsize=8)
ds=[F(i,100) for i in range(101)]
cs=[lifecycle(20,d) for d in ds]
for key,label in [('from_scratch_cost','From scratch'),('validated_whole_cost','Validate whole cache'),
                  ('validated_modular_cost','Validate modules'),('unvalidated_penalized_cost','No validation, penalty included')]:
    axes[2].plot([float(d) for d in ds],[c[key] for c in cs],label=label)
axes[2].set(xlabel='Breaking-change probability per module / interval',ylabel='Total abstract loss units',
            title='C  Same 20 tasks, lifecycle comparison')
axes[2].legend(fontsize=8)
fig.savefig(output/'memory-reuse-tradeoffs.png',dpi=180)
fig.savefig(output/'memory-reuse-tradeoffs.svg')
plt.close(fig)
