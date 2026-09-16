# Mind your manners? Demand, not register, is what moves an LLM agent

> **Draft status.** Title and author block are placeholders. Every figure in this abstract is
> carried from a numbered section and sourced there.

**Authors.** *[to be completed]*

---

## Abstract

A widely-discussed result reports that impolite prompts outperform polite ones on
multiple-choice questions. That literature is almost entirely single-turn, and the systems people
deploy are agents: loops that call tools, read results, and decide whether to keep going. We ask
what social register does to an agent *while it is working*.

We put a coding agent on SpreadsheetBench and varied the register of a single 28-token
interjection delivered mid-task, alongside an execution observation. Every interjection is
length-matched and opens with the same stem, so being interrupted does not covary with what the
interruption says; the injection turn is crossed rather than sampled. 11,850 graded trajectories,
eight runs, two models from different labs.

**Manners are not the operative variable; demand is** — on a coding of "demand" that is our own,
applied after we had seen the effects, with no second rater, and tested on stimuli we wrote to
embody it (§4.2, §8.7). That is the study's weakest joint and we put it here rather than in the
limitations. An affect-free "please continue working and make sure your result is correct"
reproduces the cost effect. A length-matched,
syntactically identical insult carrying no demand does not move it (−0.08 turns, *p* = 0.63).
The seven-register cost curve that looks like a politeness gradient is a demand gradient: the
four demand-carrying arms span +0.70 to +1.80 turns and the three without span −0.68 to +0.09,
with no overlap — and register does not sort them: each side carries both a
flattering and a hostile arm.

**Register acts in one direction only.** Praise carrying no task reference *shortens*
trajectories; its minimal pair with *excellent* swapped for *awful* does not. Six arms separate
three accounts of why. Praise still removes 1.35 turns relative to the identical message without
it, even when that message states the task is unfinished, which rules out a completion
inference; praising the work is no stronger than praising the assistant, which does not support
a confidence account. A bare closing cue carrying no praise, no evaluation and no task-state
claim produces the largest reduction in the study, −1.44 turns. **This leg is the least
replicated thing in the paper — one run, one model, one turn ceiling.** Weighted accordingly, the
implication is a hazard rather than a technique: on this evidence **a pleasantry can end an
agent's work**, and whether it does so generally is untested.

**Regrading every turn against the benchmark's own evaluator** shows that 55–65% of each
turn-count effect is redundant steps, and that among trajectories that could improve the first
gradable attempt is already the best in 80–91%. The remainder is real but small: an explicit
statement that work remains raises the graded fraction by 2.8 points (95% CI [+0.005, +0.052]),
replicated across three runs. No accuracy effect survives correction or replication across the seven
runs in which accuracy was tested — the six carrying a mid-task interjection, whose 22 contrasts
form the corrected family of §2.6, and the opening-tone run besides; we state that as an equivalence against a pre-specified ±4-point bound rather than as an
absence, and note the design cannot resolve an effect of a point or two.

**We also audit ourselves.** This study withdrew six substantive claims about its own data. One
reversed only after we found that the per-turn regrade never recalculated formula-writing
turns — a defect that had manufactured the appearance of run-to-run instability in the very
contrast we were using to argue for repeated measurement. Direction and significance replicate
wherever an effect is large; point estimates do not. We report ranges by default and recommend
the literature do the same.
