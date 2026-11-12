"""Assumed finite examples, not estimates or AutoOS operating policies."""
from fractions import Fraction as F
from pathlib import Path
import json


def incentive_finance():
    cost, own, success_cash = F(100), F(20), F(150)
    p_good, p_bad, private_benefit = F(4, 5), F(2, 5), F(24)
    residual = private_benefit / (p_good - p_bad)
    pledgeable = p_good * (success_cash - residual)
    return {"investment": float(cost), "own_cash": float(own),
            "expected_project_cash_less_cost": float(p_good * success_cash - cost),
            "minimum_success_residual": float(residual),
            "maximum_expected_external_payment": float(pledgeable),
            "external_funding_needed": float(cost - own),
            "external_funding_gap": float(cost - own - pledgeable),
            "minimum_own_cash_in_this_model": float(cost - pledgeable)}


def waiting():
    discount, cost = F(19, 20), F(100)
    states = [(F(1, 2), F(200)), (F(1, 2), F(40))]
    now = discount * sum(p * value for p, value in states) - cost
    wait = discount * sum(p * max(value - cost, 0) for p, value in states)
    return {"discount": float(discount), "investment_cost": float(cost),
            "state_values": [200, 40], "state_probabilities": [0.5, 0.5],
            "invest_now_present_net_cash": float(now),
            "wait_for_information_present_net_cash": float(wait),
            "scope": "One-period information arrival, investment opportunity retained, no delay damage or setup lead time"}


def budget_path(award_schedule, fee_schedule=(40, 20, 20, 40), bridge=False):
    # Signed forecasts identify infeasibility; negative funds never authorize spending.
    public, platform = F(4), F(12)
    beta, platform_cost, maintenance, customer_principal = F(2, 5), F(20), F(12), F(100)
    rows = []
    debt = F(0)
    for t, (fee, award) in enumerate(zip(fee_schedule, award_schedule), 1):
        public_in, platform_in = beta * fee, (1 - beta) * fee
        loan_in, repayment = F(0), F(0)
        if bridge and t == 3:
            loan_in = F(4)
            debt += loan_in
        if bridge and t == 4:
            repayment = debt
            debt = F(0)  # Scheduled repayment, not evidence the funds are available.
        public += public_in + loan_in - maintenance - award - repayment
        platform += platform_in - platform_cost
        rows.append({"period": t, "technical_fee": fee,
            "public_inflow": float(public_in), "platform_inflow": float(platform_in),
            "maintenance_due": float(maintenance), "award_plan": award,
            "bridge_receipt": float(loan_in), "scheduled_principal_repayment": float(repayment),
            "public_signed_forecast_balance": float(public),
            "platform_signed_forecast_balance": float(platform),
            "customer_principal_payable_and_unavailable": float(customer_principal),
            "gross_cash_signed_forecast": float(customer_principal + public + platform)})
    min_public = min(F(4), *(F(str(r["public_signed_forecast_balance"])) for r in rows))
    return {"award_schedule": list(award_schedule), "fee_schedule": list(fee_schedule),
        "initial_public_maintenance_cash": 4, "initial_platform_cash": 12,
        "required_extra_public_cash_for_schedule": float(max(0, -min_public)),
        "public_schedule_feasible": all(r["public_signed_forecast_balance"] >= 0 for r in rows),
        "platform_schedule_feasible": all(r["platform_signed_forecast_balance"] >= 0 for r in rows),
        "rows": rows}


finance, option = incentive_finance(), waiting()
early, late = budget_path((4, 0, 0, 0)), budget_path((0, 0, 0, 4))
bridged = budget_path((4, 0, 0, 0), bridge=True)
weak_recovery = budget_path((4, 0, 0, 0), fee_schedule=(40, 20, 20, 20), bridge=True)
assert finance["expected_project_cash_less_cost"] == 20
assert (finance["maximum_expected_external_payment"], finance["external_funding_gap"]) == (72, 8)
assert (option["invest_now_present_net_cash"], option["wait_for_information_present_net_cash"]) == (14, 47.5)
assert early["required_extra_public_cash_for_schedule"] == 4
assert not early["public_schedule_feasible"] and late["public_schedule_feasible"]
assert bridged["public_schedule_feasible"]
assert not weak_recovery["public_schedule_feasible"]
assert weak_recovery["rows"][-1]["public_signed_forecast_balance"] == -8
assert all(r["gross_cash_signed_forecast"] > 0 for r in early["rows"])

result = {"date_local": "2026-11-12",
    "status": "assumed_teaching_examples_not_empirical_results_or_operating_rules",
    "incentive_finance": finance, "waiting_option": option,
    "public_budget_early_unawarded_recognition": early,
    "public_budget_deferred_unawarded_recognition": late,
    "public_budget_zero_interest_bridge": bridged,
    "public_budget_bridge_with_weaker_recovery": weak_recovery,
    "limits": "All parameters assumed. Award schedules apply only before grants become binding. Zero-interest bridge is arithmetic only. Customer principal stays unavailable. No terminal reserve floor or proof of long-run sustainability."}
path = Path(__file__).resolve().parents[1] / "surveys/08-price-income-and-reinvestment/credit-model-results.json"
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"finance": finance, "waiting": option,
    "early_public_cash_gap": early["required_extra_public_cash_for_schedule"],
    "late_schedule_feasible": late["public_schedule_feasible"],
    "weak_recovery_final_gap": weak_recovery["rows"][-1]["public_signed_forecast_balance"]}, ensure_ascii=False))
