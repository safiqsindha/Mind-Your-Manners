# 1. Introduction

> **Draft status.** Every empirical figure here is carried from a later section and is sourced
> there. Appendix C records read depth and version hazards for the bibliography.

## 1.1 The question

*Mind Your Tone* reported that impolite prompts outperform polite ones on multiple-choice questions —
80.8% under "Very Polite" framings against 84.8% under "Very Rude" [dobariya-kumar-2025]. We take our
title from theirs. It landed in a receptive context, emotional prompting having already reported that
affect-laden additions change what a model produces [li-2023]. Three things about that literature
motivated this study.

**It is almost entirely single-turn**, measuring a model answering one question, while what matters
for a deployed agent is how much work it does and when it stops — which nothing in the tone
literature measures.

**The manipulation is often not the variable it is named after.** In several published stimulus sets
the conditions labelled rude also carry instructions — not to give extra text in one, to attend and
attempt in another — and the conditions labelled emotional also instruct the model to verify or
persist. Affect and task demand co-vary, and the movement is attributed to tone. This is visible in
the authors' own tables (§3). The entanglement varies sharply: in one of four papers only two of six
hostile variants carry a demand, and we rest nothing on that case; in the one paper whose
per-condition outcomes are fully inspectable, every condition whose prefix constrains output length
is shorter than every condition whose prefix does not, on all four of its models. It is also not
universal — §3.4 gives a published tone study where the format instruction is pinned identically
across conditions and the tone effect largely vanishes.

**The effects are not stable.** The headline above was re-run by its own authors and did not
reproduce on GPT-4o: 82.2% against 82.6%. The re-run is not a null — on those same 50 questions both
extremes significantly beat Neutral, a U-shape in extremity rather than a rudeness gradient, and the
same paper reports 11–12-point spreads on two other models [dobariya-kumar-2026]. Independently, a
1,446-question replication across three models found the *opposite* direction [cai-2025-tone], and
five prompt-engineering techniques including emotional prompting largely failed to replicate
[vaugrante-2024].

## 1.2 What we did

We put a coding agent on SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel forums,
graded by executing the agent's code against the benchmark's own test cases — and varied the **social
register** of a single interjection delivered *mid-task*, alongside an execution observation, while
the agent was working. Every interjection is exactly 28 tokens, opens with the same `Checking in.`
stem, and leaves the opening instruction unchanged, so that *being interrupted* does not covary with
what the interruption says; the injection turn is crossed rather than sampled (§2.2). **11,850 graded
trajectories across eight runs and two models from different labs**, of which 9,850 were regraded
turn by turn (§6); the five register runs cost \$48.47 in API spend. Appendix A lists every
interjection verbatim.

The design is, as far as our review could establish, unoccupied — but the boundary needs care,
because affect has already been shown to reach an agent's actions. Agents primed with anxiety-inducing
narratives select less healthy baskets in a shopping task [benzion-2026]; emotion introduced at the
representation level, by steering hidden states rather than through any prompt, shapes multi-step
agent behaviour [sun-2026-esteer]. We take that as settled rather than as a contribution of ours. The
second bears directly on our praise result and we flag it here rather than where it is convenient:
E-STEER reports positive valence *reducing* replan frequency relative to neutral, an agent-effort
count moving the way §5 reports for praise. We cite its direction only, never a magnitude
(Appendix C).

Neither varies register in a message reaching the agent while it works. One delivers its prime as a
narrative *between two complete runs* of the task, the other intervenes on hidden states rather than
through the model's input at all, and neither scores against verifiable ground truth. What we could
not find is prior work that varies register mid-task inside an agentic loop, decomposes politeness
into affect and demand as separate factors, or connects conversational closing sequences to agent
termination — §5.1 records what a review panel's findings narrowed in that last claim. On the channel:
our interjection rides along with an execution observation rather than arriving as a fresh user turn,
and §8.2 records that as a limitation rather than a property we claim.

## 1.3 What we found

**Opening tone does nothing that survives correction.** Across seven registers on the opening
instruction, no trend survives multiplicity correction, on cost or accuracy; the reasoning-token
trend is *p* = 0.36, and its interval excludes the 44% effect the pre-registered hypothesis targeted.

**A mid-task interruption does a great deal, but not because of its manners.** An affect-free
continuation request reproduces the effect; an insult carrying no demand, identical in syntax and
length to the praise arm, is indistinguishable from control. **What persistence tracks is implied
task demand, not social register** (§4) — with the caveat, put here rather than in the limitations,
that "demand" is our own category, coded after the effects were visible, and probed with sentences we
wrote to instantiate it. Five blinded raters agree on six of seven register arms and dissent
unanimously on the seventh (κ = 0.70); under their coding the no-demand group is a single arm (§4.2).
A reader who suspects the dissociation reduces to "explicit instructions change behaviour, decorative
text does not" is raising the right objection, and §8.4 says what would settle it.

**Except in one direction, where register acts alone.** Praise carrying no task reference *shortens*
the trajectory; its structural minimal pair, *excellent* swapped for *awful*, does not. Six arms
separate three readings of why, and **praise behaves as a closing move**: it removes 1.35 turns
relative to the identical message without it even when that message states the task is unfinished,
while a bare closing cue carrying no praise, no evaluation and no task-state claim produces the
largest stop in the study, −1.44 turns (§5).

**The extra turns are mostly repetition**, 55–65% of each effect, and among trajectories that could
improve the first gradable attempt is already the best in 80–91%. The remainder is real but small
(§6.4). **No accuracy effect survives correction or replication**, which we state as an equivalence
rather than an absence (§2.8). **And our own magnitudes are unstable:** direction and significance
reproduce wherever the effect is large, while point estimates span 1.5× to 3.4× across
re-measurements of the same contrast on the same model (§7.3).

## 1.4 What this means, and scope

For practitioners the inference is the reverse of the popular one. Manners are not the lever; what
the agent acts on is the demand, and the work it buys is mostly repeated. The hazard runs the other
way: closing-like language can curtail an agent that is still working — though that leg rests on one
run of one model at one ceiling (§8.3).

**The hazard is not a correctness hazard.** Accuracy did not fall in any arm and the pooled contrasts
are equivalent within ±4 points. What moved was **control flow**. Text arriving in the agent's
observation channel — where tool output arrives, not where the user speaks — changed when the agent
stopped, while instructing it to do nothing. The bare closing cue is also not a pleasantry: "this is
the final status note recorded for this task here" is an informational claim about the environment,
and an agent that treats an unauthenticated claim in its tool-output stream as grounds to stop is
showing the compliance behaviour the indirect prompt-injection literature is concerned with
[greshake-2023], which showed that once an application ingests content from a tool rather than from
its user, the line between data and instructions collapses.

For the research literature the claim is narrower and harder to dispute than "these results are
wrong": **the factor several of these papers vary is not the factor they name**. In the two of four
audited papers whose per-condition outcomes can be inspected, the demand-bearing conditions are the
ones that moved (§3.4) — and §3.4 supplies the contrast case that makes this a claim about particular
stimulus sets rather than about tone research generally.

We make one methodological contribution and one audit of ourselves. The contribution is a per-turn
regrade against an execution-grounded benchmark's own evaluator, which turns a binary verdict into a
curve and makes "did the extra turn help?" answerable (§6). The audit is §7: this study withdrew six
substantive claims about its own data, including one that reversed when a defect in that same regrade
was found and fixed (§7.3).

**Scope.** Two models, one benchmark, fifty tasks, one agent scaffold. Everything here is a claim
about what these agents did on these tasks, and §8 is explicit about which findings we expect to
generalise and which we do not.
