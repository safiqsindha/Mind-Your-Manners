"""Every number section 6 reports, recomputed from the per-turn regrade.

Written after the regrade was found to be blind to formula-writing turns
(progress.py read agent output with data_only=True and never recalculated, so
any turn answering with `=SUMIFS(...)` scored 0.0). This script recomputes the
section's figures from the corrected regrade and states each denominator
explicitly, because several of the old figures were right about the number and
wrong about what it counted.

Definitions, fixed here so the paper and the script cannot drift:

  gradable output   a turn that ran code and produced a readable value over
                    the graded range. A turn whose code crashed is not one.
  redundant step    a turn after which the graded range is unchanged.
  first-is-best     among trajectories with AT LEAST TWO gradable outputs,
                    the first gradable output already equals the best the
                    trajectory ever reaches. Trajectories with fewer than two
                    cannot exhibit improvement and are excluded rather than
                    counted as successes -- the old figure included them.
  still improving   the last gradable output beat the one before it, so the
                    trajectory was on an upswing when it stopped.

Run:  python results/analysis/regrade_summary.py
"""

from __future__ import annotations

import ast
import json
import math
import pathlib
import statistics
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "results" / "analysis"
SEED = 20260914
BOOT = 20000

RUNS = {
    "probe (Luna, ceiling 10)": (
        "gpt-luna-probe-P0_control",
        [("demand only", "gpt-luna-probe-P1_demand_only"),
         ("praise only", "gpt-luna-probe-P2_praise_only"),
         ("insult only", "gpt-luna-probe-P3_insult_only")],
    ),
    "praise run (Luna, ceiling 10)": (
        "gpt-luna-praise-Q0_control",
        [("praise the assistant", "gpt-luna-praise-Q1_praise_assistant"),
         ("praise the work", "gpt-luna-praise-Q2_praise_work"),
         ("closing cue", "gpt-luna-praise-Q3_closing_neutral"),
         ("praise + work remains", "gpt-luna-praise-Q4_praise_remains"),
         ("work remains", "gpt-luna-praise-Q5_remains_only")],
    ),
    "seven-level (Luna, ceiling 10)": (
        "gpt-luna-cross7-L4_neutral",
        [("L1 sycophantic", "gpt-luna-cross7-L1_sycophantic"),
         ("L2 very polite", "gpt-luna-cross7-L2_very_polite"),
         ("L3 polite", "gpt-luna-cross7-L3_polite"),
         ("L5 rude", "gpt-luna-cross7-L5_rude"),
         ("L6 very rude", "gpt-luna-cross7-L6_very_rude"),
         ("L7 threatening", "gpt-luna-cross7-L7_threatening")],
    ),
    "stage 1 (Luna, ceiling 20)": (
        "gpt-luna-s1luna-P0_control",
        [("demand only", "gpt-luna-s1luna-P1_demand_only"),
         ("praise only", "gpt-luna-s1luna-P2_praise_only"),
         ("insult only", "gpt-luna-s1luna-P3_insult_only"),
         ("work remains", "gpt-luna-s1luna-Q5_remains_only")],
    ),
    "stage 1 (GLM, ceiling 20)": (
        "glm-current-s1glm-P0_control",
        [("demand only", "glm-current-s1glm-P1_demand_only"),
         ("praise only", "glm-current-s1glm-P2_praise_only"),
         ("insult only", "glm-current-s1glm-P3_insult_only")],
    ),
    "dedicated re-run (Luna, ceiling 20)": (
        "gpt-luna-ceiling20-Q0_control",
        [("work remains", "gpt-luna-ceiling20-Q5_remains_only")],
    ),
}


INSTRUMENT = ROOT / "harness" / "study2" / "progress.py"


def load(stem):
    """Load one arm's regrade, refusing anything older than the instrument.

    A regrade produced before the last change to progress.py was produced by a
    different instrument, and comparing one against another is how you
    manufacture an effect out of nothing. While the formula-recalculation fix
    was rolling out, a freshly regraded control against stale treatment arms
    produced a clean -0.36 final-match "effect" at p < 0.0001 in three arms at
    once -- identical in all three, which is the only reason it was obvious.
    Cross-instrument comparison fails loudly here rather than reading as a
    result.
    """
    path = ANALYSIS / f"study2_core_{stem}_progress.json"
    if not path.exists():
        return None
    if path.stat().st_mtime < INSTRUMENT.stat().st_mtime:
        raise SystemExit(
            f"STALE: {path.name} predates {INSTRUMENT.name}. Re-run the "
            f"regrade for this arm before comparing it to anything."
        )
    return json.loads(path.read_text())


def curve(rec):
    raw = rec["curve"]
    return ast.literal_eval(raw) if isinstance(raw, str) else raw


def gradable(rec):
    """Matches of the turns that produced a readable value, in order."""
    return [t["match"] for t in curve(rec) if t.get("match") is not None]


def per_task(records, fn):
    buckets = defaultdict(list)
    for r in records:
        v = fn(r)
        if v is not None:
            buckets[r["task_id"]].append(float(v))
    return {t: statistics.fmean(v) for t, v in buckets.items() if v}


def contrast(treat, control, rng):
    shared = sorted(set(treat) & set(control))
    if len(shared) < 5:
        return None
    diffs = np.array([treat[t] - control[t] for t in shared])
    idx = rng.integers(0, len(diffs), size=(BOOT, len(diffs)))
    boot = diffs[idx].mean(axis=1)
    observed = abs(float(diffs.mean()))
    flips = rng.choice([-1.0, 1.0], size=(BOOT, len(diffs)))
    null = np.abs((flips * diffs).mean(axis=1))
    return {
        "est": float(diffs.mean()),
        "lo": float(np.percentile(boot, 2.5)),
        "hi": float(np.percentile(boot, 97.5)),
        "p": float((null >= observed - 1e-12).sum() + 1) / (BOOT + 1),
        "n": len(shared),
    }


def structural(records):
    """First-is-best and still-improving, with their denominators stated."""
    eligible = [r for r in records if len(gradable(r)) >= 2]
    first_best = sum(1 for r in eligible
                     if abs(gradable(r)[0] - max(gradable(r))) < 1e-9)
    improving = sum(1 for r in eligible if gradable(r)[-1] > gradable(r)[-2] + 1e-9)
    return {
        "trajectories": len(records),
        "eligible": len(eligible),
        "first_is_best": first_best / len(eligible) if eligible else float("nan"),
        "still_improving": improving / len(eligible) if eligible else float("nan"),
    }


def peak_turns(records):
    """Where the best answer is first reached, among ceiling-bound runs."""
    peaks, improvements_at = [], []
    for r in records:
        c = [t for t in curve(r) if t.get("match") is not None]
        if len(c) < 2:
            continue
        best = max(t["match"] for t in c)
        peaks.append(next(t["turn"] for t in c if abs(t["match"] - best) < 1e-9))
        prev = None
        for t in c:
            if prev is not None and t["match"] > prev + 1e-9:
                improvements_at.append(t["turn"])
            prev = t["match"]
    return peaks, improvements_at


# Contrasts measured more than once, for pooling. A progress effect seen in
# one run is a draw (see the paper's section 8); the pooled estimate and
# Cochran's Q are what the paper quotes.
POOLED = {
    "demand vs control": [
        ("gpt-luna-probe-P1_demand_only", "gpt-luna-probe-P0_control"),
        ("gpt-luna-s1luna-P1_demand_only", "gpt-luna-s1luna-P0_control"),
        ("glm-current-s1glm-P1_demand_only", "glm-current-s1glm-P0_control"),
    ],
    "praise vs control": [
        ("gpt-luna-probe-P2_praise_only", "gpt-luna-probe-P0_control"),
        ("gpt-luna-praise-Q1_praise_assistant", "gpt-luna-praise-Q0_control"),
        ("gpt-luna-s1luna-P2_praise_only", "gpt-luna-s1luna-P0_control"),
        ("glm-current-s1glm-P2_praise_only", "glm-current-s1glm-P0_control"),
    ],
    "insult vs control": [
        ("gpt-luna-probe-P3_insult_only", "gpt-luna-probe-P0_control"),
        ("gpt-luna-s1luna-P3_insult_only", "gpt-luna-s1luna-P0_control"),
        ("glm-current-s1glm-P3_insult_only", "glm-current-s1glm-P0_control"),
    ],
    "'work remains' vs control": [
        ("gpt-luna-praise-Q5_remains_only", "gpt-luna-praise-Q0_control"),
        ("gpt-luna-ceiling20-Q5_remains_only", "gpt-luna-ceiling20-Q0_control"),
        ("gpt-luna-s1luna-Q5_remains_only", "gpt-luna-s1luna-P0_control"),
    ],
}


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


def pool_progress(rng):
    """Inverse-variance pool of final-match contrasts across measurements."""
    out = {}
    for label, pairs in POOLED.items():
        ms = []
        for treat_stem, control_stem in pairs:
            t, c = load(treat_stem), load(control_stem)
            if t is None or c is None:
                continue
            m = contrast(per_task(t, lambda r: r["final_match"]),
                         per_task(c, lambda r: r["final_match"]), rng)
            if m:
                m["se"] = (m["hi"] - m["lo"]) / (2 * 1.959963985)
                ms.append(m)
        if len(ms) < 2:
            continue
        w = [1.0 / m["se"] ** 2 for m in ms]
        est = sum(wi * m["est"] for wi, m in zip(w, ms)) / sum(w)
        q = sum(wi * (m["est"] - est) ** 2 for wi, m in zip(w, ms))

        # The runs share their 50 tasks, so an inverse-variance interval that
        # treats them as independent understates the SE -- the paper's section
        # 2.8 says so and uses a joint bootstrap for accuracy. Final match gets
        # the same treatment: resample TASKS once and recompute every run's
        # mean from that draw, and sign-flip a whole task across all runs at
        # once. On the continue-signal contrast this moves p from 0.004 to
        # 0.024; the effect survives, the confidence does not.
        joint = joint_task_bootstrap(pairs, w, rng)
        out[label] = {
            "k": len(ms), "est": est,
            "lo": joint["lo"], "hi": joint["hi"], "p": joint["p"],
            "iv_se": math.sqrt(1.0 / sum(w)),
            "q": q, "df": len(ms) - 1, "q_p": chi2_sf(q, len(ms) - 1),
            "each": [m["est"] for m in ms], "shared_tasks": joint["n"],
        }
    return out


def joint_task_bootstrap(pairs, weights, rng, reps=8000):
    """Pool across runs resampling TASKS jointly, not runs independently."""
    per_run = []
    for treat_stem, control_stem in pairs:
        t, c = load(treat_stem), load(control_stem)
        if t is None or c is None:
            continue
        tt = per_task(t, lambda r: r["final_match"])
        cc = per_task(c, lambda r: r["final_match"])
        per_run.append({k: tt[k] - cc[k] for k in set(tt) & set(cc)})
    shared = sorted(set.intersection(*[set(d) for d in per_run]))
    mats = [np.array([d[k] for k in shared]) for d in per_run]
    w = np.array(weights[: len(mats)], dtype=float)

    def combine(rows):
        return float((w * np.array([m[rows].mean() for m in mats])).sum() / w.sum())

    idx = rng.integers(0, len(shared), size=(reps, len(shared)))
    boot = np.array([combine(i) for i in idx])
    observed = combine(np.arange(len(shared)))
    flips = rng.choice([-1.0, 1.0], size=(reps, len(shared)))
    null = np.abs(np.array([
        float((w * np.array([(f * m).mean() for m in mats])).sum() / w.sum())
        for f in flips
    ]))
    return {
        "lo": float(np.percentile(boot, 2.5)),
        "hi": float(np.percentile(boot, 97.5)),
        "p": float((null >= abs(observed) - 1e-12).sum() + 1) / (reps + 1),
        "n": len(shared),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    missing = []

    for run, (control_stem, arms) in RUNS.items():
        control = load(control_stem)
        if control is None:
            missing.append(control_stem)
            continue
        c_noop = per_task(control, lambda r: r["n_noop_turns"])
        c_match = per_task(control, lambda r: r["final_match"])
        cs = structural(control)

        print(f"\n=== {run} ===")
        print(f"  control: {cs['trajectories']} trajectories, "
              f"{cs['eligible']} with >=2 gradable outputs; "
              f"first-is-best {100*cs['first_is_best']:.0f}%, "
              f"still improving at stop {100*cs['still_improving']:.1f}%, "
              f"mean redundant steps {statistics.fmean(c_noop.values()):.2f}")
        print(f"  {'arm':<24}{'Δ redundant':>13}{'p':>9}{'Δ final match':>15}{'p':>9}"
              f"{'first-best':>12}{'n':>5}")
        for label, stem in arms:
            recs = load(stem)
            if recs is None:
                missing.append(stem)
                continue
            a = contrast(per_task(recs, lambda r: r["n_noop_turns"]), c_noop, rng)
            b = contrast(per_task(recs, lambda r: r["final_match"]), c_match, rng)
            st = structural(recs)
            if a is None or b is None:
                continue
            print(f"  {label:<24}{a['est']:>+13.2f}{a['p']:>9.4f}"
                  f"{b['est']:>+15.3f}{b['p']:>9.4f}"
                  f"{100*st['first_is_best']:>11.0f}%{a['n']:>5}"
                  f"   still-improving {100*st['still_improving']:.1f}%"
                  f" (control {100*cs['still_improving']:.1f}%)")

    pooled = pool_progress(rng)
    if pooled:
        print("\n=== final match, pooled across measurements ===")
        print(f"  {'contrast':<28}{'k':>3}{'pooled':>10}{'95% CI':>22}{'p':>9}"
              f"{'Cochran Q':>12}")
        for label, m in pooled.items():
            ci = f"[{m['lo']:+.4f}, {m['hi']:+.4f}]"
            print(f"  {label:<28}{m['k']:>3}{m['est']:>+10.4f}{ci:>22}{m['p']:>9.4f}"
                  f"{m['q']:>8.2f}/{m['df']}df")
            print(f"  {'':<28}   each: "
                  + ", ".join(f"{e:+.3f}" for e in m["each"])
                  + f"   (heterogeneity p={m['q_p']:.3f})")

    c20 = load("gpt-luna-ceiling20-Q5_remains_only")
    c20c = load("gpt-luna-ceiling20-Q0_control")
    if c20 and c20c:
        peaks, imps = peak_turns(c20 + c20c)
        if peaks:
            peaks_sorted = sorted(peaks)
            print("\n=== ceiling-20 run: is 20 turns binding? ===")
            print(f"  best answer first reached at a median turn of "
                  f"{statistics.median(peaks_sorted):.0f}")
            for cut in (10, 14):
                share = sum(1 for p in peaks if p <= cut) / len(peaks)
                print(f"  peaked by turn {cut}: {100*share:.1f}%")
            late = sum(1 for t in imps if t >= 15)
            print(f"  improvements at turn 15 or later: {late} of {len(imps)}")

    if missing:
        print(f"\nMISSING (regrade not yet written): {len(missing)} arms")
        for m in sorted(set(missing)):
            print(f"  {m}")


if __name__ == "__main__":
    main()
