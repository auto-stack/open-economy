"""Chosen finite examples: inference within a two-model library, not rule invention."""
from functools import lru_cache
from pathlib import Path
import json
import math
import random
import statistics


def chance_match(p):
    return 0.9 - 0.8 * p


def posterior(p, match):
    # Hidden regime1 reverses the old cue mapping; only the noisy observation is given.
    likelihood1 = 0.1 if match else 0.9
    likelihood0 = 0.9 if match else 0.1
    return p * likelihood1 / (p * likelihood1 + (1 - p) * likelihood0)


def predict(p, hazard):
    return hazard + (1 - 2 * hazard) * p


def finite_value(p, horizon, cost):
    """Exact action tree for a fixed hidden regime; a test consumes a whole period."""
    @lru_cache(None)
    def solve(belief, remaining):
        if remaining == 0:
            return 0.0, 'stop'
        a = chance_match(belief)
        use = max(a, 1 - a) + solve(belief, remaining - 1)[0]
        probe = -cost
        for outcome, prob in [(True, a), (False, 1 - a)]:
            probe += prob * solve(posterior(belief, outcome), remaining - 1)[0]
        return (probe, 'probe') if probe > use + 1e-12 else (use, 'act')
    value, first = solve(p, horizon)
    return dict(horizon=horizon, test_cost=cost, expected_total_points=value,
                first_action=first, no_test_value=horizon * max(chance_match(p), 1 - chance_match(p)))


class Observer:
    def __init__(self, hazard):
        self.p = 0.01
        self.hazard = hazard

    def advance(self):
        self.p = predict(self.p, self.hazard)

    def observe(self, match):
        self.p = posterior(self.p, match)

    def rule(self):
        return int(self.p > 0.5)


def run(seed, change_at, interval, hazard, probe_cost):
    rng = random.Random(seed)
    agent = Observer(hazard)
    score = 0.0
    fixed = 0.0
    first_detection = None
    false_alarm = False
    probes = 0
    rows = []
    for t in range(1, 121):
        hidden_regime = int(change_at is not None and t >= change_at)
        # World creates feedback; agent never receives regime, switch time or score.
        match = rng.random() < (0.9 if hidden_regime == 0 else 0.1)
        agent.advance()
        fixed += 0.9 if hidden_regime == 0 else 0.1
        probe = t % interval == 0
        rule_before_feedback = agent.rule()
        if probe:
            probes += 1
            score -= probe_cost  # No task reward in this period: opportunity cost is explicit.
            agent.observe(match)
            if agent.p >= 0.8:
                if hidden_regime == 0:
                    false_alarm = True
                elif first_detection is None:
                    first_detection = t
        else:
            score += 0.9 if rule_before_feedback == hidden_regime else 0.1
        rows.append(dict(t=t, diagnostic=probe, observed_match=match if probe else None,
                         belief_regime1_after_feedback=agent.p, deployed_rule_before_feedback=rule_before_feedback,
                         cumulative_expected_task_points_minus_probe_cost=score))
    return dict(points=score, fixed_old_rule_points=fixed, mixed_rule_points=60.0,
                diagnostic_count=probes, any_false_threshold_crossing=false_alarm,
                detection_delay=None if first_detection is None else first_detection - change_at,
                trace=rows)


def summarize(change_at, interval, hazard, cost):
    trials = [run(seed, change_at, interval, hazard, cost) for seed in range(200)]
    delays = [x['detection_delay'] for x in trials if x['detection_delay'] is not None]
    return dict(change_at=change_at, interval=interval, assumed_hazard=hazard, test_cost=cost,
                simulated_sequences=len(trials), mean_net_points=statistics.mean(x['points'] for x in trials),
                sd_net_points=statistics.stdev(x['points'] for x in trials),
                fixed_old_rule_points=trials[0]['fixed_old_rule_points'], mixed_rule_points=60.0,
                diagnostics_per_sequence=trials[0]['diagnostic_count'],
                false_threshold_path_fraction=statistics.mean(x['any_false_threshold_crossing'] for x in trials),
                detection_path_fraction=None if change_at is None else len(delays) / len(trials),
                mean_delay_among_detected=None if not delays else statistics.mean(delays),
                median_delay_among_detected=None if not delays else statistics.median(delays))


def main():
    # Bayes rule cross-check by enumeration, not a hidden-state lookup.
    assert math.isclose(posterior(0.5, True), 0.1, abs_tol=1e-12)
    assert math.isclose(posterior(0.5, False), 0.9, abs_tol=1e-12)
    short = finite_value(0.5, 1, 0.05)
    assert short['first_action'] == 'act' and math.isclose(short['expected_total_points'], 0.5)
    long = finite_value(0.5, 6, 0.05)
    assert long['first_action'] == 'probe' and long['expected_total_points'] > 3.0
    assert finite_value(0.5, 6, 10)['first_action'] == 'act'
    sample = run(7, 61, 4, 0.02, 0.05)
    expensive = run(7, 61, 4, 0.02, 1.0)
    assert math.isclose(sample['points'] - expensive['points'], 30 * 0.95, abs_tol=1e-10)
    assert all(a['belief_regime1_after_feedback'] == b['belief_regime1_after_feedback']
               for a, b in zip(sample['trace'], expensive['trace']))
    # In the Adams/MacKay Algorithm1 timing, constant hazard makes normalized r_t=0 equal H.
    weights, likelihoods, h = [0.2, 0.3, 0.5], [0.01, 0.2, 0.8], 0.02
    evidence = sum(w * l for w, l in zip(weights, likelihoods))
    reset_posterior = sum(w * l * h for w, l in zip(weights, likelihoods)) / evidence
    assert math.isclose(reset_posterior, h, abs_tol=1e-12)
    result = dict(kind='chosen finite models; no empirical calibration or paper simulation replication',
                  points_unit='task reward points; no conversion to joules, lifespan, money or Ordo',
                  finite_horizon_cases=[finite_value(0.5, n, c) for n in [1, 3, 6] for c in [0.05, 0.5, 10]],
                  online_cases=[summarize(cp, interval, hazard, cost) for cp, interval, hazard, cost in [
                      (61, 4, 0.02, 0.05), (None, 4, 0.02, 0.05), (61, 4, 0.02, 1.0),
                      (61, 8, 0.02, 0.05), (61, 4, 0, 0.05)]],
                  threshold='first post-diagnostic belief>=0.8; not sustained recovery or a physiological event',
                  controller_knows='two likelihoods, initial prior, assumed hazard, fixed observation schedule; no true switch time',
                  controller_does_not_observe='hidden regime, free full outcomes, true reward during task or future observations',
                  online_policy='fixed periodic tests, not a claimed optimal sampling policy',
                  boCPD_constant_hazard_reset_posterior=reset_posterior,
                  example_seed=7, example_trace=sample['trace'])
    (Path(__file__).parent / 'model-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'example_trace'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
