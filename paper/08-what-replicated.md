# 8. What replicated, and what only looked like it did

> **Draft status.** Every figure in §8.2 is printed by `results/analysis/replication_table.py`,
> which recomputes each contrast from the archived records under the estimator of §2.4. Citation
> keys are placeholders.

## 8.1 Why this section exists

This study measured several of its contrasts more than once, not by design at first but because
the design kept changing — a probe run, a follow-up with more arms, a re-run at a higher ceiling,
a second model. That accident is the most useful thing in the paper, because it lets us ask of
our own results the question this literature mostly does not ask of its own: **measured again, on
the same tasks and the same model, what comes back?**

The answer is not uniform, and the useful finding is *which* properties survive.

Reporting this is not a courtesy. [vaugrante-2024] re-ran five prompt-engineering techniques
against their originals and found "a general lack of statistically significant differences across
nearly all techniques tested" — emotional prompting replicated at +1%, χ² = 0.11, p = .74 — and
their diagnosis of the original was not fabrication but selection: "instead of communicating the
average improvement of the enhanced prompts over the regular prompts, they focused on
improvements when cherry-picking the most performant emotional cue." Recomputed from the
original's own data, the average was 4.42% on BIG-Bench and 2.58% across all benchmarks against a
headline of 115%. We would rather do this to ourselves than have it done for us.

## 8.2 The replication table

Every contrast we measured more than once on the same model, under the estimator of §2.4. Turn
count, the primary outcome:

| Contrast | Measurement | Δ turns | 95% CI | p |
|---|---|---:|---|---:|
| **Praise vs control** | probe, ceiling 10 | −0.59 | [−0.88, −0.29] | 0.0002 |
| | praise run, ceiling 10 | −1.08 | [−1.46, −0.71] | <0.0001 |
| | stage 1, ceiling 20 | −1.01 | [−1.81, −0.23] | 0.017 |
| **Demand vs control** | probe, ceiling 10 | +1.17 | [+0.80, +1.55] | <0.0001 |
| | stage 1, ceiling 20 | +1.75 | [+0.77, +2.73] | 0.0010 |
| **Insult vs control** | probe, ceiling 10 | −0.08 | [−0.40, +0.24] | 0.62 |
| | stage 1, ceiling 20 | +0.57 | [−0.22, +1.35] | 0.17 |
| **"Work remains" vs control** | praise run, ceiling 10 | +1.85 | [+1.39, +2.29] | <0.0001 |
| | dedicated re-run, ceiling 20 | +6.20 | [+4.90, +7.50] | <0.0001 |
| | stage 1, ceiling 20 | +5.77 | [+4.70, +6.91] | <0.0001 |

Three things follow, and they are different claims.

**Direction and significance replicate wherever the effect is large.** Praise is negative and
significant in all three measurements; demand positive and significant in both; "work remains"
positive and significant in all three. The qualitative findings of §4 and §5 are not fragile.

**Magnitude does not, and the ratios are not small.** Praise spans 1.8× across three
measurements. "Work remains" spans 3.4×. Demand spans 1.5×. **A point estimate from any single
run of this study should be read as a draw, not as a value.**

**The null is the least stable cell.** Insult versus control is −0.08 in one measurement and
+0.57 in the other — a sign flip and a 7× ratio — though neither reaches significance and both
intervals contain zero. An effect that is not there is not thereby measured precisely.

## 8.3 Some of that spread is the instrument, and some is not

Two of the contrasts above were measured twice at the *same* turn ceiling, which is the only fair
magnitude comparison — a different ceiling is a different instrument, and the arms that persist
longest are the ones a low ceiling truncates hardest.

| Contrast, matched ceiling | Measurements | Spread |
|---|---|---:|
| "Work remains" vs control, ceiling 20 | +6.20, +5.77 | **1.1×** |
| Praise vs control, ceiling 10 | −0.59, −1.08 | **1.8×** |

**The large effect replicates tightly and the small one does not.** That is the expected pattern
rather than a surprise, and it locates the instability: it is sampling noise on effects that are
near the design's resolution, not a defect in the harness. §2.7 gives the realized MDEs that make
this concrete — 0.42 turns for the probe's praise contrast, 1.13 for stage 1's.

So the honest generalisation is narrower than "nothing replicates". It is: **in this design, a
turn-count effect above about 1.5 turns reproduces its magnitude within ~10%; an effect below one
turn reproduces its direction but not its size.**

## 8.4 The outcome that did not replicate at all

Two contrasts flip sign across measurements on outcomes other than turn count, and both involve
the same arm.

| | Ceiling 10 | Ceiling 20 | Ceiling 20, third run |
|---|---:|---:|---:|
| "Work remains", Δ turns | +1.85 | +6.20 | +5.77 |
| "Work remains", Δ final match | +0.014 (p = 0.50) | **+0.061 (p = 0.0028)** | +0.019 (p = 0.16) |
| "Work remains", Δ accuracy | +2.4 pts (p = 0.24) | **+7.0 pts (p = 0.0043)** | **−1.8 pts** (p = 0.38) |

The turn effect replicates. **Neither outcome measure does.** Final match is null in two of three.
Accuracy came in at +7.0 points and then at −1.8 points on identical tasks, model and ceiling —
opposite signs — so the p = 0.0043 was noise.

This is worth dwelling on because of how convincing the middle column was at the time. It carried
two *different instruments* agreeing: a progress measure and the benchmark's own grade, both
positive, both significant, on the same contrast. That felt like corroboration. It was two
measures agreeing inside a single unreplicated run, which is a much weaker thing — the two
instruments share every source of run-level noise, so their agreement adds almost nothing.

We also tested the obvious rescue and it failed. The natural reading is that the 10-turn ceiling
truncated real progress, which is testable: truncate the ceiling-20 run's own analysis to ten
turns and see whether the effect survives. It does — +0.049 (p = 0.0065) at ten turns, +0.056 at
fifteen, +0.061 at twenty. The effect is fully present within the first ten turns of that run. The
ceiling explains almost none of the gap between +0.014 and +0.049; what separates them is that
they are two different runs.

**So: a continue signal buys more turns, reliably, on two models. Whether it buys a better answer
is unresolved, and we report it as unresolved rather than as either a null or a finding.**

## 8.5 Four claims this study withdrew about itself

Instability is one failure mode. Analysis error is another, and this study produced four of them
that survived at least one draft. We list them because a paper arguing that a literature's
headline effects are artefacts of design should be legible about its own.

**A timing effect that was selection.** An early micro-experiment split the interruption effect by
injection turn and found +21% at turn 1 against +39% at turn 2, p = 0.004. The injection turn was
drawn at random, and a turn-2 injection can only fire in a trajectory that reaches turn 2 — the
harder, longer tasks. The two positions were measured on different task populations, 50 tasks
against 35. Recomputed on a control-defined population of 29 tasks: +20.0% against +29.1%,
p = 0.32. Withdrawn. This is why injection turn is crossed rather than sampled (§2.2) and why the
comparison population is fixed from control (§2.5).

**A timing effect that was a proxy.** The crossed run then found the interjection inert at turn 0
and large at turns 1 and 2, which looks like position. §4.6 shows it is not: holding turn index
fixed and varying whether a candidate answer exists yet changes the effect from +0.34 to +1.97,
while holding the moderator fixed and varying the turn index changes it from +1.97 to +1.66. The
operative variable is whether there is work for the message to be about.

**A ceiling explanation that we tested and withdrew.** §8.4 above. The correction was written,
then the correction was checked, then the correction was withdrawn.

**A productive window that was a rate on a small denominator.** A per-turn improvement rate of
1–5% out at turns 10–14 was read as evidence that the productive window extended that far. The
rate was real. In absolute terms those turns contain almost no improvements: zero of 43
improvements in the run occurred at turn 15 or later, and 97% of trajectories had peaked by turn
10 (§6.5).

Three of the four were caught by a test we ran on ourselves rather than by a reviewer. The
fourth — the selection confound — was caught by noticing that two arms had different task counts.

## 8.6 Two infrastructure failures worth recording

Neither changed a conclusion, but both are the kind of thing that silently corrupts a result.

**Shared scratch directories.** Two runs used the same tone over the same 50 tasks and the same 8
trials, and the scratch path did not include the run label — so 800 trajectories shared 400
execution directories, and two concurrent processes unlinked and rewrote one another's output
workbook. Every pass/fail flag in those runs was suspect. Token counts come from the provider's
API response and never touch the filesystem, so the cost effect was never in question. The grades
were recovered by regrading from the archived logs, at no cost. Scratch paths are now namespaced
by run tag and injection turn.

**A silent range-parser bug.** `"P2:P7"` parsed as sheet `P2:` plus cell `P7`, grading a one-cell
range on a sheet that does not exist. Every affected lookup returned `None`, which reads as
*unmeasurable* rather than as *broken*. It was caught by validating the regrade against a real
task before scaling up, and it is the reason §6.2 describes that validation step.

## 8.7 What we would ask of this literature

Nothing here is a novel methodological proposal; it is the discipline [vaugrante-2024],
[sclar-2024] and [miller-2024] already ask for, applied to a study small enough that applying it
is cheap. Three things, in order of how much they cost:

1. **Report the estimator.** The unpaired difference of arm means and the paired task-clustered
   difference give different numbers for the same contrast (§2.4). Ours differed by up to 6% on
   the praise contrast. A paper that does not say which it used cannot be compared to one that
   does.
2. **Measure at least one contrast twice.** It cost us nothing we would not have spent anyway and
   it changed what we were willing to claim about four separate results. The second measurement is
   the cheapest experiment in the paper.
3. **Report ranges where you have them and say so where you do not.** We quote a range wherever a
   quantity was measured more than once and flag the single measurements as single.

The first two are what would have caught the effect this paper is positioned against before it
was published — and, to their credit, its own authors caught it themselves within seven months
[dobariya-kumar-2026].
