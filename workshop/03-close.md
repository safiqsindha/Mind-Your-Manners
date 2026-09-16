# 5. What the extra turns buy

We regraded every turn of 9,850 of the 11,850 trajectories — the six runs carrying a mid-task
interjection; the opening-tone run and one superseded batch were not regraded — against the
benchmark's own evaluator, turning a binary verdict into a curve. Roughly **55–65% of each
turn-count effect is redundant steps**, and among trajectories that could improve, the first
gradable attempt is already the best in 80–91%.

The remainder is real but small, and it is measured on a different outcome from accuracy. The
**graded fraction** is the share of the benchmark's graded range that matches the answer; **binary
accuracy** is its pass/fail verdict, which requires every test case to pass. A trajectory can climb
from 0.2 to 0.9 on the first and still fail the second, so the two can move independently. An
explicit statement that work remains raises the graded fraction by 2.8 points (95% CI
[+0.005, +0.052]), replicated across three runs, while **no accuracy effect survives correction or
replication** across the seven runs in which accuracy was tested. Pooled across repeated
measurements, the demand, praise and insult contrasts are each equivalent to zero within the
pre-specified ±4-point bound (TOST *p* = 0.0014, 0.0000, 0.0001). The two statements are
compatible: a small gain in partial credit, and no detectable change in whether the task is
passed.

This regrade also caught the study's worst defect. The regrader read a turn's workbook without
passing it through a spreadsheet engine first, so any turn that answered with a formula rather
than a literal value read back as empty and scored zero — and formula-writing turns are common
here. Fixing it reversed a conclusion. Six substantive claims about our own data were withdrawn
over the course of this work. **Direction and statistical significance were reproduced on
remeasurement for the larger effects**; point estimates were not. The praise-the-assistant
stimulus is the cleanest illustration: byte-identical text, measured in two runs, gives −0.59 and
−1.08 turns, a factor of 1.8 — within the 1.5×–3.4× spread we see across re-measurements of the
same contrast on the same model. We report ranges by default and recommend the literature do the
same.

# 6. Limitations

Two models, one benchmark, fifty tasks, one agent scaffold. Beyond the demand-coding objection in
§3, three limits bear directly on how far these results travel. **Every construct is a single
28-token sentence**; a stimulus-sampling design with several paraphrases per construct is the
right version of this experiment and we did not run it. **The interjection arrives as an execution
observation**, not as a fresh user turn, and whether an agent responds the same way to a
user-channel message is untested — a plausible moderator of the closure result in particular.
**Every contrast is against a neutral interjection rather than silence**; the one comparison of
interruption against no interruption is *p* = 0.15, on one model, and was never rechecked, so any
reading of an arm's absolute cost against an uninterrupted agent is unbounded.

# 7. What this means

For practitioners, the evidence argues against treating manners themselves as the useful lever. In
our interventions, messages that implied continued work increased persistence, and most of the
additional work was repeated. The hazard runs the other way: closing-like language can curtail an
agent that is still working.

That hazard is worth stating precisely, because it is not a correctness hazard. Accuracy did not
fall in any arm, and pooled contrasts are equivalent within ±4 points. What moved was **control
flow**: text that arrived in the agent's observation channel — where tool output arrives, not
where the user speaks — changed when the agent stopped, while instructing it to do nothing. The
closing cue is also not a pleasantry. "This is the final status note recorded for this task here,
and no further notes will follow it" is an informational claim about the environment, and an agent
that treats an unauthenticated claim in its tool-output stream as grounds to stop working is
exhibiting the compliance behaviour the indirect prompt-injection literature is concerned with
`[AUTHOR: supply an indirect prompt-injection citation — e.g. a benchmark or taxonomy paper — and
add it to the bibliography]`. The register findings and this one point the same way: what reaches
an agent through its observation channel is part of its effective control surface.

For the tone literature, the narrower claim is that several widely used manipulations vary
task-directed content together with social register, so effects attributed to tone may not
identify register alone.

**Artifact.** Code, the full stimulus set, the per-turn regrade pipeline and per-trajectory
outcomes are available at `[AUTHOR: anonymized artifact URL]`.
