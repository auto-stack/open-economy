"""Reproduce the L240 trial audit. Run this file from any directory (Python + openpyxl)."""

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from statistics import mean

from openpyxl import load_workbook


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "wiki/raw/round-55/L240-wisdom-dyads/mmc2.xlsx"
ARCHIVE = ROOT / "wiki/raw/round-56"
SHEETS = ("Experiment1", "Experiment2", "Experiment3a", "Experiment3b")
LIMIT = 120
SCALE = 128
RADII = (0, 1, 5, 10)  # integer units of 1/100 world coordinate
SEED = 610240


def target_tick(value):
    tick = round(value * 100)
    assert abs(value * 100 - tick) < 1e-8
    return tick


@dataclass
class Trial:
    row: int
    dyad: int
    block: int
    trial: int
    condition: str
    members: tuple
    angles: tuple
    target: tuple
    error: tuple
    seconds: float
    speech: str
    agreement: str

    @classmethod
    def read(cls, row, d):
        error = tuple(SCALE * d["Error_Coord" + axis] for axis in "XY")
        target = tuple(target_tick(d["Target_Coord" + axis]) for axis in "XY")
        for axis, e in zip("XY", error):
            assert abs(SCALE * (d["Judgment_Coord" + axis] - d["Target_Coord" + axis]) - e) < 0.001
        assert abs(math.hypot(*error) - math.hypot(d["Error_Right-Left_mm"], d["Error_Depth_mm"])) < 1e-8
        return cls(row, d["Dyad#"], d["Block"], d["Trial"], d["Condition"].lower(),
                   (d["Subject1#"], d["Subject2#"]), (d["Viewpoint1_Azimuth"], d["Viewpoint2_Azimuth"]),
                   target, error, d["Rt"], d["Communication"], d["AggrementType"])

    @property
    def valid(self):
        agreed = self.condition != "joint" or self.agreement in ("Consensual", "Consentual")
        return 0 <= self.seconds <= LIMIT and agreed


def unit(angle):
    return math.cos(math.radians(angle)), math.sin(math.radians(angle))


def metrics(a, b, orthogonal):
    ax, ay = a.error
    bx, by = b.error
    estimates = {"midpoint": math.hypot((ax + bx) / 2, (ay + by) / 2),
                 "single_mean": (math.hypot(ax, ay) + math.hypot(bx, by)) / 2,
                 "parallel_seconds": max(a.seconds, b.seconds)}
    if orthogonal:
        u, v = unit(a.angles[0]), unit(b.angles[0])
        assert abs(u[0] * v[0] + u[1] * v[1]) < 1e-9
        p, q = ax * u[0] + ay * u[1], bx * v[0] + by * v[1]
        estimates["lateral_axes"] = math.hypot(p * u[0] + q * v[0], p * u[1] + q * v[1])
    return estimates


def nearest(pool, target):
    def distance_sq(t):
        return sum((x - y) ** 2 for x, y in zip(t.target, target))
    chosen = min(pool, key=lambda t: (distance_sq(t), t.row))
    return chosen, distance_sq(chosen)


def means(rows):
    return {key: mean(r[key] for r in rows) for key in rows[0]}


def by_dyad(entries):
    blocks = defaultdict(list)
    for dyad, block, values in entries:
        blocks[dyad, block].append(values)
    dyads = defaultdict(list)
    for (dyad, _block), rows in blocks.items():
        dyads[dyad].append(means(rows))
    return {dyad: means(rows) for dyad, rows in dyads.items()}


def contrast(values):
    vals = list(values)
    rng = random.Random(SEED)
    bootstrap = sorted(sum(rng.choices(vals, k=len(vals))) / len(vals) for _ in range(10000))
    leave_one_out = [(sum(vals) - v) / (len(vals) - 1) for v in vals] if len(vals) > 1 else []
    return {"diff_mean": mean(vals), "n_joint_lower": sum(v < 0 for v in vals),
            "bootstrap95": [bootstrap[249], bootstrap[9749]],
            "leave_one_out_range": [min(leave_one_out), max(leave_one_out)] if leave_one_out else None}


def summary(entries, intervals):
    data = by_dyad(entries)
    if not data:
        return {"dyads": 0}
    estimates = means(list(data.values()))
    out = {"dyads": len(data), "means": estimates, "contrasts": {}}
    for rule in ("midpoint", "lateral_axes"):
        if rule in estimates:
            delta = [v["joint"] - v[rule] for v in data.values()]
            out["contrasts"][rule] = contrast(delta) if intervals else {"diff_mean": mean(delta)}
    return out


def analyze(sheet, ledger):
    rows = sheet.values
    headers = next(rows)
    design = Counter()
    joint_blocks = defaultdict(list)
    solo = defaultdict(list)
    joint_status = Counter()
    solo_status = Counter()
    for index, row in enumerate(rows, 2):
        d = dict(zip(headers, row))
        condition = d["Condition"].lower()
        design[condition] += 1
        if condition == "id":
            continue
        t = Trial.read(index, d)
        if condition == "joint":
            joint_blocks[t.dyad, t.block].append(t)
            joint_status[f"{t.agreement}|{'over' if t.seconds > LIMIT else 'within'}"] += 1
        else:
            assert condition in ("is-pre", "is-post") and t.members[1] == 0
            solo_status["within" if t.valid else "outside"] += 1
            if t.valid:
                solo[t.dyad, t.members[0], t.angles[0]].append(t)

    orthogonal = sheet.title in SHEETS[:2]
    sizes = Counter()
    one_or_more = one_or_more_valid = independent_pairs = 0
    independent_pair_ids = []
    tiers = {r: [] for r in RADII}
    used = {r: [] for r in RADII}
    summaries = []
    for (dyad, block), trials in sorted(joint_blocks.items()):
        j = trials[0]
        assert all((t.members, t.angles, t.speech) == (j.members, j.angles, j.speech) for t in trials)
        assert (abs(j.angles[1] - j.angles[0]) == 90) if orthogonal else (j.angles[0] == j.angles[1])
        pools = [solo[dyad, sid, angle] for sid, angle in zip(j.members, j.angles)]
        phases = {t.condition for pool in pools for t in pool}
        assert len(phases) == 1 and all(t.block == block for pool in pools for t in pool)
        assert all(len(pool) == 20 for pool in pools) and len(trials) == 20
        phase = phases.pop()
        valid = [t for t in trials if t.valid]
        combos = list(product(*pools))
        for a, b in combos:
            if a.target == b.target:
                independent_pairs += 1
                independent_pair_ids.append([dyad, block, a.row, b.row, list(a.target)])
        estimates = means([metrics(a, b, orthogonal) for a, b in combos])
        estimates.update(joint=mean(math.hypot(*t.error) for t in valid),
                         joint_seconds=mean(t.seconds for t in valid))
        summaries.append({"dyad": dyad, "block": block, "phase": phase, "speech": j.speech,
                          "joint_all": len(trials), "joint_valid": len(valid), "independent_pairs": len(combos),
                          "means": estimates})
        for t in trials:
            (a, da), (b, db) = [nearest(pool, t.target) for pool in pools]
            size = max(da, db)
            one_or_more += min(da, db) == 0
            one_or_more_valid += t.valid and min(da, db) == 0
            sizes["joint_valid"] += t.valid
            for radius in RADII:
                if size <= radius ** 2:
                    sizes[f"before_screen_r{radius}"] += 1
                    if t.valid:
                        result = metrics(a, b, orthogonal)
                        result.update(joint=math.hypot(*t.error), joint_seconds=t.seconds)
                        tiers[radius].append((dyad, block, result))
                        used[radius].extend([a.row, b.row])
            ledger.writerow([sheet.title, dyad, block, phase, j.speech, t.trial, t.row, *j.members,
                             *j.angles, *t.target, int(t.valid), t.seconds, t.agreement,
                             a.row, *a.target, da, b.row, *b.target, db])
    coverage = {}
    for r in RADII:
        sample = tiers[r]
        coverage[r] = {"before_screen": sizes[f"before_screen_r{r}"], "valid_rows": len(sample),
                       "blocks": len({(d, b) for d, b, _ in sample}),
                       "unique_solo_rows": len(set(used[r])), "solo_uses": len(used[r]),
                       **summary(sample, False)}
    strata = {}
    for label in ("all", "is-pre", "is-post", "Com", "No-Com"):
        entries = [(s["dyad"], s["block"], s["means"]) for s in summaries
                   if label in ("all", s["phase"], s["speech"])]
        strata[label] = summary(entries, True)
    return {"condition_rows": dict(design), "joint_screen": dict(joint_status),
            "joint_valid": sizes["joint_valid"], "solo_screen": dict(solo_status),
            "joint_exactly_at_least_one_member": one_or_more,
            "joint_valid_exactly_at_least_one_member": one_or_more_valid,
            "independent_same_target_pairs": independent_pairs, "independent_exact_rows": independent_pair_ids,
            "nearest": coverage, "distributional": strata, "blocks": summaries}


def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert digest == "2bd19b101608ebd2d212327f2809f404bd960191bbb393f2e930c90f2d2d6842"
    workbook = load_workbook(SOURCE, read_only=True, data_only=True)
    ARCHIVE.mkdir(exist_ok=True)
    results = {"source_sha256": digest, "scale_mm": SCALE, "time_limit_seconds": LIMIT,
               "bootstrap_seed": SEED, "bootstrap_repeats": 10000, "sheets": {}}
    with (ARCHIVE / "trial-pairing.tsv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(("sheet dyad block phase speech trial joint_row member1 member2 angle1 angle2 "
                         "target_x_tick target_y_tick valid seconds agreement solo1_row solo1_x_tick "
                         "solo1_y_tick distance1_squared_ticks solo2_row solo2_x_tick solo2_y_tick "
                         "distance2_squared_ticks").split())
        for name in SHEETS:
            results["sheets"][name] = analyze(workbook[name], writer)
    workbook.close()
    (ARCHIVE / "comparison-results.json").write_bytes((json.dumps(results, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
