# 6. Finding 3: what the extra turns contain, and why accuracy does not move

## 6.1 The per-turn regrade

The benchmark grades the **final state** of the workbook, pass or fail, so the extra turns are
uninterpretable from the grade alone: an agent converging on the answer and an agent rewriting the
same wrong cells produce identical records. Opening the trajectory up requires no model calls and no
new data — about four machine-hours of replay. The regrader reconstructs the workbook after
**every** turn from the archived call log, re-executing that turn's code against the task's input
workbook; what makes this well posed is a property of the agent loop rather than of the regrader,
since **each turn receives the original input workbook, never the previous turn's output** (§2.1).

Two measures. **Redundant step**: this turn's output does not differ from the previous readable
turn's over the graded range. It needs no recalculation and is exact. **`final_match`**: the share of
the graded range matching the answer, in the last turn that produced a readable one. **This is not the
benchmark's pass/fail and must not be reported as accuracy** — a trajectory can climb from 0.2 to
0.9 and still fail, because the hard restriction requires every test case to pass. Both the answer
file and the agent's output must be recalculated through LibreOffice, because openpyxl writes
formulas with no cached value; a first version of this instrument skipped that step, and Appendix
C.3 records what it cost.

**Population.** Every figure in this section uses the trajectories of the primary turn-count
analysis: those on which the interjection fired and, in the register run, injection turns 1 and 2.
Each regrade row is joined to its run record on task, trial and injection turn, so a ratio of a
progress effect to a turn effect has the same trajectories in both parts; on those trajectories the
turn effects are exactly the ones §4 and §5 report. `results/analysis/regrade_summary.py` prints
every number below (`--all-rows` gives the unfiltered population). An earlier version divided progress
effects measured on every scheduled trajectory by turn effects measured on the fired ones; Appendix
C.3 records what that changed.

**Validation.** Trajectories the benchmark passed should score a final match of 1.0; on the probe
control arm, **119 of 126 (94.4%)** do. The residual seven are **all on one task** (54513), whose
graded range is a single cell, and all score exactly 0.0 — undiagnosed. That task does **not** cancel
in paired contrasts: it scores 0.0 in some trajectories and 1.0 in others of the same arm. Its
influence is on the final-match results, so §6.3 reports them with and without it; the
redundant-step shares are barely moved (53–93% without it, against 56–93%). In the other
direction, **47 of 274 benchmark-*failed* probe-control trajectories score a final match of 1.0**,
because `final_match` is computed against the first test case's answer file only while a pass requires
all three. 9,850 trajectories were regraded across 28 arms, six runs and two models; 6,616 are in the
primary population.

## 6.2 Most of the effect is redundant steps

Against each run's own neutral control, paired and clustered by task: on Luna's single-signal arms,
**every arm that moves turn count moves redundant steps, and the arms that do not, do not.**
Redundant steps account for **56–93%** of each turn effect that is clear (median 80% over 16 arms) —
demand +0.92 against +1.17 turns (78%), praise −0.33 against −0.59 (56%), the closing cue −1.04
against −1.44 (72%) — and the same band holds at ceiling 20, where the demand arm adds +1.57 against
+1.75 turns (90%). "Redundant" means only that the graded range did not change; checking a result can
leave it unchanged without being wasted. The full per-arm table is Appendix C.4.

One exception bounds that sentence. GLM's demand arm moves turns (+0.55) but its redundant steps
only +0.26 (*p* = 0.087), 48% of the effect with an interval from −20% to 80%: a model that barely
repeats itself has little repetition to add. The seven-level arms line up with §4.1's split rather
than with register: `L5_rude` adds nothing (+0.05, *p* = 0.77) and **L1 sycophantic significantly
removes redundant steps** (−0.62, *p* < 0.0001) — under *our* coding of `L5_rude`; under the raters'
coding that arm carries maximal demand and still moves nothing here, the same tension §4.2 records.

## 6.3 The remainder is small, and not distinguishable from zero

Point estimates are inverse-variance weighted; intervals and *p*-values come from a bootstrap
resampling **tasks jointly across runs**, 20,000 resamples, as §2.5 does for accuracy, because the
runs share their 50 tasks. Cochran's *Q* and the inverse-variance weights treat the runs as
independent although they share those tasks, so read the heterogeneity *p*-values as descriptive.

| Contrast | *k* | Pooled Δ final match | 95% CI | *p* | Cochran's *Q* |
|---|---:|---:|---|---:|---:|
| **"Work remains" vs control** | 3 | **+0.022** | [−0.002, +0.048] | **0.088** | 2.88/2 df (*p* = 0.24) |
| Demand only vs control | 3 | −0.003 | [−0.046, +0.019] | 0.54 | 4.21/2 df (*p* = 0.12) |
| Insult only vs control | 3 | −0.003 | [−0.034, +0.016] | 0.50 | 0.24/2 df (*p* = 0.88) |
| Praise vs control | 4 | −0.015 | [−0.040, +0.006] | 0.17 | 8.76/3 df (*p* = 0.033) |

**The explicit continue signal — "there is still more work remaining on this task here beyond what
you have done" — points toward a higher graded fraction, +2.2 points, but the interval includes
zero.** Its three measurements, across two turn ceilings and three runs, differ in size: +0.020
(*p* = 0.43), **+0.051** (*p* = 0.014) and +0.009 (*p* = 0.54), and only the dedicated ceiling-20
re-run is significant on its own. **Without task 54513 the pooled estimate is +1.4 points,
95% CI [−0.8, +3.5]**, so we call it suggestive and put it no more strongly. **The milder demand does
not**: it pools to −0.003 and its three measurements are heterogeneous (−0.017, −0.012, and **+0.056
on GLM**, *p* = 0.083 on its own), which we do not read as a finding. The pattern is **consistent
with** the explicitness of the claim that work remains being what the agent acts on, and no higher: on
the one run carrying both texts against the same control, the paired contrast between them is +0.021,
95% CI [−0.014, +0.058], *p* = 0.27. Praise is the contrast most affected by the one task, moving
from −1.5 to −1.8 points with an interval that then just reaches zero.

Two bounds on the size of this. It is about 2 points of the graded range, bought alongside 1.5 extra
redundant steps at ceiling 10 and 4.7–5.2 at ceiling 20. And **it need not be partial credit**: the
share of trajectories ending *fully* correct on the first test case moves by +3.3, **+6.8** (*p* =
0.019) and +0.3 points across the three measurements, while the accuracy series on the same contrast
(+2.4, +6.6, −1.8) is of that same order and cannot resolve it, since §2.5 puts the minimum
detectable accuracy effect at 3.7–7.8 points. So §2.5's accuracy null and a gain of this size are
compatible **because accuracy is underpowered here, not because such a gain could not cross the pass
threshold.**

## 6.4 The first attempt is usually the answer, and the ceiling is not binding

| Run | Trajectories | With ≥2 gradable outputs | First gradable output is already the best |
|---|---:|---:|---:|
| probe control, ceiling 10 | 300 | 112 | 80% |
| praise-run control, ceiling 10 | 236 | 97 | 89% |
| seven-level control, ceiling 10 | 220 | 67 | 94% |
| stage-1 Luna control, ceiling 20 | 229 | 58 | 84% |
| stage-1 GLM control, ceiling 20 | 193 | 47 | 83% |

The denominator matters: a trajectory that never produced two readable answers cannot exhibit
improvement. Among trajectories that *could* improve — a quarter to two-fifths of each sample — the
first gradable output is already the best in **80–94%**. Huang et al. [huang-2024] report "No Change"
rates of 90.5% on GPT-4 and 96.0% / 88.0% on GPT-4-Turbo; the numbers sit close together and the
statistics are not the same one. Their argument is that LLMs cannot reliably self-correct **without
external feedback**, and they point to execution feedback as the expected fix — a code executor
"serves as the perfect verifier" where a task supplies unit tests — but never test it. Our agent has
the executor and not the tests, so we test the **weaker** form of that escape hatch, and the answer
is mixed rather than negative; where scaling work reports gains from more attempts, the selection is
oracle-assisted [balachandran-2025].

**The 20-turn ceiling is not binding.** In the dedicated ceiling-20 re-run the best answer was first
reached at a **median turn of 2**, with **98.3% peaked by turn 10 and 100% by turn 14**; the other
two ceiling-20 runs agree. Trajectories that run long are not converging slowly — they reach their
best answer early — so raising the ceiling further buys mostly steps that change nothing, while five
rounds, the benchmark's official cap, would truncate the arms that persist longest.

## 6.5 Accuracy

No accuracy contrast in this study survives multiplicity correction (§2.4) or replication. That
register moves output length rather than correctness is already published for single-turn settings
by [kumar-dobariya-2026] and [yin-2024], and independently in the near-null of [cai-2025-tone]
(§3.4); our accuracy null is a replication of that in an agentic substrate, not a new finding. We
state it as equivalence rather than absence: demand versus control at −0.31 accuracy points, 95% CI
[−2.71, +2.09], and praise versus control at −0.12, [−1.80, +1.57], each equivalent to zero within
the four points the tone literature reports (§2.5). The design cannot exclude an effect of a point
or two and we do not claim it does. What it excludes is an accuracy effect of the size this
literature reports, in a setting where the same interjections move turn count by roughly 15 to 40%.

What this section does **not** establish is that the continue-signal gain is distinguishable from
zero, that a milder demand buys progress, that praise costs nothing, why the first attempt is usually best, or that the progress gain would appear on a scaffold
that accumulates workbook state across turns.
