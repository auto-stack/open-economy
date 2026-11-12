"""Project-constructed phenomenological model; not biological or thermal measurements."""

from pathlib import Path
import json
import math


PARAMETERS = {"delta": 0.1, "k": 1.0, "d": 0.1, "error_limit": 0.25}
SCENARIOS = [
    {"name": "regulation_without_maintenance", "g": 0.3, "mode": "none", "initial": [0.125, 0.8, 0.8]},
    {"name": "mutual_maintenance", "g": 0.3, "mode": "mutual", "initial": [0.125, 0.8, 0.8]},
    {"name": "maintenance_below_losses", "g": 0.08, "mode": "mutual", "initial": [0.125, 0.8, 0.8]},
    {"name": "one_maintenance_path_removed", "g": 0.3, "mode": "cut_q", "initial": [0.125, 0.8, 0.8]},
    {"name": "no_initial_working_or_repair_capacity", "g": 0.3, "mode": "mutual", "initial": [0.125, 0.0, 0.0]},
]


def derivative(state, scenario):
    error, q, m = state
    g = scenario["g"]
    delta = PARAMETERS["delta"]
    q_gain = g * m * (1 - q) if scenario["mode"] == "mutual" else 0.0
    m_gain = g * q * (1 - m) if scenario["mode"] != "none" else 0.0
    return [PARAMETERS["d"] - PARAMETERS["k"] * q * error,
            q_gain - delta * q, m_gain - delta * m]


def solve(scenario, dt):
    state = scenario["initial"][:]
    sample_steps = {round(t / dt) for t in [0, 5, 10, 20, 50]}
    samples = []
    crossing = None
    for step in range(round(50 / dt) + 1):
        t = step * dt
        if step in sample_steps:
            samples.append({"t": round(t, 10), "error": state[0], "q": state[1], "m": state[2]})
        assert all(math.isfinite(v) for v in state)
        assert state[0] >= -1e-10 and all(-1e-10 <= v <= 1 + 1e-10 for v in state[1:])
        if step == round(50 / dt):
            break
        k1 = derivative(state, scenario)
        k2 = derivative([x + dt * y / 2 for x, y in zip(state, k1)], scenario)
        k3 = derivative([x + dt * y / 2 for x, y in zip(state, k2)], scenario)
        k4 = derivative([x + dt * y for x, y in zip(state, k3)], scenario)
        new = [x + dt * (a + 2*b + 2*c + d) / 6 for x, a, b, c, d in zip(state, k1, k2, k3, k4)]
        limit = PARAMETERS["error_limit"]
        if crossing is None and state[0] <= limit < new[0]:
            crossing = t + dt * (limit - state[0]) / (new[0] - state[0])
        state = new
    return {"samples": samples, "first_error_limit_crossing_approx": crossing}


def symmetric_capacity(t, z0, g, delta):
    if z0 == 0:
        return 0.0
    a = g - delta
    if abs(a) < 1e-14:
        return z0 / (1 + g * z0 * t)
    return z0 * math.exp(a*t) / (1 + g*z0*math.expm1(a*t)/a)


def main():
    results = []
    for scenario in SCENARIOS:
        coarse, fine = solve(scenario, 0.02), solve(scenario, 0.01)
        difference = max(abs(a[key] - b[key])
                         for a, b in zip(coarse["samples"], fine["samples"])
                         for key in ["error", "q", "m"])
        assert difference < 1e-7
        for row in fine["samples"]:
            if scenario["mode"] == "mutual":
                expected = symmetric_capacity(row["t"], scenario["initial"][1], scenario["g"], PARAMETERS["delta"])
                assert abs(row["q"] - expected) < 1e-7
                assert abs(row["m"] - expected) < 1e-7
            else:
                expected_q = scenario["initial"][1] * math.exp(-PARAMETERS["delta"] * row["t"])
                assert abs(row["q"] - expected_q) < 1e-7
        results.append({**scenario, **fine, "max_sample_difference_dt_002_vs_001": difference})
    output = {
        "kind": "project_constructed_model", "empirical_data": False,
        "parameters": PARAMETERS, "integration": "RK4; dt=0.01; horizon=50 abstract time units",
        "scope": "e is task error; q and m are bounded functional capacities, not material or energy quantities. g is an externally conditioned effective maintenance rate. No physical energy budget or biological implementation is modeled. Crossing the task limit is not death.",
        "assumptions": "Maintenance of q by m and of m by q is stipulated. Gains saturate; losses are linear; external conditions and coefficients are fixed; error does not feed back into capacities.",
        "results": results,
    }
    path = Path(__file__).with_name("self-maintenance-results.json")
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        end = row["samples"][-1]
        print(row["name"], "q50=", round(end["q"], 6), "m50=", round(end["m"], 6),
              "error50=", round(end["error"], 6), "first crossing=", row["first_error_limit_crossing_approx"],
              "step difference=", row["max_sample_difference_dt_002_vs_001"])


if __name__ == "__main__":
    main()
