# 7. What replicated, and what only looked like it did

> **Draft status.** Every figure in §7.1–§7.3 is printed by `results/analysis/replication_table.py`, which
> recomputes each contrast from the archived records under the estimator of §2.4.

## 7.1 The replication table

This study measured several contrasts more than once, not by design at first but because the design kept
changing. That lets us ask of our own results the question this literature mostly does not ask of its own:
**measured again, on the same tasks and the same model, what comes back?** There is precedent for asking —
[vaugrante-2024] re-ran five prompt-engineering techniques and found "a general lack of statistically
significant differences across nearly all techniques tested", diagnosing the original not as fabrication
but as selection. Below, every arm that appears against a control in more than one run on Luna, under the
estimator of §2.4, on the primary outcome; each cell is 50 tasks.

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

**Direction and significance replicate wherever the effect is large.** Praise is negative and significant
in all three measurements; demand, threatening and "work remains" positive and significant in every one.
**The null is the least stable cell**: insult versus control is −0.08 in one measurement and +0.57 in the
other — a sign flip — though neither reaches significance and both intervals contain zero. Two caveats about
reading magnitudes off the table: the cross-ceiling rows are not magnitude comparisons, because the arms
that persist longest are the ones a 10-turn ceiling truncates hardest and "work remains" has a mean of 6.37
turns against that ceiling; and a ratio of estimates is scale-dependent and meaningless near zero, so §7.2
uses a test instead.

The reasoning-token outcome carries one inconvenient row that a section called "what replicated" should not
omit. Demand is +214 and +357 across the two measurements (both *p* < 0.0001) and praise −131 and −113
(*p* = 0.0009 then 0.17), but **insult flips sign and reaches significance in one of the two**: −26
(*p* = 0.45) in the probe run and **+176 (*p* = 0.0086)** at stage 1. This is the only place in the study
where the insult arm moves anything. It qualifies two statements made elsewhere — §4.3's "flat on both
measures" is true of the probe run, and §2.7's "insult does not move it at all" is about turn count — and it
does not survive the multiplicity correction of §2.6, is not replicated, and runs opposite to the arm's
other measurement. We report it because a section about selective reporting cannot practise it.

## 7.2 Matched-ceiling pairs: a test, not an impression

Three contrasts were measured twice at the *same* ceiling, the only fair magnitude comparison. For each we
report the difference in standard errors of the difference, treating the runs as independent — which, since
they share the same 50 tasks, is generous to the reading that they agree.

| Contrast, matched ceiling | Measurements | *z* | *p* | Verdict |
|---|---|---:|---:|---|
| Threatening vs neutral, ceiling 10 | +1.32, +1.46 | −0.52 | 0.60 | consistent |
| "Work remains" vs control, ceiling 20 | +6.20, +5.77 | +0.49 | 0.62 | consistent |
| Praise vs control, ceiling 10 | −0.59, −1.08 | **+2.03** | **0.042** | **inconsistent** |

**The two larger effects agree; the smallest does not.** Threatening and "work remains" each reproduce
within 10%. Praise reproduces its direction and its significance, but its two measurements differ by about
two standard errors — **and those two measurements are of a byte-identical stimulus**, since
`Q1_praise_assistant` in the praise run *is* `P2_praise_only` in the probe run (§5.2). Nothing about the
text differs, which removes one candidate explanation and leaves the other two: the runs differ in trial
count (four against three) and in date, so sampling variation and drift between runs are not separable here.
What we can say is bounded: **of the three contrasts measured twice on one instrument, the two larger ones
agreed within 10% and the smallest is marginally inconsistent with a common value.** Three pairs will not
support a threshold and we do not propose one. Reasoning tokens behave the same way, and the praise pair is
consistent there (*z* = 0.95, *p* = 0.34), a further reason to treat the turn-count result as marginal
rather than as established drift.

## 7.3 An instability that was the instrument

The continue-signal arm is the one contrast measured three times, and until we rebuilt the instrument it was
this paper's showpiece for run-to-run instability. It is now a worked example of a defective measure
producing the *appearance* of instability.

| "Work remains" vs control | praise run, ceiling 10 | dedicated re-run, ceiling 20 | stage 1, ceiling 20 |
|---|---:|---:|---:|
| Δ turns | +1.85 | +6.20 | +5.77 |
| Δ final match, **defective regrade** | +0.014 (*p* = 0.49) | **+0.061 (*p* = 0.003)** | +0.019 (*p* = 0.16) |
| Δ final match, **corrected** | +0.026 (*p* = 0.32) | +0.034 (*p* = 0.043) | +0.025 (*p* = 0.089) |
| Δ accuracy | +2.4 pts (*p* = 0.24) | **+6.6 pts (*p* = 0.004)** | **−1.8 pts** (*p* = 0.39) |

Read the two middle rows against each other. Under the defective regrade the three measurements looked like
one hit between two nulls, spanning 4.4×, and we wrote a subsection about what that implied. Corrected, they
pool to **+0.028, 95% CI [+0.005, +0.052], *p* = 0.022, Cochran's *Q* = 0.20 on 2 df**. The defect is
described in §6.5: the regrade never recalculated the agent's formula-writing turns, so a majority of final
answers read as empty and scored zero. That is a *noise* injection, and noise does not merely widen
intervals — it made one run look special and two look null, which is indistinguishable from the instability
this section exists to document.

**Accuracy still replicates in neither direction.** Its two matched-ceiling measurements are +6.6 and −1.8
points on identical tasks, model and ceiling: *z* = 2.79, *p* = 0.005. They are inconsistent with a common
value, so at least one is wrong and the data do not say which. That is real instability, and it survives the
instrument fix, which is what makes the contrast with the row above informative rather than embarrassing.
The middle column also looked like corroboration at the time — a progress measure and the benchmark's own
grade, both positive, both significant — and that reading was mistaken for a reason worth naming
independently of the defect: accuracy and `final_match` are not two instruments but two functions of the
same final workbook, so their agreement carries almost no independent information.

**So the corrected statement is:** a continue signal buys more turns on two models, most of them redundant,
and about 2.8 points of the graded range, replicated three times. It does not show up as a better pass rate —
because accuracy is underpowered to resolve a gain of this size, not because partial credit cannot cross the
pass threshold. One note on population: the per-turn regrade outputs carry no record of whether the
interjection fired, so these contrasts are over all rows with a readable final match (48 tasks) rather than
the fired-only population §2.5 specifies elsewhere; firing is pre-treatment and does not differ by arm, so
we do not expect bias, but it is a different population. **Without the fix we would have concluded that
extra persistence buys nothing and that our own measurements of it were unstable.** Both were wrong, in the
same direction, from one unrecalculated workbook.

## 7.4 Claims this study withdrew about itself

Instability is one failure mode; analysis error is another. Four withdrawals each changed a substantive
claim, and they are not the complete list — the arithmetic and estimator errors recorded in §2.2, §2.4 and
`RESULTS.md` include a double-counted token total, an un-clustered confidence interval roughly 35% too
narrow, a mislabelled "monotonic decline", a false-positive claim that compared two different tests, a
pooled inert cell that diluted every seven-level effect by about a third, and an unpaired-versus-paired
estimator mix-up.

**A timing effect, +21% at turn 1 against +39% at turn 2 (*p* = 0.004), was selection.** The injection turn
was drawn at random, and a turn-2 injection can only fire in a trajectory that reaches turn 2 — the harder,
longer tasks — so the two positions were measured on different task populations, 50 against 35. Recomputed
on a control-defined population of 29 tasks: +20.0% against +29.1%, *p* = 0.32. This is why injection turn is
crossed (§2.2) and the comparison population fixed from control (§2.5). **A second timing effect was a
proxy** (§4.5). **A ceiling explanation was tested and withdrawn**: truncating the ceiling-20 run's own
analysis to ten turns left the continue signal's progress effect intact, so the ceiling explained almost none
of the gap that §7.3 then traced to the instrument. **And a "productive window" at turns 10–14 was a rate on
a small denominator**: the 1–5% per-turn improvement rate was real, but in absolute terms those turns contain
almost no improvements, since 98.3% of trajectories have peaked by turn 10 (§6.4).

Four infrastructure failures in the regrade subsystem presented as data rather than as error, and are worth
recording because they are the kind of thing that corrupts a result without announcing itself: the
unrecalculated workbook of §7.3; **shared scratch directories**, where the path omitted the run label so 800
trajectories shared 400 execution directories and concurrent processes rewrote one another's output, making
every pass/fail flag in those runs suspect until they were regraded from the archived logs; **a silent
range-parser bug**, where `"P2:P7"` parsed as sheet `P2:` plus cell `P7` so every affected lookup returned
`None`, which reads as *unmeasurable* rather than as *broken*; and **a LibreOffice timeout** that killed a
450-trajectory arm because a documented log-and-continue contract was a comment rather than a behaviour. The
range-parser bug was caught by validating the regrade against a real task before scaling up, which is why
§6.1 describes that validation step.

## 7.5 What we would ask of this literature

Nothing here is a new methodological proposal; it is the discipline [vaugrante-2024], [sclar-2024] and
[miller-2024] already ask for, applied to a study small enough that applying it is cheap. **Report the
estimator**: the unpaired difference of arm means and the paired task-clustered difference give different
numbers for the same contrast — ours differed by up to 6% on the praise contrast (§2.4) — and a paper that
does not say which it used cannot be compared with one that does. This is the defensible complaint about
[dobariya-kumar-2025], whose paired *t*-tests treat ten runs as the unit and ignore clustering within the 50
items. **Measure at least one contrast twice, on the same instrument**: it cost us nothing we would not have
spent anyway, and it changed what we were willing to claim about four results. **Report ranges where you
have them and say so where you do not**, in the scoped form [sclar-2024] give. The first is what the design
this paper is positioned against lacked; the second is what its own authors eventually supplied, re-running
the experiment and not reproducing its headline contrast on GPT-4o [dobariya-kumar-2026] — and what
[cai-2025-tone] supplied independently, at 1,446 questions and three models, finding the opposite direction
(§3.4).
