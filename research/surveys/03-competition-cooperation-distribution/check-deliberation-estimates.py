"""Recheck Fig. 1C and compare consensus with four recorded guesses on the same item."""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "wiki/raw/round-63/L268-deliberation/osf"
ANSWERS = dict(enumerate([171, 206, 373, 10800, 37, 7, 236, 48], start=1))
EXCLUDED_GROUPS = {168, 317, 516, 195, 260}


def rows(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as source:
        yield from csv.DictReader(source)


def compare_errors(joint, baseline):
    if math.isclose(joint, baseline, abs_tol=1e-10):
        return "tied"
    return "closer" if joint < baseline else "farther"


def crosscheck():
    initial_by_question = defaultdict(list)
    initial_by_team_item = defaultdict(dict)
    for row in rows("data_experiment_1__by_participant.csv"):
        team, question = int(row["group_id"]), int(row["question_id"])
        if team in EXCLUDED_GROUPS or not row["s1_value"].strip():
            continue
        value = float(row["s1_value"])
        if not math.isfinite(value) or (question == 3 and value > 1000):
            continue
        answers = initial_by_team_item[team, question]
        person = row["subject_id"]
        assert person not in answers
        answers[person] = value
        initial_by_question[question].append(value)

    center = {q: median(v) for q, v in initial_by_question.items()}
    scale = {q: median(abs(x - center[q]) for x in v) for q, v in initial_by_question.items()}
    errors = defaultdict(list)
    tally = {method: dict(closer=0, tied=0, farther=0) for method in ("mean", "best_afterwards")}
    matched_teams = set()
    seen = set()
    example = None
    for row in rows("data_experiment_1__with_features.csv"):
        team, question = int(row["group_id"]), int(row["question_id"])
        assert (team, question) not in seen
        seen.add((team, question))
        if team in EXCLUDED_GROUPS:
            continue
        initial_mean, consensus = float(row["s1_mean_value"]), float(row["consensus_value"])
        if not all(math.isfinite(y) and abs(y - center[question]) <= 2.5 * scale[question]
                   for y in (initial_mean, consensus)):
            continue

        truth = ANSWERS[question]
        independent_error, joint_error = abs(initial_mean - truth), abs(consensus - truth)
        errors[team].append((independent_error / scale[question], joint_error / scale[question]))
        values = list(initial_by_team_item[team, question].values())
        if len(values) != 4 or not math.isclose(mean(values), initial_mean, abs_tol=1e-8):
            continue
        matched_teams.add(team)
        best_error = min(abs(v - truth) for v in values)
        tally["mean"][compare_errors(joint_error, independent_error)] += 1
        tally["best_afterwards"][compare_errors(joint_error, best_error)] += 1
        if team == 70 and question == 2:
            example = dict(group=team, item=question, initial=values, mean=initial_mean,
                           consensus=consensus, correct=truth)

    return {
        "figure_1c": {
            "paired_group_items": sum(len(v) for v in errors.values()),
            "groups": len(errors),
            "normalized_error_independent_mean": mean(mean(x for x, _ in v) for v in errors.values()),
            "normalized_error_consensus": mean(mean(y for _, y in v) for v in errors.values()),
        },
        "complete_four_person_subset": {
            "groups": len(matched_teams), "group_items": sum(tally["mean"].values()),
            "consensus_vs_baseline": tally, "obelisk_example": example,
        },
    }


if __name__ == "__main__":
    print(json.dumps(crosscheck(), indent=2))
