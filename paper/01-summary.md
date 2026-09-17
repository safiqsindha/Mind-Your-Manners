# 1. Summary

**Demand drives agent persistence; social register does not.** A message that tells a working agent
to keep going makes it take more turns, in whatever register it is phrased. A message that is merely
rude does nothing measurable. A message that is merely warm, or that merely signals the exchange is
over, makes the agent stop early. None of it changes how often the task is solved.

## 1.1 Why the question

*Mind Your Tone* reported accuracy on GPT-4o rising from 80.8% under "Very Polite" prompts to 84.8%
under "Very Rude" ones [dobariya-kumar-2025]; we take our title from theirs. It landed in a
receptive context, emotional prompting having already reported that affect-laden additions change
what a model produces [li-2023]. Three things about that literature motivated this study. **It is
almost entirely single-turn**, measuring a model answering one question, while what matters for a
deployed agent is how much work it does and when it stops. **The manipulation is often not the
variable it is named after**: in several published stimulus sets the conditions labelled rude also
carry instructions — not to give extra text in one, to attend and attempt in another — and the
conditions labelled emotional also instruct the model to verify or persist, so affect and task
demand co-vary and the movement is attributed to tone (§3). **And the effects are not stable.** The
headline above was re-run by its own authors and did not reproduce on GPT-4o, 82.2% against 82.6%
[dobariya-kumar-2026]; a 1,446-question replication found the *opposite* direction [cai-2025-tone];
and five prompt-engineering techniques including emotional prompting largely failed to replicate
[vaugrante-2024].

Affect has already been shown to reach an agent's actions: agents select less healthy baskets in a
shopping task after an anxiety-inducing narrative delivered in its own turn between two complete
runs of that task [benzion-2026], and emotion introduced at the representation level, by steering
hidden states rather than through any prompt, shapes multi-step agent trajectories
[sun-2026-esteer]. What is untested is varying *register* in a message that reaches the agent while
it is working, on a task with verifiable ground truth, and separating affect from implied demand as
experimental factors.

## 1.2 What we did, and what we found

We put a ReAct coding agent on SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel
forums, graded by executing the agent's code against the benchmark's own test cases — and varied the
**social register** of a single interjection delivered *mid-task*, alongside an execution
observation, while the agent was working. Every interjection is exactly 28 tokens and opens with the
same `Checking in.` stem, so that *being interrupted* does not covary with what the interruption
says. **11,850 graded trajectories across eight runs and two models from different labs**, of which
9,850 were regraded turn by turn; the five register runs cost \$48.47 in API spend. Appendix A lists
every interjection verbatim.

**Finding 1: demand, not politeness, drives turn count (§4).** An affect-free continuation request
costs +1.17 turns; an insult carrying no demand, identical in syntax and length to the praise arm,
is indistinguishable from control at −0.08, 95% CI [−0.40, +0.24]. Across seven registers the
ordering follows implied demand, and each side of the split holds one flattering and one hostile
arm. The demand coding is ours and was made after the effects were visible; five blinded raters
reproduce it on six of seven arms and dissent, unanimously, on the seventh (κ = 0.70), so the
*dichotomy* is our reading of one contested arm. The continuous form of the claim survives the
blinded coding intact (*r* = +0.72).

**Finding 2: praise and closing cues shorten trajectories; insult has no measurable effect (§5).**
Praise removes 1.35 turns relative to the identical message without it *even when that message
states the task is unfinished*, which a simple propositional-completion account does not predict;
praising the work is no stronger than praising the assistant, against a confidence account. A bare
closing cue carrying no praise, no evaluation and no task-state claim produces the largest reduction
in the study, −1.44 turns. **This leg is the least replicated thing in the paper — one run, one
model, one turn ceiling.**

**Finding 3: no accuracy effect survives correction, and the extra turns are mostly repetition
(§6).** Regrading every turn against the benchmark's own evaluator shows 55–65% of each turn-count
effect is redundant steps, and that among trajectories that could improve the first gradable attempt
is already the best in 80–91%. The remainder is real but small: an explicit statement that work
remains raises the graded fraction by 2.8 points (95% CI [+0.005, +0.052]), replicated across three
runs. No accuracy contrast survives multiplicity correction or replication, and we state that as an
equivalence against a pre-specified ±4-point bound rather than as an absence (§2.5).

## 1.3 What this means, and scope

For practitioners the inference is the reverse of the popular one. Manners are not the lever; what
the agent acts on is the demand, and the work it buys is mostly repeated. The hazard runs the other
way: closing-like language can curtail an agent that is still working. **It is not a correctness
hazard** — accuracy did not fall in any arm, and the pooled contrasts are equivalent within ±4
points. What moved was **control flow**: text arriving in the agent's observation channel, where
tool output arrives rather than where the user speaks, changed when the agent stopped while
instructing it to do nothing. The bare closing cue is also not a pleasantry. "This is the final
status note recorded for this task here" is an informational claim about the environment, and an
agent that treats an unauthenticated claim in its tool-output stream as grounds to stop is showing
the compliance behaviour the indirect prompt-injection literature is concerned with [greshake-2023].

For the research literature the claim is narrower and harder to dispute than "these results are
wrong": **the factor several of these papers vary is not the factor they name.** In the two of four
audited papers whose per-condition outcomes can be inspected, the demand-bearing conditions are the
ones that moved (§3.2–3.3), and §3.4 supplies the contrast case that makes this a claim about
particular stimulus sets rather than about tone research generally.

**Scope.** Two models, one benchmark, fifty tasks, one agent scaffold. Everything here is a claim
about what these agents did on these tasks, and §7 is explicit about which findings we expect to
generalise and which we do not.
