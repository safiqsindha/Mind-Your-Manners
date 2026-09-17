# 7. What replicated, and what only looked like it did

> **Draft status.** Every figure here is printed by `results/analysis/replication_table.py`, which
> recomputes each contrast from the archived records under the estimator of §2.4.

## 7.1 The replication table

Several contrasts were measured more than once, not by design at first but because the design kept
changing, which lets us ask of our own results the question this literature mostly does not ask of its own:
**measured again, on the same tasks and the same model, what comes back?** Below, every arm appearing
against a control in more than one run on Luna, on the primary outcome; each cell is 50 tasks.

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

**Direction and significance replicate wherever the effect is large**, and **the null is the least stable
cell**: insult versus control is −0.08 in one measurement and +0.57 in the other, a sign flip, though
neither reaches significance. The cross-ceiling rows are not magnitude comparisons, since the arms that
persist longest are the ones a 10-turn ceiling truncates hardest. One inconvenient row on the secondary
outcome: **insult flips sign on reasoning tokens and reaches significance in one of its two measurements**,
−26 (*p* = 0.45) against **+176 (*p* = 0.0086)**. It is the only place in the study where that arm moves
anything, it does not survive §2.6's correction, and it qualifies §4.3's "flat on both measures", true of
the probe run, and §2.7's "insult does not move it at all", which is about turn count.

## 7.2 Matched-ceiling pairs: a test, not an impression

Three contrasts were measured twice at the *same* ceiling, the only fair magnitude comparison. Below, the
difference in standard errors of the difference, treating the runs as independent — generous, since they
share their 50 tasks, to the reading that they agree.

| Contrast, matched ceiling | Measurements | *z* | *p* | Verdict |
|---|---|---:|---:|---|
| Threatening vs neutral, ceiling 10 | +1.32, +1.46 | −0.52 | 0.60 | consistent |
| "Work remains" vs control, ceiling 20 | +6.20, +5.77 | +0.49 | 0.62 | consistent |
| Praise vs control, ceiling 10 | −0.59, −1.08 | **+2.03** | **0.042** | **inconsistent** |

**The two larger effects agree within 10%; the smallest does not** — and the two praise measurements are of
a **byte-identical stimulus**, since `Q1_praise_assistant` in the praise run *is* `P2_praise_only` in the
probe run (§5.2), which leaves the runs' differing trial count and date, so sampling variation and drift are
not separable here. Reasoning tokens behave the same way and the praise pair is consistent there
(*z* = 0.95). Across the study, point estimates span 1.5× to 3.4× across re-measurements of one contrast on
one model, most of that across ceilings. **Accuracy replicates in neither direction**: the continue-signal
contrast gives +6.6 and −1.8 points on identical tasks, model and ceiling (*z* = 2.79, *p* = 0.005), so at
least one is wrong and the data do not say which.

## 7.3 An instability that was the instrument, and the claims we withdrew

The continue-signal arm was this paper's showpiece for run-to-run instability until we rebuilt the
instrument. Under the defective regrade of §6.5 its three final-match measurements read one hit between two
nulls, spanning 4.4×; corrected, they are +0.026, +0.034 and +0.025. The defect injected *noise*, and noise
made one run look special and two look null, which is indistinguishable from the instability this section
exists to document. **Without the fix we would have concluded that extra persistence buys nothing and that
our own measurements of it were unstable**, both wrong, from one unrecalculated workbook. That contrast's
accuracy row is real instability and survives the fix; its apparent corroboration by the progress measure
was never independent, since accuracy and `final_match` are two functions of the same workbook.

Analysis error is the other failure mode, and four withdrawals each changed a substantive claim. **A timing
effect, +21% at turn 1 against +39% at turn 2 (*p* = 0.004), was selection** — a turn-2 injection could only
fire in trajectories reaching turn 2, the harder and longer tasks, and recomputed on a control-defined
population it is +20.0% against +29.1%, *p* = 0.32, which is why injection turn is crossed (§2.2) and the
comparison population fixed from control (§2.5). **A second timing effect was a proxy** (§4.5); **a ceiling
explanation was tested and withdrawn**; and **a "productive window" at turns 10–14 was a rate on a small
denominator** (§6.4). §2.2, §2.4 and `RESULTS.md` record the rest, including an un-clustered interval
roughly 35% too narrow and an unpaired-versus-paired estimator mix-up — which is why every number here is
the paired one — while §6.5 records four infrastructure failures in the regrade subsystem that presented as
data rather than as error, among them a scratch-directory collision that let concurrent processes overwrite
one another's output workbooks. What we would ask of this literature is the discipline [vaugrante-2024],
[sclar-2024] and [miller-2024] already ask for: report the estimator, measure at least one contrast twice on
the same instrument, and report ranges where you have them. The second is what this paper's own target
eventually supplied against itself, failing to reproduce its headline contrast on GPT-4o
[dobariya-kumar-2026] — as did [cai-2025-tone] independently, at 1,446 questions and three models, in the
opposite direction (§3.4).
