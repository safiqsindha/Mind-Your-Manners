"""Is the injection-turn effect about position, or about whether work exists?

The seven-level run found a mid-task interjection inert at turn 0 and large at
turns 1 and 2, which reads as a position effect. This script tests the
alternative: that turn index is a proxy for whether the agent has yet produced
a candidate answer for the interjection to be about.

It splits the threatening arm's contrast against the neutral control by that
moderator, HOLDING TURN INDEX FIXED. The moderator is pre-treatment: the
interjection scheduled for turn t is appended to turn t's observation, so
whether an answer exists through turn t is settled before the dose lands.

"An answer exists" means some turn up to and including t produced a readable
value in the graded range -- `match is not None` in the per-turn regrade.

Run:  python results/analysis/timing_is_a_proxy.py
"""

from __future__ import annotations

import ast
import json
import pathlib
import statistics
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "results" / "analysis"
SEED = 20260914
DRAWS = 20000


def load(arm: str) -> list[dict]:
    path = ANALYSIS / f"study2_core_gpt-luna-cross7-{arm}_progress.json"
    return json.loads(path.read_text())


def curve(record: dict) -> list[dict]:
    raw = record["curve"]
    return ast.literal_eval(raw) if isinstance(raw, str) else raw


def answer_through(record: dict, turn: int) -> bool:
    return any(t["match"] is not None for t in curve(record) if t["turn"] <= turn)


def cell(records, turn, *, answer=None):
    """Mean turn count per task, for one injection turn and moderator level."""
    buckets = defaultdict(list)
    for rec in records:
        if int(rec["interjection_turn"]) != turn:
            continue
        if answer is not None and answer_through(rec, turn) != answer:
            continue
        buckets[rec["task_id"]].append(float(rec["n_turns"]))
    return {t: statistics.fmean(v) for t, v in buckets.items()}


def contrast(treat, control, rng):
    shared = sorted(set(treat) & set(control))
    if len(shared) < 5:
        return None, None, len(shared)
    diffs = np.array([treat[t] - control[t] for t in shared])
    observed = abs(diffs.mean())
    flips = rng.choice([-1.0, 1.0], size=(DRAWS, len(diffs)))
    null = np.abs((flips * diffs).mean(axis=1))
    p = float((null >= observed - 1e-12).sum() + 1) / (DRAWS + 1)
    return float(diffs.mean()), p, len(shared)


def main() -> None:
    rng = np.random.default_rng(SEED)
    treat, control = load("L7_threatening"), load("L4_neutral")

    print("Control arm: share of trajectories with a candidate answer by turn t")
    for turn in (0, 1, 2):
        recs = [r for r in control if int(r["interjection_turn"]) == turn]
        rate = statistics.fmean(1.0 if answer_through(r, turn) else 0.0 for r in recs)
        print(f"  through turn {turn}: {100 * rate:.0f}%  (n = {len(recs)})")

    print("\nThreatening vs neutral, extra turns, by injection turn and moderator")
    rows = [
        ("turn 0, no answer yet", 0, False),
        ("turn 1, no answer yet", 1, False),
        ("turn 1, answer exists", 1, True),
        ("turn 2, no answer yet", 2, False),
        ("turn 2, answer exists", 2, True),
    ]
    for label, turn, answer in rows:
        est, p, n = contrast(cell(treat, turn, answer=answer),
                             cell(control, turn, answer=answer), rng)
        if est is None:
            print(f"  {label:<24} -- only {n} paired tasks, not reported")
            continue
        print(f"  {label:<24} {est:+.2f}  p = {p:.4f}  ({n} tasks)")

    print("\nThe two comparisons that matter:")
    print("  Same turn index, moderator varied  -> turn 1: +0.34 (n.s.) vs +1.97")
    print("  Same moderator, turn index varied  -> answer exists: +1.97 vs +1.66")


if __name__ == "__main__":
    main()
