# 1. Introduction

> **Draft status.** Every empirical figure here is carried from a later section and is sourced
> there. Citation keys resolve to §9.

## 1.1

A widely-discussed short paper, *Mind Your Tone*, reported that impolite prompts outperform
polite ones on multiple-choice questions — 80.8% under "Very Polite" framings against 84.8%
under "Very Rude" ones [dobariya-kumar-2025]. We take our title from theirs, and the debt is
not only nominal: this study exists because that result made the question worth asking of
something other than a single answer.

It landed in a receptive context. Emotional prompting had already
reported that affect-laden additions to a prompt change what a model produces [li-2023], and
further results since have reported that how you speak to a model changes how well it performs.
The practical inference drawn from this is that users should adjust their manners to get better
output.

Three things about that literature motivated this study.

**It is almost entirely single-turn.** The measurements are of a model answering one question.
But the systems people actually deploy are agents: loops that call tools, read the results, and
decide whether to keep going. The quantity that matters there is not only whether a single
response is correct but **how much work the agent does and when it stops** — and nothing in the
tone literature measures that.

**The manipulation is not the variable it is named after.** In the published stimulus sets, the
conditions labelled rude also carry instructions — not to give extra text in one, to attend and
attempt in another — and the conditions labelled emotional also instruct the model to verify or
persist.
Affect and task demand co-vary, and the movement is attributed to tone. This is visible in their
own tables, without re-running anything (§3). The strength of the entanglement varies, and we
report it case by case rather than uniformly: in one of the four papers only two of six hostile
variants carry a demand, and we rest nothing on that case (§3.3). In the one paper whose
per-condition outcomes are fully inspectable, the split is clean — on all four of its models,
every condition whose prefix constrains output length is shorter than every condition whose
prefix does not, and affect does not order the result (§3.2).

**The effects are not stable.** The headline above was re-run by its own authors the following
spring and did not reproduce on GPT-4o: 82.2% against 82.6%, with that model's tone sensitivity
labelled "weak / noisy" — a 4.0-point polite-to-rude gap becoming 0.4. The re-run is not a null,
and we are careful about this: on those same 50 questions both extremes significantly beat
Neutral, which is a U-shape in extremity rather than the rudeness gradient the original claimed,
and the same paper reports 11–12-point spreads on two other models. Its finding is that register
effects are real and strongly model-dependent, not that they are absent [dobariya-kumar-2026]. Independently, five prompt-engineering techniques including
emotional prompting were tested against their originals and largely failed to replicate
[vaugrante-2024].

## 1.2 What we did

We put a coding agent on SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel
forums, graded by executing the agent's code against the benchmark's own test cases — and varied
the **social register** of a single interjection delivered *mid-task*, alongside an execution
observation, while the agent was working.

Every interjection in every arm is exactly 28 tokens, opens with the same `Checking in.` stem,
and leaves the opening instruction unchanged, so that *being interrupted* does not covary with
what the interruption says. The injection turn is crossed rather than sampled in every run after
the first micro-experiment (§2.2). **11,850 graded trajectories across eight runs and two models
from different labs**, of which 9,850 were additionally regraded turn by turn (§6); the five
register runs reported in §4–§6 cost $48.47 in API spend.

The design is, as far as our review could establish, unoccupied — but the boundary needs
stating carefully, because affect has already been shown to reach an agent's actions. Agents
primed with anxiety-inducing narratives select less healthy baskets in a budget-constrained
shopping task, across three models and 2,250 runs [benzion-2026]; emotion introduced at the
representation level shapes multi-step agent trajectories [sun-2026-esteer]. Both establish
that emotional context changes what an agent *does* and not only what it says, and we take
that as settled rather than as something this paper contributes.

Neither, however, varies register in a message that reaches the agent while it is working. One
primes with narratives before the task begins, the other intervenes on hidden states rather
than through the model's input at all, and neither scores the agent against a verifiable ground
truth. What we could not find is prior work that varies register *mid-task, while the agent is
working*, inside an agentic loop; that decomposes politeness into affect and demand as separate
experimental factors; or that connects conversational closing sequences to agent termination.
On the channel our interjection arrives through, be precise: it rides along with an execution
observation rather than as a fresh user turn, and §8.5 records that as a limitation of this
design rather than a property we claim for it. The nearest designs — opening instructions split
across turns, and content-typed interruptions answered in
a single response — manipulate task content rather than register, and neither measures
downstream persistence.

## 1.3 What we found

**Opening tone does nothing that survives correction.** Across seven registers on the opening
instruction, no trend survives multiplicity correction, on cost or on accuracy. The
reasoning-token trend is p = 0.36, and its interval — −4% to +14% across the whole scale —
excludes the 44% effect the pre-registered hypothesis targeted, though not the smallest published
effects. The uncorrected lead in that run is reported in §2.6 rather than suppressed.

**A mid-task interruption does a great deal** — but not because of its manners. An affect-free
"please continue working and make sure your result is correct" reproduces the effect. An
insult carrying no demand, identical in syntax and length to the praise arm, is indistinguishable
from control (−0.08 turns, p = 0.63; +0.57, p = 0.17 on re-measurement). **The operative variable
is implied task demand, not social register** (§4).

**Except in one direction, where register acts alone.** Praise carrying no task reference
*shortens* the trajectory. Its structural minimal pair — same syntax, same length, *excellent*
swapped for *awful* — does not. Register is not inert; it is asymmetric.

**Praise behaves as a closing move.** We designed six arms to separate three readings of why
praise stops the agent. Praise removes 1.35 turns relative to the identical message without
praise, even when that message states the task is unfinished, which rules out completion.
Praising the *work* is no stronger than praising the *assistant*, which does not support
confidence. A bare closing cue carrying no praise, no evaluation and no task-state claim — "this
is the final status note recorded for this task, and no further notes will follow it" — produces
the largest stop in the study, −1.44 turns (§5). The ordering is monotone in how strongly the
message projects an end to the exchange; that praise operates *through* pre-closing structure is
the hypothesis this is consistent with, not one the design establishes (§5.4).

**The extra turns are mostly repetition.** Regrading every turn against the benchmark's own
answer shows that roughly 55–65% of each turn-count effect is *redundant steps*, and that among
trajectories that could improve, the first gradable attempt is already the best in 80–91%. The
remainder is real but small: an explicit statement that work remains raises the graded fraction by
2.8 points across three measurements. Accuracy does not move — though it is too underpowered to
resolve a gain that size either way (§6.4).

**No accuracy effect survives correction or replication**, across the seven runs in which
accuracy was tested: the six that carried a mid-task interjection, whose 22 contrasts make up the
corrected family (§2.6), and the opening-tone run. We state that as
an equivalence rather than an absence: pooled, a mid-task interjection changes accuracy by less
than the four points the tone literature reports (§2.8).

**And our own magnitudes are unstable.** Direction and significance reproduce wherever the
effect is large; point estimates span 1.5× to 3.4× across re-measurements of the same contrast on
the same model, though most of that spread is across different turn ceilings. At a matched
ceiling the two larger effects reproduce within 10% and the smallest does not (§7.3).

## 1.4 What this means

For practitioners the inference is the reverse of the popular one. Manners are not the lever;
**demand is**, and the work it buys is mostly repeated. The practical hazard runs the other way
too: a pleasantry to an agent that is still working reads as a closing move and curtails it.
Adding "there's still more to do" does not cancel the praise — praise removes 1.35 turns relative
to the identical message without it — though that combined message does still lengthen the
trajectory relative to control (§5.3).

For the research literature, the claim is narrower and harder to dispute than "these results are
wrong". It is that **the factor these papers vary is not the factor they name**. In the two of
four papers whose per-condition outcomes can be inspected, the demand-bearing conditions are the
ones that moved, with the qualifications §3 states.

We make one methodological contribution and one audit of ourselves. The contribution is a
per-turn regrade against an execution-grounded benchmark's own evaluator, which turns a binary
verdict into a curve and makes "did the extra turn help?" answerable (§6). The audit is §7, and it
is not decorative: this study withdrew six substantive claims about its own data, including one
that reversed when a defect in that same regrade was found and fixed (§6.8). Its point estimates
moved on re-measurement often enough that we report ranges by default.

## 1.5 Scope

Two models, one benchmark, fifty tasks, one agent scaffold. Everything here is a claim about what
these agents did on these tasks, and §8 is explicit about which findings we expect to generalise
and which we do not.
