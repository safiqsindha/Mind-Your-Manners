# 2. Design, estimators, and what our nulls exclude

> **Draft status.** Every number in §2.7–§2.9 is reproduced by
> `results/analysis/accuracy_null_mde.py`, which reads the archived records in
> `results_archive/` and prints the table below. Citation keys are placeholders.

## 2.1 Substrate, sample, and why the ceiling is ours

All runs use SpreadsheetBench [ma-2024], a benchmark of real workbook-editing instructions
taken from Excel forums, with 912 instructions and 2,729 test cases. Our sample is a fixed set
of 50 instructions, a strict subset of an earlier 100-instruction validation sample, so every
task in the study has a measured neutral baseline and a verified no-op floor of zero — a task
on which doing nothing scores a pass would silently inflate every arm equally, and none of ours
does.

The agent is a ReAct loop with code execution and execution feedback, structurally the same
configuration SpreadsheetBench specifies for its multi-round setting. **The turn ceiling is
not.** The benchmark imposes a limit of five rounds; we use twenty. That is our choice and we
state it as one rather than let the paper imply continuity with an official protocol. The
choice is defended empirically in §6: among trajectories that ran to the 20-turn ceiling, the
best answer was first reached at a median turn of 2, 97% had peaked by turn 10, and no
improvement anywhere in the run occurred at turn 15 or later. Twenty is comfortably past the
point where more turns buy anything; five would have truncated the arms that persist longest.

One property of the loop matters for every per-turn measure in this paper: **each turn receives
the original instruction, never the previous turn's output.** Turns are therefore independent
attempts at the same problem rather than refinements of a running draft, which is what makes
"did attempt *k+1* land closer than attempt *k*" a well-posed question.

## 2.2 The manipulation

Each arm delivers a single interjection mid-task, appended to an execution observation. Every
interjection in every arm is **exactly 28 tokens** under a fixed reference tokenizer and opens
with the same `Checking in.` stem, so that *being interrupted* does not covary with what the
interruption says. The opening instruction is held at a single neutral wrapper in every arm of
every run after the first; only the interjection varies.

This matters because the first run of this study was confounded by wrapper length. Across its
seven opening wrappers, length was U-shaped (35/35/30/30/31/32/34 tokens) — the same shape as
accuracy — and predicted accuracy better than tone rank did (r = +0.82 against r = −0.72 on the
seven arm means). Length matching is not a nicety here; it is the fix for a confound we
measured in our own instrument.

Injection turn is **crossed**, not sampled. An earlier micro-experiment drew the injection turn
at random from {1, 2}; because a turn-2 injection can only fire in a trajectory that reaches
turn 2, the arms were then compared on different populations, and what looked like a timing
effect was selection. Crossing the turn and analysing each level separately removes that.

## 2.3 Outcomes, and which one is primary

| Measure | Role | Source |
|---|---|---|
| Turn count | **primary** | harness |
| Reasoning tokens | secondary | provider usage fields |
| Accuracy (hard restriction) | reported, underpowered by design | benchmark evaluator |
| `final_match` — fraction of the graded range correct in the **last** turn | progress | per-turn regrade |
| Redundant steps — turns after which the graded range is unchanged | waste | per-turn regrade |

Turn count is primary because it is the quantity that moves, it is model-agnostic, and it is
far better powered than accuracy at our *n* (§2.7). Reasoning tokens were the pre-registered
primary in the first run and were demoted on evidence, which we report as a change rather than
present as the original plan.

**We report `final_match`, not `best_match`, and the difference is not cosmetic.** Best match
takes the maximum over a trajectory's turns, so an arm that takes more turns gets more draws
from the same distribution and a higher maximum for free. In the one run where the two
disagree, best match gives +0.035 (p = 0.0046) for the continue-signal arm where final match
gives +0.019 (p = 0.16) — and within that arm best match rises monotonically with turn count
(0.273 → 0.293 → 0.330) while within control it does not. Best match is biased toward exactly
the arms this study makes longer. Final match — what the agent actually ended with — is the
fair comparison.

Following [yao-2024] we report **pass^k**, the probability that all *k* trials of a task
succeed, wherever consistency across trials is at issue, rather than inventing a term for it.
For redundant turns we adopt **redundant step** from [redundancybench], noting that our
criterion is the counterfactual one (the graded range is unchanged) rather than their stricter
*duplicated step* subtype, which additionally requires identical tool name, arguments and
output. We do not compare base rates against theirs: some of their redundant steps are
synthetically injected.

## 2.4 The estimator: paired within task, clustered by task

Every trajectory in this study belongs to one of 50 tasks, and three or four trials of the same
task are not independent observations. Treating them as independent is the single easiest way
to manufacture significance here, and an early version of our results did exactly that: its
accuracy confidence intervals were roughly 35% too narrow because the bootstrap resampled
trajectories rather than tasks.

Throughout, therefore:

- **Point estimates are paired within task.** For each task we average the outcome over that
  task's trials in each arm and take the difference; the reported effect is the mean of those
  50 per-task differences. This is the paired-and-clustered variant of Miller's clustered
  estimator [miller-2024], which is the right one here because our trajectories cluster within
  tasks *and* our comparison is paired across conditions on the same tasks.
- **Intervals come from a cluster bootstrap over tasks** — tasks, never trajectories, are the
  resampling unit.
- **p-values come from a task-clustered permutation test**: the sign of a whole task's
  difference is flipped, all of its trials together.

The correction is not negligible in general — Miller reports a clustered-to-CLT standard-error
ratio of 3.05 on DROP, though 1.10 on RACE-H and 1.88 on MGSM, so the "up to 3×" figure is
dataset-specific and we cite it as such.

One consequence deserves stating plainly because it bit us. The unpaired difference of arm
means and the paired task-clustered difference are **two estimators of the same contrast, and
they do not give the same number.** The praise contrast is −0.62 and −1.14 turns under the
first and −0.59 and −1.08 under the second. Both are correct; only one is comparable to the
rest of this paper, and a paper whose §8 is about point estimates failing to replicate cannot
afford to quote two different pairs for one contrast. Every number in this paper is the paired,
task-clustered one.

## 2.5 The comparison population is defined by the control arm

An interjection scheduled for turn *t* fires only if the trajectory reaches turn *t*. Arms that
run longer therefore fire more often, and conditioning on firing conditions on an outcome. In
the seven-level run the turn-0 cell fired in ~98% of trajectories and the turn-2 cell in ~55%.

We fix the comparison population from the **control** arm: a task enters a turn-*t* contrast
only if the control arm's trajectories for that task reach turn *t*. The population is then the
same for every arm at that turn and is defined by a quantity the manipulation cannot have moved.
Where this shrinks the sample we report the reduced task count with the estimate.

## 2.6 Multiplicity

Two families are corrected, and we name them rather than choosing after seeing the results.

The first run tested twelve outcomes for a linear trend across seven arms. Under a global null
the chance that at least one lands below p = 0.023 is 0.24, and the accuracy trend that did so
does not survive Benjamini–Hochberg across that family (critical value 0.0042). We report it as
a lead, not a result.

The accuracy family is the fourteen arm-versus-control contrasts in §2.7. One of them,
praise versus control on GLM, is nominally significant at p = 0.014; its BH critical value at
rank 1 is 0.0036 and its Bonferroni-adjusted p is 0.195. It does not survive, it is the only
one of fourteen that comes close, and one nominal hit in fourteen is slightly fewer than a
global null predicts. We report it because suppressing it would be the same error this paper
accuses others of, and we do not build on it.

## 2.7 What the design can detect

A null is only worth reporting if the design could have seen the effect it is being contrasted
with. For each contrast we invert the standard power relation at the realized cluster-bootstrap
standard error — the minimum detectable effect at 80% power and α = 0.05 two-sided is
(z₀.₉₇₅ + z₀.₈₀)·SE ≈ 2.80·SE, following [miller-2024]'s sample-size inversion.

**On turn count the design is comfortable.** Realized MDE ranges from 0.42 to 1.39 turns across
the demand/praise/insult contrasts on both models, against control means of 2.94 turns (GLM)
to 4.95 (Luna). The effects we report are above it: the demand arm's +1.17 turns in the probe
run sits at 2.2× its own MDE of 0.54.

**On accuracy it is not, and this is the honest limitation.** Across all fourteen contrasts the
realized MDE has a median of 5.58 accuracy points and a range of 3.87 to 7.82. The largest
accuracy movement we observed anywhere is 6.16 points, and the published tone-accuracy gap we
are contrasting against is about 4 points [dobariya-kumar-2025]. A single one of our contrasts
therefore **cannot** exclude a published-size accuracy effect: two-one-sided-tests equivalence
at ±4 points is reached in only 4 of 14. At ±7.5 points — the *median* format-induced spread
reported by [sclar-2024], which is the right comparator, not their 76-point single-task
maximum — 12 of 14 reach equivalence.

## 2.8 Stating the accuracy null as equivalence, not as absence

Accuracy has not moved in any of seven runs. "We found no significant difference" is not a
finding, so we state the null the way a null should be stated [lakens-2017]. (We do not cite
[miller-2024] for this: his paper contains no equivalence framework, and the MDE machinery we
borrow from him is a different thing.)

Pooling the repeated measurements of each contrast by inverse variance:

| Contrast | k | Estimate | 95% CI | MDE₈₀ | Equivalent within |
|---|---:|---:|---|---:|---|
| Demand vs control | 3 | −0.30 pts | [−2.56, +1.95] | 3.22 | ±3 pts (p = 0.0095) |
| Praise vs control | 4 | −0.11 pts | [−1.96, +1.75] | 2.65 | ±2 pts (p = 0.023) |
| Insult vs control | 3 | −0.04 pts | [−2.22, +2.14] | 3.12 | ±3 pts (p = 0.0039) |

So the claim the paper makes is bounded and specific: **a mid-task interjection — demanding,
praising, or insulting — does not change task accuracy by as much as three points, while the
same interjections move turn count by 20–40%.** It is not "tone does not affect accuracy"; it
is that an effect of the size the tone literature reports is excluded, and an effect of a point
or two is not.

Two caveats, both against us. The pooled standard errors are mildly optimistic because the runs
share their 50 tasks, so task-level effects are common across measurements rather than
independent. And the praise pooling is heterogeneous — Cochran's Q = 8.54 on 3 df, p = 0.036 —
driven entirely by the GLM contrast of §2.6. The demand and insult poolings are homogeneous
(p = 0.20 and p = 0.25).

## 2.9 Ranges, not point estimates

Seven quantities in this study moved materially when measured again on the same tasks, model
and ceiling. The praise contrast gave −0.59 turns in one run and −1.08 in another; the
continue-signal effect on final match gave +0.014 (p = 0.50), then +0.061 (p = 0.0028), then
+0.019 (p = 0.16); accuracy on that contrast gave +7.0 points and then −1.8. Direction and
significance replicated in every case where the effect was large; the point estimates did not.

We follow [sclar-2024] and [mizrahi-2024] in reporting ranges rather than point estimates
wherever a quantity has been measured more than once, and we treat a point estimate quoted once
as provisional by default rather than by exception. Where only one measurement exists we say so.

## 2.10 The noise floor

The benchmark's own evaluator audit bounds what any of this can resolve: on 50 sampled
instructions, [ma-2024] report an instruction-level false-negative rate of 4% and a test-case-
level false-omission rate of 3.8%, with a false-discovery rate of 0% — the failures are
one-directional, usually from generated code writing content beyond the target cells. Our
per-turn regrade inherits that floor.

Because our contrasts are paired on the same tasks, a one-directional evaluator bias is largely
common to both arms and mostly cancels; what it does not cancel is the variance it adds, which
attenuates any real differential effect toward zero. So the floor is a reason our accuracy
estimates are noisy, not a reason they are biased — and the pooled intervals of §2.8 should be
read as what they are: bounds that exclude a published-size effect and admit a small one.
