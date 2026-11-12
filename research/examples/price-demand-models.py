"""Finite teaching examples; all parameters assumed, no empirical calibration."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations, permutations
import json


def bargaining(v, cost, budget, seller_disagreement=0, buyer_disagreement=0):
    lower = F(cost + seller_disagreement)
    upper = min(F(v - buyer_disagreement), F(budget))
    if lower > upper:
        return {"agreement_feasible": False, "price": None}
    unconstrained = F(v + cost + seller_disagreement - buyer_disagreement, 2)
    price = max(lower, min(upper, unconstrained))
    buyer_gain = F(v) - price - buyer_disagreement
    seller_gain = price - cost - seller_disagreement
    return {"agreement_feasible": True, "price": float(price),
            "buyer_gain_above_disagreement": float(buyer_gain),
            "seller_gain_above_disagreement": float(seller_gain),
            "product": float(buyer_gain * seller_gain)}


buyers, sellers = [100, 80, 50], [20, 40, 70]
allocations = []
for size in range(4):
    for chosen_buyers in combinations(buyers, size):
        for chosen_sellers in combinations(sellers, size):
            for ordering in permutations(chosen_sellers):
                allocations.append({"units": size,
                    "total_gain": sum(v - c for v, c in zip(chosen_buyers, ordering))})
maximum = max(x["total_gain"] for x in allocations)
assert maximum == 120
assert all(x["units"] == 2 for x in allocations if x["total_gain"] == maximum)
# At interior prices 51..69, exactly two buyers and two sellers strictly accept.
assert all(sum(v > p for v in buyers) == sum(c < p for c in sellers) == 2
           for p in range(51, 70))

cases = {
    "budget100": bargaining(100, 20, 100),
    "budget50": bargaining(100, 20, 50),
    "budget15": bargaining(100, 20, 15),
    "seller_disagreement20_budget100": bargaining(100, 20, 100, 20),
}
assert [cases[k]["price"] for k in cases] == [60.0, 50.0, None, 70.0]

before = F(4, 5) * 20 + F(1, 5) * 80
after = F(4, 5) * 30 + F(1, 5) * 70
autonomous, propensity, capacity = F(20), F(3, 5), F(100)
income = autonomous / (1 - propensity)
assert (before, after, after - before) == (32, 38, 6)
assert income == 50 and income < capacity

result = {
    "date_local": "2026-11-12",
    "status": "assumed_parameter_teaching_examples_not_empirical_results",
    "market": {"buyer_values": buyers, "seller_costs": sellers,
        "one_unit_per_actor": True, "matchings_enumerated": len(allocations),
        "maximum_total_gain": maximum, "maximizing_trade_units": 2,
        "uniform_supporting_price_interval": [50, 70],
        "interval_endpoint_condition": "Indifferent marginal actors may abstain; no uniqueness or convergence claim"},
    "bargaining": cases,
    "fixed_income_distribution": {"income_total": 100,
        "assumed_propensities": [0.8, 0.2], "income_before": [20, 80],
        "income_after": [30, 70], "spending_before": float(before),
        "spending_after": float(after), "difference": float(after - before)},
    "fixed_price_aggregate_example": {"equation": "Y=A+cY", "A": 20,
        "c": 0.6, "capacity": 100, "fixed_point_Y": float(income),
        "scope": "Closed fixed-price teaching model with spare capacity, fixed autonomous spending and behavior; not a policy estimate"}
}
target = Path(__file__).resolve().parents[1] / "surveys/08-price-income-and-reinvestment/model-results.json"
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
