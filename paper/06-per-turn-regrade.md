# 6. What the extra turns contain

> **Draft status.** Numbers verified against `RESULTS.md` and `results/analysis/*_progress.json`.
> The instrument is `harness/study2/progress.py`; the contrasts follow §2.4. Citation keys are
> placeholders.

## 6.1 The question the binary grade cannot answer

Every live finding in this study is about persistence. A demand interjection adds turns, praise
removes them, insult does nothing. But the benchmark grades the **final state** of the workbook,
pass or fail, so the extra turns are uninterpretable from the grade alone. An agent spending
them converging on the answer and an agent spending them rewriting the same wrong cells produce
identical records. The two readings support opposite conclusions about whether a continue signal
is useful or merely expensive, and §4's headline — that the effect is real — does not decide
between them.

This section opens the trajectory up. It costs nothing: no model calls, no new data.

## 6.2 The instrument

`harness/study2/progress.py` reconstructs the workbook after **every** turn, from the archived
call log. Each turn's code is in the log's response text; re-executing it against the task's
input workbook reproduces that turn's output exactly, because the harness kept the code and the
inputs.

What makes this well posed is a property of the agent loop rather than of the regrader: **each
turn receives the original input workbook, never the previous turn's output.** Turns are
independent attempts at the whole task, not edits to a running draft. There is no accumulated
state to disentangle, and "progress" has an unambiguous meaning — is attempt *k+1* closer to the
answer than attempt *k*?

Two measures, deliberately different in cost and in what they can say:

- **`changed`** — did this turn's output differ from the previous turn's over the graded range?
  A turn that changes nothing is a **redundant step**: the agent spent a model call and produced
  the same answer again. This needs no recalculation and is exact.
- **`match_fraction`** — what share of the graded range matches the answer? This is the progress
  signal. It requires recalculating the answer file, whose shipped ground truth contains uncached
  formulas, and the agent's output too when the agent writes formulas rather than values.

**`match_fraction` is not the benchmark's pass/fail and must not be reported as accuracy.** A
trajectory can climb from 0.2 to 0.9 and still fail: the benchmark's hard restriction requires
every test case to pass. It is a finer instrument for a different question.

7,150 trajectories were regraded across four runs.

**Validation before use.** Trajectories the benchmark passed score a final match of 1.0; long
failing ones score 0.0. That check is what caught a range-parser bug, and the bug is worth
recording because of how it presented. `"P2:P7"` was parsed as sheet `P2:` plus cell `P7`,
grading a one-cell range on a sheet that does not exist. Every affected lookup returned `None`,
which reads as *unmeasurable*, not as *broken* — the failure mode was silence. It was caught only
by validating against a real task before scaling up.

**The floor.** §2.10 bounds what this can resolve: the benchmark's own audit reports a 4%
instruction-level false-negative rate. The regrade inherits it.

## 6.3 What a continue signal buys

Contrasts against the neutral control, at the 10-turn ceiling, paired and clustered by task:

| Arm | Extra redundant steps | p | Change in final match | p |
|---|---:|---:|---:|---:|
| Demand only | **+0.96** | <0.0001 | +0.006 | 0.77 |
| "Work remains" | **+1.23** | <0.0001 | +0.014 | 0.50 |
| Praise the assistant | **−0.76** | <0.0001 | −0.027 | 0.079 |
| Closing cue | **−1.01** | <0.0001 | −0.004 | 0.72 |
| Insult only | +0.09 | 0.49 | 0.000 | 0.98 |

Read the two halves together. **Every arm that moves turn count moves redundant steps by
essentially the same amount, and no arm moves the progress measure.** The turn-count effect of
§4 is, almost entirely, an effect on the number of times the agent re-produces an answer it
already has.

This is the sharper version of §4.5's claim. There, "the extra turns are mostly repetition" was
an inference from the flat accuracy. Here it is measured directly, on a continuous scale, per
turn.

## 6.4 The first attempt is usually the answer

| | Ceiling 10 (Stage 0) | Ceiling 20, Luna | Ceiling 20, GLM |
|---|---:|---:|---:|
| First code turn is already the best the agent produces | **90%** | 87% | 85% |

Only 10% of multi-turn trajectories improve after their first code turn at the 10-turn ceiling.
The probability that a given turn changes anything decays from ~10% at turn 3 to 2–4% by turn 8.

**A reviewer will set this beside Huang et al.** [huang-2024], whose "No Change" rates are 90.5%
and 96.0% on GPT-4 and GPT-4-Turbo. The numbers sit close together and the statistics are not
the same one. Theirs is *the answer is unchanged after two rounds of intrinsic self-correction on
reasoning QA*. Ours is *the first attempt was the best of all attempts made, in an
execution-grounded agent loop running to a 10- or 20-turn ceiling*. We name the run and ceiling
for each of our figures for that reason.

The relationship to their argument is worth stating precisely, because it is stronger than it
first appears. Huang et al. argue that LLMs cannot reliably self-correct **without external
feedback**, and they point to execution feedback as the expected fix, citing Self-Debug's
description of the code executor as "the perfect verifier to judge the correctness of predicted
programs." **They never test it.** A naive reading of their paper predicts our agent should
improve across turns, because ours does have a code executor and does see its output. It does
not improve. This section tests the escape hatch they proposed and did not run.

We are careful about one adjacent literature. Where scaling-law work reports gains from more
attempts, the selection is typically oracle-assisted — best-of-*n* picks the winner knowing the
answer, and even "sequential" critics in that setting are given the ground truth and asked to
write feedback from it. Our agent's execution feedback is real but not oracle-informed. So the
flat progress here is **consistent with** that literature rather than a contradiction of it.

For the redundancy vocabulary we follow [redundancybench] and call these **redundant steps**,
noting in §2.3 that our criterion sits between their counterfactual definition and their stricter
*duplicated step* subtype. We do not compare base rates: some of their redundant steps are
synthetically injected.

## 6.5 The 20-turn ceiling is not binding

Among trajectories that ran all the way to the 20-turn ceiling, the best match was first reached
at a **median turn of 2**. 97% had peaked by turn 10 and 100% by turn 14. Across every trajectory
in that run, **zero of 43 improvements occurred at turn 15 or later.**

So the trajectories pinned at the ceiling are not converging slowly. They reached their best
answer early and then spent another fifteen turns not changing it. Raising the ceiling further
buys more repetition, not more progress.

An earlier reading of this same data claimed the productive window extended to turn ~14, from a
per-turn improvement *rate* of 1–5% at those indices. The rate was real; the conclusion was not.
It is a small rate on a small denominator — in absolute terms those turns contain almost no
improvements. We record the correction because the two statistics are easy to confuse and the
wrong one is the more flattering.

This also settles the ceiling question §2.1 leaves open. Five rounds, the benchmark's official
cap, would truncate the arms that persist longest. Twenty is comfortably past where anything
useful stops happening.

## 6.6 Praise's early stop is not premature

§5 shows praise and closing cues shortening trajectories substantially. The natural worry is that
they are cutting off productive work, and the per-turn regrade is what can check it.

They are not. The share of trajectories still improving at the point they stopped is **2–6% in
every arm, with no gap between praise and control.** What praise removes is mostly repetition.

This matters for terminology as well as for the finding. [cuadron-2025] coin **premature
disengagement** for agents that terminate on internal simulation rather than on task state, and
it would be an easy term to borrow. We do not borrow it, because our regrade shows the praise
stop is *earlier* but not *premature* — the work it cuts off was not going anywhere. That is a
sharper claim than the borrowed term would license, and a less alarming one.

The practical reading of §5 therefore needs care. Wrapping up politely with an agent that is
still working does curtail its work. On these tasks, with this model, what it curtails is mostly
repetition — which is not the same as saying it is harmless, only that our data do not show harm.

## 6.7 One contrast that did not settle cleanly

The continue-signal arm's effect on final match was measured three times:

| Measurement | Extra turns | Final match | p |
|---|---:|---:|---:|
| Ceiling 10 | +1.85 | +0.014 | 0.50 |
| Ceiling 20 | +6.20 | **+0.061** | **0.0028** |
| Ceiling 20, third run | +5.77 | +0.019 | 0.16 |

The middle row is a clear positive. It is also the odd one out, and the obvious explanation —
that the 10-turn ceiling truncated real progress — is testable and false. Truncating the
ceiling-20 run's own analysis to ten turns leaves the effect intact: +0.049 (p = 0.0065) at 10
turns, +0.056 at 15, +0.061 at 20. The effect is fully present within the first ten turns of that
run. What separates +0.014 from +0.049 is not the turn budget; it is that they are two different
runs.

The turn effect replicates (+6.20 then +5.77, both p < 0.0001). **The progress effect does not.**
Final match is null in two of three measurements, and §8 treats this as the study's most
consequential instance of run-to-run instability.

**What the paper can say, and no more:** a continue signal buys more turns on two models and buys
no detectable improvement in the answer on either, with one unreplicated measurement pointing the
other way, reported rather than dropped.

## 6.8 The measure we do not report, and why

`best_match` — the maximum over a trajectory's turns — gives +0.035 (p = 0.0046) on the third
measurement where `final_match` gives +0.019 (p = 0.16). It is tempting and it is wrong here.
More turns means more draws from the same distribution and a higher maximum for free, so best
match is biased toward exactly the arms this study lengthens. Within the continue-signal arm it
rises monotonically with turn count (0.273 → 0.293 → 0.330); within control it does not.

We could not cleanly separate that inflation from task difficulty, so we report `final_match` —
what the agent actually ended with — throughout, and record `best_match` only here, so that the
choice is visible rather than silent.

## 6.9 What this establishes and what it does not

**Establishes.** The turn-count effects of §4 and §5 are effects on redundant steps. The first
attempt is the best one in 85–90% of trajectories, in an execution-grounded loop that Huang et
al.'s argument predicts should improve. Praise's early stop removes repetition, not productive
work. A 20-turn ceiling is not binding.

**Does not establish that persistence never helps.** It establishes that on these 50 tasks, these
two models and this scaffold, it did not — with one measurement out of three pointing the other
way, unreplicated.

**Does not establish anything about why the first attempt is best.** Whether the agent's later
attempts are constrained by the instruction, by its own prior, or by the task structure is not
addressed here.
