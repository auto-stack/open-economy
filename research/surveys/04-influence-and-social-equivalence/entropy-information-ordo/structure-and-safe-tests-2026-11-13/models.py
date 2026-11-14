"""Finite chosen examples of grammar extension and safety certification; no GP replication."""
from pathlib import Path
import json
import math


def fit_polynomial(rows, degree):
    # Least squares by normal equations, adequate only for this tiny well-conditioned example.
    n = degree + 1
    matrix = [[sum(x ** (i + j) for x, _ in rows) for j in range(n)]
              + [sum(y * x ** i for x, y in rows)] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(matrix[i][k]))
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        assert abs(matrix[k][k]) > 1e-12
        z = matrix[k][k]
        matrix[k] = [v / z for v in matrix[k]]
        for i in range(n):
            if i != k:
                z = matrix[i][k]
                matrix[i] = [a - z * b for a, b in zip(matrix[i], matrix[k])]
    return [row[-1] for row in matrix]


def evaluate(coefficients, x):
    return sum(c * x ** i for i, c in enumerate(coefficients))


class Fixture:
    """Known admissible input range, supplied externally; output is a hidden toy plant."""
    def __init__(self, budget=2):
        self.budget = budget
        self.observations = []

    def query(self, x):
        if not 0 <= x <= 1:
            return None  # Refused without reading the plant or spending budget.
        if self.budget <= 0:
            return None
        self.budget -= 1
        result = x * x
        self.observations.append((x, result))
        return result


def structure_example():
    history = [(0.0, 0.0), (1.0, 1.0)]  # Existing observations; previous costs not charged anew.
    original = fit_polynomial(history, 1)
    fixture = Fixture()
    assert fixture.query(2.0) is None and fixture.budget == 2
    diagnostic_x = 0.5  # Predefined diagnostic design, not an oracle-optimal experiment.
    diagnostic_y = fixture.query(diagnostic_x)
    old_error = abs(evaluate(original, diagnostic_x) - diagnostic_y)
    threshold = 0.1
    rows = history + [(diagnostic_x, diagnostic_y)]
    affine_refit = fit_polynomial(rows, 1)
    affine_error = max(abs(evaluate(affine_refit, x) - y) for x, y in rows)
    # At the midpoint a line predicts the average of its endpoint predictions.
    # If all three errors are at most E, the endpoint-to-midpoint gap is at most 2E.
    assert diagnostic_x == (history[0][0] + history[1][0]) / 2
    midpoint_gap = evaluate(original, diagnostic_x) - diagnostic_y
    minimax_error = abs(midpoint_gap) / 2
    minimax_line = [original[0] - midpoint_gap / 2, original[1]]
    assert all(math.isclose(abs(evaluate(minimax_line, x) - y), minimax_error)
               for x, y in rows)
    grammar = ['1', 'x']
    if minimax_error > threshold:
        grammar.append('x*x')
    expanded = fit_polynomial(rows, len(grammar) - 1)
    validation_x = 0.75  # Not used to fit or generate the expanded model.
    validation_prediction = evaluate(expanded, validation_x)
    validation_y = fixture.query(validation_x)
    assert fixture.query(0.25) is None  # Finite budget has been exhausted.
    assert old_error > threshold and affine_error >= minimax_error > threshold
    assert all(math.isclose(c, target, abs_tol=1e-10) for c, target in zip(expanded, [0, 0, 1]))
    assert math.isclose(validation_prediction, validation_y, abs_tol=1e-10)

    def alternate(x):
        return x * x + x * (x - 0.5) * (x - 0.75) * (x - 1)
    observed = history + fixture.observations
    assert all(math.isclose(alternate(x), y, abs_tol=1e-12) for x, y in observed)
    assert not math.isclose(alternate(0.25), 0.25 ** 2)
    return dict(initial_features=['1', 'x'], generated_features=grammar, threshold=threshold,
                initial_coefficients=original, diagnostic_error=old_error,
                refitted_affine_max_training_error=affine_error,
                affine_minimax_coefficients=minimax_line, affine_minimax_max_error=minimax_error,
                expanded_coefficients=expanded,
                new_observations=fixture.observations, incremental_query_budget=2,
                budget_remaining=fixture.budget, validation_x=validation_x,
                validation_prediction=validation_prediction, validation_observed=validation_y,
                alternate_matches_all_observations=True, unobserved_x=0.25,
                expanded_at_unobserved=0.25 ** 2, alternate_at_unobserved=alternate(0.25),
                output_unit='toy response units; input and response not money, heat or Ordo')


def certificate(observed, domain, lipschitz, threshold):
    return sorted(x for x in domain if any(value - lipschitz * abs(x - z) >= threshold - 1e-12
                                          for z, value in observed.items()))


def safety_example():
    domain = list(range(6))
    truth = [1.2, 1.1, 0.6, 0.1, 0.8, 1.5]
    threshold, valid_lipschitz = 0.5, 0.7
    measured_lipschitz = max(abs(truth[x] - truth[y]) / abs(x - y)
                            for x in domain for y in domain if x != y)
    assert measured_lipschitz <= valid_lipschitz + 1e-12
    observed = {0: truth[0]}  # A reliable, externally supplied initial safe seed.
    queries = []
    budget = 2
    while budget:
        eligible = [x for x in certificate(observed, domain, valid_lipschitz, threshold) if x not in observed]
        if not eligible:
            break
        x = eligible[0]
        observed[x] = truth[x]
        queries.append(x)
        budget -= 1
    safe_set = certificate(observed, domain, valid_lipschitz, threshold)
    assert safe_set == [0, 1]
    assert all(truth[x] >= threshold for x in queries)
    wrong_set = certificate({0: truth[0]}, domain, 0.1, threshold)
    false_safe = [x for x in wrong_set if truth[x] < threshold]
    assert false_safe == [3]
    extra_seed_set = certificate({0: truth[0], 5: truth[5]}, domain, valid_lipschitz, threshold)
    assert extra_seed_set == [0, 1, 4, 5]
    return dict(domain=domain, true_function_for_external_evaluation_only=truth,
                threshold=threshold, valid_lipschitz=valid_lipschitz,
                initial_safe_seed=0, new_queries=queries, remaining_budget=budget,
                certified_set=safe_set, best_certified_value=max(truth[x] for x in safe_set),
                true_global_max=max(truth), underestimated_lipschitz=0.1,
                wrongly_certified_unsafe_points=false_safe,
                certified_with_additional_externally_verified_seed5=extra_seed_set,
                scope='noiseless Lipschitz certificate, not SAFEOPT or a GP safety proof')


def main():
    structure = structure_example()
    safety = safety_example()
    mean, threshold, noise = 0.6, 0.5, [-0.2, 0.2]
    observed = [mean + n for n in noise]
    assert mean >= threshold and min(observed) < threshold
    result = dict(kind='finite chosen examples, no empirical calibration or original-algorithm replication',
                  structure=structure, safety=safety,
                  mean_vs_outcome=dict(mean=mean, threshold=threshold, equally_likely_zero_mean_noise=noise,
                                       outcomes=observed, below_threshold_fraction=0.5),
                  limits=['grammar, variables and diagnostic design supplied externally',
                          'fixture admissibility supplied externally, not inferred from fit',
                          'passing finite validation does not identify a unique true function',
                          'static input safety is not dynamic recoverability or social legitimacy'])
    (Path(__file__).parent / 'model-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
