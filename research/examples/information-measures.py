"""Q3: exact finite examples, not fits to data or replications of cited papers.

Run from any directory. Writes a companion JSON next to this file.
Entropy uses bits; KL uses natural logarithms. Energies in the two-level example
are dimensionless multiples of k_B T. No physical memory device is simulated.
"""
import json
import math
from collections import Counter
from itertools import product
from pathlib import Path


def entropy(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


def kl(p, q):
    return sum(x * math.log(x / y) for x, y in zip(p, q) if x > 0)


channels = []
for accuracy in (1.0, 0.75, 0.5, 0.25, 0.0):
    joint = [accuracy / 2, (1 - accuracy) / 2,
             (1 - accuracy) / 2, accuracy / 2]
    mutual = 2.0 - entropy(joint)
    assert math.isclose(mutual, 1 - entropy([accuracy, 1 - accuracy]), abs_tol=1e-12)
    channels.append(dict(sensor_correct_probability=accuracy,
                         sensor_entropy_bits=1.0,
                         mutual_information_bits=mutual,
                         fixed_copy_policy_success=accuracy,
                         optimal_binary_decoder_success=max(accuracy, 1 - accuracy)))

# Stationary processes; no external clock/phase is supplied to the predictor.
# Predictive states and block entropies are derived from these definitions,
# rather than inferred from finite samples.
processes = []
for name, marginal, state_probs, block in [
    ('constant_zero', [1.0, 0.0], [1.0], lambda n: 0.0),
    ('alternating_random_phase', [0.5, 0.5], [0.5, 0.5], lambda n: 1.0),
    ('iid_fair_bit', [0.5, 0.5], [1.0], lambda n: float(n)),
]:
    processes.append(dict(name=name, symbol_entropy_bits=entropy(marginal),
                          block_entropy_bits={str(n): block(n) for n in (1, 2, 4, 8)},
                          entropy_rate_bits_per_step=block(2) - block(1),
                          predictive_state_entropy_bits=entropy(state_probs)))

# All deterministic maps from two input bits to one output bit, uniform inputs.
target = [a ^ b for a, b in product((0, 1), repeat=2)]
policies = list(product((0, 1), repeat=4))
scores = [sum(x == y for x, y in zip(p, target)) / 4 for p in policies]
counts = Counter(scores)
assert counts == {0.0: 1, 0.25: 4, 0.5: 6, 0.75: 4, 1.0: 1}
functional = []
for threshold in (0.5, 0.75, 1.0):
    count = sum(score >= threshold for score in scores)
    fraction = count / len(policies)
    functional.append(dict(threshold_inclusive=threshold, achieving_policies=count,
                           total_policies=len(policies), reference='uniform over policies',
                           fraction=fraction, functional_information_bits=-math.log2(fraction)))
# Own weighted-reference variant, explicitly not the uniform counting formula.
weighted_variant = dict(reference='mass 1/2 on XOR, remaining 1/2 uniform on other 15 maps',
                        threshold_inclusive=1.0, achieving_probability=0.5,
                        negative_log_probability_bits=1.0)

levels = [0.0, 1.0]
partition = sum(math.exp(-e) for e in levels)
equilibrium = [math.exp(-e) / partition for e in levels]
f_eq = -math.log(partition)
physical = []
for name, p in [('ground_certain', [1.0, 0.0]), ('excited_certain', [0.0, 1.0]),
                ('canonical', equilibrium), ('uniform', [0.5, 0.5])]:
    mean_e = sum(x * e for x, e in zip(p, levels))
    s_over_k = entropy(p) * math.log(2)
    f = mean_e - s_over_k
    divergence = kl(p, equilibrium)
    assert math.isclose(f - f_eq, divergence, abs_tol=1e-12)
    uniform_divergence = kl(p, [0.5, 0.5])
    assert math.isclose(uniform_divergence, math.log(2) - s_over_k, abs_tol=1e-12)
    physical.append(dict(name=name, probabilities=p, entropy_over_kB=s_over_k,
                         mean_energy_over_kBT=mean_e, free_energy_over_kBT=f,
                         excess_free_energy_over_kBT=f - f_eq,
                         kl_to_canonical_nats=divergence,
                         kl_to_uniform_nats=uniform_divergence))

k_b = 1.380649e-23  # SI exact value, J/K
erasure = []
for temperature in (273.15, 300.0):
    energy = k_b * temperature * math.log(2)
    erasure.append(dict(temperature_K=temperature, ideal_erasure_lower_bound_J=energy,
                        one_kWh_divided_by_lower_bound=3.6e6 / energy,
                        interpretation='ideal unbiased-bit erasure count; not stored bits, power, or value'))

result = dict(scope='analytic finite examples; not observations of real organizations',
              channels=channels, processes=processes,
              xor_policy_score_counts={str(k): counts[k] for k in sorted(counts)},
              functional_information=functional, weighted_reference_variant=weighted_variant,
              two_level_canonical_probabilities=equilibrium, two_level_system=physical,
              ideal_erasure_energy=erasure,
              checks='binary channel identity, exact policy counts, canonical free-energy/KL identity, uniform-reference identity')
output = Path(__file__).with_name('information-measures-results.json')
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Exact examples verified; results: {output}')
