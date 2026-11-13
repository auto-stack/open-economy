"""Finite analytical examples; chosen parameters, not fitted biological data."""
from pathlib import Path
import json
import math


def information(a):
    return math.log(2) + a * math.log(a) + (1 - a) * math.log(1 - a)


def growth(a, q):
    # Environment and cue have uniform marginals; P(environment=cue)=a.
    # Public cue; fraction q matches cue; only matching phenotype multiplies by 2.
    return math.log(2) + a * math.log(q) + (1 - a) * math.log(1 - q)


def mismatch(a, q):
    return a * math.log(a / q) + (1 - a) * math.log((1 - a) / (1 - q))


def main():
    memory = []
    for t in [0.5, 0.8, 0.95]:
        measurement = 0.5 * math.log(t / (1 - t))
        erasure = math.log(2) - measurement
        assert math.isclose(measurement + erasure, math.log(2), abs_tol=1e-12)
        memory.append(dict(volume_fraction=t, measurement_over_kBT=measurement,
                           erasure_over_kBT=erasure, total_over_kBT=measurement + erasure))

    cost_cases = []
    for a, c in [(0.5, 0), (0.9, 0.05), (0.99, 0.75)]:
        gross = growth(a, a)
        assert math.isclose(gross, information(a), abs_tol=1e-12)
        cost_cases.append(dict(cue_match_probability=a, mutual_information_nats=information(a),
                               implementation_penalty_per_step=c, net_log_growth=gross - c))

    before, after = 0.9, 0.1
    delay, pre_steps, post_steps, overhead, update = 5, 30, 30, 0.05, 0.5
    assert math.isclose(information(before), information(after), abs_tol=1e-12)
    loss = mismatch(after, before)
    assert math.isclose(growth(after, after) - growth(after, before), loss, abs_tol=1e-12)
    trajectories = {name: [] for name in ['no_cue', 'frozen', 'revised_after_delay']}
    for step in range(1, pre_steps + post_steps + 1):
        a = before if step <= pre_steps else after
        for name, rows in trajectories.items():
            revise = name == 'revised_after_delay' and step == pre_steps + delay + 1
            q = 0.5 if name == 'no_cue' else (
                after if name == 'revised_after_delay' and step > pre_steps + delay else before)
            c = 0 if name == 'no_cue' else overhead
            value = growth(a, q) - c - (update if revise else 0)
            rows.append(dict(step=step, environment_cue_match=a, fraction_matching_cue=q,
                             expected_log_increment=value,
                             cumulative_expected_log_size=value + (rows[-1]['cumulative_expected_log_size'] if rows else 0)))
    final = {name: rows[-1]['cumulative_expected_log_size'] for name, rows in trajectories.items()}
    advantage = (post_steps - delay) * loss - update
    assert math.isclose(final['revised_after_delay'] - final['frozen'], advantage, abs_tol=1e-10)
    # Sensitivity of revision versus keeping the old policy, with known post-change rule.
    sensitivity = [dict(delay=d, remaining_post_change_steps=post_steps - d,
                        advantage_over_frozen=(post_steps - d) * loss - (update if d < post_steps else 0))
                   for d in [0, 5, 15, 29, 30]]
    result = dict(kind='analytical finite examples, no empirical calibration or author-simulation replication',
                  memory_work_unit='kBT; quasistatic equal-probability memory example',
                  memory=memory, cost_cases=cost_cases,
                  growth_unit='natural-log population multiplier per chosen time step, not joules',
                  parameters=dict(before=before, after=after, pre_steps=pre_steps, post_steps=post_steps,
                                  delay=delay, implementation_penalty=overhead, one_off_revision_penalty=update),
                  information_before_nats=information(before), information_after_nats=information(after),
                  mismatch_loss_per_step=loss, final_expected_log_size=final,
                  revision_advantage_over_frozen=advantage, revision_delay_sensitivity=sensitivity,
                  trajectories=trajectories)
    (Path(__file__).parent / 'model-results.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'trajectories'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
