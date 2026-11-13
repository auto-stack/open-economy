"""Recompute the two available feedback conditions from the archived Painter et al. sessions."""

import csv
import json
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.stats import t


ARCHIVE = Path(__file__).resolve().parents[4] / "wiki/raw/round-57"
SOURCE = ARCHIVE / "L243-painter"
OFFSETS = np.array([72, 86, 101, 115])  # 0.5 to 0.8 seconds after the move cue at 144 Hz
LAGS = (14, 29, 43)  # approximately 100, 200 and 300 ms
WINDOW = 7  # average the next seven frame increments


def session(path):
    fields = ["data", "D", "cursor", "array", "LOC_CODE", "mon", "fliptime", "str"]
    d = loadmat(path, variable_names=fields, squeeze_me=True, struct_as_record=False)
    table, cols, cursor = d["data"], d["D"], d["cursor"]
    col = lambda key: table[:, getattr(cols, key) - 1].astype(int)
    assert list(d["str"].cond) == ["solo", "co-op"] and d["mon"].ref == 144
    trial = np.arange(len(table))
    condition, cue = col("cond"), col("move_cue_frame") - 1
    target = d["LOC_CODE"][col("position_combo") - 1, col("location") - 1] - 1
    xy = np.column_stack((d["array"].x[target], d["array"].y[target]))
    lateral = np.column_stack((-xy[:, 1], xy[:, 0])) / np.linalg.norm(xy, axis=1)[:, None]
    cells, counts = np.unique(np.stack((col("block"), target, condition), axis=1), axis=0, return_counts=True)
    assert len(cells) == 15 * 8 * 2 and np.all(counts == 4)
    both_inputs = np.ones(len(table), dtype=bool)
    lost_blocks = []
    for block in np.unique(col("block")):
        mask = col("block") == block
        # All trials flagged as missing a timely response from one player in an entire block.
        silent = np.all(table[mask][:, cols.RT_slow[:2] - 1] == 1, axis=0)
        if silent.any():
            for player in np.flatnonzero(silent):
                assert np.nanmax(abs(cursor.inc[:, :, mask, player])) == 0
            both_inputs[mask] = False
            lost_blocks.append(int(block))
    result = {"session": path.stem, "scheduled": len(table), "trials": int(both_inputs.sum()),
              "excluded_blocks": lost_blocks, "per_block_target_condition": 4,
              "conditions": {}, "mean_delay_ms": {}}
    # Use the same gate and the same third cursor in both conditions. In solo it is invisible.
    correct = table[:, cols.correct[-1] - 1]
    assert np.all(np.isin(correct, [0, 1]))
    frames = cue[:, None] + OFFSETS
    assert np.all(frames[:, -1] + max(LAGS) + WINDOW < col("feedback_frame") - 1)
    inc = cursor.inc
    for f in frames.T:
        sample = inc[:, f, trial, :]
        gate = np.all(np.any(sample[:, :, :2] != 0, axis=0), axis=1)
        combined = sample[:, :, :2].mean(axis=2) * gate
        assert np.allclose(combined, sample[:, :, 2], atol=1e-5)
    pos = cursor.xy[:, frames, trial[:, None], 2]
    side = np.einsum("dno,nd->no", pos, lateral)
    initial_inputs = np.einsum("dnop,nd->nop", inc[:, frames, trial[:, None], :2], lateral)
    clocks = d["fliptime"].trial
    for code, name in [(1, "independent_hidden_joint"), (2, "live_visible_joint")]:
        keep = (condition == code) & both_inputs
        row = {"n": int(keep.sum()), "success_pct": 100 * float(np.mean(correct[keep])),
               "timing": {}}
        for lag in LAGS:
            # Compare each person's later input with the side of the *joint* cursor at the anchor.
            forward = np.stack([inc[:, frames + lag + k, trial[:, None], :2] for k in range(WINDOW)]).mean(axis=0)
            later_inputs = np.einsum("dnop,nd->nop", forward, lateral)
            signed = -np.sign(side)[:, :, None] * later_inputs
            active = keep[:, None] & (np.abs(side) >= 3)
            assert np.isfinite(signed[active]).all() and np.any(active)
            scores = signed[active].mean(axis=0)
            row["timing"][lag] = {"anchors": int(active.sum()), "p1": float(scores[0]),
                                  "p2": float(scores[1]), "mean": float(scores.mean())}
            # Cross both actor directions, retaining task phase. Compare the real trial
            # with all other repeats of the identical target, block and condition.
            aligned, shuffled = [], []
            for block_id, target_id in set(zip(col("block")[keep], target[keep])):
                idx = np.flatnonzero(keep & (col("block") == block_id) & (target == target_id))
                assert len(idx) == 4
                early = initial_inputs[idx]
                later_partner = later_inputs[idx, :, ::-1]
                products = -(early[:, None] * later_partner[None, :]).mean(axis=(2, 3))
                aligned.append(np.diag(products).mean())
                shuffled.append(products[~np.eye(4, dtype=bool)].mean())
            row["timing"][lag]["partner_opposition_minus_cross_trial"] = float(np.mean(aligned) - np.mean(shuffled))
            delta = clocks[frames + lag, trial[:, None]] - clocks[frames, trial[:, None]]
            result["mean_delay_ms"][lag] = float(np.mean(delta) * 1000)
        result["conditions"][name] = row
    return result


def describe(values):
    a = np.asarray(values)
    m = float(a.mean())
    margin = float(t.ppf(.975, len(a) - 1) * a.std(ddof=1) / np.sqrt(len(a)))
    return {"mean": m, "paired_t95": [m - margin, m + margin],
            "positive_dyads": int(np.sum(a > 0))}


def main():
    sessions = [session(f) for f in sorted(SOURCE.glob("S*-behave.mat"))]
    assert len(sessions) == 20
    pairs = [(x["conditions"]["independent_hidden_joint"], x["conditions"]["live_visible_joint"])
             for x in sessions]
    results = {"sessions": sessions, "contrasts": {}}
    results["contrasts"]["accuracy_live_minus_independent_pp"] = describe(
        [live["success_pct"] - solo["success_pct"] for solo, live in pairs])
    for lag in LAGS:
        results["contrasts"][f"input_live_minus_independent_lag_{lag}"] = describe(
            [live["timing"][lag]["mean"] - solo["timing"][lag]["mean"] for solo, live in pairs])
        results["contrasts"][f"partner_opposition_live_minus_independent_lag_{lag}"] = describe(
            [live["timing"][lag]["partner_opposition_minus_cross_trial"]
             - solo["timing"][lag]["partner_opposition_minus_cross_trial"] for solo, live in pairs])
    with (SOURCE / "Fig. 2b.csv").open(encoding="utf-8") as f:
        fig = [r for r in csv.DictReader(f) if r["Control"] == "Joint"]
    # The figure's anonymized pair order need not match the raw S-number order.
    raw_pairs = sorted((r["success_pct"], l["success_pct"]) for r, l in pairs)
    fig_pairs = sorted(tuple(float(next(r["DV"] for r in fig if r["subject_id"] == i and r["Cursor"] == c))
                             for c in ("Invisible", "Visible")) for i in {r["subject_id"] for r in fig})
    assert np.allclose(raw_pairs, fig_pairs)
    (ARCHIVE / "painter-comparison.json").write_bytes((json.dumps(results, indent=2) + "\n").encode())


if __name__ == "__main__":
    main()
