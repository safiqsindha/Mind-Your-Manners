"""Every contrast this study measured more than once, and what it gave each time.

Section 8's evidence. For each contrast measured on the SAME model more than
once, this prints the per-measurement estimate, its cluster-bootstrap CI and
its task-clustered permutation p, so that direction, significance and magnitude
can be checked for replication separately -- they do not behave the same way.

Cross-model pairs are printed separately and are NOT counted as replications of
magnitude: a different model is a different instrument.

Run:  python results/analysis/replication_table.py
"""

from __future__ import annotations

import json
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


def load(path):
    return json.loads(path.read_text())


def per_task(records, *, arm=None, field="n_turns", model=None, turns=None):
    buckets = defaultdict(list)
    for r in records:
        if arm is not None and r.get("interjection") != arm:
            continue
        if model is not None and r.get("model_key") != model:
            continue
        if "interjection_fired" in r and not _bool(r["interjection_fired"]):
            continue
        if turns is not None and r.get("interjection_turn") not in turns:
            continue
        raw = r[field]
        buckets[r["task_id"]].append(
            (1.0 if _bool(raw) else 0.0) if field == "passed" else float(raw)
        )
    return {t: statistics.fmean(v) for t, v in buckets.items() if v}


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
        "lo": float(np.percentile(boot, 2.5)),
        "hi": float(np.percentile(boot, 97.5)),
        "p": float((null >= observed - 1e-12).sum() + 1) / (BOOT + 1),
        "n": n,
    }


def report_spread(label, ests):
    vals = [e[1] for e in ests]
    mags = [abs(v) for v in vals]
    spread = max(mags) / min(mags) if min(mags) > 1e-9 else float("inf")
    sign = "SAME" if all(v > 0 for v in vals) or all(v < 0 for v in vals) else "FLIPS"
    sig = [e[2] < 0.05 for e in ests]
    sig_word = "all" if all(sig) else ("none" if not any(sig) else "SOME")
    print(f"   -> {label:<40}{'sign ' + sign:>9}   "
          f"|est| spread {spread:.1f}x   significant: {sig_word}")


def main() -> None:
    rng = np.random.default_rng(SEED)
    probe = load(ARCHIVE / "core_gpt-luna_probe_records.json")
    praise = load(ARCHIVE / "core_gpt-luna_praise_records.json")
    stage1 = load(ARCHIVE / "stage1_cross_model_records.json")
    c20c = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q0_control_records.json")
    c20q5 = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q5_remains_only_records.json")

    # (contrast label, [(run label, treat records+arm, control records+arm), ...])
    families = {
        "praise vs control": [
            ("probe, ceiling 10", (probe, "P2_praise_only"), (probe, "P0_control")),
            ("praise run, ceiling 10", (praise, "Q1_praise_assistant"), (praise, "Q0_control")),
            ("stage 1, ceiling 20", (stage1, "P2_praise_only"), (stage1, "P0_control")),
        ],
        "demand vs control": [
            ("probe, ceiling 10", (probe, "P1_demand_only"), (probe, "P0_control")),
            ("stage 1, ceiling 20", (stage1, "P1_demand_only"), (stage1, "P0_control")),
        ],
        "insult vs control": [
            ("probe, ceiling 10", (probe, "P3_insult_only"), (probe, "P0_control")),
            ("stage 1, ceiling 20", (stage1, "P3_insult_only"), (stage1, "P0_control")),
        ],
        "'work remains' vs control": [
            ("praise run, ceiling 10", (praise, "Q5_remains_only"), (praise, "Q0_control")),
            ("dedicated re-run, ceiling 20", (c20q5, None), (c20c, None)),
            ("stage 1, ceiling 20", (stage1, "Q5_remains_only"), (stage1, "P0_control")),
        ],
    }

    for field, unit, scale in [("n_turns", "turns", 1.0),
                               ("reasoning_tokens", "reasoning tokens", 1.0),
                               ("passed", "accuracy points", 100.0)]:
        print(f"\n=== {unit}, all Luna, paired and clustered by task ===")
        print(f"{'contrast / measurement':<46}{'est':>9}{'95% CI':>21}{'p':>9}{'n':>5}")
        print("-" * 90)
        for label, runs in families.items():
            print(f"{label}")
            ests = []
            for run_label, (t_recs, t_arm), (c_recs, c_arm) in runs:
                if field == "reasoning_tokens" and t_recs is c20q5:
                    continue  # ceiling-20 side run did not archive usage fields
                try:
                    t = per_task(t_recs, arm=t_arm, field=field, model="gpt-luna")
                    c = per_task(c_recs, arm=c_arm, field=field, model="gpt-luna")
                except (KeyError, ValueError):
                    continue
                if len(set(t) & set(c)) < 5:
                    continue
                m = measure(t, c, rng, scale=scale)
                ests.append((run_label, m["est"], m["p"]))
                ci = f"[{m['lo']:+.2f}, {m['hi']:+.2f}]"
                print(f"   {run_label:<43}{m['est']:>+9.2f}{ci:>21}{m['p']:>9.4f}{m['n']:>5}")
            if len(ests) > 1:
                report_spread("across all measurements", ests)
                # Matched-ceiling subsets: the only fair magnitude comparison,
                # since a different turn ceiling is a different instrument.
                for ceiling in ("ceiling 10", "ceiling 20"):
                    same = [e for e in ests if ceiling in e[0]]
                    if len(same) > 1:
                        report_spread(f"same instrument ({ceiling})", same)


if __name__ == "__main__":
    main()
