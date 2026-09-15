"""Every contrast this study measured more than once, and what it gave each time.

Section 8's evidence. For each contrast measured on the SAME model more than
once, this prints the per-measurement estimate, its cluster-bootstrap CI and
its task-clustered permutation p, under the estimator of the paper's section
2.4 -- so that direction, significance and magnitude can be checked for
replication separately. They do not behave the same way.

The family is exhaustive by construction: every arm that appears against a
control in more than one run on Luna. It includes the threatening arm, whose
two measurements (the micro-experiment and the seven-level run) use
byte-identical interjection text at the same ceiling.

MATCHED-CEILING PAIRS are reported separately and are the only fair magnitude
comparison: a different turn ceiling is a different instrument, and the arms
that persist longest are the ones a low ceiling truncates hardest. For each
such pair we report the difference in standard errors of the difference, so
that "these two disagree" is a test rather than an impression.

Outcomes covered: turn count (primary), reasoning tokens (secondary),
accuracy, and final match from the per-turn regrade.

Run:  python results/analysis/replication_table.py
"""

from __future__ import annotations

import json
import math
import pathlib
import statistics
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "results_archive"
ANALYSIS = ROOT / "results" / "analysis"
SEED = 20260914
BOOT = 20000


def _bool(v) -> bool:
    return str(v).strip().lower() == "true"


def load(path) -> list[dict]:
    return json.loads(pathlib.Path(path).read_text())


def per_task(records, *, arm=None, field="n_turns", model=None):
    """Mean outcome per task for one arm.

    Trajectories on which the interjection did not fire received no dose and
    are excluded wherever the records say (paper section 2.5). Rows whose
    outcome is unreadable -- `final_match` is None when no turn produced a
    readable value in the graded range -- are dropped and counted.
    """
    buckets = defaultdict(list)
    dropped = 0
    for r in records:
        if arm is not None and r.get("interjection", r.get("arm")) != arm:
            continue
        if model is not None and r.get("model_key") != model:
            continue
        if "interjection_fired" in r and not _bool(r["interjection_fired"]):
            continue
        raw = r[field]
        if raw is None or raw == "None":
            dropped += 1
            continue
        buckets[r["task_id"]].append(
            (1.0 if _bool(raw) else 0.0) if field == "passed" else float(raw)
        )
    return {t: statistics.fmean(v) for t, v in buckets.items() if v}, dropped


def measure(treat, control, rng, *, scale=1.0):
    shared = sorted(set(treat) & set(control))
    diffs = np.array([scale * (treat[t] - control[t]) for t in shared])
    n = len(diffs)
    idx = rng.integers(0, n, size=(BOOT, n))
    boot = diffs[idx].mean(axis=1)
    observed = abs(float(diffs.mean()))
    flips = rng.choice([-1.0, 1.0], size=(BOOT, n))
    null = np.abs((flips * diffs).mean(axis=1))
    return {
        "est": float(diffs.mean()),
        "se": float(boot.std(ddof=1)),
        "lo": float(np.percentile(boot, 2.5)),
        "hi": float(np.percentile(boot, 97.5)),
        "p": float((null >= observed - 1e-12).sum() + 1) / (BOOT + 1),
        "n": n,
    }


def agreement(a, b):
    """Are two measurements of one contrast consistent with a common value?

    z on the difference, treating the runs as independent -- they use the same
    50 tasks, so this is if anything generous to the "they agree" reading.
    """
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2)
    z = (a["est"] - b["est"]) / se if se > 0 else float("inf")
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return z, p


def main() -> None:
    rng = np.random.default_rng(SEED)

    probe = load(ARCHIVE / "core_gpt-luna_probe_records.json")
    praise = load(ARCHIVE / "core_gpt-luna_praise_records.json")
    stage1 = [r for r in load(ARCHIVE / "stage1_cross_model_records.json")
              if r.get("model_key") == "gpt-luna"]
    cross7 = load(ARCHIVE / "core_gpt-luna_cross7_records.json")
    cross7 = [r for r in cross7 if r.get("interjection_turn") in (1, 2)]
    micro_n = load(ARCHIVE / "core_gpt-luna_reinject_neutral_records.json")
    micro_t = load(ARCHIVE / "core_gpt-luna_reinject_threatening_records.json")
    c20c = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q0_control_records.json")
    c20q5 = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q5_remains_only_records.json")

    # (run label, ceiling, (treat records, arm), (control records, arm))
    FAMILIES = {
        "praise vs control": [
            ("probe", 10, (probe, "P2_praise_only"), (probe, "P0_control")),
            ("praise run", 10, (praise, "Q1_praise_assistant"), (praise, "Q0_control")),
            ("stage 1", 20, (stage1, "P2_praise_only"), (stage1, "P0_control")),
        ],
        "demand vs control": [
            ("probe", 10, (probe, "P1_demand_only"), (probe, "P0_control")),
            ("stage 1", 20, (stage1, "P1_demand_only"), (stage1, "P0_control")),
        ],
        "insult vs control": [
            ("probe", 10, (probe, "P3_insult_only"), (probe, "P0_control")),
            ("stage 1", 20, (stage1, "P3_insult_only"), (stage1, "P0_control")),
        ],
        "threatening vs neutral": [
            ("micro-experiment", 10, (micro_t, "L7_threatening"), (micro_n, "L4_neutral")),
            ("seven-level run", 10, (cross7, "L7_threatening"), (cross7, "L4_neutral")),
        ],
        "'work remains' vs control": [
            ("praise run", 10, (praise, "Q5_remains_only"), (praise, "Q0_control")),
            ("dedicated re-run", 20, (c20q5, None), (c20c, None)),
            ("stage 1", 20, (stage1, "Q5_remains_only"), (stage1, "P0_control")),
        ],
    }

    # Progress outcomes live in separate per-arm files from the regrade. They
    # carry no fired flag, so these contrasts are over all rows with a readable
    # final match -- stated in the paper rather than left implicit.
    PROGRESS = {
        "'work remains' vs control": [
            ("praise run", 10, "gpt-luna-praise-Q5_remains_only", "gpt-luna-praise-Q0_control"),
            ("dedicated re-run", 20, "gpt-luna-ceiling20-Q5_remains_only",
             "gpt-luna-ceiling20-Q0_control"),
            ("stage 1", 20, "gpt-luna-s1luna-Q5_remains_only", "gpt-luna-s1luna-P0_control"),
        ],
    }

    for field, unit, scale, fmt in [
        ("n_turns", "turn count", 1.0, "+.2f"),
        ("reasoning_tokens", "reasoning tokens per trajectory", 1.0, "+.0f"),
        ("passed", "accuracy points", 100.0, "+.2f"),
    ]:
        print(f"\n=== {unit} -- Luna, paired and clustered by task ===")
        print(f"{'contrast / measurement':<44}{'ceil':>5}{'est':>10}{'95% CI':>22}"
              f"{'p':>9}{'n':>5}")
        print("-" * 95)
        for label, runs in FAMILIES.items():
            print(label)
            got = []
            for run_label, ceiling, (t_recs, t_arm), (c_recs, c_arm) in runs:
                if field == "reasoning_tokens" and field not in t_recs[0]:
                    continue
                t, _ = per_task(t_recs, arm=t_arm, field=field)
                c, _ = per_task(c_recs, arm=c_arm, field=field)
                if len(set(t) & set(c)) < 5:
                    continue
                m = measure(t, c, rng, scale=scale)
                m["run"], m["ceiling"] = run_label, ceiling
                got.append(m)
                ci = f"[{format(m['lo'], fmt)}, {format(m['hi'], fmt)}]"
                print(f"   {run_label:<41}{ceiling:>5}{format(m['est'], fmt):>10}"
                      f"{ci:>22}{m['p']:>9.4f}{m['n']:>5}")
            summarise(got, fmt)

        if field == "n_turns":
            continue

    print("\n=== final match (per-turn regrade) -- Luna, paired and clustered "
          "by task ===")
    print("   (no fired flag in the regrade outputs: all rows with a readable "
          "final match)")
    print(f"{'contrast / measurement':<44}{'ceil':>5}{'est':>10}{'95% CI':>22}"
          f"{'p':>9}{'n':>5}")
    print("-" * 95)
    for label, runs in PROGRESS.items():
        print(label)
        got = []
        for run_label, ceiling, t_stem, c_stem in runs:
            t, dt = per_task(load(ANALYSIS / f"study2_core_{t_stem}_progress.json"),
                             field="final_match")
            c, dc = per_task(load(ANALYSIS / f"study2_core_{c_stem}_progress.json"),
                             field="final_match")
            m = measure(t, c, rng)
            m["run"], m["ceiling"] = run_label, ceiling
            got.append(m)
            ci = f"[{m['lo']:+.3f}, {m['hi']:+.3f}]"
            print(f"   {run_label:<41}{ceiling:>5}{m['est']:>+10.3f}{ci:>22}"
                  f"{m['p']:>9.4f}{m['n']:>5}   (unreadable dropped: {dt}/{dc})")
        summarise(got, "+.3f")


def summarise(got, fmt):
    if len(got) < 2:
        return
    vals = [m["est"] for m in got]
    sign = "SAME" if all(v > 0 for v in vals) or all(v < 0 for v in vals) else "FLIPS"
    sig = [m["p"] < 0.05 for m in got]
    sig_word = "all" if all(sig) else ("none" if not any(sig) else "SOME")
    print(f"   -> across all measurements: sign {sign}, significant: {sig_word}")
    by_ceiling = defaultdict(list)
    for m in got:
        by_ceiling[m["ceiling"]].append(m)
    for ceiling, pair in sorted(by_ceiling.items()):
        for i in range(len(pair)):
            for j in range(i + 1, len(pair)):
                a, b = pair[i], pair[j]
                z, p = agreement(a, b)
                verdict = "consistent" if p >= 0.05 else "INCONSISTENT"
                print(f"   -> same instrument (ceiling {ceiling}): "
                      f"{a['run']} {format(a['est'], fmt)} vs "
                      f"{b['run']} {format(b['est'], fmt)}  "
                      f"z={z:+.2f}, p={p:.3f} -> {verdict}")


if __name__ == "__main__":
    main()
