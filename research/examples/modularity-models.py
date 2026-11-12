"""Q4 analytic examples: restart checkpoints and fixed-budget diffusion.

These are project-created models, not replications or empirical estimates.
Run this file to regenerate the JSON and scientific figure beside it.
"""
from fractions import Fraction
import json
import math
from pathlib import Path


def run_wait(n, failure):
    q = 1 - failure
    return Fraction(n) if failure == 0 else (q ** (-n) - 1) / failure


def wait_from_state_equations(n, failure):
    # E_i = 1 + q E_(i+1) + p E_0, E_n = 0.
    constant = coefficient = Fraction(0)
    for _ in range(n):
        constant = 1 + (1 - failure) * constant
        coefficient = failure + (1 - failure) * coefficient
    return constant / (1 - coefficient)


def checkpoint_cost(n, size, failure, overhead):
    assert n % size == 0
    blocks = n // size
    return blocks * run_wait(size, failure) + (blocks - 1) * overhead


n = 12
sizes = [s for s in range(1, n + 1) if n % s == 0]
assembly = []
for p in (Fraction(0), Fraction(1, 1000), Fraction(1, 100),
          Fraction(1, 20), Fraction(1, 10), Fraction(1, 5)):
    for size in sizes:
        assert run_wait(size, p) == wait_from_state_equations(size, p)
    for overhead in (0, 1, 5, 20):
        costs = {s: checkpoint_cost(n, s, p, overhead) for s in sizes}
        best = min(costs.values())
        assembly.append(dict(failure_probability=float(p), overhead_time=overhead,
                             best_block_sizes=[s for s in sizes if costs[s] == best],
                             best_expected_time=float(best),
                             monolithic_expected_time=float(costs[n]),
                             costs_by_block_size={str(s): float(costs[s]) for s in sizes}))


def derivative(x, edges):
    result = [0.0] * 4
    for i, j, w in edges:
        flow = w * (x[j] - x[i])
        result[i] += flow
        result[j] -= flow
    return result


def edges_for(a, b):
    return [(0, 1, a), (2, 3, a)] + [(i, j, b) for i in (0, 1) for j in (2, 3)]


def analytic_state(x, a, b, t):
    mean = sum(x) / 4
    contrast = (x[0] + x[1] - x[2] - x[3]) / 4 * math.exp(-4 * b * t)
    left = (x[0] - x[1]) / 2 * math.exp(-(2 * a + 2 * b) * t)
    right = (x[2] - x[3]) / 2 * math.exp(-(2 * a + 2 * b) * t)
    return [mean + contrast + left, mean + contrast - left,
            mean - contrast + right, mean - contrast - right]


def integrate_rk4(x, edges, dt, time):
    x = list(x)
    steps = round(time / dt)
    assert math.isclose(steps * dt, time)
    for _ in range(steps):
        k1 = derivative(x, edges)
        k2 = derivative([v + dt * k / 2 for v, k in zip(x, k1)], edges)
        k3 = derivative([v + dt * k / 2 for v, k in zip(x, k2)], edges)
        k4 = derivative([v + dt * k for v, k in zip(x, k3)], edges)
        x = [v + dt * (a + 2*b + 2*c + d) / 6
             for v, a, b, c, d in zip(x, k1, k2, k3, k4)]
    return x


budget = 6.0  # Sum of undirected edge weights; units 1/model-time, not joules.
deadline = 1.0
tolerance = 0.02
diffusion = []
max_error = max_step_difference = 0.0
for b in (0.0, 0.05, 0.5, 1.0, 1.4, 1.5):
    a = (budget - 4 * b) / 2
    edges = edges_for(a, b)
    assert math.isclose(sum(w for _, _, w in edges), budget)
    local_rate, global_rate = 2 * a + 2 * b, 4 * b
    for v, rate in [([1, 1, 1, 1], 0), ([1, 1, -1, -1], global_rate),
                    ([1, -1, 0, 0], local_rate), ([0, 0, 1, -1], local_rate)]:
        assert all(math.isclose(d, -rate * z, abs_tol=1e-12)
                   for d, z in zip(derivative(v, edges), v))
    x0 = [1.0, 0.2, -0.3, 0.7]
    exact = analytic_state(x0, a, b, deadline)
    coarse = integrate_rk4(x0, edges, 0.002, deadline)
    fine = integrate_rk4(x0, edges, 0.001, deadline)
    max_error = max(max_error, max(abs(x-y) for x, y in zip(fine, exact)))
    max_step_difference = max(max_step_difference, max(abs(x-y) for x, y in zip(fine, coarse)))
    assert math.isclose(sum(exact), sum(x0), abs_tol=1e-12)
    d = derivative(x0, edges)
    assert math.isclose(sum(x*y for x, y in zip(x0, d)),
                        -sum(w*(x0[i]-x0[j])**2 for i,j,w in edges), abs_tol=1e-12)
    local_error, global_error = math.exp(-local_rate*deadline), math.exp(-global_rate*deadline)
    pulse = analytic_state([1.0, 0.0, 0.0, 0.0], a, b, deadline)
    remote_mean = (pulse[2] + pulse[3]) / 2
    assert math.isclose(remote_mean, (1 - math.exp(-global_rate*deadline))/4, abs_tol=1e-12)
    diffusion.append(dict(a=a, b=b, budget=budget, local_rate=local_rate,
                          global_rate=global_rate,
                          local_normalized_error_at_deadline=local_error,
                          global_normalized_contrast_at_deadline=global_error,
                          local_task_pass=local_error <= tolerance,
                          global_task_pass=global_error <= tolerance,
                          remote_mean_after_unit_pulse=remote_mean))

assert max_error < 1e-10
assert max_step_difference < 1e-9
lower = math.log(1/tolerance)/(4*deadline)
upper = (budget - math.log(1/tolerance)/deadline)/2

# Same block means but different derivatives when cross-boundary totals differ.
heterogeneous_edges = [(0, 1, 1.0), (2, 3, 1.0), (0, 2, 0.2)]
closure_example = []
for x in ([1.0, -1.0, 0.0, 0.0], [0.0]*4):
    d = derivative(x, heterogeneous_edges)
    closure_example.append(dict(state=x, block_means=[(x[0]+x[1])/2, (x[2]+x[3])/2],
                                block_mean_derivatives=[(d[0]+d[1])/2, (d[2]+d[3])/2]))

output = Path(__file__).parent
result = dict(scope='project-created analytic examples, not observations or paper replications',
              assembly=dict(useful_steps=n, possible_block_sizes=sizes, cases=assembly,
                            assumptions='independent failures per attempted useful step; current block resets; completed blocks never fail; deterministic overhead is interruption-free'),
              diffusion=dict(budget=budget, deadline=deadline, tolerance=tolerance, cases=diffusion,
                             simultaneous_task_feasible_b_interval=[lower, upper],
                             nonclosing_block_mean_example=closure_example),
              verification=dict(exact_fraction_state_equations=True, eigenmodes_verified=True,
                                conservation_and_dissipation_verified=True,
                                rk4_max_error_against_analytic=max_error,
                                rk4_step_halving_max_difference=max_step_difference))
(output/'modularity-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
print(json.dumps({'assembly_p_0.1': [c for c in assembly if c['failure_probability']==0.1],
                  'diffusion':diffusion,'feasible_b':[lower,upper],'checks':result['verification']},indent=2))

# Static research figure, regenerated from the same declared parameters.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
bs = [budget/4*i/300 for i in range(301)]
axes[0].plot(bs,[math.exp(-(budget-2*b)*deadline) for b in bs],label='Within-block discrepancy')
axes[0].plot(bs,[math.exp(-4*b*deadline) for b in bs],label='Between-block contrast')
axes[0].axhline(tolerance,color='black',linestyle=':',label='Task threshold 0.02')
axes[0].axvspan(lower,upper,color='green',alpha=0.12)
axes[0].set(xlabel='Cross-block weight b (1 / model time)',ylabel='Normalized remainder at t = 1',
            yscale='log',title='A  Fixed total coupling weight B = 6')
axes[0].legend(fontsize=8)
hs = [i/10 for i in range(201)]
for size in sizes:
    axes[1].plot(hs,[float(checkpoint_cost(n,size,Fraction(1,10),Fraction(str(h)))) for h in hs],label=f'Block size {size}')
axes[1].set(xlabel='Checkpoint overhead h (model time)',ylabel='Expected completion time',
            title='B  12 useful steps, failure probability 0.1',ylim=(10,65))
axes[1].legend(fontsize=8,ncol=2)
fig.savefig(output/'modularity-tradeoffs.png',dpi=180)
fig.savefig(output/'modularity-tradeoffs.svg')
plt.close(fig)
