# C. Robustness and replication

## C.1 What replicated

Several contrasts were measured more than once, not by design at first but because the design kept
changing. Below, every arm appearing against a control in more than one run on Luna, on the primary
outcome; each cell is 50 tasks.

| Contrast | Measurement | Ceiling | Δ turns | 95% CI | *p* |
|---|---|---:|---:|---|---:|
| **Praise vs control** | probe | 10 | −0.59 | [−0.88, −0.29] | 0.0002 |
| | praise run | 10 | −1.08 | [−1.46, −0.71] | <0.0001 |
| | stage 1 | 20 | −1.01 | [−1.81, −0.23] | 0.017 |
| **Demand vs control** | probe | 10 | +1.17 | [+0.80, +1.55] | <0.0001 |
| | stage 1 | 20 | +1.75 | [+0.77, +2.73] | 0.0010 |
| **Insult vs control** | probe | 10 | −0.08 | [−0.40, +0.24] | 0.62 |
| | stage 1 | 20 | +0.57 | [−0.22, +1.35] | 0.17 |
| **Threatening vs neutral** | micro-experiment | 10 | +1.32 | [+0.99, +1.66] | <0.0001 |
| | seven-level run | 10 | +1.46 | [+1.03, +1.88] | <0.0001 |
| **"Work remains" vs control** | praise run | 10 | +1.85 | [+1.40, +2.28] | <0.0001 |
| | dedicated re-run | 20 | +6.20 | [+4.91, +7.52] | <0.0001 |
| | stage 1 | 20 | +5.77 | [+4.71, +6.92] | <0.0001 |

**Direction and significance replicate wherever the effect is large**, and **the null is the least
stable cell**: insult versus control is −0.08 in one measurement and +0.57 in the other, a sign
flip, though neither reaches significance. The cross-ceiling rows are not magnitude comparisons,
since the arms that persist longest are the ones a 10-turn ceiling truncates hardest. One
inconvenient row on the secondary outcome: **insult flips sign on reasoning tokens and reaches
significance in one of its two measurements**, −26 (*p* = 0.45) against **+176 (*p* = 0.0086)**. It
is the only place in the study where that arm moves anything; it does not survive §2.4's correction,
and it qualifies §4.3's "flat on both measures", true of the probe run.

Three contrasts were measured twice at the *same* ceiling, the only fair magnitude comparison,
compared below in standard errors of the difference, treating the runs as independent — generous,
since they share their 50 tasks, to the reading that they agree.

| Contrast, matched ceiling | Measurements | *z* | *p* | Verdict |
|---|---|---:|---:|---|
| Threatening vs neutral, ceiling 10 | +1.32, +1.46 | −0.52 | 0.60 | consistent |
| "Work remains" vs control, ceiling 20 | +6.20, +5.77 | +0.49 | 0.62 | consistent |
| Praise vs control, ceiling 10 | −0.59, −1.08 | **+2.03** | **0.042** | **inconsistent** |

**The two larger effects agree within 10%; the smallest does not** — and the two praise measurements
are of a **byte-identical stimulus**, since `Q1_praise_assistant` in the praise run *is*
`P2_praise_only` in the probe run (§5.1), which leaves the runs' differing trial count and date, so
sampling variation and drift are not separable here. Reasoning tokens behave the same way and the
praise pair is consistent there (*z* = 0.95). Across the study, point estimates span 1.5× to 3.4×
across re-measurements of one contrast on one model, most of that across ceilings. **Accuracy
replicates in neither direction**: the continue-signal contrast gives +6.6 and −1.8 points on
identical tasks, model and ceiling (*z* = 2.79, *p* = 0.005), so at least one is wrong and the data
do not say which.

## C.2 The apparent timing effect is a proxy, and other withdrawn claims

The interjection is inert at turn 0 and large at turns 1 and 2, which looks like position. At turn 0
there is nothing to act on: 98% of first turns run code and **0% produce a candidate answer**, while
in the control arm a candidate answer exists in 56% of trajectories through turn 1 and 80% through
turn 2, tracking the effect curve. Splitting the threatening-versus-neutral contrast by whether an
answer existed yet, holding turn index fixed, gives +0.34 (*p* = 0.27, 31 tasks) against **+1.97**
(*p* = 0.0003, 38 tasks) at turn 1, and +0.40 (*p* = 0.65, 8 tasks) against **+1.66** (*p* = 0.0002,
46 tasks) at turn 2. Holding the moderator fixed and moving the interjection changes little; holding
the turn index fixed and varying the moderator changes everything. The no-answer cells are small,
and tasks with no answer by turn 1 are also the harder tasks, so difficulty is not fully separated
from the moderator.

This is the second timing account this study has withdrawn. The first was selection: **a timing
effect of +21% at turn 1 against +39% at turn 2 (*p* = 0.004)** came from a turn-2 injection only
firing in trajectories that reach turn 2, the harder and longer tasks; recomputed on a
control-defined population it is +20.0% against +29.1%, *p* = 0.32. That is why injection turn is
crossed and the comparison population fixed from control (§2.2). Three other claims were withdrawn
on re-analysis: a ceiling explanation, tested and dropped; a "productive window" at turns 10–14 that
was a rate on a small denominator — "zero of 43 improvements occurred at turn 15 or later" was about
improvements to a trajectory's *running best*, and under the looser definition of any turn beating
the one before it, 10 of 95 occur at turn 15 or later; and an earlier claim that the praise stop was
demonstrably not premature, which the corrected regrade does not support (§5.3).

## C.3 The regrade instrument was wrong, and this is what changed

The first version of §6 reported a clean null: no arm moved the progress measure. That was an
artefact. The regrader read each turn's output with openpyxl's `data_only=True` and **never
recalculated it**, while the live grader had always passed output workbooks through LibreOffice
first. A formula written by openpyxl carries no cached value, so every turn that answered with a
formula read as empty and scored 0.0 — indistinguishable from a turn that wrote nothing, and roughly
56–62% of Luna's final gradable turns write formulas. The section's own validation paragraph would
have caught it: on the archived data **89 of 126 passed control trajectories scored exactly 0.0**.
The check was described and not run.

| | Broken | Corrected |
|---|---|---|
| Passed trajectories scoring 1.0 | 29.4% | **94.4%** |
| Redundant-step effects | +0.96 / −0.76 / −1.01 | +0.75 / −0.61 / −0.86 — all signs and significance held |
| "Work remains" on final match | +0.014 / **+0.061** / +0.019 | **+0.026 / +0.034 / +0.025** |
| Conclusion | extra turns buy nothing | extra turns buy 2.8 points, replicated |

The middle row is the paper's: the redundant-step finding survived with every sign and significance
level intact, about 20% smaller. The bottom row is the reversal. Under the defective regrade the
continue-signal arm's three final-match measurements read one hit between two nulls, spanning 4.4×,
and were presented as this study's most consequential instance of run-to-run instability. **Without
the fix we would have concluded that extra persistence buys nothing and that our own measurements of
it were unstable**, both wrong, from one unrecalculated workbook. That contrast's accuracy row is
real instability and survives the fix; its apparent corroboration by the progress measure was never
independent, since accuracy and `final_match` are two functions of the same workbook. The progress
measure now carries a regression test pinning the failure directly — a workbook answering with
`=A1*2` scores 0.0 without recalculation and 1.0 with it — but its redundant-step companion is the
exact one, and readers should weight the two accordingly.

## C.4 Redundant steps, per arm

Contrasts against each run's own neutral control, paired and clustered by task (§2.3):

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
