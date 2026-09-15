# 7. What replicated, and what only looked like it did

> **Draft status.** Every figure in §7.2–§7.4 is printed by
> `results/analysis/replication_table.py`, which recomputes each contrast from the archived
> records under the estimator of §2.4. Citation keys resolve to §9.

## 7.1 Why this section exists

This study measured several of its contrasts more than once, not by design at first but because
the design kept changing — a micro-experiment, a seven-register run, a probe, a follow-up with
more arms, a re-run at a higher ceiling, a second model. That lets us ask of our own results the
question this literature mostly does not ask of its own: **measured again, on the same tasks and
the same model, what comes back?**

The answer is not uniform, and the useful part is *which* properties survive.

There is precedent for asking. [vaugrante-2024] re-ran five prompt-engineering techniques against
their originals and found "a general lack of statistically significant differences across nearly
all techniques tested"; their emotional-prompting replication came in at +1%, χ² = 0.11, p = .74.
Their diagnosis of the original was not fabrication but selection: "instead of communicating the
average improvement of the enhanced prompts over the regular prompts, they focused on improvements
when cherry-picking the most performant emotional cue." Recomputed from the original's own data,
the *relative* improvement averaged 4.42% on BIG-Bench and 2.58% across all benchmarks, against a
headline of 115% on BIG-Bench [li-2023]. Their own design is single-run at temperature 0 with no
repeated sampling, so repeated measurement is a step past their practice rather than a borrowing
of it.

## 7.2 The replication table

Every arm that appears against a control in more than one run on Luna, under the estimator of
§2.4, on the primary outcome. Each cell is 50 tasks.

| Contrast | Measurement | Ceiling | Δ turns | 95% CI | p |
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

**Direction and significance replicate wherever the effect is large.** Praise is negative and
significant in all three measurements; demand, threatening and "work remains" positive and
significant in every one. The qualitative findings that were re-measured are not fragile.

**The null is the least stable cell.** Insult versus control is −0.08 in one measurement and
+0.57 in the other — a sign flip — though neither reaches significance and both intervals contain
zero. An effect that is not there is not thereby measured precisely.

Two caveats about how to read magnitudes off this table. First, the cross-ceiling rows are not
magnitude comparisons: the arms that persist longest are the ones a 10-turn ceiling truncates
hardest, and "work remains" has a mean of 6.37 turns against a ceiling of 10, so most of the
+1.85-to-+6.20 gap is censoring rather than instability. Second, a ratio of estimates is a poor
summary — it is scale-dependent and meaningless near zero. §7.3 uses a test instead.

## 7.3 Matched-ceiling pairs: a test, not an impression

Three contrasts were measured twice at the *same* ceiling, which is the only fair magnitude
comparison. For each we report the difference in standard errors of the difference, treating the
runs as independent — which, since they share the same 50 tasks, is generous to the reading that
they agree.

| Contrast, matched ceiling | Measurements | z | p | Verdict |
|---|---|---:|---:|---|
| Threatening vs neutral, ceiling 10 | +1.32, +1.46 | −0.52 | 0.60 | consistent |
| "Work remains" vs control, ceiling 20 | +6.20, +5.77 | +0.49 | 0.62 | consistent |
| Praise vs control, ceiling 10 | −0.59, −1.08 | **+2.03** | **0.042** | **inconsistent** |

**The two larger effects agree; the smallest does not.** Threatening (≈1.4 turns) and "work
remains" (≈6 turns) each reproduce within 10% and are comfortably consistent with a single value.
Praise (≈0.8 turns) reproduces its direction and its significance, but its two measurements differ
by about two standard errors — at the edge of what sampling variation alone predicts.

We do not claim to know why. The two praise runs also differ in trial count (four against three)
and in date, so sampling variation and drift between runs are not separable here. What we can say
is bounded: **of the three contrasts measured twice on one instrument, the two larger ones agreed
within 10% and the smallest is marginally inconsistent with a common value.** Three pairs will not
support a threshold, and we do not propose one.

Reasoning tokens behave the same way, and the praise pair is consistent there (−131 against −182,
z = 0.95, p = 0.34), which is a further reason to treat the turn-count result as marginal rather
than as established drift.

## 7.4 An instability that was the instrument

The continue-signal arm is the one contrast measured three times, and it was, until we rebuilt the
instrument, this paper's showpiece for run-to-run instability. It is now something more useful: a
worked example of a defective measure producing the *appearance* of instability.

| "Work remains" vs control | praise run, ceiling 10 | dedicated re-run, ceiling 20 | stage 1, ceiling 20 |
|---|---:|---:|---:|
| Δ turns | +1.85 | +6.20 | +5.77 |
| Δ final match, **defective regrade** | +0.014 (p = 0.49) | **+0.061 (p = 0.003)** | +0.019 (p = 0.16) |
| Δ final match, **corrected** | +0.026 (p = 0.32) | +0.034 (p = 0.043) | +0.025 (p = 0.089) |
| Δ accuracy | +2.4 pts (p = 0.24) | **+6.6 pts (p = 0.004)** | **−1.8 pts** (p = 0.39) |

Read the two middle rows against each other. Under the defective regrade the three measurements
looked like one hit between two nulls, spanning 4.4×, and we wrote a subsection about what that
implied. Corrected, they are +0.026, +0.034 and +0.025 — pooling to **+0.028, 95% CI
[+0.005, +0.052], p = 0.022, with Cochran's Q = 0.20 on 2 df (heterogeneity p = 0.91)**, under the
joint task bootstrap of §2.8. Their *point estimates* agree more closely than anything else in
this study, though only one of the three reaches significance on its own (§6.4).

The defect is described in §6.8: the regrade never recalculated the agent's formula-writing turns,
so a majority of final answers read as empty and scored zero. That is a *noise* injection, and
noise does not merely widen intervals — it made one run look special and two look null, which is
indistinguishable from the instability this section exists to document.

**Accuracy still replicates in neither direction.** Its two matched-ceiling measurements are +6.6
and −1.8 points on identical tasks, model and ceiling: z = 2.79, p = 0.005. They are inconsistent
with a common value, so at least one is wrong and the data do not say which. That one is real
instability, and it survives the instrument fix — which is what makes the contrast with the row
above informative rather than embarrassing.

The middle column also looked like corroboration at the time: a progress measure and the
benchmark's own grade, both positive, both significant. That reading was mistaken for a reason
worth naming independently of the defect. Accuracy and `final_match` are not two instruments. They
are two functions of the same final workbook — one asks whether all three test cases pass, the
other what fraction of the graded range is correct — so they share not only every source of
run-level noise but the underlying object. Their agreement carries almost no independent
information.

**So the corrected statement is:** a continue signal buys more turns on two models, most of them
redundant, and buys about 2.8 points of the graded range, replicated three times. It does not show
up as a better pass rate — but that is because accuracy is underpowered to resolve a gain of this
size (§2.7's MDE is 3.7–7.8 points), not because partial credit cannot cross the pass threshold.
The share of trajectories ending *fully* correct rises by 2.6–6.0 points across the same three
measurements (§6.4).

One note on population. The per-turn regrade outputs carry no record of whether the interjection
fired, so these contrasts are over all rows with a readable final match — 48 tasks — rather than
the fired-only population §2.5 specifies elsewhere. Firing is pre-treatment and does not differ by
arm (§2.5), so we do not expect bias, but it is a different population and we say so.

**What we would have concluded without the fix.** That extra persistence buys nothing, and that
our own measurements of it were unstable. Both were wrong, in the same direction, from one
unrecalculated workbook. §7.6 lists the claims we withdrew after re-analysing data we already had;
this is the one we withdrew after fixing the thing that produced it, which is a different and
more expensive category.

## 7.5 The reasoning-token outcome, including an inconvenient row

The first run's pre-registered outcome was reasoning tokens, and a section called "what
replicated" should not quietly report only the outcome that behaved.

| Contrast | probe, ceiling 10 | stage 1, ceiling 20 |
|---|---:|---:|
| Demand vs control | +214 (p < 0.0001) | +357 (p < 0.0001) |
| Praise vs control | −131 (p = 0.0009) | −113 (p = 0.17) |
| **Insult vs control** | **−26 (p = 0.45)** | **+176 (p = 0.0086)** |

**Insult flips sign and reaches significance in one of the two measurements.** This is the only
place in the study where the insult arm moves anything, and it qualifies two statements made
elsewhere: §4.3's "flat on both measures" is true of the probe run, and §2.8's "insult does not
move it at all" is about turn count. On reasoning tokens at the 20-turn ceiling, insult is +176,
p = 0.0086 uncorrected — which does not survive the multiplicity correction of §2.6, is not
replicated, and runs opposite to the arm's other measurement. We report it because a section about
selective reporting cannot practise it, and we do not build on it.

Praise on tokens likewise loses significance at stage 1 (p = 0.17), which §4.7's turn-count table
does not show.

## 7.6 Claims this study withdrew about itself

Instability is one failure mode; analysis error is another. We discuss four here, chosen because
each changed a substantive claim. They are not the complete list — the arithmetic and estimator
errors are recorded in §2.4, §2.2 and `RESULTS.md`, and include a double-counted token total, an
un-clustered confidence interval roughly 35% too narrow, a mislabelled "monotonic decline", a
false-positive claim that compared two different tests, a pooled inert cell that diluted every
seven-level effect by about a third, and an unpaired-versus-paired estimator mix-up.

**A timing effect that was selection.** An early micro-experiment split the interruption's
reasoning-token effect by injection turn and found +21% at turn 1 against +39% at turn 2,
p = 0.004. The injection turn was drawn at random, and a turn-2 injection can only fire in a
trajectory that reaches turn 2 — the harder, longer tasks. The two *positions* were therefore
measured on different task populations, 50 against 35. Recomputed on a control-defined population
of 29 tasks: +20.0% against +29.1%, p = 0.32. Withdrawn. This is why injection turn is crossed
rather than sampled (§2.2) and why the comparison population is fixed from control (§2.5).

**A timing effect that was a proxy.** The crossed run then found the interjection inert at turn 0
and large at turns 1 and 2, which looks like position. §4.6 shows it is not: holding turn index
fixed and varying whether a candidate answer exists changes the effect from +0.34 to +1.97, while
holding the moderator fixed and varying the turn index changes it from +1.97 to +1.66.

**A ceiling explanation we tested and withdrew.** When the continue signal's progress effect
looked like one hit between two nulls, the natural reading was that the 10-turn ceiling had
truncated real progress. Truncating the ceiling-20 run's own analysis to ten turns left the effect
intact, so the ceiling explained almost none of the gap. The correction was written, then checked,
then withdrawn — and §7.4 now shows the gap itself was the instrument.

**A productive window that was a rate on a small denominator.** A per-turn improvement rate of
1–5% at turn indices around 10–14 was read as evidence that the productive window extended that
far. The rate was real; the conclusion was not. In absolute terms those turns contain almost no
improvements — 98.3% of trajectories have reached their best answer by turn 10, at a median turn
of 2 (§6.6).

## 7.7 Two infrastructure failures worth recording

Neither changed a conclusion; both are the kind of thing that corrupts a result without announcing
itself.

**Shared scratch directories.** Two runs used the same tone over the same 50 tasks and the same 8
trials, and the scratch path did not include the run label — so 800 trajectories shared 400
execution directories, and two concurrent processes unlinked and rewrote one another's output
workbook. Every pass/fail flag in those runs was suspect. Token counts come from the provider's
API response and never touch the filesystem, so the cost effect was never in question. The grades
were recovered by regrading from the archived logs, at no cost. Scratch paths are now namespaced
by run tag and injection turn.

**A silent range-parser bug.** `"P2:P7"` parsed as sheet `P2:` plus cell `P7`, grading a one-cell
range on a sheet that does not exist. Every affected lookup returned `None`, which reads as
*unmeasurable* rather than as *broken*. It was caught by validating the regrade against a real task
before scaling up, and it is why §6.2 describes that validation step.

## 7.8 What we would ask of this literature

Nothing here is a new methodological proposal; it is the discipline [vaugrante-2024], [sclar-2024]
and [miller-2024] already ask for, applied to a study small enough that applying it is cheap.
Three things, in order of what they cost.

1. **Report the estimator.** The unpaired difference of arm means and the paired task-clustered
   difference give different numbers for the same contrast — ours differed by up to 6% on the
   praise contrast (§2.4). A paper that does not say which it used cannot be compared with one that
   does. This is the defensible complaint about [dobariya-kumar-2025]: its paired t-tests treat ten
   runs as the unit and ignore clustering within the 50 items.
2. **Measure at least one contrast twice, on the same instrument.** It cost us nothing we would not
   have spent anyway, and it changed what we were willing to claim about four results: the
   continue-signal progress effect, the accuracy movement that accompanied it, the praise magnitude,
   and the timing effect of §7.6.
3. **Report ranges where you have them and say so where you do not.** We quote a range wherever a
   quantity was measured more than once and flag the single measurements as single (§8.6).
   [sclar-2024] recommend this while also noting that single-format evaluation "may still be
   sufficient for many use cases", so it is a reporting discipline rather than a design requirement.

The first is what the design this paper is positioned against lacked. The second is what its own
authors eventually supplied, re-running the experiment the following spring and not reproducing
its headline contrast on GPT-4o [dobariya-kumar-2026]. Their re-run is not a null — §1.1 and §3.3
give it in full — but the 4.0-point polite-to-rude gap it was known for becomes 0.4.
