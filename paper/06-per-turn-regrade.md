# 6. What the extra turns contain

> **Draft status.** Every figure is printed by `results/analysis/regrade_summary.py` from the archived
> regrade. **This section was rewritten after the instrument it describes was found to be defective; §6.5
> records what changed.**

## 6.1 The instrument

Every live finding in this study is about persistence, but the benchmark grades the **final state** of the
workbook, pass or fail, so the extra turns are uninterpretable from the grade alone: an agent converging on
the answer and an agent rewriting the same wrong cells produce identical records. Opening the trajectory up
requires no model calls and no new data — about four machine-hours of replay. `harness/study2/progress.py`
reconstructs the workbook after **every** turn from the archived call log, re-executing that turn's code
against the task's input workbook; what makes this well posed is a property of the agent loop rather than
of the regrader, since **each turn receives the original input workbook, never the previous turn's output**
(§2.1).

Two measures, deliberately different in cost and in what they can say. **`changed`** — did this turn's
output differ from the previous turn's over the graded range? A turn that changes nothing is a **redundant
step**; this needs no recalculation and is exact. **`final_match`** — what share of the graded range matches
the answer, in the last turn that produced a readable one? **This is not the benchmark's pass/fail and must
not be reported as accuracy:** a trajectory can climb from 0.2 to 0.9 and still fail, because the hard
restriction requires every test case to pass. **Both the answer file and the agent's output must be
recalculated**, and getting that wrong is what §6.5 is about: openpyxl writes formulas with no cached value,
so a turn answering with `=SUMIFS(...)` reads back as empty unless the workbook is passed through
LibreOffice first, which is what the live grader has always done.

**Validation.** Trajectories the benchmark passed should score a final match of 1.0; on the probe control
arm, **119 of 126 (94.4%)** do. The residual seven are **all on one task**, whose graded range is a single
cell, and all score exactly 0.0 — a systematic miss, not stochastic noise, and undiagnosed; it does not bias
paired contrasts, since that task contributes a zero difference to every arm, but it is a known blind spot.
The converse gap matters more for reading §6.3: **47 of 274 benchmark-*failed* probe-control trajectories
score a final match of 1.0**, because `final_match` is computed against the first test case's answer file
only while a pass requires all three. 9,850 trajectories were regraded across 28 arms, six runs and two
models.

## 6.2 What an interjection does to redundant steps

Contrasts against each run's own neutral control, paired and clustered by task (§2.4):

| Arm | Run | Δ redundant steps | *p* |
|---|---|---:|---:|
| Demand only | probe, ceiling 10 | **+0.75** | <0.0001 |
| Demand only | stage 1, ceiling 20 | **+1.03** | 0.0063 |
| Demand only | stage 1 GLM, ceiling 20 | +0.19 | 0.086 |
| "Work remains" | praise run, ceiling 10 | **+1.11** | <0.0001 |
| "Work remains" | stage 1, ceiling 20 | **+3.16** | <0.0001 |
| "Work remains" | ceiling-20 run | **+3.64** | <0.0001 |
| Praise the assistant | praise run, ceiling 10 | **−0.61** | <0.0001 |
| Praise the work | praise run, ceiling 10 | **−0.48** | 0.0012 |
| Closing cue | praise run, ceiling 10 | **−0.86** | <0.0001 |
| Insult only | probe, ceiling 10 | +0.03 | 0.85 |
| L7 threatening | seven-level, ceiling 10 | **+0.67** | 0.0001 |
| L3 polite | seven-level, ceiling 10 | **+0.90** | <0.0001 |
| L5 rude | seven-level, ceiling 10 | +0.07 | 0.53 |

**On Luna's single-signal arms, every arm that moves turn count moves redundant steps, and the arms that do
not, do not.** Against the turn effects of §4 and §5, redundant steps account for **roughly 55–65%** of
each: demand +0.75 against +1.17 turns (64%), praise −0.61 against −1.08 (56%), the closing cue −0.86
against −1.44 (60%), and the same band at ceiling 20. Two exceptions bound that sentence: GLM's demand arm
moves turns (+17.7%) but its redundant steps only +0.19 (*p* = 0.086), a model that barely repeats itself
having little repetition to add; and `Q4`, praise plus "work remains", lengthens trajectories while its
redundant-step effect is +0.19 (*p* = 0.18). The seven-level arms line up with §4.2's split rather than with
register: L5 rude adds nothing and **L1 sycophantic significantly removes redundant steps** (−0.29,
*p* = 0.0025). That is the split under *our* coding of `L5_rude`; under the blinded raters' coding that arm
carries a demand at maximum strength and is nonetheless the one that moves nothing here, which is the same
tension §4.2 records.

## 6.3 A continue signal does buy progress — but only the explicit one

This is where the corrected instrument changed the paper's answer. Point estimates are inverse-variance
weighted; intervals and *p*-values come from a bootstrap resampling **tasks jointly across runs**, as §2.7
does for accuracy, because the runs share their 50 tasks. Treating the runs as independent would give
*p* = 0.0038 on the first row; it is reported at the weaker and more defensible figure.

| Contrast | *k* | Pooled Δ final match | 95% CI | *p* | Cochran's *Q* |
|---|---:|---:|---|---:|---:|
| **"Work remains" vs control** | 3 | **+0.028** | [+0.005, +0.052] | **0.022** | 0.20/2 df (*p* = 0.91) |
| Demand only vs control | 3 | +0.009 | [−0.020, +0.039] | 0.52 | 6.42/2 df (*p* = 0.040) |
| Insult only vs control | 3 | +0.009 | [−0.018, +0.030] | 0.62 | 2.26/2 df (*p* = 0.32) |
| Praise vs control | 4 | −0.008 | [−0.027, +0.013] | 0.52 | 9.63/3 df (*p* = 0.022) |

**The explicit continue signal — "there is still more work remaining on this task here beyond what you have
done" — raises the graded fraction by 2.8 points**, across two turn ceilings and three separate runs
(+0.026, +0.034, +0.025). The *point estimates* agree more closely than anything else in this paper; we put
it no more strongly, because only one of the three reaches significance on its own (*p* = 0.32, 0.043,
0.089). **The milder demand does not**: it pools to +0.009 and its three measurements are heterogeneous
(−0.012, +0.002, and **+0.060 on GLM**, *p* = 0.015 on its own), and we do not read that GLM result as a
finding — one nominal hit, uncorrected, in a family where praise is equally heterogeneous in the opposite
direction. The pattern is **consistent with** the explicitness of the claim that work remains being what
the agent acts on, and no higher: on the one run carrying both texts against the same control, the paired
contrast between them is +0.023, 95% CI [−0.012, +0.060], *p* = 0.23, and the two texts differ in more than
strength.

Two bounds on the size of this. It is 2.8 points of the graded range, bought alongside 1.1 extra redundant
steps at ceiling 10 and 3.2–3.6 at ceiling 20. And **it is not merely partial credit**: the share of
trajectories ending *fully* correct rises by +2.8, +6.0 and +2.6 points across the three measurements,
while the accuracy series on the same contrast (+2.4, +6.6, −1.8) is of that same order and cannot resolve
it, since §2.7 puts the minimum detectable accuracy effect at 3.7–7.8 points. So §2.7's accuracy null and
this result are compatible **because accuracy is underpowered here, not because a gain of this size could
not cross the pass threshold.**

## 6.4 The first attempt is usually the answer, and the ceiling is not binding

| Run | Trajectories | With ≥2 gradable outputs | First gradable output is already the best |
|---|---:|---:|---:|
| probe control, ceiling 10 | 400 | 112 | 80% |
| praise-run control, ceiling 10 | 300 | 97 | 89% |
| seven-level control, ceiling 10 | 450 | 106 | 91% |
| stage-1 Luna control, ceiling 20 | 300 | 58 | 84% |
| stage-1 GLM control, ceiling 20 | 300 | 49 | 84% |

The denominator matters and an earlier draft got it wrong: a trajectory that never produced two readable
answers cannot exhibit improvement. Among trajectories that *could* improve — a sixth to a third of each
sample — the first gradable output is already the best in **80–91%**. A reviewer will set this beside Huang
et al. [huang-2024], whose "No Change" rates are 90.5% on GPT-4 and 96.0% / 88.0% on GPT-4-Turbo; the
numbers sit close together and the statistics are not the same one. Their argument is that LLMs cannot
reliably self-correct **without external feedback**, and they point to execution feedback as the expected
fix — a code executor "serves as the perfect verifier" where a task supplies unit tests — but never test
it. Our agent has the executor and not the tests, so we test the **weaker** form of that escape hatch, and
the answer is mixed rather than negative. Where scaling work reports gains from more attempts the selection
is oracle-assisted [balachandran-2025], so a small gain here is consistent with that literature rather than
a contradiction of it.

**The 20-turn ceiling is not binding.** In the dedicated ceiling-20 re-run the best answer was first reached
at a **median turn of 2**, with **98.3% peaked by turn 10 and 100% by turn 14**; the other two ceiling-20
runs agree. Trajectories that run long are not converging slowly — they reach their best answer early — so
raising the ceiling further buys mostly repetition, while five rounds, the benchmark's official cap, would
truncate the arms that persist longest. One statistic from an earlier draft does not survive as stated:
"zero of 43 improvements occurred at turn 15 or later" was about improvements to a trajectory's *running
best*, and under the looser definition of any turn beating the one before it, 10 of 95 occur at turn 15 or
later.

**Whether praise's early stop is premature is not settled**, and an earlier draft of this paragraph got it
backwards. Among trajectories that could improve, the share still improving when they stopped is **3.1–7.1%
in the Luna controls and 7.5–12.3% in the praise and closing-cue arms** — higher in every one of seven
comparisons, by a factor of two to three. No single paired contrast reaches significance (*p* = 0.095 to
0.65, on 19–34 tasks), so this is an underpowered test with a consistent sign, which is not a null. **We
therefore cannot say praise removes only repetition.** What we can say is that the absolute count is small:
6 of 53 trajectories under praise were still climbing when they stopped, against 3 of 97 in control. GLM is
worse on both sides — 14.3% of its controls and 29.2% of its praise arm — because a model that stops earlier
leaves more on the table. We use neither [cuadron-2025]'s term *premature disengagement* nor "premature",
and say instead what we measured: the stop is earlier, and whether it is costly is unresolved.

## 6.5 The instrument was wrong, and this is what changed

The first version of this section reported a clean null: no arm moved the progress measure. That was an
artefact. `progress.py` read each turn's output with openpyxl's `data_only=True` and **never recalculated
it**, while the live grader had always passed output workbooks through LibreOffice first. A formula written
by openpyxl carries no cached value, so every turn that answered with a formula read as empty and scored
0.0 — indistinguishable from a turn that wrote nothing, and roughly 56–62% of Luna's final gradable turns
write formulas. The section's own validation paragraph would have caught it: it claimed that
benchmark-passed trajectories score 1.0, and on the archived data **89 of 126 passed control trajectories
scored exactly 0.0**. The check was described and not run.

| | Broken | Corrected |
|---|---|---|
| Passed trajectories scoring 1.0 | 29.4% | **94.4%** |
| Redundant-step effects | +0.96 / −0.76 / −1.01 | +0.75 / −0.61 / −0.86 — all signs and significance held |
| "Work remains" on final match | +0.014 / **+0.061** / +0.019 | **+0.026 / +0.034 / +0.025** |
| Conclusion | extra turns buy nothing | extra turns buy 2.8 points, replicated |

The middle row is the paper's: the redundant-step finding survived with every sign and significance level
intact, about 20% smaller. The bottom row is the reversal — what §7 originally presented as this study's
most consequential instance of run-to-run instability, one significant measurement between two nulls, was
the instrument. It is the latest of four failures in this subsystem that presented as data rather than as an
error (§7.3).

**The honest scope of §6 is therefore narrower than its numbers suggest.** Its redundant-step measure is
exact and needs no recalculation; its progress measure depends on a recalculation path that was silently
broken until this rewrite, and now carries a regression test pinning the failure directly — a workbook
answering with `=A1*2` scores 0.0 without recalculation and 1.0 with it. The validation check of §6.1 still
leaves seven trajectories on one task unexplained. Readers should weight the two measures accordingly.

**In sum**, the turn-count effects of §4 and §5 are in the main effects on redundant steps; an explicit
statement that work remains raises the graded fraction by 2.8 points with three closely agreeing
measurements, while accuracy is too underpowered to rule an effect of that size in or out; the first
gradable attempt is the best in 80–91% of trajectories that could improve; and a 20-turn ceiling is not
binding. What this does **not** establish is that a milder demand buys progress, that praise costs nothing,
why the first attempt is usually best, or that the progress gain would appear on a scaffold that accumulates
workbook state across turns.
