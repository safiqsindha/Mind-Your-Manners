# 6. What the extra turns contain

> **Draft status.** Every figure is printed by `results/analysis/regrade_summary.py` from the
> archived regrade in `results_archive/progress_regrade_corrected/`. **This section was rewritten
> after the instrument it describes was found to be defective; §6.8 records what changed and what
> the earlier version claimed.** Citation keys are placeholders.

## 6.1 The question the binary grade cannot answer

Every live finding in this study is about persistence. A demand interjection adds turns, praise
removes them, insult does nothing. But the benchmark grades the **final state** of the workbook,
pass or fail, so the extra turns are uninterpretable from the grade alone. An agent spending them
converging on the answer and an agent spending them rewriting the same wrong cells produce
identical records. Those readings support opposite conclusions about whether a continue signal is
useful or merely expensive, and §4's finding that the effect is real does not decide between them.

This section opens the trajectory up. It requires no model calls, no API spend and no new data — about four machine-hours of replay.

## 6.2 The instrument

`harness/study2/progress.py` reconstructs the workbook after **every** turn from the archived call
log. Each turn's code is in the log's response text; re-executing it against the task's input
workbook reproduces that turn's output, because the harness kept both the code and the inputs.

What makes this well posed is a property of the agent loop rather than of the regrader: **each
turn receives the original input workbook, never the previous turn's output.** Turns are
independent attempts at the whole task in *workbook state* — the message history does accumulate,
so attempt *k+1* is conditioned on the text of attempts 1…*k*, but there is no inherited
spreadsheet to disentangle. "Progress" therefore has an unambiguous meaning: is attempt *k+1*
closer to the answer than attempt *k*?

Two measures, deliberately different in cost and in what they can say:

- **`changed`** — did this turn's output differ from the previous turn's over the graded range? A
  turn that changes nothing is a **redundant step**: the agent spent a model call and produced the
  same answer again. This needs no recalculation and is exact.
- **`final_match`** — what share of the graded range matches the answer, in the last turn that
  produced a readable one? This is the progress signal.

**`final_match` is not the benchmark's pass/fail and must not be reported as accuracy.** A
trajectory can climb from 0.2 to 0.9 and still fail: the hard restriction requires every test case
to pass. It is a finer instrument for a different question, and §6.6 turns on exactly that gap.

**Both the answer file and the agent's output must be recalculated**, and getting this wrong is
what §6.8 is about. openpyxl writes formulas with no cached value, so a turn answering with
`=SUMIFS(...)` reads back as empty unless the workbook is passed through LibreOffice first — which
is what the live grader has always done.

**Validation.** Trajectories the benchmark passed should score a final match of 1.0. On the probe
control arm, **119 of 126 (94.4%)** do. The residual seven are **all on one task**, 54513, whose
graded range is a single cell, and all score exactly 0.0 — a systematic miss by the regrade on
that task, not stochastic noise, and it is undiagnosed. It does not bias paired contrasts, since
that task contributes a zero difference to every arm, but it is a known blind spot. (It is not
the benchmark's own false-negative rate: that error runs the other way, and the benchmark's
audited false-discovery rate is 0%.)

The converse gap matters more for reading §6.4: **47 of 274 benchmark-*failed* probe-control
trajectories score a final match of 1.0.** `final_match` is computed against the first test case's
answer file only, while a benchmark pass requires all three test cases. The two measures are not
interchangeable and a perfect final match is not a pass.

This check is the one that caught the defect in §6.8, and it is the reason to run it before
trusting any number here.

28 arms were regraded, across six runs and two models.

## 6.3 What an interjection does to redundant steps

Contrasts against each run's own neutral control, paired and clustered by task (§2.4):

| Arm | Run | Δ redundant steps | p |
|---|---|---:|---:|
| Demand only | probe, ceiling 10 | **+0.75** | <0.0001 |
| Demand only | stage 1, ceiling 20 | **+1.03** | 0.0063 |
| Demand only | stage 1 GLM, ceiling 20 | +0.19 | 0.086 |
| "Work remains" | praise run, ceiling 10 | **+1.11** | <0.0001 |
| "Work remains" | stage 1, ceiling 20 | **+3.16** | <0.0001 |
| Praise the assistant | praise run, ceiling 10 | **−0.61** | <0.0001 |
| Praise the work | praise run, ceiling 10 | **−0.48** | 0.0012 |
| Closing cue | praise run, ceiling 10 | **−0.86** | <0.0001 |
| Insult only | probe, ceiling 10 | +0.03 | 0.85 |
| L7 threatening | seven-level, ceiling 10 | **+0.67** | 0.0001 |
| L3 polite | seven-level, ceiling 10 | **+0.90** | <0.0001 |
| L5 rude | seven-level, ceiling 10 | +0.07 | 0.53 |

**On Luna's single-signal arms, every arm that moves turn count moves redundant steps, and the
arms that do not, do not.** Against the turn effects of §4 and §5, redundant steps account for
**roughly 55–65%** of each: demand +0.75 against +1.17 turns (64%), praise −0.61 against −1.08
(56%), the closing cue −0.86 against −1.44 (60%), and the same band at ceiling 20 (55–59%). The
rest is §6.4.

Two exceptions bound that sentence. GLM's demand arm moves turns (+17.7%, p = 0.004) but its
redundant steps only +0.19 (p = 0.086) — a model that barely repeats itself has little repetition
to add. And Q4, praise plus "work remains", lengthens trajectories while its redundant-step effect
is +0.19 (p = 0.18).

The seven-level arms line up with §4.2's split rather than with register. The two arms carrying no
persistence demand behave like the praise family rather than like the demand family: L5 rude adds
nothing (+0.07, p = 0.53) and **L1 sycophantic significantly removes redundant steps** (−0.29,
p = 0.0025), which is the praise pattern and strengthens the split.

## 6.4 A continue signal does buy progress — but only the explicit one

This is where the corrected instrument changed the paper's answer.

Pooling each contrast's final-match measurements by inverse variance:

Intervals come from a bootstrap that resamples **tasks jointly across runs**, as §2.8 does for
accuracy, because the runs share their 50 tasks. Treating the runs as independent would give
p = 0.0038 on the first row; it is reported here at the weaker and more defensible figure.

| Contrast | k | Pooled Δ final match | 95% CI | p | Cochran's Q |
|---|---:|---:|---|---:|---:|
| **"Work remains" vs control** | 3 | **+0.028** | [+0.005, +0.052] | **0.022** | 0.20/2 df (p = 0.91) |
| Demand only vs control | 3 | +0.009 | [−0.020, +0.039] | 0.52 | 6.42/2 df (p = 0.040) |
| Insult only vs control | 3 | +0.009 | [−0.018, +0.030] | 0.62 | 2.26/2 df (p = 0.32) |
| Praise vs control | 4 | −0.008 | [−0.027, +0.013] | 0.52 | 9.63/3 df (p = 0.022) |

**The explicit continue signal — "there is still more work remaining on this task here beyond what
you have done" — raises the graded fraction by 2.8 points.** Its three measurements are +0.026,
+0.034 and +0.025, across two turn ceilings and three separate runs. The *point estimates* agree
more closely than anything else in this paper; we put it no more strongly than that, because only
one of the three reaches significance on its own (p = 0.32, 0.043, 0.089) and Cochran's Q on 2 df
has little power to detect heterogeneity anyway (§2.8). A fourth measurement of the same clause —
Q4, which appends "work remains" to praise — gives +0.035 (p = 0.10) and is not in the pool.

**The milder demand does not.** "Please continue working on the task here and make sure that your
final result is correct" pools to +0.009 and does not reach significance, and its three
measurements are heterogeneous (p = 0.040) — −0.012 on Luna at ceiling 10, +0.002 on Luna at
ceiling 20, **+0.060 on GLM** (p = 0.015 on its own). We do not read the GLM result as a finding:
it is one nominal hit, uncorrected, in a family where praise is equally heterogeneous in the
opposite direction (p = 0.023, spanning −0.035 to +0.041).

The pattern is **consistent with** the explicitness of the claim that work remains being what the
agent acts on, rather than register. We put it no higher, because the direct test is weak: on the
one run carrying both texts against the same control, the paired contrast between them is +0.023,
95% CI [−0.012, +0.060], p = 0.23. Two texts is two points, and they differ in more than strength
— one asserts a fact about task state, the other asks for continuation and care. This is a reading
of two arms, not a demonstrated gradient.

Two bounds on the size of this, and the second corrects a tempting story. It is 2.8 points of the
graded range, bought alongside 1.1 extra redundant steps at ceiling 10 and 3.2–3.6 at ceiling 20.

**It is not merely partial credit.** The share of trajectories ending *fully* correct on the graded
range rises by +2.8, +6.0 and +2.6 points across the three measurements. The accuracy series on
the same contrast (+2.4, +6.6, −1.8) is of that same order and simply cannot resolve it: §2.7 puts
the minimum detectable accuracy effect at 3.7–7.8 points. So §2.8's accuracy null and this result
are compatible **because accuracy is underpowered here, not because a gain of this size could not
cross the pass threshold.**

## 6.5 The first attempt is usually the answer

| Run | Trajectories | With ≥2 gradable outputs | First gradable output is already the best |
|---|---:|---:|---:|
| probe control, ceiling 10 | 400 | 112 | 80% |
| praise-run control, ceiling 10 | 300 | 97 | 89% |
| seven-level control, ceiling 10 | 450 | 106 | 91% |
| stage-1 Luna control, ceiling 20 | 300 | 58 | 84% |
| stage-1 GLM control, ceiling 20 | 300 | 49 | 84% |

The denominator matters and the earlier draft got it wrong. A trajectory that never produced two
readable answers cannot exhibit improvement; counting it as a success inflates the figure. Among
trajectories that *could* improve — **a sixth to a third of each sample** — the first gradable
output is already the best in **80–91%**, depending on the run.

**A reviewer will set this beside Huang et al.** [huang-2024], whose "No Change" rates are 90.5%
on GPT-4 (both GSM8K and CommonSenseQA) and 96.0% / 88.0% on GPT-4-Turbo. The numbers sit close
together and the statistics are not the same one. Theirs is *the answer is unchanged after two
rounds of intrinsic self-correction on reasoning QA*. Ours is *the first gradable attempt was the
best of all attempts made, in an execution-grounded agent loop*.

The relationship to their argument needs care, because §6.4 changes it. Huang et al. argue that
LLMs cannot reliably self-correct **without external feedback**, and point to execution feedback as
the expected fix, citing Self-Debug — in their words, the code executor "serves as the perfect
verifier" *when the task supplies unit tests* [chen-2023]. They never test it. Our agent has the
executor but not the tests: execution feedback tells it whether its code ran, not whether the
answer is right. So we test the **weaker** form of the escape hatch, and the answer is mixed
rather than negative — improvement is rare per turn, and a sufficiently explicit instruction to
continue does produce a small, replicated gain.

We are careful about one adjacent literature. Where scaling work reports gains from more attempts,
the selection is oracle-assisted — best-of-*n* picks the winner knowing the answer, and even
"sequential" critics there are given the ground truth and asked to write feedback from it
[balachandran-2025]. Our agent's execution feedback is real but not oracle-informed, so a small
gain here is consistent with that literature rather than a contradiction of it.

## 6.6 The 20-turn ceiling is not binding

In the **dedicated ceiling-20 re-run**, the best answer was first reached at a **median turn of
2**, with **98.3% peaked by turn 10 and 100% by turn 14**. The other two ceiling-20 runs agree:
stage-1 Luna is 99.3% by turn 10 and 99.8% by turn 14 (one trajectory peaks at 15), and GLM is
100% by turn 10.

So the trajectories that run long are not converging slowly. They reach their best answer early.
Raising the ceiling further buys mostly repetition, and five rounds — the benchmark's official cap
— would truncate the arms that persist longest. Twenty is past where the peak lands.

One statistic from the earlier draft does not survive as stated. "Zero of 43 improvements occurred
at turn 15 or later" was about improvements to a trajectory's running best; under the looser
definition of any turn beating the one before it, 10 of 95 occur at turn 15 or later in this run,
and 17 of 189 in stage-1 Luna. Both are true of different statistics, and the ceiling conclusion
rests on the peak distribution above, which is unambiguous.

## 6.7 Whether praise's early stop is premature is not settled

§5 shows praise and closing cues shortening trajectories substantially, and the natural worry is
that they cut off productive work.

On the only test we can run, the answer is not clean, and the earlier draft of this section got it
backwards. Among trajectories that could improve, the share still improving when they stopped is
**3.1–7.1% in the Luna controls and 7.5–12.3% in the praise and closing-cue arms** — higher in
every one of seven comparisons, by a factor of two to three. No single paired contrast reaches
significance (p = 0.095 to 0.65, on 19–34 tasks), so this is an underpowered test with a
consistent sign, which is not a null.

**We therefore cannot say praise removes only repetition.** What we can say is that the absolute
count is small: 6 of 53 trajectories under praise were still climbing when they stopped, against
3 of 97 in control.

GLM is worse on both sides: 14.3% of its controls and 29.2% of its praise arm. A model that stops
earlier leaves more on the table.

This bears on terminology. [cuadron-2025] coin **premature disengagement** for agents that
"terminate tasks based solely on their internal simulation of the problem space, either through
direct abandonment or by delegating hypothetical action sequences", warning that overreliance on
internal reasoning "can lead to decisions without environmental validation". That names a
*trigger*, and the praise stop has a different one — a discourse cue. We use neither their term
nor "premature", and say instead what we measured: the stop is earlier, and whether it is costly
is unresolved.

The practical reading of §5 therefore needs care. Wrapping up politely with an agent that is still
working does curtail its work. On these tasks, on Luna, what it curtails is mostly repetition;
on GLM, less clearly so.

## 6.8 The instrument was wrong, and this is what changed

The first version of this section reported a clean null: no arm moved the progress measure. That
was an artefact.

`progress.py` read each turn's output with openpyxl's `data_only=True` and **never recalculated
it**, while the live grader had always passed output workbooks through LibreOffice first. A
formula written by openpyxl carries no cached value, so every turn that answered with a formula
read as empty and scored 0.0 — indistinguishable from a turn that wrote nothing. Roughly 56–62% of
Luna's final gradable turns write formulas.

The section's own validation paragraph would have caught it. It claimed that benchmark-passed
trajectories score 1.0; on the archived data **89 of 126 passed control trajectories scored exactly
0.0**. The check was described and not run.

What the correction did:

| | Broken | Corrected |
|---|---|---|
| Passed trajectories scoring 1.0 | 29.4% | **94.4%** |
| Redundant-step effects | +0.96 / −0.76 / −1.01 | +0.75 / −0.61 / −0.86 — all signs and significance held |
| "Work remains" on final match | +0.014 / **+0.061** / +0.019 | **+0.026 / +0.034 / +0.025** |
| Conclusion | extra turns buy nothing | extra turns buy 2.8 points, replicated |

The middle row is the paper's. The redundant-step finding survived the correction with every sign
and significance level intact, about 20% smaller. The bottom row is the reversal: what §8
originally presented as this study's most consequential instance of run-to-run instability — one
significant measurement between two nulls — was the instrument. Corrected, the three agree
(Q = 0.20 on 2 df). §8.4 now reports the defect as the explanation rather than the instability.

This is the latest of four failures in this subsystem that presented as data rather than as an
error. The others: a range parser that read `"P2:P7"` as a sheet named `P2:` and returned `None`
for every affected lookup (§8.7); a scratch-directory collision that let concurrent processes
overwrite one another's output workbooks; and a LibreOffice timeout that killed a 450-trajectory
arm because a documented log-and-continue contract was a comment rather than a behaviour. A fifth
near miss came during this rewrite's own rollout: comparing a freshly regraded control against
not-yet-regraded arms produced a −0.36 final-match "effect" at p < 0.0001 in three arms at once.

**The honest scope of §6 is therefore narrower than its numbers suggest.** Its redundant-step
measure is exact and needs no recalculation. Its progress measure depends on a recalculation path
that was silently broken until this rewrite — and which **still has no regression test of its
own**: the tests added in response cover the timeout and the staleness guard, not the formula
blindness that caused the reversal. The validation check of §6.2 is what stands in for one, and it
leaves seven trajectories on one task unexplained. Readers should weight the two measures
accordingly.

## 6.9 The measure we do not report

`best_match` — the maximum over a trajectory's turns — is biased toward arms with more turns: more
draws from the same distribution means a higher maximum for free, and this study's whole subject
is arms that take more turns. We report `final_match`, what the agent actually ended with, and
record `best_match` only here so the choice is visible.

## 6.10 What this establishes and what it does not

**Establishes.** The turn-count effects of §4 and §5 are, in the main, effects on redundant steps —
roughly 55–65% of each, on Luna's single-signal arms. An explicit statement that work remains
raises the graded fraction by 2.8 points, 95% CI [+0.005, +0.052], with three measurements whose
point estimates agree closely; accuracy does not move, but is too underpowered to rule an effect
of that size in or out. The first gradable attempt is the best in 80–91% of the trajectories that
could improve. A 20-turn ceiling is not binding in the run we examined.

**Does not establish that a milder demand buys progress.** It pools to +0.009 and is
heterogeneous; the single GLM hit is not built on.

**Does not establish that praise costs nothing.** Trajectories in the praise and closing-cue arms
are two to three times more likely than control's to have been still improving when they stopped,
in all seven comparisons, none individually significant. The test is underpowered and the sign is
against us; the absolute counts are small. Open.

**Does not establish why the first attempt is usually best**, nor that the progress gain would
appear on a scaffold that accumulates workbook state across turns.
