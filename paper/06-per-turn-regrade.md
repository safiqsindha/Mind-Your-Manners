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

This section opens the trajectory up. It costs nothing: no model calls, no new data.

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
control arm, **94.4%** do. The residual 5.6% is consistent with the benchmark's own audited 4%
instruction-level false-negative rate, which our regrade inherits for the answer-file component
(§2.10). This check is the one that caught the defect in §6.8, and it is the reason to run it
before trusting any number here.

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

**Every arm that moves turn count moves redundant steps, and the arms that do not, do not.**
Against the turn effects of §4 and §5, redundant steps account for roughly two-thirds to
four-fifths of each: demand +0.75 against +1.17 turns, praise −0.61 against −1.08, the closing cue
−0.86 against −1.44. The rest is productive, which is §6.4.

The seven-level arms line up with §4.2's split rather than with register: the two arms carrying no
persistence demand (L5 rude, L1 sycophantic) are the two that do not add redundant steps.

## 6.4 A continue signal does buy progress — but only the explicit one

This is where the corrected instrument changed the paper's answer.

Pooling each contrast's final-match measurements by inverse variance:

| Contrast | k | Pooled Δ final match | 95% CI | p | Cochran's Q |
|---|---:|---:|---|---:|---:|
| **"Work remains" vs control** | 3 | **+0.028** | [+0.009, +0.048] | **0.0038** | 0.20/2 df (p = 0.91) |
| Demand only vs control | 3 | +0.009 | [−0.013, +0.032] | 0.42 | 6.42/2 df (p = 0.040) |
| Insult only vs control | 3 | +0.009 | [−0.013, +0.030] | 0.44 | 2.28/2 df (p = 0.32) |
| Praise vs control | 4 | −0.009 | [−0.028, +0.011] | 0.38 | 9.56/3 df (p = 0.023) |

**The explicit continue signal — "there is still more work remaining on this task here beyond what
you have done" — raises the graded fraction by 2.8 points, and it is the most consistent
replication in the study.** Its three measurements are +0.026, +0.034 and +0.025, across two turn
ceilings and three separate runs, with a heterogeneity p of 0.91. Nothing else in this paper
reproduces that tightly.

**The milder demand does not.** "Please continue working on the task here and make sure that your
final result is correct" pools to +0.009 and does not reach significance, and its three
measurements are heterogeneous (p = 0.040) — −0.012 on Luna at ceiling 10, +0.002 on Luna at
ceiling 20, **+0.060 on GLM** (p = 0.015 on its own). We do not read the GLM result as a finding:
it is one nominal hit, uncorrected, in a family where praise is equally heterogeneous in the
opposite direction (p = 0.023, spanning −0.035 to +0.041).

So the pattern is a **dose–response in the strength of the continue signal, not in register**. The
arm that says the task is unfinished buys progress; the arm that says keep going and be careful
does not, reliably. That is consistent with §4's demand gradient and sharpens it: what the agent
acts on is the explicitness of the claim that work remains.

Two bounds on the size of this. It is **2.8 points of partial credit**, and the benchmark's hard
restriction requires every test case to pass, so it does not move accuracy — which is why §2.8's
accuracy null and this result are compatible rather than contradictory. And most of the extra
turns are still redundant (§6.3): the continue signal buys about three extra redundant steps and
about three points of the graded range.

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
trajectories that *could* improve — only a quarter to a third of the sample — the first gradable
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

Among trajectories in the ceiling-20 run, the best answer was first reached at a **median turn of
2**. **98.3% had peaked by turn 10 and 100% by turn 14.**

So the trajectories that run long are not converging slowly. They reach their best answer early.
Raising the ceiling further buys mostly repetition, and five rounds — the benchmark's official cap
— would truncate the arms that persist longest. Twenty is past where the peak lands.

One statistic from the earlier draft does not survive as stated. "Zero of 43 improvements occurred
at turn 15 or later" was about improvements to a trajectory's running best; under the looser
definition of any turn beating the one before it, 10 of 95 occur at turn 15 or later. Both are
true of different statistics, and the ceiling conclusion rests on the peak distribution above,
which is unambiguous.

## 6.7 Praise's early stop is not premature

§5 shows praise and closing cues shortening trajectories substantially, and the natural worry is
that they cut off productive work.

On the only test we can run, they do not. The share of trajectories still improving at the point
they stopped is **3.1–7.1% across the Luna arms**, with no gap between praise and control. And the
turns praise removes are, in control, the late turns — which improve the answer only a few percent
of the time.

**GLM behaves differently and we report it rather than average it away:** 14.3% of its control
trajectories were still improving when they stopped, twice the highest Luna figure. A model that
stops earlier leaves more on the table, and on GLM the claim that praise removes only repetition
is correspondingly weaker.

This bears on terminology. [cuadron-2025] coin **premature disengagement** for termination "based
solely on internal simulation… without environmental validation." That names a *trigger*, and the
praise stop has a different trigger — a discourse cue. We use neither their term nor "premature",
and say instead what we measured: the stop is earlier, and on Luna what it removes is mostly
repetition.

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

This is the third failure in this subsystem that presented as data rather than as an error. The
other two: a LibreOffice timeout that killed a 450-trajectory arm because a documented
log-and-continue contract was a comment rather than a behaviour; and, during the corrected
regrade's rollout, comparing a freshly regraded control against not-yet-regraded arms, which
produced a −0.36 final-match "effect" at p < 0.0001 in three arms at once. That one was caught
only because all three numbers were nearly identical, which no real effect would be. Both now have
regression tests, and `regrade_summary.py` refuses any arm whose regrade predates the instrument.

**The honest scope of §6 is therefore narrower than its numbers suggest.** This is a new
instrument with a short and eventful track record. Its redundant-step measure is exact and needs
no recalculation; its progress measure depends on a recalculation path that was silently broken
until this rewrite, and readers should weight the two accordingly.

## 6.9 The measure we do not report

`best_match` — the maximum over a trajectory's turns — is biased toward arms with more turns: more
draws from the same distribution means a higher maximum for free, and this study's whole subject
is arms that take more turns. We report `final_match`, what the agent actually ended with, and
record `best_match` only here so the choice is visible.

## 6.10 What this establishes and what it does not

**Establishes.** The turn-count effects of §4 and §5 are, in the main, effects on redundant steps —
two-thirds to four-fifths of each, on Luna. An explicit statement that work remains raises the
graded fraction by 2.8 points, replicated across three runs and two ceilings with no detectable
heterogeneity, while leaving accuracy unmoved. The first gradable attempt is the best in 80–91% of
the trajectories that could improve. A 20-turn ceiling is not binding.

**Does not establish that a milder demand buys progress.** It pools to +0.009 and is
heterogeneous; the single GLM hit is not built on.

**Does not establish that praise costs nothing.** On Luna what it removes is mostly repetition. On
GLM, 14.3% of control trajectories were still improving at their stop, and the question is open.

**Does not establish why the first attempt is usually best**, nor that the progress gain would
appear on a scaffold that accumulates workbook state across turns.
