"""Power, equivalence, and multiplicity for this study's accuracy null.

Accuracy has not moved in any run. A null is only informative if the design
could have seen the effect it is being contrasted with, so this script reports,
for every accuracy contrast in the study's mid-task interjection runs:

  * the paired, task-clustered point estimate (the estimator used throughout),
  * a cluster-bootstrap 95% CI over tasks,
  * a task-clustered sign-flip permutation p-value,
  * the realized minimum detectable effect at 80% power, alpha = 0.05
    two-sided, following Miller's MDE inversion: MDE = (z_.975 + z_.80) * SE,
  * two-one-sided-tests (TOST) verdicts against the effect sizes the prior
    tone literature reports.

The contrast FAMILY is defined exhaustively and in advance: every
arm-versus-control accuracy contrast in every run that delivered a mid-task
interjection. That is 22 contrasts across 6 runs and 2 models. Defining it
any more narrowly would drop the contrast that came in nominally strongest.

It also reports the same machinery for TURN COUNT, which is the study's
primary outcome, so the two power regimes can be compared directly.

Run:  python results/analysis/accuracy_null_mde.py
"""

from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.stats import benjamini_hochberg  # noqa: E402  (needs ROOT on sys.path)

ARCHIVE = ROOT / "results_archive"
ANALYSIS = ROOT / "results" / "analysis"

Z_ALPHA = 1.959963985  # two-sided 0.05
Z_90 = 1.644853627  # two-sided 0.10, for the descriptive equivalence interval
Z_POWER = 0.8416212336  # 80% power
BOOT = 20000
SEED = 20260914

# Equivalence bounds, in accuracy points, fixed before looking at the results.
# 4.0  -- Dobariya & Kumar 2025's headline polite-vs-rude accuracy gap
#          (80.8% vs 84.8%). This is the study's pre-specified smallest
#          effect of interest: the effect the paper is positioned against.
# 7.5  -- Sclar et al.'s MEDIAN format-induced spread across 50+ tasks.
#          (Their famous 76 points is a single-task maximum; see the
#          literature review. Do not use it as a comparator.)
BOUNDS = {"published tone effect": 4.0, "median format spread": 7.5}

# Expected family size. Asserted so that a silent filter bug -- which this
# script had once, comparing an int field against string turn labels -- fails
# loudly instead of quietly shrinking the family.
EXPECTED_ACCURACY_CONTRASTS = 22


def _as_bool(value) -> bool:
    return str(value).strip().lower() == "true"


def load(path: pathlib.Path) -> list[dict]:
    return json.loads(path.read_text())


def per_task(records, *, arm=None, field="passed", model=None, turns=None,
             require_fired=True):
    """Mean outcome per task for one arm, as {task_id: value}.

    Trajectories on which the interjection did not fire received no dose and
    are excluded. Firing is decided before the interjection is delivered, so
    it cannot differ by arm except by chance (see firing_rates below).
    """
    buckets = defaultdict(list)
    for rec in records:
        if arm is not None and rec.get("interjection") != arm:
            continue
        if model is not None and rec.get("model_key") != model:
            continue
        if require_fired and "interjection_fired" in rec:
            if not _as_bool(rec["interjection_fired"]):
                continue
        if turns is not None and rec.get("interjection_turn") not in turns:
            continue
        raw = rec[field]
        value = 1.0 if field == "passed" and _as_bool(raw) else (
            0.0 if field == "passed" else float(raw)
        )
        buckets[rec["task_id"]].append(value)
    return {t: statistics.fmean(v) for t, v in buckets.items() if v}


def firing_rates(records, *, turn, model=None):
    """Fired / scheduled per arm at one injection turn -- the check that the
    firing exclusion is pre-treatment and not differential by arm."""
    out = defaultdict(lambda: [0, 0])
    for rec in records:
        if rec.get("interjection_turn") != turn:
            continue
        if model is not None and rec.get("model_key") != model:
            continue
        if "interjection_fired" not in rec:
            continue
        cell = out[rec["interjection"]]
        cell[1] += 1
        cell[0] += 1 if _as_bool(rec["interjection_fired"]) else 0
    return dict(out)


def paired_diffs(treat, control, *, scale=1.0):
    shared = sorted(set(treat) & set(control))
    return np.array([scale * (treat[t] - control[t]) for t in shared]), shared


def analyse(label, treat, control, *, scale=1.0, rng=None):
    rng = rng or np.random.default_rng(SEED)
    diffs, shared = paired_diffs(treat, control, scale=scale)
    if len(diffs) < 5:
        raise ValueError(f"{label}: only {len(diffs)} paired tasks -- check filters")
    n = len(diffs)
    idx = rng.integers(0, n, size=(BOOT, n))
    boot = diffs[idx].mean(axis=1)
    se = float(boot.std(ddof=1))
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))

    observed = abs(float(diffs.mean()))
    flips = rng.choice([-1.0, 1.0], size=(BOOT, n))
    null = (flips * diffs).mean(axis=1)
    # Phipson & Smyth: never report an exact zero from a finite permutation set.
    p = float((np.abs(null) >= observed - 1e-12).sum() + 1) / (BOOT + 1)

    est = float(diffs.mean())
    return {
        "contrast": label,
        "tasks": n,
        "estimate": est,
        "ci_lo": lo,
        "ci_hi": hi,
        "se": se,
        "p": p,
        "mde_80": (Z_ALPHA + Z_POWER) * se,
        "tost": {name: tost(est, se, b) for name, b in BOUNDS.items()},
        "per_task": {t: float(d) for t, d in zip(shared, diffs)},
    }


def tost(estimate, se, bound):
    """Two one-sided tests. Returns the larger of the two p-values."""
    def upper_tail(z):
        return 0.5 * math.erfc(z / math.sqrt(2.0))

    return max(upper_tail((estimate + bound) / se), upper_tail((bound - estimate) / se))


def chi2_sf(x, k):
    """Upper tail of a chi-square, for Cochran's Q."""
    a, xx = k / 2.0, x / 2.0
    if xx < a + 1:
        s = term = 1.0 / a
        for i in range(1, 10000):
            term *= xx / (a + i)
            s += term
            if term < s * 1e-14:
                break
        return 1.0 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a))
    tiny = 1e-300
    b, c, d = xx + 1 - a, 1 / tiny, 1 / (xx + 1 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-14:
            break
    return math.exp(-xx + a * math.log(xx) - math.lgamma(a)) * h


def pool(rows, names, *, rng=None):
    """Pool repeated measurements of one contrast.

    Reports BOTH a fixed-effect inverse-variance pool and a DerSimonian-Laird
    random-effects pool, plus a bootstrap that resamples TASKS JOINTLY across
    runs -- the runs share their 50 tasks, so an inverse-variance interval that
    treats them as independent understates the SE. The joint bootstrap is the
    interval we quote; the others are shown so the reader can see how little
    the choice matters here.
    """
    sel = [r for r in rows if r["contrast"] in names]
    if len(sel) < 2:
        return None
    w = [1.0 / r["se"] ** 2 for r in sel]
    fixed = sum(wi * r["estimate"] for wi, r in zip(w, sel)) / sum(w)
    fixed_se = math.sqrt(1.0 / sum(w))
    q_stat = sum(wi * (r["estimate"] - fixed) ** 2 for wi, r in zip(w, sel))
    df = len(sel) - 1
    q_p = chi2_sf(q_stat, df) if df else 1.0

    # DerSimonian-Laird between-study variance.
    c = sum(w) - sum(wi ** 2 for wi in w) / sum(w)
    tau2 = max(0.0, (q_stat - df) / c) if c > 0 else 0.0
    w_re = [1.0 / (r["se"] ** 2 + tau2) for r in sel]
    random = sum(wi * r["estimate"] for wi, r in zip(w_re, sel)) / sum(w_re)
    random_se = math.sqrt(1.0 / sum(w_re))

    # Joint task-clustered bootstrap, fixed weights.
    rng = rng or np.random.default_rng(SEED + 1)
    tasks = sorted(set().union(*(set(r["per_task"]) for r in sel)))
    draws = []
    for _ in range(4000):
        pick = rng.choice(tasks, size=len(tasks), replace=True)
        parts, wts = [], []
        for wi, r in zip(w, sel):
            vals = [r["per_task"][t] for t in pick if t in r["per_task"]]
            if vals:
                parts.append(statistics.fmean(vals))
                wts.append(wi)
        if parts:
            draws.append(sum(a * b for a, b in zip(wts, parts)) / sum(wts))
    joint_se = float(np.std(draws, ddof=1))

    return {
        "k": len(sel),
        "fixed": fixed,
        "fixed_se": fixed_se,
        "random": random,
        "random_se": random_se,
        "joint_se": joint_se,
        "cochran_q": q_stat,
        "df": df,
        "q_p": q_p,
        "tau2": tau2,
        "ci90_lo": fixed - Z_90 * joint_se,
        "ci90_hi": fixed + Z_90 * joint_se,
        "ci95_lo": fixed - Z_ALPHA * joint_se,
        "ci95_hi": fixed + Z_ALPHA * joint_se,
        "mde_80": (Z_ALPHA + Z_POWER) * joint_se,
        "tost_fixed": {n: tost(fixed, joint_se, b) for n, b in BOUNDS.items()},
        "tost_random": {n: tost(random, random_se, b) for n, b in BOUNDS.items()},
    }


def build_accuracy_family(rng):
    rows = []

    cross7 = load(ARCHIVE / "core_gpt-luna_cross7_records.json")
    # Turn 0 is inert in every arm and fires in ~98% of trajectories, so it is
    # analysed separately throughout; turns are stored as ints, not strings.
    l4 = per_task(cross7, arm="L4_neutral", turns={1, 2})
    for arm in ["L1_sycophantic", "L2_very_polite", "L3_polite", "L5_rude",
                "L6_very_rude", "L7_threatening"]:
        rows.append(analyse(f"{arm} vs neutral (seven-level, Luna, ceiling 10)",
                            per_task(cross7, arm=arm, turns={1, 2}), l4,
                            scale=100.0, rng=rng))

    probe = load(ARCHIVE / "core_gpt-luna_probe_records.json")
    ctrl = per_task(probe, arm="P0_control")
    for arm, name in [("P1_demand_only", "demand"), ("P2_praise_only", "praise"),
                      ("P3_insult_only", "insult")]:
        rows.append(analyse(f"{name} vs control (probe, Luna, ceiling 10)",
                            per_task(probe, arm=arm), ctrl, scale=100.0, rng=rng))

    praise = load(ARCHIVE / "core_gpt-luna_praise_records.json")
    qctrl = per_task(praise, arm="Q0_control")
    for arm, name in [("Q1_praise_assistant", "praise-assistant"),
                      ("Q2_praise_work", "praise-work"),
                      ("Q3_closing_neutral", "closing cue"),
                      ("Q4_praise_remains", "praise+remains"),
                      ("Q5_remains_only", "remains-only")]:
        rows.append(analyse(f"{name} vs control (praise run, Luna, ceiling 10)",
                            per_task(praise, arm=arm), qctrl, scale=100.0, rng=rng))

    stage1 = load(ARCHIVE / "stage1_cross_model_records.json")
    for model, tag in [("gpt-luna", "Luna"), ("glm-current", "GLM")]:
        c = per_task(stage1, arm="P0_control", model=model)
        for arm, name in [("P1_demand_only", "demand"), ("P2_praise_only", "praise"),
                          ("P3_insult_only", "insult")]:
            rows.append(analyse(f"{name} vs control (stage 1, {tag}, ceiling 20)",
                                per_task(stage1, arm=arm, model=model), c,
                                scale=100.0, rng=rng))

    c20_ctrl = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q0_control_records.json")
    c20_q5 = load(ANALYSIS / "study2_core_gpt-luna-ceiling20-Q5_remains_only_records.json")
    rows.append(analyse("remains-only vs control (ceiling-20 run, Luna)",
                        per_task(c20_q5), per_task(c20_ctrl), scale=100.0, rng=rng))

    # The micro-experiment drew its injection turn at random from {1,2} rather
    # than crossing it, so its comparison population is selection-affected
    # (see the paper's section 2.5). It is in the family anyway: excluding the
    # runs one dislikes is how families get gerrymandered.
    micro_n = load(ARCHIVE / "core_gpt-luna_reinject_neutral_regraded.json")
    micro_t = load(ARCHIVE / "core_gpt-luna_reinject_threatening_regraded.json")
    rows.append(analyse("threatening vs neutral (micro-experiment, Luna, ceiling 10)",
                        per_task(micro_t), per_task(micro_n), scale=100.0, rng=rng))

    return rows


def build_turn_rows(rng):
    rows = []
    probe = load(ARCHIVE / "core_gpt-luna_probe_records.json")
    ctrl = per_task(probe, arm="P0_control", field="n_turns")
    for arm, name in [("P1_demand_only", "demand"), ("P2_praise_only", "praise"),
                      ("P3_insult_only", "insult")]:
        rows.append(analyse(f"{name} vs control (probe, Luna)",
                            per_task(probe, arm=arm, field="n_turns"), ctrl, rng=rng))

    stage1 = load(ARCHIVE / "stage1_cross_model_records.json")
    for model, tag in [("gpt-luna", "Luna"), ("glm-current", "GLM")]:
        c = per_task(stage1, arm="P0_control", field="n_turns", model=model)
        for arm, name in [("P1_demand_only", "demand"), ("P2_praise_only", "praise"),
                          ("P3_insult_only", "insult")]:
            rows.append(analyse(f"{name} vs control (stage 1, {tag})",
                                per_task(stage1, arm=arm, field="n_turns", model=model),
                                c, rng=rng))
        rows[-1]["control_mean"] = statistics.fmean(c.values())
    rows[0]["control_mean"] = statistics.fmean(ctrl.values())
    return rows


def main() -> None:
    # Populate results/analysis/ from results_archive/ first. The inputs this
    # script reads are git-ignored here and committed there under different
    # names, so without this step a fresh clone fails with FileNotFoundError.
    from _inputs import materialise
    materialise()
    rng = np.random.default_rng(SEED)

    print("Firing is pre-treatment: fired/scheduled by arm, probe run, turn 2")
    for arm, (fired, total) in sorted(firing_rates(
            load(ARCHIVE / "core_gpt-luna_probe_records.json"), turn=2).items()):
        print(f"  {arm:<22} {fired:>4}/{total:<4} = {100*fired/total:.1f}%")

    acc = build_accuracy_family(rng)
    assert len(acc) == EXPECTED_ACCURACY_CONTRASTS, (
        f"family is {len(acc)} contrasts, expected {EXPECTED_ACCURACY_CONTRASTS} -- "
        "a filter has silently dropped rows"
    )

    header = (f"\n{'accuracy contrast':<52}{'n':>4}{'est':>8}{'95% CI':>19}"
              f"{'SE':>7}{'p':>8}{'MDE80':>8}{'TOST4':>9}{'TOST7.5':>9}")
    print(header)
    print("-" * (len(header) - 1))
    for r in acc:
        ci = f"[{r['ci_lo']:+.1f}, {r['ci_hi']:+.1f}]"
        print(f"{r['contrast']:<52}{r['tasks']:>4}{r['estimate']:>+8.2f}{ci:>19}"
              f"{r['se']:>7.2f}{r['p']:>8.4f}{r['mde_80']:>8.2f}"
              f"{r['tost']['published tone effect']:>9.4f}"
              f"{r['tost']['median format spread']:>9.4f}")

    # The shared, tested step-up implementation -- NOT a local reimplementation.
    # A previous local copy here compared each p against its own critical value
    # individually, which is not BH: it could reject rank 4 while refusing rank 3
    # at a smaller p. See tests/test_accuracy_null_mde_bh.py.
    bh = [(r.rank, r.critical_value, r.significant)
          for r in benjamini_hochberg([r["p"] for r in acc])]
    print(f"\nBenjamini-Hochberg over the {len(acc)}-contrast accuracy family (q=0.05):")
    for r, (rank, crit, passed) in sorted(zip(acc, bh), key=lambda z: z[1][0])[:3]:
        print(f"  rank {rank}: p={r['p']:.4f} vs critical {crit:.4f} -> "
              f"{'SURVIVES' if passed else 'does not survive'}  ({r['contrast']})")
    smallest = min(r["p"] for r in acc)
    print(f"  Bonferroni-adjusted smallest p: {min(1.0, smallest*len(acc)):.3f}")
    print(f"  nominal hits at 0.05: {sum(1 for r in acc if r['p'] < 0.05)}; "
          f"expected under a global null: {0.05*len(acc):.1f} "
          f"(P(at least one) = {1-0.95**len(acc):.2f})")

    mdes = [r["mde_80"] for r in acc]
    print(f"  MDE at 80% power: median {statistics.median(mdes):.2f}, "
          f"range {min(mdes):.2f}-{max(mdes):.2f} points")
    print(f"  largest |estimate| in the family: "
          f"{max(abs(r['estimate']) for r in acc):.2f} points")
    for name in BOUNDS:
        n_eq = sum(1 for r in acc if r["tost"][name] < 0.05)
        print(f"  equivalent to zero within +/-{BOUNDS[name]} ({name}): {n_eq}/{len(acc)}")

    print("\nPooled across repeated measurements of the same contrast")
    print("  (CI and MDE from the joint task-clustered bootstrap):")
    specs = {
        "demand vs control": {
            "demand vs control (probe, Luna, ceiling 10)",
            "demand vs control (stage 1, Luna, ceiling 20)",
            "demand vs control (stage 1, GLM, ceiling 20)",
        },
        "praise vs control": {
            "praise vs control (probe, Luna, ceiling 10)",
            "praise-assistant vs control (praise run, Luna, ceiling 10)",
            "praise vs control (stage 1, Luna, ceiling 20)",
            "praise vs control (stage 1, GLM, ceiling 20)",
        },
        "insult vs control": {
            "insult vs control (probe, Luna, ceiling 10)",
            "insult vs control (stage 1, Luna, ceiling 20)",
            "insult vs control (stage 1, GLM, ceiling 20)",
        },
        "praise vs control, Luna only": {
            "praise vs control (probe, Luna, ceiling 10)",
            "praise-assistant vs control (praise run, Luna, ceiling 10)",
            "praise vs control (stage 1, Luna, ceiling 20)",
        },
    }
    pools = {}
    for label, names in specs.items():
        m = pool(acc, names, rng=rng)
        if not m:
            continue
        pools[label] = m
        print(f"  {label:<30} k={m['k']}  {m['fixed']:+.2f} pts  "
              f"95% [{m['ci95_lo']:+.2f}, {m['ci95_hi']:+.2f}]  "
              f"90% [{m['ci90_lo']:+.2f}, {m['ci90_hi']:+.2f}]  MDE80={m['mde_80']:.2f}")
        print(f"  {'':<30} Q={m['cochran_q']:.2f} on {m['df']} df, p={m['q_p']:.3f}; "
              f"random-effects {m['random']:+.2f} +/- {m['random_se']:.2f}; "
              f"TOST+/-4 fixed {m['tost_fixed']['published tone effect']:.4f}, "
              f"random {m['tost_random']['published tone effect']:.4f}")

    turns = build_turn_rows(rng)
    print(f"\n{'turn-count contrast':<44}{'est':>8}{'SE':>7}{'MDE80':>8}{'est/MDE':>9}")
    print("-" * 76)
    for r in turns:
        print(f"{r['contrast']:<44}{r['estimate']:>+8.2f}{r['se']:>7.3f}"
              f"{r['mde_80']:>8.2f}{abs(r['estimate'])/r['mde_80']:>9.2f}")
    print("  control mean turns (mean of per-task means over fired control "
          "trajectories):")
    for r in turns:
        if "control_mean" in r:
            print(f"    {r['contrast']}: {r['control_mean']:.2f}")

    for row in acc + turns:
        row.pop("per_task", None)
    out = ANALYSIS / "accuracy_null_mde.json"
    out.write_text(json.dumps(
        {"accuracy": acc, "pooled": pools, "turns": turns}, indent=2))
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
