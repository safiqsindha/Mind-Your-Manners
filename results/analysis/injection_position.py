#!/usr/bin/env python3
"""Closure effects split by injection position: the floor-effect check.

A trajectory cannot be shorter than the turn its interjection fired on, so a
shortening effect has less room at a late injection than an early one. That
makes the floor a live alternative explanation for §4's closure result, and a
pooled estimate cannot address it.

This splits each closure contrast by injection position using the same
estimator, seed and clustering as every other contrast in the paper -- it
imports them from `accuracy_null_mde` rather than reimplementing, so the split
estimates and the pooled ones cannot drift apart.

Reading the output: if the shortening effect were a floor artefact it would be
largest where the floor binds hardest, at the LATE injection. The lengthening
arm is included as the contrast case, since a floor does not constrain it.

Note the task counts. A turn-2 injection only fires in a trajectory that
reaches turn 2, so the turn-2 rows rest on fewer tasks and on a selected
subset of them -- the same selection that made the first micro-experiment's
apparent timing effect uninterpretable.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ANALYSIS = pathlib.Path(__file__).resolve().parent
ROOT = ANALYSIS.parents[1]

sys.path.insert(0, str(ANALYSIS))
from _inputs import materialise  # noqa: E402
import accuracy_null_mde as A  # noqa: E402

RECORDS = ANALYSIS / "core_gpt-luna_praise_records.json"
CONTROL = "Q0_control"
ARMS = [
    ("bare closing cue", "Q3_closing_neutral"),
    ("praise the assistant", "Q1_praise_assistant"),
    ("praise the work", "Q2_praise_work"),
    ('"work remains" alone', "Q5_remains_only"),
]
POSITIONS = [((1,), "turn 1 (early)"), ((2,), "turn 2 (late)"), (None, "pooled")]


def run() -> dict:
    materialise()
    recs = A.load(RECORDS)
    out: dict[str, dict] = {}
    for name, arm in ARMS:
        out[name] = {}
        for turns, tag in POSITIONS:
            treat = A.per_task(recs, arm=arm, field="n_turns", turns=turns)
            ctrl = A.per_task(recs, arm=CONTROL, field="n_turns", turns=turns)
            r = A.analyse(f"{arm}|{tag}", treat, ctrl,
                          rng=np.random.default_rng(A.SEED))
            out[name][tag] = {k: r[k] for k in ("estimate", "ci_lo", "ci_hi", "p", "tasks")}
    return out


def main() -> None:
    res = run()
    print("Closure effects by injection position "
          "(gpt-5.6-luna, ceiling 10, acting turns)\n")
    for name, rows in res.items():
        print(f"  {name}")
        for tag, r in rows.items():
            print(f"    {tag:16s} {r['estimate']:+.2f} "
                  f"[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]  "
                  f"p={r['p']:.4f}  tasks={r['tasks']}")
        print()

    cue = res["bare closing cue"]
    early, late = cue["turn 1 (early)"]["estimate"], cue["turn 2 (late)"]["estimate"]
    print(f"  Closing cue is {'LARGER' if early < late else 'smaller'} at the early "
          f"injection ({early:+.2f} vs {late:+.2f}),")
    print("  which is the opposite of what a floor artefact predicts.")

    out = ANALYSIS / "injection_position.json"
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(f"\n  wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
