# Mind your manners? LLM-agent persistence tracks demand, not social register

> **Draft status.** Title and author block are placeholders. Every figure in this abstract is
> carried from a numbered section and sourced there.

**Authors.** *[to be completed]*

---

## Abstract

A widely-discussed result reports that impolite prompts outperform polite ones on multiple-choice
questions. That literature is almost entirely single-turn; the systems people deploy are agents,
loops that call tools, read results, and decide whether to keep going. We put a coding agent on
SpreadsheetBench and varied the register of a single 28-token interjection delivered mid-task.
Every interjection is length-matched and opens with the same stem, so being interrupted does not
covary with what the interruption says. 11,850 graded trajectories, eight runs, two models from
different labs.

**Persistence tracks implied task demand rather than social register.** An affect-free "please
continue working and make sure your result is correct" reproduces the cost effect; a
length-matched, syntactically identical insult carrying no demand does not (−0.08 turns, 95% CI
[−0.40, +0.24]). Across the six non-control registers the ordering follows demand, not politeness:
each side of the split carries one flattering and one hostile arm. The demand coding is ours and
was made after the effects were visible. Five blinded raters reproduce it on six of seven arms and
dissent, unanimously, on the seventh (κ = 0.70), so the *dichotomy* is our reading of one contested
arm; the continuous form of the claim survives the blinded coding intact (*r* = +0.72).

**Register acts on its own in one direction only.** Praise carrying no task reference *shortens*
trajectories; its minimal pair with *excellent* swapped for *awful* does not. Six arms separate
three accounts of why. Praise still removes 1.35 turns relative to the identical message without it
*even when that message states the task is unfinished*, which is inconsistent with a simple
propositional completion account; praising the work is no stronger than praising the assistant,
against a confidence account. A bare closing cue carrying no praise, no evaluation and no task-state
claim produces the largest reduction in the study, −1.44 turns, largest where a floor on trajectory
length binds least. **This leg is the least replicated thing in the paper — one run, one model, one
turn ceiling.**

**Regrading every turn against the benchmark's own evaluator** shows 55–65% of each turn-count
effect is redundant steps, and that among trajectories that could improve the first gradable attempt
is already the best in 80–91%. The remainder is real but small: an explicit statement that work
remains raises the graded fraction by 2.8 points (95% CI [+0.005, +0.052]), replicated across three
runs. No accuracy effect survives correction or replication; we state that as an equivalence against
a pre-specified ±4-point bound rather than as an absence.

The implication is not lost correctness but altered control flow: **text arriving in the agent's
observation channel changed when it stopped, without instructing it to stop.** We also audit
ourselves: this study withdrew six substantive claims about its own data, one of which reversed only
after we found that the per-turn regrade never recalculated formula-writing turns — a defect that
had manufactured the appearance of instability in the very contrast we were using to argue for
repeated measurement. Direction and significance replicate wherever an effect is large; point
estimates do not.
