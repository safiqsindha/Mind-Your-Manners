# 2. Design and statistics

## 2.1 Substrate, sample, and models

All runs use SpreadsheetBench [ma-2024]. Accuracy throughout is its **hard restriction**: all three
of an instruction's test cases must pass, no partial credit. Our sample is a fixed set of 50
instructions, a strict subset of an earlier 100-instruction validation sample, so every task has a
measured neutral baseline and a verified no-op floor of zero. The agent is a ReAct loop with code
execution and execution feedback, structurally the configuration SpreadsheetBench specifies for its
multi-round setting. **Luna** is `openai/gpt-5.6-luna`, pinned to `openai/gpt-5.6-luna-20260709`;
**GLM** is `z-ai/glm-5.3-flash`, pinned to `z-ai/glm-5.3-flash-20260826`, both through OpenRouter.
Two further models passed the *n* = 100 validation gate and were never run: "two models from
different labs" describes what the budget reached, not a design choice.

**The turn ceiling is ours, and it changed mid-study.** The benchmark caps at five rounds; the first
three interjection runs used ten, and the cross-model run twenty, after the ten-turn ceiling was
found to censor the continue-signal arms hardest. Where a contrast pools across runs the ceilings
differ, and the tables say which. Twenty is defended empirically in §6.4.

One property of the loop matters for every per-turn measure: **each turn receives the original input
workbook, never the previous turn's output.** Turns are independent attempts in *workbook state* —
the message history does accumulate — which is what makes "did attempt *k+1* land closer?" well
posed (§6.1).

## 2.2 The manipulation

Each arm delivers a single interjection mid-task, appended to an execution observation. Every
interjection is **exactly 28 tokens** under `cl100k_base` and opens with the same `Checking in.`
stem; the opening instruction is held at one neutral wrapper in every arm of every run after the
first. Appendix A prints all of them, generated from the harness, with token counts recomputed
rather than asserted. Length matching fixes a confound we measured in our own instrument: the
study's first run varied seven *opening* wrappers whose length was U-shaped (35/35/30/30/31/32/34
tokens) — the same shape as accuracy — and length predicted accuracy better than register rank did
(*r* = +0.82 against −0.72).

Injection turn is **crossed**, not sampled, in every run but the first micro-experiment; that
sampling made a selection artefact look like a timing effect (Appendix C.2). Arm order is shuffled
per (model, task) from a fixed seed and position does not predict accuracy (*p* = 0.61). Temperature
is 0 where settable — Luna's advertised parameters omit it entirely — and no roster model
returned identical output across repeated identical calls, which is why trials exist.
Trajectories that end before the interjection is due received no dose and are excluded — a
pre-treatment exclusion that does not differ by arm, 54.0% to 59.5% firing across the probe's four
arms at turn 2, but differs sharply **across** injection turns, roughly 98% at turn 0 against 55% at
turn 2, so for timing contrasts only we fix the comparison population from the **control** arm.

## 2.3 Outcomes and estimator

**Turn count is the primary outcome**: it is the quantity that moves, it is model-agnostic, and it
is far better powered than accuracy at our *n*. Reasoning tokens per trajectory are secondary; they
were the pre-registered primary in the first run and were demoted on evidence. Accuracy is reported
and underpowered by design (§2.5). The per-turn regrade adds `final_match`, the fraction of the
graded range correct in the **last** turn, and **redundant steps**, turns after which the graded
range is unchanged, a measure adopted from [redundancybench]. One definition a reader comparing our
turn counts with another paper's needs: the run records store *acting* turns, those that emitted
code, while the per-turn regrade stores model calls, including the closing `FINAL:` message that
carries none — mean 3.57 against 4.69 on the micro-experiment, a 31% relative gap. **Turn count in
this paper means acting turns throughout.**

Every contrast is against a *neutral interjection*, not against silence: each arm is compared with a
control arm that also receives a 28-token message at the same turn, which isolates register from the
fact of being interrupted. How much the baseline itself moves was measured **once** — a neutral
interruption against no interruption, 3.47 versus 4.11 turns, ***p* = 0.15, on one model at one
ceiling** — so an arm's absolute cost against an *uninterrupted* agent is not something this design
bounds, though a shared offset cancels in every contrast reported here.

Every trajectory belongs to one of 50 tasks, and each (task, arm) cell holds six to nine
trajectories, which are not independent. Throughout: **point estimates are paired within task** (per
task, the mean over that task's trials in each arm, differenced, then averaged — the
paired-and-clustered form of Miller's clustered estimator [miller-2024]); **intervals come from a
cluster bootstrap over tasks**, 20,000 resamples; ***p*-values come from a task-clustered sign-flip
permutation test**, 20,000 draws, reported as (count + 1)/(draws + 1) so that no *p* is quoted as
exactly zero. **20,000 is the only replicate count in this paper.** Every interval and every
*p*-value, in every table and every figure, is read from one run of that procedure, so a contrast
quoted twice is quoted identically; the pooled contrasts of §2.5 and §6.3 resample tasks jointly
across runs rather than within one, at the same 20,000. A permutation *p* at this count cannot
resolve below 1/20,001, so anything smaller is reported as <0.0001 rather than as a more
precise-looking figure. Clustering is not a formality: Miller reports clustered-to-CLT
standard-error ratios of 1.10, 1.88 and 3.05 across three datasets, and an early unclustered version
of our own results had accuracy intervals roughly 35% too narrow. Following [sclar-2024] and
[mizrahi-2024] we report ranges wherever a quantity was measured more than once.

## 2.4 Multiplicity

The accuracy family is **every arm-versus-control accuracy contrast in every run that delivered a
mid-task interjection**: 22 contrasts across six runs and two models, defined exhaustively rather
than after the fact. Two are nominally significant against 1.1 expected under a global null — the
continue-signal contrast at *p* = 0.0040 and praise versus control on GLM at *p* = 0.0137 — and
neither survives Benjamini–Hochberg (rank-1 critical value 0.0023); the first reversed sign on
re-measurement.

**The primary outcome is corrected too**, over the *same* 22 comparisons with the outcome switched
to turns, because choosing a turn-count family by hand after seeing which contrasts are large is
gerrymandering. **Seventeen of the 22 survive at *q* = 0.05**; the Bonferroni-adjusted smallest *p*
is 0.0011. The five that do not are praise vs control on GLM (−0.35, *p* = 0.058), all three insult
contrasts (+0.57, −0.08, +0.07; *p* = 0.165, 0.624, 0.659) and `L5_rude` vs neutral (+0.09,
*p* = 0.654) — so **all three insult contrasts fail, as does the one rude register arm**, which is
the dissociation §4 argues for, holding under correction. §5's two designed within-run contrasts
form a second family of two, which corrects almost nothing: praise isolated, `Q4` − `Q5`, at −1.35
turns (*p* < 0.0001) and closing cue versus praise at −0.36 (*p* = 0.017) both survive at
*q* = 0.05. Correcting a primary outcome after the fact is weaker than pre-registering the family,
and we did not pre-register it.

## 2.5 Power, and the accuracy null as equivalence

A null is worth reporting only if the design could have seen the effect it is contrasted with. For
each contrast we invert the standard power relation at the realized cluster-bootstrap standard error
— the MDE at 80% power and α = 0.05 two-sided is (z₀.₉₇₅ + z₀.₈₀)·SE ≈ 2.80·SE, following
[miller-2024] — and state the null as an equivalence [lakens-2017].

**On turn count the design is adequately powered, unevenly.** Realized MDE runs from 0.42 to 1.39
turns against control means of 2.94 (GLM) and 4.07–4.95 (Luna). The demand effects sit at 1.1–2.2×
their own MDE, the praise effects at 0.7–1.4×, so the cross-model praise contrasts are below 80%
power at their observed size. **On accuracy it is not, and that is the limitation.** Across the 22
contrasts the realized MDE has a median of 5.52 accuracy points and a range of 3.74 to 7.77, against
a published tone-accuracy gap of about 4 [dobariya-kumar-2025]. So **a single contrast cannot
exclude the smallest published effect** — TOST equivalence at ±4 is reached in 6 of 22 — **but every
contrast can exclude the largest ones**: at ±7.5, the *median* format-induced spread reported by
[sclar-2024], 19 of 22 reach equivalence. The reason is structural: **26 of our 50 tasks are never
solved by the control arm and 4 are always solved**, so for more than half the sample the per-task
accuracy difference is pinned at zero whatever the manipulation does. Turn count varies on every
task.

The pre-specified smallest effect of interest is **±4 accuracy points**, the polite-versus-rude gap
of the paper this work is positioned against. Pooling each contrast's repeated measurements, with
the interval from a bootstrap that resamples tasks **jointly across runs**, since the runs share
their 50 tasks:

| Contrast | *k* | Ceilings | Estimate | 95% CI | MDE₈₀ | TOST at ±4 |
|---|---:|---|---:|---|---:|---:|
| Demand vs control | 3 | 10, 20, 20 | −0.31 pts | [−2.71, +2.09] | 3.43 | 0.0013 |
| Praise vs control | 4 | 10, 10, 20, 20 | −0.12 pts | [−1.80, +1.57] | 2.41 | <0.0001 |
| Insult vs control | 3 | 10, 20, 20 | −0.04 pts | [−2.15, +2.08] | 3.03 | 0.0001 |

So the claim is bounded and specific: **a mid-task interjection — demanding, praising, or insulting
— does not change task accuracy by as much as the four points the tone literature reports, while
demand raises turn count by 18–33%, praise lowers it by 11–24%, and insult does not move it at
all.** It is not "register does not affect accuracy"; it is that an effect of the published size is
excluded and an effect of a point or two is not.

Two caveats, both against us. The praise pooling is heterogeneous — Cochran's *Q* = 8.45 on 3 df,
*p* = 0.038 — and between models rather than within: Luna's three praise measurements alone give
*Q* = 0.36 and −1.27 points, 95% CI [−3.11, +0.57]. Under a random-effects pool the praise estimate
becomes +0.21 with a standard error of 1.68 and the ±4 equivalence weakens to *p* = 0.0119 but
holds. And **no accuracy effect in this study has replicated**: the larger nominal hit, +6.6 points
on the continue-signal contrast, came back at −1.8 on identical tasks and ceiling.
