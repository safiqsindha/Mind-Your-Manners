#!/usr/bin/env python3
"""Appendix C of the workshop paper: the supplementary analyses reviewers asked for.

Written in response to the 2026-10-15 review round (our own pass plus Google's
Deep Review). Every number here comes from the same estimator as the paper's
headline contrasts (`accuracy_null_mde.per_task` / `analyse`: per-task means,
paired within task, task bootstrap, task-level sign-flip permutation, 20,000
draws), so nothing in this appendix is computed a second way.

  C.1  the 22-contrast Benjamini-Hochberg family, enumerated
  C.2  turn 0 in the register run, and the pooled turns 0-2 estimates
  C.3  both models at the twenty-turn budget, in turns and in percent
  C.4  closure-run checks: Q2-Q1, closing-cue accuracy, the floor check on
       matched tasks, control means by position, and run-to-run drift
  C.5  the blinded ratings, all fourteen texts
  C.6  the per-turn progress measure: definitions, population, redundant-step shares
  C.7  pooled accuracy equivalence, and the one comparison against no interjection

Writes workshop/99c-supplement.md. Run after turn_count_family.py.
"""
from __future__ import annotations

import glob
import json
import pathlib
import runpy
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
AN = ROOT / "results" / "analysis"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AN))

import numpy as np  # noqa: E402

import accuracy_null_mde as A  # noqa: E402
from _inputs import materialise  # noqa: E402

materialise()
OUT = ROOT / "workshop" / "99c-supplement.md"
FAMILY = AN / "turn_count_family.json"


def load(name):
    return json.loads((AN / name).read_text())


def contrast(recs, treat, control, *, field="n_turns", turns=None, scale=1.0,
             tasks=None, model=None, label=""):
    t = A.per_task(recs, arm=treat, field=field, turns=turns, model=model)
    c = A.per_task(recs, arm=control, field=field, turns=turns, model=model)
    if tasks is not None:
        t = {k: v for k, v in t.items() if k in tasks}
        c = {k: v for k, v in c.items() if k in tasks}
    return A.analyse(label or f"{treat} vs {control}", t, c, scale=scale,
                     rng=np.random.default_rng(A.SEED))


def p_str(p):
    return "<0.0001" if p < 1e-4 else f"{p:.4f}"


def num(x):
    """Signed, two decimals, with a typographic minus to match the prose."""
    out = f"{x:+.2f}"
    if out in ("+0.00", "-0.00"):          # a value that rounds to zero carries no sign
        return "0.00"
    return out.replace("-", "\u2212")


def fmt(r, unit=""):
    return (f"{num(r['estimate'])}{unit} [{num(r['ci_lo'])}, {num(r['ci_hi'])}]",
            p_str(r["p"]), r["tasks"])


# The family script labels runs by their working names; the paper names them by
# what they test. One mapping, so a label cannot say one thing here and another
# in the text.
RUN_NAMES = [
    ("(seven-level, Luna, ceiling 10)", "register run, Luna, budget 10"),
    ("(probe, Luna, ceiling 10)", "probe run, Luna, budget 10"),
    ("(praise run, Luna, ceiling 10)", "closure run, Luna, budget 10"),
    ("(stage 1, Luna, ceiling 20)", "cross-model run, Luna, budget 20"),
    ("(stage 1, GLM, ceiling 20)", "cross-model run, GLM, budget 20"),
    ("(ceiling-20 run, Luna)", "re-measurement run, Luna, budget 20"),
    ("(micro-experiment, Luna, ceiling 10)", "micro-experiment, Luna, budget 10"),
]


def run_label(name):
    for old, new in RUN_NAMES:
        name = name.replace(old, f"({new})")
    return name.replace(" [turns]", "")


INVENTORY = [
    ("Opening tone (wrapper on the first message, no mid-task interjection)", "Luna", 10, 1050, "no"),
    ("Micro-experiment: threatening vs neutral, re-injected mid-task", "Luna", 10, 800, "no"),
    ("Superseded control batch (earlier wrapper version)", "Luna", 10, 150, "no"),
    ("Register run (Figure 1A)", "Luna", 10, 3150, "yes"),
    ("Probe run (Figure 1B)", "Luna", 10, 1600, "yes"),
    ("Closure run (Figure 2)", "Luna", 10, 1800, "yes"),
    ("Cross-model run", "Luna, GLM", 20, 2700, "yes"),
    ("Re-measurement of \"work remains\"", "Luna", 20, 600, "yes"),
]


def fired(recs, arm, *, turns=None, model=None):
    return [r for r in recs
            if r.get("interjection") == arm and r.get("interjection_fired")
            and (turns is None or r.get("interjection_turn") in turns)
            and (model is None or r.get("model_key") == model)]


def mean_sd(recs):
    x = [r["n_turns"] for r in recs]
    return st.fmean(x), st.stdev(x), len(x)


def _flagged(recs, *, turns=None, model=None):
    """(delivered, primary-analysis) counts, or None where the run has no firing flag."""
    d = e = 0
    for r in recs:
        if model is not None and r.get("model_key") != model:
            continue
        if "interjection_fired" not in r:
            return None
        if A._as_bool(r["interjection_fired"]):
            d += 1
            if turns is None or r.get("interjection_turn") in turns:
                e += 1
    return d, e


def population():
    """Delivered and primary-analysis counts per INVENTORY row, from the records."""
    arch = lambda n: json.loads((A.ARCHIVE / n).read_text())
    s1 = arch("stage1_cross_model_records.json")
    c20 = load("study2_core_gpt-luna-ceiling20-Q0_control_records.json") + \
        load("study2_core_gpt-luna-ceiling20-Q5_remains_only_records.json")
    # The register run is analysed at injection turns 1 and 2 only (Appendix C.2).
    return {
        "Register run (Figure 1A)": _flagged(arch("core_gpt-luna_cross7_records.json"), turns={1, 2}),
        "Probe run (Figure 1B)": _flagged(arch("core_gpt-luna_probe_records.json")),
        "Closure run (Figure 2)": _flagged(arch("core_gpt-luna_praise_records.json")),
        # The turn-count family reads the micro-experiment from its records files (not the
        # regraded ones, which carry no firing flag).
        "Micro-experiment: threatening vs neutral, re-injected mid-task": _flagged(
            arch("core_gpt-luna_reinject_neutral_records.json")
            + arch("core_gpt-luna_reinject_threatening_records.json")),
        "Cross-model run": _flagged(s1),
        "Re-measurement of \"work remains\"": _flagged(c20),
    }


def c1():
    if not FAMILY.exists():
        runpy.run_path(str(AN / "turn_count_family.py"), run_name="__main__")
    probe = json.loads((A.ARCHIVE / "core_gpt-luna_probe_records.json").read_text())
    rates = [100 * f / t for f, t in A.firing_rates(probe, turn=2).values()]
    FIRING = f"{min(rates):.1f}–{max(rates):.1f}% across the four arms"
    fam = json.loads(FAMILY.read_text())["arm_vs_control"]["contrasts"]
    m = len(fam)
    ranked = sorted(range(m), key=lambda i: fam[i]["p"])
    # Benjamini-Hochberg step-up at q = 0.05.
    k = 0
    for rank, i in enumerate(ranked, 1):
        if fam[i]["p"] <= rank / m * 0.05:
            k = rank
    survive = {ranked[j] for j in range(k)}
    out = ["## C.1 Runs and the 22-contrast family", "",
           "All 11,850 scheduled trajectories, by run. *Delivered* means the interjection fired "
           "before the trajectory ended; firing is decided before delivery, so it differs by arm only "
           "by chance (probe run, injection at turn 2: "
           f"{FIRING}). *Primary analysis* means delivered and, in the register run, injected at "
           "turn 1 or 2 (turn 0 is Appendix C.2). Runs without a mid-task interjection show a dash.", "",
           "| Run | Model | Turn budget | Scheduled | Delivered | Primary analysis | Regraded per turn |",
           "|---|---|---:|---:|---:|---:|:---:|"]
    pop, tot = population(), [0, 0, 0]
    for name, model, budget, n, rg in INVENTORY:
        d_e = pop.get(name)
        if rg == "yes":
            tot[0] += n
            tot[1] += d_e[0]
            tot[2] += d_e[1]
        cells = f"{d_e[0]:,} | {d_e[1]:,}" if d_e else "— | —"
        out.append(f"| {name} | {model} | {budget} | {n:,} | {cells} | {rg} |")
    out += ["", f"The six regraded runs (the cross-model run counts once per model, so the table has five "
            f"regraded rows) hold {tot[0]:,} scheduled trajectories, {tot[1]:,} delivered and "
            f"{tot[2]:,} in the primary analysis; the per-turn figures of §5 use the last."]
    # The family omits the cross-model run's fifth Luna arm; show that adding it changes nothing.
    from harness.stats import benjamini_hochberg
    s1 = json.loads((A.ARCHIVE / "stage1_cross_model_records.json").read_text())
    extra = A.analyse("stage 1 work remains",
                      A.per_task(s1, arm="Q5_remains_only", field="n_turns", model="gpt-luna"),
                      A.per_task(s1, arm="P0_control", field="n_turns", model="gpt-luna"),
                      rng=np.random.default_rng(A.SEED))
    ps = [c["p"] for c in fam]
    sv22 = sum(x.significant for x in benjamini_hochberg(ps, 0.05))
    sv23 = sum(x.significant for x in benjamini_hochberg(ps + [extra["p"]], 0.05))
    out += ["", "**What the family leaves out.** The cross-model run's Luna half has a fifth arm, "
            f"`work remains`, that the 22 contrasts do not include ({extra['estimate']:+.2f} turns against its "
            f"control); it is in the delivered counts above and in the progress analysis of §5. Adding it as a "
            f"23rd test leaves the correction unchanged: {sv23} of 23 survive, the {sv22} that already did and "
            "this one. The micro-experiment's contrast uses its run records, which carry the firing flag "
            "(618 of 800 delivered)."]
    mn_ = mean_sd(fired(json.loads((A.ARCHIVE / "core_gpt-luna_reinject_neutral_records.json").read_text()),
                        "L4_neutral"))
    rm_ = mean_sd(fired(load("study2_core_gpt-luna-ceiling20-Q0_control_records.json"), "Q0_control"))
    out += ["", "Control means, in acting turns over delivered trajectories: the micro-experiment's neutral arm "
            f"{mn_[0]:.2f} (SD {mn_[1]:.2f}, {mn_[2]} trajectories); the re-measurement run's control "
            f"{rm_[0]:.2f} (SD {rm_[1]:.2f}, {rm_[2]})."]
    out += ["",
           "Every arm-versus-control turn-count contrast in every run that delivered a mid-task "
           f"interjection, sorted by *p*. Benjamini–Hochberg at *q* = 0.05: {k} of {m} survive. Intervals "
           "are bootstrap percentiles and *p*-values come from the sign-flip permutation, so at the "
           "margin they can disagree (GLM praise: upper bound just below zero, *p* = 0.058).", "",
           "| Contrast | Turns [95% CI] | *p* | BH |", "|---|---|---:|:---:|"]
    for i in ranked:
        r = fam[i]
        out.append(f"| {run_label(r['contrast'])} | {fmt(r)[0]} "
                   f"| {p_str(r['p'])} | {'yes' if i in survive else 'no'} |")
    return out + [""]


REGISTER = ["L1_sycophantic", "L2_very_polite", "L3_polite", "L5_rude",
            "L6_very_rude", "L7_threatening"]
DEMAND_ARMS = {"L2_very_polite", "L3_polite", "L6_very_rude", "L7_threatening"}   # our coding


def c2():
    reg = load("core_gpt-luna_cross7_records.json")
    out = ["## C.2 Turn 0 in the register run", "",
           "Turn *k* means the interjection is appended to the observation that follows the "
           "agent's acting turn *k* (0-indexed), so a turn-0 interjection arrives after the "
           "first code execution; in 96% of register-run trajectories the agent inspects the "
           "workbook before acting on it. The main text reports turns 1 and 2. That "
           "choice was made after the turn-0 contrasts below were seen, so all are shown, "
           "with the estimate pooled over all three positions beside them.", "",
           "| Arm | Turn 0 only | *p* | Turns 0–2 pooled | *p* |", "|---|---|---:|---|---:|"]
    t0p = []
    for arm in REGISTER:
        a = contrast(reg, arm, "L4_neutral", turns={0})
        b = contrast(reg, arm, "L4_neutral", turns={0, 1, 2})
        t0p.append(a["p"])
        out.append(f"| `{arm}` | {fmt(a)[0]} | {fmt(a)[1]} | {fmt(b)[0]} | {fmt(b)[1]} |")
    # Position-stratified check: difference within each injection position, then average the two
    # positions with equal weight, on the tasks that have firing trajectories at both.
    strat = []
    for arm in REGISTER:
        d = []
        for pos in (1, 2):
            a = A.per_task(reg, arm=arm, field="n_turns", turns={pos})
            b = A.per_task(reg, arm="L4_neutral", field="n_turns", turns={pos})
            d.append({k: a[k] - b[k] for k in set(a) & set(b)})
        both = set(d[0]) & set(d[1])
        strat.append((arm, st.fmean(st.fmean((d[0][k], d[1][k])) for k in both), len(both)))
    out += ["", "**Position weighting.** The main estimator pools turns 1 and 2 within each task before "
            "differencing, so a chance imbalance in how many trajectories fired at each position could "
            "tilt a contrast. Differencing within each position and then averaging the two with equal weight, "
            "on the tasks that fired at both (" + f"{min(n for *_, n in strat)}–{max(n for *_, n in strat)}" +
            " of 50), gives " + ", ".join(f"`{a}` {v:+.2f}".replace("-", "−") for a, v, _ in strat) +
            (": the four arms we code as carrying a demand still sit above the two we code as carrying none"
             if min(v for a, v, _ in strat if a in DEMAND_ARMS) > max(v for a, v, _ in strat if a not in DEMAND_ARMS)
             else ": the demand split does not hold on these tasks")
            + (", though `L3_polite` and `L7_threatening` exchange the top place."
               if max(strat, key=lambda t: t[1])[0] != "L3_polite" else ".")]
    out += ["", f"No turn-0 contrast survives correction across the six (smallest *p* = "
            f"{min(t0p):.4f}), and their signs are mixed. Pooled over all three positions, the "
            "four arms we code as carrying a demand still sit above the two we code as carrying "
            "none in point estimates.", ""]
    return out


def c3():
    s1 = load("stage1_cross_model_records.json")
    fam = {r["contrast"]: r for r in json.loads(FAMILY.read_text())["arm_vs_control"]["contrasts"]}
    tag = {"gpt-luna": "Luna", "glm-current": "GLM"}
    names = {"gpt-luna": "Luna", "glm-current": "GLM"}
    out = ["## C.3 Both models at the twenty-turn budget", "",
           "The cross-model run: both models, same 50 tasks, twenty-turn budget, injections at "
           "turns 1 and 2. Percent is the turn effect over that model's own control mean. "
           "Estimates and *p*-values are the family's (C.1).", "",
           "| Model | Control mean (SD), acting turns | At the 20-turn cap | Arm | Turns [95% CI] | % of control | *p* |",
           "|---|---|---:|---|---|---:|---:|"]
    for mk in ("gpt-luna", "glm-current"):
        mu, sd, _ = mean_sd(fired(s1, "P0_control", model=mk))
        allf = [r for r in s1 if r.get("model_key") == mk and r.get("interjection_fired")]
        cap = sum(1 for r in allf if r["n_turns"] >= 20)
        first = True
        for arm, lab in (("P1_demand_only", "demand"), ("P2_praise_only", "praise"),
                         ("P3_insult_only", "insult")):
            r = fam[f"{lab} vs control [turns] (stage 1, {tag[mk]}, ceiling 20)"]
            lead = (f"| {names[mk]} | {mu:.2f} ({sd:.2f}) | {cap}/{len(allf)} "
                    if first else "| | | ")
            pct = f"{100 * r['estimate'] / mu:+.1f}".replace("-", "\u2212")
            out.append(f"{lead}| {lab} | {fmt(r)[0]} | {pct}% "
                       f"| {fmt(r)[1]} |")
            first = False
    return out + [""]


def c4():
    cl = load("core_gpt-luna_praise_records.json")
    probe = load("core_gpt-luna_probe_records.json")
    q21 = contrast(cl, "Q2_praise_work", "Q1_praise_assistant")
    acc = contrast(cl, "Q3_closing_neutral", "Q0_control", field="passed", scale=100)
    out = ["## C.4 Closure-run checks", "",
           f"- **Praising the work against praising the assistant** (`Q2` − `Q1`): "
           f"{fmt(q21)[0]} turns, *p* = {fmt(q21)[1]}.",
           f"- **Closing cue, binary accuracy** (`Q3` − `Q0`): {fmt(acc, ' pts')[0]}, "
           f"*p* = {fmt(acc)[1]}. Measured in one run.",
           "", "**Floor check on matched tasks.** The turn-1 estimate restricted to the tasks "
           "that also have firing trajectories at turn 2 in both arms, against the turn-2 "
           "estimate on those same tasks:", "",
           "| Arm | Turn 1, matched tasks | Turn 2 | Tasks |", "|---|---|---|---:|"]
    for arm in ("Q3_closing_neutral", "Q1_praise_assistant", "Q2_praise_work"):
        both = (set(A.per_task(cl, arm=arm, turns={2}))
                & set(A.per_task(cl, arm="Q0_control", turns={2})))
        a = contrast(cl, arm, "Q0_control", turns={1}, tasks=both)
        b = contrast(cl, arm, "Q0_control", turns={2})
        out.append(f"| `{arm}` | {fmt(a)[0]} | {fmt(b)[0]} | {len(both)} |")
    m1 = mean_sd(fired(cl, "Q0_control", turns={1}))
    m2 = mean_sd(fired(cl, "Q0_control", turns={2}))
    tw = lambda recs, arm: st.fmean(A.per_task(recs, arm=arm, field="n_turns").values())
    mn = lambda x: f"{x:+.2f}".replace("-", "\u2212")
    pc, cc = tw(probe, "P0_control"), tw(cl, "Q0_control")
    pp, qp = tw(probe, "P2_praise_only"), tw(cl, "Q1_praise_assistant")
    out += ["", f"Control means by position: {m1[0]:.2f} acting turns (SD {m1[1]:.2f}) at turn 1, "
            f"{m2[0]:.2f} (SD {m2[1]:.2f}) at turn 2 (means over trajectories).", "",
            f"**Run-to-run drift.** On task-weighted means, the same ones the contrasts difference, the "
            f"byte-identical control text averaged {pc:.2f} acting turns in the probe run and {cc:.2f} in the "
            f"closure run, and the byte-identical praise text {pp:.2f} and {qp:.2f}. The two praise estimates "
            f"({mn(pp - pc)} and {mn(qp - cc)}) therefore differ by {abs((qp - cc) - (pp - pc)):.2f} turns, of which "
            f"{cc - pc:.2f} is the control moving and {pp - qp:.2f} the praise arm moving. The paper's intervals "
            "resample tasks within a run and do not include this variation, so single-run differences of "
            "under about half a turn should be read as provisional.", ""]
    return out


def c5():
    key = json.loads((ROOT / "rating" / "key.json").read_text())["key"]
    raters = [json.loads(pathlib.Path(f).read_text())
              for f in sorted(glob.glob(str(ROOT / "rating" / "ratings" / "*.json")))]
    out = ["## C.5 Blinded ratings, all fourteen texts", "",
           "Means over the five raters. *Demand* asks how strongly the message demands "
           "continued work or greater care (0 = says nothing about the task; 2 = touches on it, "
           "asks nothing; 4 = asks indirectly; 6 = directly instructs to keep working or get it "
           "right). *Closure* asks how strongly it projects that the exchange is ending (0 = "
           "nothing, or the opposite; 2 = neutral; 4 = a wind-down; 6 = states that nothing "
           "further follows). The three duplicate arms (`P0`, `Q0`, `Q1`) were rated once, "
           "under the text they share.", "",
           "| Arm | Demand, yes/5 | Demand (0–6) | Closure (0–6) |", "|---|---:|---:|---:|"]
    rows = []
    for sid, arm in key.items():
        yes = sum(1 for r in raters if r[sid]["demand_binary"] == "yes")
        d = st.fmean(r[sid]["demand_strength"] for r in raters)
        c = st.fmean(r[sid]["closure_strength"] for r in raters)
        rows.append((arm, yes, d, c))
    for arm, yes, d, c in sorted(rows):
        out.append(f"| `{arm}` | {yes} | {d:.1f} | {c:.1f} |")
    out += ["", "Item counts: Cohen's κ is computed over the 7 register arms, Krippendorff's α "
            "over all 14 texts, and Spearman's ρ over the 6 closure arms including the control.",
            ""]
    return out


def c6():
    import regrade_summary as R

    rng = np.random.default_rng(R.SEED + 1)
    table = R.share_table(rng)
    out = ["## C.6 The per-turn progress measure", "",
           "**Definitions.** The regrade replays each acting turn's code on the original workbook, "
           "recalculates formulas, and compares the graded cells with the answer file of the "
           "benchmark's *first* test case. A turn is *readable* if its code ran and produced a value "
           "over the graded range; *match* is the fraction of graded cells equal to the answer. The "
           "**graded fraction** is the match at the last readable turn, which need not be the final "
           "turn, and turns with no readable output are skipped. A **redundant step** is a readable "
           "turn whose graded range equals that of the previous readable turn; the first readable turn "
           "has no predecessor and is not counted. Binary accuracy uses the benchmark's evaluator over "
           "all test cases.", ""]

    # Instrument validation, from the probe control (all 400 scheduled trajectories).
    recs = R.load_aligned("gpt-luna-probe-P0_control")
    allrows = R.ALL_ROWS
    ctrl = json.loads((A.ARCHIVE / "core_gpt-luna_probe_records.json").read_text())
    passed = {(r["task_id"], r["trial"], r["interjection_turn"]): A._as_bool(r["passed"])
              for r in ctrl if r["interjection"] == "P0_control"}
    prog = R.load("gpt-luna-probe-P0_control")
    one = lambda p: p["final_match"] is not None and p["final_match"] >= 1 - 1e-9
    ok = [p for p in prog if passed[(p["task_id"], p["trial"], p["interjection_turn"])]]
    bad = [p for p in prog if not passed[(p["task_id"], p["trial"], p["interjection_turn"])]]
    miss = [p["task_id"] for p in ok if not one(p)]
    top = max(set(miss), key=miss.count) if miss else None
    out += [f"**Validation.** In the probe control (all {len(prog)} scheduled trajectories), {sum(map(one, ok))} of {len(ok)} trajectories that pass "
            f"the benchmark end with match 1 on the first test case, and the {len(miss)} that do not are all "
            f"in one task ({top}); {sum(map(one, bad))} of {len(bad)} that fail also reach match 1, because "
            "a trajectory can solve the first test case and fail a later one. Progress is therefore a "
            "first-test-case measure and not a second grader of accuracy.", ""]

    # The pooled graded-fraction contrasts with and without the one task on which the
    # instrument disagrees with the benchmark. That task scores 0.0 and 1.0 in different
    # trajectories of the same arm, so it does not cancel in paired contrasts.
    full = R.pool_progress(np.random.default_rng(R.SEED))
    R.EXCLUDE_TASKS = {top}
    try:
        without = R.pool_progress(np.random.default_rng(R.SEED))
    finally:
        R.EXCLUDE_TASKS = set()
    pts = lambda m: (f"{100*m['est']:+.1f} [{100*m['lo']:+.1f}, {100*m['hi']:+.1f}], "
                     f"*p* = {m['p']:.2f}").replace("-", "−").replace("−0.0]", "0.0]")
    pooled_runs = {"demand vs control": "probe; cross-model Luna; cross-model GLM",
                   "praise vs control": "probe; closure (`Q1`); cross-model Luna; cross-model GLM",
                   "insult vs control": "probe; cross-model Luna; cross-model GLM",
                   "'work remains' vs control": "closure; re-measurement; cross-model Luna"}
    out += [f"All seven disagreements are in task {top}, whose graded range is a single cell; the cause is "
            "undiagnosed. It scores both 0.0 and 1.0 in different trajectories of the same arm, so it does "
            "not cancel in paired contrasts. The pooled graded-fraction contrasts are sensitive to it, in "
            "points of the graded range:", "",
            "| Contrast | Runs pooled | All 50 tasks | Without that task |", "|---|---|---|---|"]
    for label in full:
        out.append(f"| {label.replace(chr(39), '')} | {pooled_runs.get(label, '')} | "
                   f"{pts(full[label])} | {pts(without[label])} |")
    each = full["'work remains' vs control"]["each"]
    out += ["", "The three `work remains` measurements are " +
            f"{100*each[0]:+.1f} (closure run), {100*each[1]:+.1f} (re-measurement run) and "
            f"{100*each[2]:+.1f} (cross-model run) points.".replace("-", "−"), ""]

    alias = {"probe (Luna, ceiling 10)": "Probe run, Luna, budget 10",
             "praise run (Luna, ceiling 10)": "Closure run, Luna, budget 10",
             "seven-level (Luna, ceiling 10)": "Register run, Luna, budget 10",
             "stage 1 (Luna, ceiling 20)": "Cross-model run, Luna, budget 20",
             "stage 1 (GLM, ceiling 20)": "Cross-model run, GLM, budget 20",
             "dedicated re-run (Luna, ceiling 20)": "Re-measurement run, Luna, budget 20"}
    sg = lambda x: f"{x:+.2f}".replace("-", "−")
    out += ["**Population.** Progress and turn counts use the same trajectories: those on which the "
            "interjection fired (and, in the register run, turns 1 and 2), joined to the run records on "
            "task, trial and injection turn. The turn-count effect below is the primary outcome, "
            "reproduced on those trajectories. Each share is redundant steps divided by acting turns, "
            "both as paired per-task differences against the arm's control, with a task-bootstrap "
            "interval. An arm's turn effect is *clear* if its sign-flip *p* is below 0.05, the criterion "
            "used for both models; the share is undefined otherwise, and its interval can pass 100% when "
            "the effect is small. Shares are computed from unrounded values and can differ by a point from "
            "the ratio of the printed columns. For arms that shorten trajectories the share is the fraction "
            "of the steps given up that would have left the graded range unchanged.", "",
            "| Run | Arm | Δ turns | Δ redundant steps | Share of turn effect [95% CI] | Trajectories (treated / control) |",
            "|---|---|---:|---:|---|---:|"]
    for r in table:
        share = (f"{100*r['share']:.0f}% [{100*r['lo']:.0f}%, {100*r['hi']:.0f}%]"
                 if r["clear"] else "not defined (turn effect not clear)")
        out.append(f"| {alias.get(r['run'], r['run'])} | {r['arm']} | {sg(r['turns'])} | {sg(r['noop'])} | "
                   f"{share.replace('-', '−')} | {r['n_treat']} / {r['n_control']} |")
    for tag, is_glm in (("Luna", False), ("GLM", True)):
        sel = [r["share"] for r in table if r["clear"] and (("GLM" in r["run"]) == is_glm)]
        out.append("")
        out.append(f"{tag}, arms with a clear turn effect (n = {len(sel)}): "
                   f"{100*min(sel):.0f}% to {100*max(sel):.0f}%, median {100*st.median(sel):.0f}%.")

    out += ["", "**What the rest of the turn effect is.** Acting turns split into redundant steps, other readable "
            "turns (including each trajectory's first readable turn) and unreadable turns whose code ran but "
            "produced no value over the graded range. For the arms with a clear effect:", "",
            "| Run | Arm | Δ turns | Δ redundant | Δ other readable | Δ unreadable |", "|---|---|---:|---:|---:|---:|"]
    for r in table:
        if r["clear"]:
            out.append(f"| {alias.get(r['run'], r['run'])} | {r['arm']} | {sg(r['turns'])} | {sg(r['noop'])} | "
                       f"{sg(r['d_other'])} | {sg(r['d_unread'])} |")
    out += ["", "A trajectory with no readable turn has no match and drops out of the graded-fraction "
            "contrasts; it is not scored 0.0. Its unreadable turns still count in the turn effect, which is "
            "why a share is a share of the net turn effect and not of the turns that changed the graded range.", ""]
    return out + [""]


def c7():
    """Pooled accuracy equivalence (from accuracy_null_mde.py) and the no-interjection comparison."""
    pools = json.loads((AN / "accuracy_null_mde.json").read_text())["pooled"]
    runs = {"demand vs control": "probe; cross-model Luna; cross-model GLM",
            "praise vs control": "probe; closure (`Q1`); cross-model Luna; cross-model GLM",
            "insult vs control": "probe; cross-model Luna; cross-model GLM",
            "praise vs control, Luna only": "probe; closure (`Q1`); cross-model Luna"}
    mn = lambda x: f"{x:+.2f}".replace("-", "−")
    acc = json.loads((AN / "accuracy_null_mde.json").read_text())["accuracy"]
    out = ["## C.7 Binary accuracy, per run and pooled, and the one comparison against no interjection", "",
           "Every arm-versus-control contrast of the 22-contrast family, on binary accuracy in percentage "
           "points (paired within task; 95% task-bootstrap interval; sign-flip permutation *p*):", "",
           "| Contrast | Accuracy [95% CI] | *p* |", "|---|---|---:|"]
    for r in sorted(acc, key=lambda r: r["p"]):
        out.append(f"| {run_label(r['contrast'])} | {mn(r['estimate'])} [{mn(r['ci_lo'])}, {mn(r['ci_hi'])}] "
                   f"| {p_str(r['p'])} |")
    out += ["", "None survives Benjamini–Hochberg at *q* = 0.05. Pooled over repeated measurements of one "
            "contrast, the 95% and 90% intervals and the fixed-effect TOST come from a bootstrap that resamples "
            "tasks jointly across runs; Cochran's *Q* and the random-effects TOST use inverse-variance weights "
            "that treat the runs as independent although they share their 50 tasks, so read them as "
            "descriptive.", "",
           "| Contrast | Runs pooled | Estimate [95% CI] | 90% CI | TOST ±4 (joint) | TOST ±4 (random effects) | *Q* *p* |",
           "|---|---|---|---|---:|---:|---:|"]
    for label, m in pools.items():
        t4, tr = m["tost_fixed"]["published tone effect"], m["tost_random"]["published tone effect"]
        out.append(f"| {label} | {runs.get(label, '')} | {mn(m['fixed'])} [{mn(m['ci95_lo'])}, {mn(m['ci95_hi'])}] "
                   f"| [{mn(m['ci90_lo'])}, {mn(m['ci90_hi'])}] | {p_str(t4)} | {p_str(tr)} | {m['q_p']:.3f} |")
    out += [""]

    # The one comparison against no interjection: the 150-trajectory batch run with an earlier
    # wrapper version, against the neutral arm of the re-injection micro-experiment.
    none = A.load(A.ARCHIVE / "core_gpt-luna_L4_wrapper-v2_records.json")
    neu = [r for r in A.load(A.ARCHIVE / "core_gpt-luna_reinject_neutral_records.json")
           if A._as_bool(r["interjection_fired"])]
    r = A.analyse("neutral vs none", A.per_task(neu, field="n_turns"),
                  A.per_task(none, field="n_turns", require_fired=False),
                  rng=np.random.default_rng(A.SEED))
    out += [f"**No interjection at all.** Every contrast in the paper is against a neutral interjection. The one "
            f"comparison against none uses the {len(none)}-trajectory batch run with an earlier wrapper "
            f"version (no interjection; {st.fmean(x['n_turns'] for x in none):.2f} acting turns) and the "
            f"{len(neu)} fired trajectories of the neutral arm of the re-injection micro-experiment "
            f"({st.fmean(x['n_turns'] for x in neu):.2f}). Paired within task, a neutral interjection adds "
            f"{mn(r['estimate'])} turns [{mn(r['ci_lo'])}, {mn(r['ci_hi'])}], *p* = {p_str(r['p'])}. The two "
            "batches differ in wrapper version, so the difference is not cleanly the interjection, but it "
            "does not support treating the neutral baseline as free: an arm's cost against an uninterrupted "
            "agent is not bounded here.", ""]
    return out


def main() -> None:
    lines = ["# C. Supplementary analyses", ""]
    for part in (c1, c2, c3, c4, c5, c6, c7):
        lines += part()
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
