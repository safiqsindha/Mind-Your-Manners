# 2. Design, estimators, and what our nulls exclude

> **Draft status.** `results/analysis/accuracy_null_mde.py` reads the archived records and prints every
> contrast, pooled estimate, MDE, TOST, Cochran's Q and turn-count figure quoted in §2.6–§2.7, plus the
> firing-rate check in §2.5.

## 2.1 Substrate, sample, and models

All runs use SpreadsheetBench [ma-2024], a benchmark of real workbook-editing instructions from Excel
forums. Accuracy throughout is its **hard restriction**: all three of an instruction's test cases must
pass, no partial credit. Our sample is a fixed set of 50 instructions, a strict subset of an earlier
100-instruction validation sample, so every task has a measured neutral baseline and a verified no-op
floor of zero. The agent is a ReAct loop with code execution and execution feedback, structurally the
configuration SpreadsheetBench specifies for its multi-round setting.

**The turn ceiling is ours, and it changed mid-study.** The benchmark caps at five rounds; our first three
interjection runs used ten, and the cross-model run used twenty after the ten-turn ceiling was found to
censor the continue-signal arms hardest. Where a contrast pools across runs the ceilings differ, and §2.7
says which. Twenty is defended empirically in §6.4.

**Models.** **Luna** is `openai/gpt-5.6-luna`, pinned to `openai/gpt-5.6-luna-20260709`; **GLM** is
`z-ai/glm-5.3-flash`, pinned to `z-ai/glm-5.3-flash-20260826`, both through OpenRouter with the pinning
asserted in tests. Two further models passed the n=100 validation gate and were never run (§8.5): "two
models from different labs" describes what the budget reached, not a design choice. Every number here is
recomputable from the repository — harness, analysis scripts, and 46 raw per-trajectory record files
including the per-turn regrade — from a clean checkout.

One property of the loop matters for every per-turn measure: **each turn receives the original input
workbook, never the previous turn's output.** Turns are independent attempts in *workbook state* — the
message history does accumulate, so attempt *k+1* is conditioned on the text of attempts 1…*k* — which is
what makes "did attempt *k+1* land closer?" well posed (§6.1).

## 2.2 The manipulation

Each arm delivers a single interjection mid-task, appended to an execution observation. Every interjection
is **exactly 28 tokens** under `cl100k_base` and opens with the same `Checking in.` stem, so that *being
interrupted* does not covary with what the interruption says; the opening instruction is held at one
neutral wrapper in every arm of every run after the first. Appendix A prints all of them, generated from
the harness rather than transcribed, with token counts recomputed rather than asserted.

Length matching is the fix for a confound we measured in our own instrument: the study's first run varied
seven *opening* wrappers whose length was U-shaped (35/35/30/30/31/32/34 tokens) — the same shape as
accuracy — and length predicted accuracy better than register rank did (*r* = +0.82 against −0.72).

Injection turn is **crossed**, not sampled, in every run but the first micro-experiment, which drew it at
random from {1, 2}; because a turn-2 injection can only fire in a trajectory that reaches turn 2, its arms
were compared on different populations and what looked like a timing effect was selection (§7.3). Arm order
is shuffled per (model, task) from a fixed seed and position does not predict accuracy (*p* = 0.61).
Temperature is 0 where settable, which is **not** deterministic on any roster model; that is why trials
exist.

## 2.3 Outcomes, and which one is primary

| Measure | Role | Source |
|---|---|---|
| Turn count | **primary** | harness |
| Reasoning tokens per trajectory | secondary | provider usage fields |
| Accuracy, hard restriction | reported, underpowered by design | benchmark evaluator |
| `final_match` — fraction of the graded range correct in the **last** turn | progress | per-turn regrade |
| Redundant steps — turns after which the graded range is unchanged | waste | per-turn regrade |

Turn count is primary because it is the quantity that moves, it is model-agnostic, and it is far better
powered than accuracy at our *n* (§2.7). Reasoning tokens were the pre-registered primary in the first run
and were demoted on evidence, which we report as a change rather than present as the original plan. **We
report `final_match`, not `best_match`**, because best match takes the maximum over a trajectory's turns
and so hands an arm that takes more turns a higher maximum for free. We adopt **redundant step** from
[redundancybench], with a criterion between their counterfactual definition and their stricter *duplicated
step* subtype, and do not compare base rates against theirs. Following [sclar-2024] and [mizrahi-2024] we
report ranges wherever a quantity was measured more than once, in the scoped form those authors give:
average across prompts when measuring robustness, which is our case.

## 2.4 The estimator: paired within task, clustered by task

**What the denominator is, stated before any number depends on it.** Every contrast is against a *neutral
interjection*, not against silence: each arm is compared with a control arm that also receives a 28-token
message at the same turn, which is what isolates register from the fact of being interrupted. How much the
baseline itself moves is measured **once** — the micro-experiment puts a neutral interruption against no
interruption at 3.47 versus 4.11 turns, ***p* = 0.15, on one model at one ceiling**, never revisited when
the ceiling, injection turn or model changed. If the neutral interjection is not equivalent to silence,
every number here carries a common offset we have not bounded; an offset shared by treated and control arms
cancels in the difference, so the within-comparison logic survives, but any reading of an arm's absolute
cost against an uninterrupted agent does not (§8.5).

Every trajectory belongs to one of 50 tasks, and each (task, arm) cell holds six to nine trajectories. They
are not independent, and treating them as independent is the easiest way to manufacture significance here —
an early version of our results did exactly that, with accuracy intervals roughly 35% too narrow.
Throughout: **point estimates are paired within task** (per task, the mean over that task's trials in each
arm, differenced, then averaged — the paired-and-clustered form of Miller's clustered estimator
[miller-2024]); **intervals come from a cluster bootstrap over tasks**, 20,000 resamples; ***p*-values come
from a task-clustered sign-flip permutation test**, 20,000 draws, reported as (count + 1)/(draws + 1) so
that no *p* is quoted as exactly zero. Clustering is not a formality — Miller reports clustered-to-CLT
standard-error ratios of 1.10, 1.88 and 3.05 across three datasets, so "up to 3×" is dataset-specific. Note
also that the unpaired difference of arm means and the paired task-clustered difference are **two estimators
of the same contrast that do not agree**: the praise contrast is −0.62 and −1.14 turns under the first,
−0.59 and −1.08 under the second. Every number here is the paired one (§7.3).

## 2.5 Exclusions, and why they are not selection

An interjection scheduled for turn *t* is delivered only if the trajectory reaches turn *t*; trajectories on
which it did not fire received no dose and are excluded. That exclusion is pre-treatment — whether a
trajectory reaches turn *t* is settled before the interjection exists, so it cannot differ by arm except by
chance, and it does not: at turn 2 of the demand/affect probe the four arms fired on 54.0%, 57.0%, 57.0% and
59.5% of their 200 scheduled trajectories. What does differ, sharply, is reachability **across injection
turns** — roughly 98% at turn 0, 77% at turn 1, 55% at turn 2 — so comparing turns compares different task
populations. For timing contrasts only, we fix the comparison population from the **control** arm and report
the reduced task count with the estimate. Two other exclusions are recorded: 402 rows from an interrupted
first attempt at the seven-level run, and a regrade following a scratch-directory collision (§7.3).

## 2.6 Multiplicity

Two families are corrected, both defined exhaustively rather than after the fact. The first run tested twelve
outcomes for a linear trend across seven arms; the accuracy trend that came in at *p* = 0.023 does not
survive Benjamini–Hochberg across that family (critical value 0.0042), and we report it as a lead.

The accuracy family is **every arm-versus-control accuracy contrast in every run that delivered a mid-task
interjection**: 22 contrasts across six runs and two models. Defining it more narrowly would drop the
contrast that came in nominally strongest, which is the one way a family of this kind gets gerrymandered.
Two of the 22 are nominally significant against 1.1 expected under a global null — the continue-signal
contrast at *p* = 0.0040 and praise versus control on GLM at *p* = 0.0137 — and neither survives correction
(BH's rank-1 critical value is 0.0023). The first reversed sign on re-measurement.

**The primary outcome is corrected too, in two stated families.** An earlier draft left turn count
uncorrected while reporting dozens of turn-count contrasts. The first family is the *same* 22 comparisons
with the outcome switched to turns; inheriting the boundary is deliberate, because choosing a turn-count
family by hand after seeing which contrasts are large is the gerrymandering just warned against. The second
is §5's two **designed within-run contrasts** — designed, not pre-registered — which are not against
control: praise isolated, `Q4` − `Q5`, at −1.35 turns (*p* < 0.0001), and closing cue versus praise at −0.36
(*p* = 0.017), both surviving at *q* = 0.05 in a family of two. A family of two corrects almost nothing, and
we say so; its purpose is that no turn-count claim the paper relies on rests on unadjusted inference alone.
Deliberately left uncorrected, and labelled where it appears, is §7.2's same-instrument comparison between
two measurements of one contrast.

**Seventeen of the 22 survive at *q* = 0.05**; the Bonferroni-adjusted smallest *p* is 0.0011. The five that
do not are praise vs control on GLM (−0.35, *p* = 0.058), all three insult contrasts (+0.57, −0.08, +0.07;
*p* = 0.165, 0.624, 0.659) and `L5_rude` vs neutral (+0.09, *p* = 0.654). The result cuts in the paper's
favour and could have gone the other way: every demand-carrying contrast survives on both models, every
closing-cue and praise contrast on Luna survives, and **all three insult contrasts fail, as does the one
rude register arm** — which is the dissociation §4 argues for, holding under correction. It is also the arm
blinded raters code against us (§4.2), so the correction and the reliability check land on the same cell
from opposite directions.

Three qualifications. Correcting a primary outcome after the fact is weaker than pre-registering the family,
and we did not pre-register it. These *p*-values are for the *absolute* turn difference under the §2.4
estimator, while §4.6 reports the same cross-model contrasts as *percentage* changes under a separate ratio
bootstrap; the two differ in the third decimal and **no verdict at 0.05 differs on any shared contrast**. And
a reader comparing our turn counts with another paper's needs to know which quantity is meant: the run records
store *acting* turns, those that emitted code, while the per-turn regrade stores model calls, including the
closing `FINAL:` message that carries none — mean 3.57 against 4.69 on the micro-experiment, a 31% relative
gap. **Turn count in this paper means acting turns throughout.**

## 2.7 Power, and the accuracy null stated as equivalence

A null is worth reporting only if the design could have seen the effect it is contrasted with, and "we found
no significant difference" is not a finding. For each contrast we invert the standard power relation at the
realized cluster-bootstrap standard error — the MDE at 80% power and α = 0.05 two-sided is
(z₀.₉₇₅ + z₀.₈₀)·SE ≈ 2.80·SE, following [miller-2024] — and state the null as an equivalence [lakens-2017].
(Not [miller-2024], whose paper contains no equivalence framework.)

**On turn count the design is adequately powered, unevenly.** Realized MDE runs from 0.42 to 1.39 turns
against control means of 2.94 (GLM) and 4.07–4.95 (Luna). The demand effects sit at 1.1–2.2× their own MDE;
the praise effects at 0.7–1.4×, so the cross-model praise contrasts are below 80% power at their observed
size — consistent with GLM's praise arm not reaching significance, and why §4 rests the replication on the
demand arm. **On accuracy it is not, and that is the limitation.** Across the 22 contrasts the realized MDE
has a median of 5.52 accuracy points and a range of 3.74 to 7.77, against a published tone-accuracy gap of
about 4 [dobariya-kumar-2025]. So **a single contrast cannot exclude the smallest published effect** — TOST
equivalence at ±4 is reached in 6 of 22 — **but every contrast can exclude the largest ones**: at ±7.5, the
*median* format-induced spread reported by [sclar-2024] rather than their 76-point single-task maximum, 19
of 22 reach equivalence. The reason is structural: **26 of our 50 tasks are never solved by the control arm
and 4 are always solved**, so for more than half the sample the per-task accuracy difference is pinned at
zero whatever the manipulation does. Turn count varies on every task.

The pre-specified smallest effect of interest is **±4 accuracy points**, the polite-versus-rude gap of the
paper this work is positioned against. Pooling the repeated measurements of each contrast, with the interval
from a bootstrap that resamples tasks **jointly across runs** — the runs share their 50 tasks, so an
inverse-variance interval treating them as independent understates the standard error:

| Contrast | *k* | Ceilings | Estimate | 95% CI | MDE₈₀ | TOST at ±4 |
|---|---:|---|---:|---|---:|---:|
| Demand vs control | 3 | 10, 20, 20 | −0.31 pts | [−2.72, +2.10] | 3.45 | 0.0014 |
| Praise vs control | 4 | 10, 10, 20, 20 | −0.12 pts | [−1.79, +1.55] | 2.39 | 0.0000 |
| Insult vs control | 3 | 10, 20, 20 | −0.04 pts | [−2.11, +2.04] | 2.97 | 0.0001 |

So the claim is bounded and specific: **a mid-task interjection — demanding, praising, or insulting — does
not change task accuracy by as much as the four points the tone literature reports, while demand raises turn
count by 18–34%, praise lowers it by 11–24%, and insult does not move it at all.** It is not "register does
not affect accuracy"; it is that an effect of the published size is excluded and an effect of a point or two
is not.

Two caveats, both against us. The praise pooling is heterogeneous — Cochran's *Q* = 8.45 on 3 df,
*p* = 0.038 — and between models rather than within: Luna's three praise measurements alone give *Q* = 0.36
and −1.27 points, 95% CI [−3.13, +0.59]. Under a random-effects pool, which that heterogeneity warrants, the
praise estimate becomes +0.21 with a standard error of 1.68 and the ±4 equivalence weakens to *p* = 0.0119
but holds. And **no accuracy effect in this study has replicated**: the larger nominal hit, +6.6 points on
the continue-signal contrast, came back at −1.8 on identical tasks and ceiling.

## 2.8 Ranges, not point estimates — and the noise floor

Several quantities moved materially when measured again on the same tasks, model and ceiling; §7.1 tabulates
every contrast we measured more than once. The pattern differs by outcome, and conflating them would flatter
us: **for the turn-count effects, direction and significance replicated and the point estimates did not; for
final match, direction and magnitude replicated once the instrument was fixed; for accuracy, neither did.**
We therefore treat a point estimate quoted once as provisional by default rather than by exception (§8.3).

The benchmark's own evaluator audit bounds what any of this can resolve: [ma-2024] report an
instruction-level false-negative rate of 4% and a test-case-level false-omission rate of 3.8%, with a
false-discovery rate of 0%, so the failures are one-directional. Because our contrasts are paired on the
same tasks, the task-level component of that error cancels; what remains is an attenuation of at most about
0.96 on a true differential, which cannot change its sign. The floor is a reason our accuracy estimates are
noisy; it is not a reason the intervals above are wrong.
