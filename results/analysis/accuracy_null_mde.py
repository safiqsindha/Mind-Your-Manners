"""Realized MDE and equivalence bounds for the accuracy null.

Accuracy has not moved in any run of this study. A null is only informative if
the design could have seen the effect it is being contrasted with, so this
script reports, for every accuracy contrast we ran:

  * the paired, task-clustered point estimate (the estimator used throughout),
  * a cluster-bootstrap 95% CI over tasks,
  * the realized minimum detectable effect at 80% power, alpha = 0.05
    two-sided, following Miller's MDE inversion: MDE = (z_.975 + z_.80) * SE,
  * a two-one-sided-tests (TOST) verdict against the effect sizes the prior
    tone literature reports.

Run:  python results/analysis/accuracy_null_mde.py
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

Z_ALPHA = 1.959963985  # two-sided 0.05
Z_POWER = 0.8416212336  # 80% power
BOOT = 20000
RNG = np.random.default_rng(20260914)

# Equivalence bounds, in accuracy points, drawn from the prior literature.
# 4.0  -- Dobariya & Kumar 2025's headline polite-vs-rude accuracy gap
#          (80.8% vs 84.8% on their own MMLU-style set).
# 7.5  -- Sclar et al.'s MEDIAN format-induced spread across 50+ tasks.
#          (Their famous 76 points is a single-task maximum; see the
#          literature review. Do not use it as a comparator.)
BOUNDS = {"published tone effect": 4.0, "median format spread": 7.5}


def _as_bool(value) -> bool:
    return str(value).strip().lower() == "true"


def load(name: str) -> list[dict]:
    return json.loads((ARCHIVE / name).read_text())


def per_task_rates(records, arm, *, model=None, fired_only=True, turns=None):
    """Mean pass rate per task for one arm, as {task_id: rate}."""
    buckets = defaultdict(list)
    for rec in records:
        if rec.get("interjection") != arm:
            continue
        if model is not None and rec.get("model_key") != model:
            continue
        if fired_only and not _as_bool(rec.get("interjection_fired", "True")):
            continue
        if turns is not None and rec.get("interjection_turn") not in turns:
            continue
        buckets[rec["task_id"]].append(1.0 if _as_bool(rec["passed"]) else 0.0)
    return {task: statistics.fmean(vals) for task, vals in buckets.items() if vals}


def paired_contrast(treat, control):
    """Per-task paired differences in accuracy points, over shared tasks."""
    shared = sorted(set(treat) & set(control))
    return np.array([100.0 * (treat[t] - control[t]) for t in shared]), shared


def cluster_bootstrap(diffs, reps=BOOT):
    """Resample TASKS with replacement -- the clustering unit."""
    n = len(diffs)
    idx = RNG.integers(0, n, size=(reps, n))
    return diffs[idx].mean(axis=1)


def sign_flip_p(diffs, reps=BOOT):
    """Task-clustered permutation test: flip the sign of whole tasks."""
    observed = abs(diffs.mean())
    flips = RNG.choice([-1.0, 1.0], size=(reps, len(diffs)))
    null = (flips * diffs).mean(axis=1)
    return (np.abs(null) >= observed - 1e-12).mean()


def tost(estimate, se, bound):
    """Two one-sided tests. Returns the larger of the two p-values."""
    from math import erfc, sqrt

    def upper_tail(z):  # P(Z > z)
        return 0.5 * erfc(z / sqrt(2.0))

    p_lower = upper_tail((estimate - (-bound)) / se)  # H0: effect <= -bound
    p_upper = upper_tail(((bound) - estimate) / se)  # H0: effect >= +bound
    return max(p_lower, p_upper)


def report(label, treat_rates, control_rates):
    diffs, shared = paired_contrast(treat_rates, control_rates)
    if len(diffs) < 5:
        return None
    est = float(diffs.mean())
    boot = cluster_bootstrap(diffs)
    se = float(boot.std(ddof=1))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    mde = (Z_ALPHA + Z_POWER) * se
    row = {
        "contrast": label,
        "tasks": len(shared),
        "estimate_pts": est,
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "se_pts": se,
        "p": float(sign_flip_p(diffs)),
        "mde_80_pts": mde,
        "tost": {name: tost(est, se, b) for name, b in BOUNDS.items()},
    }
    return row


def benjamini_hochberg(pvals, q=0.05):
    """Return the BH critical value each rank is tested against, and verdicts."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    out = [None] * m
    for rank, i in enumerate(order, start=1):
        out[i] = (rank, q * rank / m, pvals[i] <= q * rank / m)
    return out


def inverse_variance_meta(rows, names):
    """Pool repeated measurements of the SAME contrast across runs.

    Caveat, stated in the paper: the runs share their 50 tasks, so task-level
    effects are common to them and this understates the pooled SE somewhat.
    Cochran's Q is reported so heterogeneity is visible rather than assumed away.
    """
    sel = [r for r in rows if r["contrast"] in names]
    if len(sel) < 2:
        return None
    w = [1.0 / r["se_pts"] ** 2 for r in sel]
    est = sum(wi * r["estimate_pts"] for wi, r in zip(w, sel)) / sum(w)
    se = math.sqrt(1.0 / sum(w))
    q_stat = sum(wi * (r["estimate_pts"] - est) ** 2 for wi, r in zip(w, sel))
    return {
        "k": len(sel),
        "estimate_pts": est,
        "se_pts": se,
        "ci_lo": est - Z_ALPHA * se,
        "ci_hi": est + Z_ALPHA * se,
        "mde_80_pts": (Z_ALPHA + Z_POWER) * se,
        "cochran_q": q_stat,
        "df": len(sel) - 1,
        "tost": {name: tost(est, se, b) for name, b in
                 {**BOUNDS, "3 points": 3.0, "2 points": 2.0}.items()},
    }


def main() -> None:
    rows = []

    probe = load("core_gpt-luna_probe_records.json")
    ctrl = per_task_rates(probe, "P0_control")
    for arm, name in [
        ("P1_demand_only", "demand vs control (probe, Luna)"),
        ("P2_praise_only", "praise vs control (probe, Luna)"),
        ("P3_insult_only", "insult vs control (probe, Luna)"),
    ]:
        row = report(name, per_task_rates(probe, arm), ctrl)
        if row:
            rows.append(row)

    praise = load("core_gpt-luna_praise_records.json")
    qctrl = per_task_rates(praise, "Q0_control")
    for arm, name in [
        ("Q1_praise_assistant", "praise-assistant vs control (praise run, Luna)"),
        ("Q2_praise_work", "praise-work vs control (praise run, Luna)"),
        ("Q3_closing_neutral", "closing cue vs control (praise run, Luna)"),
        ("Q4_praise_remains", "praise+remains vs control (praise run, Luna)"),
        ("Q5_remains_only", "remains-only vs control (praise run, Luna)"),
    ]:
        row = report(name, per_task_rates(praise, arm), qctrl)
        if row:
            rows.append(row)

    stage1 = load("stage1_cross_model_records.json")
    for model, tag in [("gpt-luna", "Luna"), ("glm-current", "GLM")]:
        c = per_task_rates(stage1, "P0_control", model=model)
        for arm, name in [
            ("P1_demand_only", f"demand vs control (stage 1, {tag})"),
            ("P2_praise_only", f"praise vs control (stage 1, {tag})"),
            ("P3_insult_only", f"insult vs control (stage 1, {tag})"),
        ]:
            row = report(name, per_task_rates(stage1, arm, model=model), c)
            if row:
                rows.append(row)

    cross7 = load("core_gpt-luna_cross7_records.json")
    l4 = per_task_rates(cross7, "L4_neutral", turns={"1", "2"})
    for arm in ["L1_sycophantic", "L2_very_polite", "L3_polite", "L5_rude",
                "L6_very_rude", "L7_threatening"]:
        row = report(
            f"{arm} vs neutral (seven-level, Luna)",
            per_task_rates(cross7, arm, turns={"1", "2"}),
            l4,
        )
        if row:
            rows.append(row)

    header = (
        f"{'contrast':<48}{'n':>4}{'est':>8}{'95% CI':>19}{'SE':>7}"
        f"{'p':>8}{'MDE80':>8}{'TOST 4pt':>10}{'TOST 7.5pt':>12}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        ci = f"[{r['ci_lo']:+.1f}, {r['ci_hi']:+.1f}]"
        print(
            f"{r['contrast']:<48}{r['tasks']:>4}{r['estimate_pts']:>+8.2f}{ci:>19}"
            f"{r['se_pts']:>7.2f}{r['p']:>8.3f}{r['mde_80_pts']:>8.2f}"
            f"{r['tost']['published tone effect']:>10.4f}"
            f"{r['tost']['median format spread']:>12.4f}"
        )

    bh = benjamini_hochberg([r["p"] for r in rows])
    print()
    print("Benjamini-Hochberg over the accuracy family (q=0.05):")
    for r, (rank, crit, passed) in sorted(zip(rows, bh), key=lambda z: z[1][0])[:3]:
        print(f"  rank {rank}: p={r['p']:.4f} vs critical {crit:.4f} "
              f"-> {'SURVIVES' if passed else 'does not survive'}  ({r['contrast']})")

    print()
    print("Pooled across repeated measurements of the same contrast:")
    meta_specs = {
        "demand vs control": {
            "demand vs control (probe, Luna)",
            "demand vs control (stage 1, Luna)",
            "demand vs control (stage 1, GLM)",
        },
        "praise vs control": {
            "praise vs control (probe, Luna)",
            "praise-assistant vs control (praise run, Luna)",
            "praise vs control (stage 1, Luna)",
            "praise vs control (stage 1, GLM)",
        },
        "insult vs control": {
            "insult vs control (probe, Luna)",
            "insult vs control (stage 1, Luna)",
            "insult vs control (stage 1, GLM)",
        },
    }
    metas = {}
    for label, names in meta_specs.items():
        m = inverse_variance_meta(rows, names)
        if not m:
            continue
        metas[label] = m
        print(
            f"  {label:<20} k={m['k']} {m['estimate_pts']:+.2f} pts "
            f"[{m['ci_lo']:+.2f}, {m['ci_hi']:+.2f}]  MDE80={m['mde_80_pts']:.2f}  "
            f"Q={m['cochran_q']:.2f} on {m['df']} df  "
            f"TOST+/-3={m['tost']['3 points']:.4f}  TOST+/-2={m['tost']['2 points']:.4f}"
        )

    ests = [r["estimate_pts"] for r in rows]
    mdes = [r["mde_80_pts"] for r in rows]
    print()
    print(f"{len(rows)} accuracy contrasts across 4 runs and 2 models.")
    print(f"largest |estimate|: {max(abs(e) for e in ests):.2f} points")
    print(f"realized MDE at 80% power: median {statistics.median(mdes):.2f}, "
          f"range {min(mdes):.2f}-{max(mdes):.2f} points")
    n_eq4 = sum(1 for r in rows if r["tost"]["published tone effect"] < 0.05)
    n_eq75 = sum(1 for r in rows if r["tost"]["median format spread"] < 0.05)
    print(f"equivalent to zero within +/-4.0 points (TOST, p<0.05): {n_eq4}/{len(rows)}")
    print(f"equivalent to zero within +/-7.5 points (TOST, p<0.05): {n_eq75}/{len(rows)}")

    out = ROOT / "results" / "analysis" / "accuracy_null_mde.json"
    out.write_text(json.dumps({"contrasts": rows, "pooled": metas}, indent=2))
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
