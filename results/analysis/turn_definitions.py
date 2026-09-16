#!/usr/bin/env python3
"""Reconcile the two turn counts the artefacts carry under one field name.

The run records and the per-turn regrade both write `n_turns`, and they do not
agree: across the micro-experiment's 800 trajectories they differ on 751 of
them, always with the regrade larger. That looked like a defect -- a regrade is
a grading pass and must not change an observed trajectory property -- and §2.6
carried it as an open oddity for a while. It is not a defect. The two are
different quantities:

  run records   `n_turns` = behavior.n_code_turns   (harness/study2/runner.py)
                          = turns that EMITTED CODE -- "acting turns"
  regrade       `n_turns` = len(traj.steps)         (harness/study2/regrade.py)
                          = every model call, including the closing FINAL:
                            message or refusal, which carries no code

So regrade - records = the number of non-acting turns, and that identity holds
on every trajectory. The trajectories where the two agree are exactly those
that hit the turn ceiling: a run cut off at the ceiling never gets to emit its
closing turn, so it has no non-acting turn to differ by.

The paper reports ACTING TURNS throughout. This script prints the
reconciliation; `tests/test_turn_definitions.py` asserts the identity so the
two definitions cannot silently drift into each other again.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "results" / "analysis"

sys.path.insert(0, str(ANALYSIS))
from _inputs import materialise  # noqa: E402

ARMS = ("neutral", "threatening")


def paired(arm: str) -> list[tuple[dict, dict]]:
    """(record, regrade) for every trajectory present in both files."""
    rec = json.loads((ANALYSIS / f"core_gpt-luna_reinject_{arm}_records.json").read_text())
    reg = json.loads((ANALYSIS / f"core_gpt-luna_reinject_{arm}_regraded.json").read_text())
    key = lambda r: (r["task_id"], r["trial"])  # noqa: E731
    R, G = {key(r): r for r in rec}, {key(r): r for r in reg}
    return [(R[k], G[k]) for k in sorted(set(R) & set(G))]


def acting_turns(regrade: dict) -> int:
    """Acting turns recovered from the regrade's own per-turn diagnostics."""
    return sum(1 for t in regrade["turn_diagnostics"] if t.get("had_code"))


def reconcile(arm: str) -> dict:
    rows = paired(arm)
    identity = sum(
        1 for r, g in rows
        if g["n_turns"] - r["n_turns"] == sum(
            1 for t in g["turn_diagnostics"] if not t.get("had_code")
        )
    )
    return {
        "arm": arm,
        "n": len(rows),
        "differ": sum(1 for r, g in rows if r["n_turns"] != g["n_turns"]),
        "identity_holds": identity,
        "records_is_acting_turns": sum(1 for r, g in rows if r["n_turns"] == acting_turns(g)),
        "agree_and_hit_ceiling": sum(
            1 for r, g in rows if r["n_turns"] == g["n_turns"] and g.get("hit_turn_limit")
        ),
        "agree": sum(1 for r, g in rows if r["n_turns"] == g["n_turns"]),
        "mean_acting": sum(r["n_turns"] for r, _ in rows) / len(rows),
        "mean_calls": sum(g["n_turns"] for _, g in rows) / len(rows),
    }


def main() -> None:
    materialise()
    print("Two turn counts, one field name -- reconciliation (§2.6)\n")
    for arm in ARMS:
        s = reconcile(arm)
        gap = s["mean_calls"] - s["mean_acting"]
        print(f"  {s['arm']}: {s['n']} trajectories, {s['differ']} differ")
        print(f"    records n_turns == acting turns          : {s['records_is_acting_turns']}/{s['n']}")
        print(f"    regrade - records == non-acting turns    : {s['identity_holds']}/{s['n']}")
        print(f"    the {s['agree']} that agree all hit the ceiling : "
              f"{s['agree_and_hit_ceiling']}/{s['agree']}")
        print(f"    mean acting turns {s['mean_acting']:.2f} vs mean model calls "
              f"{s['mean_calls']:.2f}  (+{gap:.2f}, {gap / s['mean_acting']:+.1%})\n")
    print("  The paper reports ACTING TURNS throughout.")


if __name__ == "__main__":
    main()
