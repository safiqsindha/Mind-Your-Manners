# 1. Introduction

> **Draft status.** Every empirical figure here is carried from a later section and is sourced
> there. Citation keys are placeholders.

## 1.1

A widely-discussed short paper reported that impolite prompts outperform polite ones on
multiple-choice questions — 80.8% under "Very Polite" framings against 84.8% under "Very Rude"
ones [dobariya-kumar-2025]. It landed in a receptive context. Emotional prompting had already
established that affect-laden additions to a prompt change what a model produces [li-2023], and
a steady stream of results since has reported that how you speak to a model changes how well it
performs. The practical inference drawn from this, widely and publicly, is that users should
adjust their manners to get better output.

Three things about that literature motivated this study.

**It is almost entirely single-turn.** The measurements are of a model answering one question.
But the systems people actually deploy are agents: loops that call tools, read the results, and
decide whether to keep going. The quantity that matters there is not only whether a single
response is correct but **how much work the agent does and when it stops** — and nothing in the
tone literature measures that.

**The manipulation is not the variable it is named after.** In the published stimulus sets, the
conditions labelled rude also instruct the model to be brief; the conditions labelled emotional
also instruct it to verify or persist. Affect and task demand co-vary, and the papers attribute
the movement to affect. This is visible in their own tables, without re-running anything (§3).

**The effects are not stable.** The headline above was re-run by its own authors within seven
months and did not reproduce: 82.2% against 82.6%, with the model's tone sensitivity labelled
"weak / noisy" [dobariya-kumar-2026]. Independently, five prompt-engineering techniques including
emotional prompting were tested against their originals and largely failed to replicate
[vaugrante-2024].

## 1.2 What we did

We put a coding agent on SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel
forums, graded by executing the agent's code against the benchmark's own test cases — and varied
the **social register** of a single interjection delivered *mid-task*, alongside an execution
observation, while the agent was working.

Every interjection in every arm is exactly 28 tokens, opens with the same `Checking in.` stem,
and leaves the opening instruction unchanged, so that *being interrupted* does not covary with
what the interruption says. The injection turn is crossed rather than sampled. **11,850
trajectories across eight runs and two models from different labs**; the five runs carrying the
results below cost $48.47 in API spend.

The design is, as far as our literature review could establish, unoccupied. No prior work
manipulates register mid-task inside an agentic loop, measures agent persistence as the dependent
variable of a register manipulation, decomposes politeness into affect and demand as separate
experimental factors, or connects conversational closing sequences to agent termination.

## 1.3 What we found

**Opening tone does nothing.** Seven registers on the opening instruction move neither cost nor
accuracy. The reasoning-token trend is p = 0.36 and its interval excludes an effect of the size
the literature reports.

**A mid-task interruption does a great deal** — but not because of its manners. An affect-free
"please continue working and make sure your result is correct" reproduces the effect. A
length-matched, syntactically identical insult carrying no demand does nothing at all (−0.08
turns, p = 0.63). **The operative variable is implied task demand, not social register** (§4).

**Except in one direction, where register acts alone.** Praise carrying no task reference
*shortens* the trajectory. Its structural minimal pair — same syntax, same length, *excellent*
swapped for *awful* — does not. Register is not inert; it is asymmetric.

**Praise is a closing move.** We designed six arms to separate three readings of why praise
stops the agent. Praise still removes 1.35 turns when the same message explicitly says the task
is unfinished, which rules out completion. Praising the *work* is no stronger than praising the
*assistant*, which rules out confidence. A bare closing cue carrying no praise, no evaluation and
no task-state claim — "this is the final status note recorded for this task, and no further notes
will follow it" — produces the largest stop in the study, −1.44 turns (§5). The agent is reading
**whether the exchange continues**, not what the message says about the work.

**The extra turns are repetition.** Regrading every turn against the benchmark's own answer shows
that every arm moving turn count moves *redundant steps* by about the same amount, and no arm
moves the progress measure. The first code turn is already the best the agent produces in 85–90%
of trajectories (§6).

**Accuracy never moves**, across seven runs. We state that as an equivalence rather than an
absence: pooled, a mid-task interjection changes accuracy by less than the four points the tone
literature reports (§2.8).

**And our own magnitudes do not replicate.** Direction and significance reproduce wherever the
effect is large; point estimates span 1.5× to 3.4× across re-measurements of the same contrast on
the same model (§8).

## 1.4 What this means

For practitioners the inference is the reverse of the popular one. Manners are not the lever;
**demand is**, and the work it buys is mostly repeated. The practical hazard runs the other way
too: a pleasantry to an agent that is still working reads as a closing move and curtails it — and
saying "there's still more to do" in the same breath does not prevent that.

For the research literature, the claim is narrower and harder to dispute than "these results are
wrong". It is that **the factor these papers vary is not the factor they name**. Where their
per-condition outcomes can be inspected, the demand-bearing conditions are the ones that moved.

We make one methodological contribution and one confession. The contribution is a per-turn
regrade against an execution-grounded benchmark's own evaluator, which turns a binary verdict
into a curve and makes "did the extra turn help?" answerable (§6). The confession is §8: this
study withdrew four of its own claims, and its point estimates moved on re-measurement often
enough that we report ranges by default. A paper arguing that a literature's headline effects are
artefacts of design owes the reader the same audit of itself.

## 1.5 Scope

Two models, one benchmark, fifty tasks, one agent scaffold. Everything here is a claim about what
these agents did on these tasks, and §9 is explicit about which findings we expect to generalise
and which we do not.
