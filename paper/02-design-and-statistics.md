# 2. Design, estimators, and what our nulls exclude

> **Draft status.** `results/analysis/accuracy_null_mde.py` reads the archived records and
> prints every contrast, pooled estimate, MDE, TOST, Cochran's Q and turn-count figure quoted
> in §2.6–§2.8, plus the firing-rate check in §2.5. Design facts in §2.1–§2.3 come from
> `RESULTS.md` and `harness/`. Citation keys resolve to §9.

## 2.1 Substrate, sample, and the turn ceiling

All runs use SpreadsheetBench [ma-2024], a benchmark of real workbook-editing instructions
taken from Excel forums, with 912 instructions and 2,729 test cases. Accuracy throughout is
the benchmark's **hard restriction**: all three of an instruction's test cases must pass, no
partial credit, following its ICPC scoring rule. We do not report the soft restriction.

Our sample is a fixed set of 50 instructions, a strict subset of an earlier 100-instruction
validation sample, so every task has a measured neutral baseline and a verified no-op floor of
zero — a task that a do-nothing agent passes would inflate every arm equally, and none of ours
is one.

The agent is a ReAct loop with code execution and execution feedback, structurally the same
configuration SpreadsheetBench specifies for its multi-round setting. **The turn ceiling is
ours, and it changed mid-study.** The benchmark imposes a limit of five rounds. Our first three
interjection runs used ten; the cross-model run used twenty, after the ten-turn ceiling was
found to censor the continue-signal arms hardest. Where a contrast pools across runs the
ceilings differ, and §2.8 says which.

Twenty is defended empirically in §6: across the dedicated ceiling-20 run, the best answer was
first reached at a median turn of 2, and 98.3% of trajectories had peaked by turn 10 with 100%
by turn 14 (§6.6).

### The models

Both are named, with the provider-pinned identifiers the runs actually used, so the study can be
re-run against the same weights rather than against whatever currently answers to a family name:

| Short name in this paper | Provider identifier | Pinned slug |
|---|---|---|
| **Luna** | `openai/gpt-5.6-luna` | `openai/gpt-5.6-luna-20260709` |
| **GLM** | `z-ai/glm-5.3-flash` | `z-ai/glm-5.3-flash-20260826` |

Both are served through OpenRouter, pinned to the dated slug above; `harness/config.py` holds the
roster and `tests/test_openrouter_pinning.py` asserts the pinning. Two further models —
`deepseek/deepseek-v4.1-flash` and `qwen/qwen3.8-flash` — passed the n=100 validation gate and
were specified in the roster but never run (§8.8); "two models from different labs" describes
what the budget reached, not a design choice.

### Data and code availability

Every number in this paper is recomputable from what is in the repository. The agent harness is
in `harness/`, the analysis scripts in `results/analysis/`, and the raw per-trajectory records —
46 files, including the per-turn regrade — in `results_archive/`.

The records are committed to `results_archive/` under archive names, partly gzipped, while the
scripts read from `results/analysis/`, which is git-ignored. Each script therefore calls
`results/analysis/_inputs.py` on startup, which copies or decompresses the archive into the names
the scripts expect; the mapping is one-to-one and is documented there. That step was added after
a review pass found that, without it, three of the five scripts failed on a fresh clone before
doing any work. It is stated here so the fix is visible rather than silent: every script has been
run from a checkout with the ignored contents of `results/analysis/` removed, and every one
completes.

One property of the loop matters for every per-turn measure in this paper: **each turn receives
the original input workbook, never the previous turn's output.** Turns are independent attempts
at the same problem in *workbook state* rather than refinements of a running draft — the message
history does accumulate, so attempt *k+1* is conditioned on the text of attempts 1…*k* — which is
what makes "did attempt *k+1* land closer than attempt *k*" well posed (§6.2).

## 2.2 The manipulation

Each arm delivers a single interjection mid-task, appended to an execution observation. Every
interjection in every arm is **exactly 28 tokens** under `cl100k_base` and opens with the same
`Checking in.` stem, so that *being interrupted* does not covary with what the interruption
says. The opening instruction is held at a single neutral wrapper in every arm of every run
after the first; only the interjection varies.

This matters because the study's first run was confounded by wrapper length. Across its seven
opening wrappers, length was U-shaped (35/35/30/30/31/32/34 tokens) — the same shape as
accuracy — and predicted accuracy better than register rank did (r = +0.82 against r = −0.72 on
the seven arm means). Length matching is the fix for a confound we measured in our own
instrument.

Injection turn is **crossed**, not sampled, in every run but the first micro-experiment. That
one drew the turn at random from {1, 2}; because a turn-2 injection can only fire in a
trajectory that reaches turn 2, its arms were compared on different populations, and what
looked like a timing effect was selection.

Arm order is shuffled per (model, task) from a fixed seed, with the realised position recorded
and tested — position does not predict accuracy (p = 0.61). The injection turn is seeded on
(task, trial) and not on arm, so the same turn schedule is used across arms. Temperature is 0
where settable, which is **not** deterministic on any roster model; that is why trials exist.

## 2.3 Outcomes, and which one is primary

| Measure | Role | Source |
|---|---|---|
| Turn count | **primary** | harness |
| Reasoning tokens per trajectory | secondary | provider usage fields |
| Accuracy, hard restriction | reported, underpowered by design | benchmark evaluator |
| `final_match` — fraction of the graded range correct in the **last** turn | progress | per-turn regrade |
| Redundant steps — turns after which the graded range is unchanged | waste | per-turn regrade |

Turn count is primary because it is the quantity that moves, it is model-agnostic, and it is
far better powered than accuracy at our *n* (§2.7). Reasoning tokens were the pre-registered
primary in the first run and were demoted on evidence, which we report as a change rather than
present as the original plan.

**We report `final_match`, not `best_match`.** Best match takes the maximum over a trajectory's
turns, so an arm that takes more turns gets more draws from the same distribution and a higher
maximum for free. In the run where we compared them, best match gives +0.045 (p = 0.0012) for
the continue-signal arm where final match gives +0.025 (p = 0.085). Best match is biased toward
exactly the arms this study makes longer.

For redundant turns we adopt **redundant step** from [redundancybench]. Our criterion — the
graded range is unchanged after the turn — sits between their counterfactual definition
(removing the step does not flip success to failure) and their stricter *duplicated step*
subtype, which additionally requires identical tool name, arguments and output. We do not
compare base rates against theirs: some of their redundant steps are synthetically injected.
Following [sclar-2024] and [mizrahi-2024] we report ranges rather than point estimates wherever
a quantity has been measured more than once (§2.9). Both scope that advice, and we adopt the
scoped version: [sclar-2024] note single-format evaluation "may still be sufficient for many use
cases", and [mizrahi-2024] recommend averaging across prompts when measuring robustness — our
case — while recommending the top-performing prompt when selecting a model for deployment.

## 2.4 The estimator: paired within task, clustered by task

**What the denominator is, stated before any number depends on it.** Every contrast in this paper
is against a *neutral interjection*, not against silence. Each arm is compared with a control arm
that also receives a 28-token message at the same turn; that is what isolates register from the
fact of being interrupted. It also means every headline figure here is a register effect measured
relative to an interrupted baseline, and inherits whatever that baseline does.

How much the baseline itself moves is measured **once**: the micro-experiment of §2.2 puts a
neutral interruption against no interruption at 3.47 versus 4.11 turns, +51 reasoning tokens,
**p = 0.15, on one model at one ceiling** — and it was never revisited when the ceiling, the
injection turn or the model changed. That single comparison is doing a lot of load-bearing work.
If the neutral interjection is not in fact equivalent to silence, every turn-count and
accuracy-equivalence number in this paper carries a common offset we have not bounded. The
within-comparison logic survives that — an offset shared by treated and control arms cancels in
the difference — but any reading of an arm's absolute cost against an uninterrupted agent does
not. §8.8 records the same gap; we state it here because this is where the estimator is defined.

Every trajectory belongs to one of 50 tasks, and each (task, arm) cell holds six to nine
trajectories — three or four trials at each of two or three injection turns. They are not
independent observations. Treating them as independent is the easiest way to manufacture
significance here, and an early version of our results did exactly that: its accuracy
confidence intervals were roughly 35% too narrow because the bootstrap resampled trajectories
rather than tasks.

Throughout:

- **Point estimates are paired within task.** For each task we average the outcome over that
  task's trials in each arm and take the difference; the reported effect is the mean of the
  per-task differences. This is the paired-and-clustered form of Miller's clustered estimator
  [miller-2024], appropriate because our trajectories cluster within tasks *and* our comparison
  is paired across conditions on the same tasks.
- **Intervals come from a cluster bootstrap over tasks**, 20,000 resamples — not Miller's
  analytic clustered standard error; the two agree to first order.
- **p-values come from a task-clustered sign-flip permutation test**, 20,000 draws, reported as
  (count + 1)/(draws + 1) so that no p is quoted as exactly zero.

Clustering is not a formality. Miller reports a clustered-to-CLT standard-error ratio of 3.05
on DROP, though 1.10 on RACE-H and 1.88 on MGSM, so "up to 3×" is dataset-specific and we cite
it as such.

One consequence deserves stating because it affected our own earlier drafts. The unpaired
difference of arm means and the paired task-clustered difference are **two estimators of the
same contrast, and they do not give the same number.** The praise contrast is −0.62 and −1.14
turns under the first and −0.59 and −1.08 under the second. Both are correct; only one is
comparable to the rest of this paper, and a paper whose §7 concerns point estimates failing to
replicate cannot quote two different pairs for one contrast. Every number here is the paired,
task-clustered one.

## 2.5 Exclusions, and why they are not selection

An interjection scheduled for turn *t* is delivered only if the trajectory reaches turn *t*.
Trajectories on which it did not fire received no dose and are excluded from every contrast.

That exclusion is pre-treatment. Whether a trajectory reaches turn *t* is settled before the
interjection exists, so it cannot differ by arm except by chance, and it does not: at turn 2 of
the demand/affect probe the four arms fired on 54.0%, 57.0%, 57.0% and 59.5% of their 200
scheduled trajectories. The per-protocol analysis is therefore unbiased here.

What does differ, sharply, is reachability **across injection turns**: roughly 98% at turn 0,
77% at turn 1, 55% at turn 2. Comparing turns compares different task populations. For timing
contrasts only, we fix the comparison population from the **control** arm — a task enters a
turn-*t* contrast only if control's trajectories for that task reach turn *t* — so the
population is the same at every turn and is defined by a quantity the manipulation cannot have
moved. Where this shrinks the sample we report the reduced task count with the estimate.

Two other exclusions, both recorded: the 402 rows from an interrupted first attempt at the
seven-level run, and the regrade that followed a scratch-directory collision in the
micro-experiment, which is why that run appears in the family below as regraded records.

## 2.6 Multiplicity

Two families are corrected, and both are defined exhaustively rather than after the fact.

The first run tested twelve outcomes for a linear trend across seven arms. Under a global null
the chance that at least one lands below p = 0.023 is 0.24, and the accuracy trend that did so
does not survive Benjamini–Hochberg across that family (critical value 0.0042). We report it as
a lead, not a result.

The accuracy family is **every arm-versus-control accuracy contrast in every run that delivered
a mid-task interjection**: 22 contrasts across six runs and two models. Defining it more
narrowly would drop the contrast that came in nominally strongest, which is the one way a
family of this kind gets gerrymandered.

Two of the 22 are nominally significant, against 1.1 expected under a global null
(P(at least one) = 0.68): the continue-signal contrast in the ceiling-20 run at p = 0.0040, and
praise versus control on GLM at p = 0.0137. Neither survives correction — BH's rank-1 critical
value is 0.0023, and the Bonferroni-adjusted smallest p is 0.089 — and the first of the two
reversed sign on re-measurement (§2.9). We report both and build on neither.

**The primary outcome is corrected too, over the same family.** An earlier draft corrected
accuracy and the trend family but left turn count — which §2.3 declares the primary outcome —
uncorrected, while reporting dozens of turn-count contrasts across §4–§7. That was the obvious
hole in this section and we have closed it rather than argued about it.

The turn-count family is not chosen separately. It is the *same* 22 comparisons as the accuracy
family above — every arm-versus-control contrast in every run that delivered a mid-task
interjection, across six runs and two models — with the outcome switched from graded pass to
turns. Inheriting the boundary is deliberate: choosing a turn-count family by hand, after seeing
which contrasts are large, is the gerrymandering this section already warns against.
`results/analysis/turn_count_family.py` recomputes it and reuses the same tested
Benjamini–Hochberg implementation.

**Seventeen of the 22 survive at q = 0.05.** The Bonferroni-adjusted smallest p is 0.0011. The
five that do not survive are:

| Contrast | Δ turns | p |
|---|---:|---:|
| praise vs control (stage 1, GLM, ceiling 20) | −0.35 | 0.058 |
| insult vs control (stage 1, Luna, ceiling 20) | +0.57 | 0.165 |
| insult vs control (probe, Luna, ceiling 10) | −0.08 | 0.624 |
| `L5_rude` vs neutral (seven-level, Luna, ceiling 10) | +0.09 | 0.654 |
| insult vs control (stage 1, GLM, ceiling 20) | +0.07 | 0.659 |

The result cuts in the paper's favour and we note that it could have gone the other way. Every
demand-carrying contrast survives, on both models. Every closing-cue and praise contrast on Luna
survives. **All three insult contrasts fail, and so does the one rude register arm** — which is
the dissociation §4 argues for, now holding under correction rather than only nominally.

Three honest qualifications. First, correcting the primary outcome after the fact is weaker than
pre-registering the family, and we did not pre-register it. Second, the p-values in this family
are for the *absolute* turn difference under the §2.4 estimator, while §4.7's table reports the
same six cross-model contrasts as *percentage* changes under a separate ratio bootstrap; the two
differ in the third decimal — GLM praise is 0.058 here and 0.062 there, Luna demand 0.0009 and
0.0013 — and **no verdict at 0.05 differs on any shared contrast**. A reader who spots the same
contrast carrying two p-values is seeing two statistics, not two data sets. Third, the family
reads turn counts from the run records throughout — including for the micro-experiment, where the
accuracy family reads the per-turn *regrade* instead, which is a grading pass and the right source
for accuracy but not for an observed trajectory count. That row is +1.32 turns, matching §7.2. An
earlier version of this script inherited the regrade file for that row and got +1.02; the
regraded file carries different turn counts for the same 50 trajectories, which a regrade should
not change. That does not touch this family, and we record it as an oddity in that artefact
rather than resolve it here.

## 2.7 What the design can detect

A null is worth reporting only if the design could have seen the effect it is contrasted with.
For each contrast we invert the standard power relation at the realized cluster-bootstrap
standard error: the minimum detectable effect at 80% power and α = 0.05 two-sided is
(z₀.₉₇₅ + z₀.₈₀)·SE ≈ 2.80·SE, following [miller-2024]'s sample-size inversion.

**On turn count the design is adequately powered, unevenly.** Realized MDE runs from 0.42 to
1.39 turns, against control means of 2.94 turns (GLM) and 4.07–4.95 (Luna, the two ceilings).
The demand effects sit at 1.1–2.2× their own MDE. The praise effects sit at 0.7–1.4×, so the
cross-model praise contrasts are below 80% power at their observed size — which is consistent
with GLM's praise arm not reaching significance on its own, and is why §4 rests the replication
on the demand arm.

**On accuracy it is not, and that is the limitation.** Across the 22 contrasts the realized MDE
has a median of 5.52 accuracy points and a range of 3.74 to 7.77. The largest accuracy movement
in the family is 6.57 points; the published tone-accuracy gap we are positioned against is
about 4 [dobariya-kumar-2025]. So **a single contrast cannot exclude the smallest published
effect** — TOST equivalence at ±4 points is reached in 6 of 22 — **but every contrast can
exclude the largest ones.** At ±7.5 points, the *median* format-induced spread reported by
[sclar-2024] and the right comparator rather than their 76-point single-task maximum, 19 of 22
reach equivalence. The 11–12 point spreads that [dobariya-kumar-2026] reports on Gemini 2.5
Flash Lite and ChatGPT-5-nano are inside every contrast's detection range.

The reason accuracy is so much worse powered than turn count is structural, not a matter of
sample size alone: **26 of our 50 tasks are never solved by the control arm and 4 are always
solved**, so for more than half the sample the per-task accuracy difference is pinned at zero
by construction whatever the manipulation does. Turn count varies on every task.

## 2.8 Stating the accuracy null as equivalence, not as absence

"We found no significant difference" is not a finding, so we state the null the way a null
should be stated [lakens-2017]. (We do not cite [miller-2024] for this; his paper contains no
equivalence framework, and the MDE machinery we borrow from him is a separate thing.)

The pre-specified smallest effect of interest is **±4 accuracy points**, the polite-versus-rude
gap of the paper this work is positioned against. Pooling the repeated measurements of each
contrast, with the interval from a bootstrap that resamples tasks **jointly across runs** — the
runs share their 50 tasks, so an inverse-variance interval treating them as independent
understates the standard error:

| Contrast | k | Ceilings | Estimate | 95% CI | 90% CI | MDE₈₀ | TOST at ±4 |
|---|---:|---|---:|---|---|---:|---:|
| Demand vs control | 3 | 10, 20, 20 | −0.31 pts | [−2.72, +2.10] | [−2.33, +1.72] | 3.45 | 0.0014 |
| Praise vs control | 4 | 10, 10, 20, 20 | −0.12 pts | [−1.79, +1.55] | [−1.52, +1.29] | 2.39 | 0.0000 |
| Insult vs control | 3 | 10, 20, 20 | −0.04 pts | [−2.11, +2.04] | [−1.78, +1.71] | 2.97 | 0.0001 |

So the claim is bounded and specific: **a mid-task interjection — demanding, praising, or
insulting — does not change task accuracy by as much as the four points the tone literature
reports, while demand raises turn count by 18–34%, praise lowers it by 11–24%, and insult does
not move it at all.** It is not "register does not affect accuracy"; it is that an effect of
the published size is excluded and an effect of a point or two is not.

Two caveats, both against us. The praise pooling is heterogeneous — Cochran's Q = 8.45 on 3 df,
p = 0.038 — and the heterogeneity is between models, not within: pooling Luna's three praise
measurements alone gives Q = 0.36, p = 0.834, and −1.27 points, 95% CI [−3.13, +0.59]. Under a
random-effects pool, which that heterogeneity warrants, the praise estimate becomes +0.21 with
a standard error of 1.68 and the ±4 equivalence weakens to p = 0.0119 but holds. Demand and
insult show no detectable heterogeneity (p = 0.196 and p = 0.246), though Q on 2 df has little
power to detect any.

**No accuracy effect in this study has replicated.** Two nominal hits exist (§2.6); the larger
of them, a +6.6-point movement on the continue-signal contrast, came back at −1.8 points on
identical tasks and ceiling (§2.9). That is the honest version of "accuracy never moves".

## 2.9 Ranges, not point estimates

Several quantities in this study moved materially when measured again on the same tasks, model
and ceiling; §7.2 tabulates every contrast we measured more than once. The praise contrast gave
−0.59 turns in one run and −1.08 in another; accuracy on the continue-signal contrast gave +6.6
points and then −1.8; the insult arm flipped sign on both turns and reasoning tokens. (A fourth
apparent instability, that contrast's effect on final match, turned out to be a defective
instrument rather than a property of the runs — see §6.8 and §7.4.)

The pattern differs by outcome, and conflating them would flatter us. **For the turn-count
effects, direction and significance replicated and the point estimates did not. For final match,
direction and magnitude replicated once the instrument was fixed, though only one of three
measurements is individually significant. For accuracy, neither did.** We therefore
treat a point estimate quoted once as provisional by default rather than by exception, and say
where only one measurement exists.

## 2.10 The noise floor

The benchmark's own evaluator audit bounds what any of this can resolve: on 50 sampled
instructions, [ma-2024] report an instruction-level false-negative rate of 4% and a
test-case-level false-omission rate of 3.8%, with a false-discovery rate of 0% — the failures
are one-directional, usually from generated code writing content beyond the target cells.

Because our contrasts are paired on the same tasks, the task-level component of that error is
common to both arms and cancels. What remains is an attenuation: a 4% one-directional
false-negative rate scales a true differential by at most about 0.96, which cannot change its
sign and is negligible against effects of the size at issue here. The floor is a reason our
accuracy estimates are noisy; it is not a reason the intervals in §2.8 are wrong.
