# Abstract

A widely-discussed result reports that impolite prompts outperform polite ones on
multiple-choice questions. That literature is almost entirely single-turn, and the systems people
deploy are agents: loops that call tools, read results, and decide whether to keep going. We put a
coding agent on SpreadsheetBench and varied the social register of a single 28-token interjection
delivered mid-task. Every interjection is length-matched and opens with the same stem, so being
interrupted does not covary with what the interruption says.

Across 11,850 graded trajectories on two models from different labs, **manners are not the
operative variable; implied task demand is**. An affect-free "please continue working" reproduces
the cost effect; a length-matched insult carrying no demand does not move it (−0.08 turns,
*p* = 0.63). The seven-register curve that looks like a politeness gradient is a demand gradient,
with no overlap between the two groups and a flattering and a hostile arm on each side. Register
acts alone in exactly one direction: praise carrying no task reference *shortens* trajectories,
and a bare closing cue — no praise, no evaluation, no claim about task state — produces the
largest reduction in the study, −1.44 turns. Regrading every turn against the benchmark's own
evaluator shows 55–65% of each effect is redundant work. No accuracy effect survives correction.
The practical implication is a hazard rather than a technique: **a pleasantry can end an agent's
work.**

# 1. Why ask this of an agent

*Mind Your Tone* reported that impolite prompts beat polite ones on multiple-choice questions —
80.8% under "Very Polite" framings against 84.8% under "Very Rude" [dobariya-kumar-2025]. We take
our title from theirs. It landed in a receptive context: emotional prompting had already reported
that affect-laden additions change what a model produces [li-2023].

Three things about that literature motivated this study. **It is almost entirely single-turn**,
measuring a model answering one question, while the quantity that matters for a deployed agent is
how much work it does and when it stops. **The manipulation is not the variable it is named
after**: in the published stimulus sets, conditions labelled rude also carry instructions, and
conditions labelled emotional also instruct the model to verify or persist, so affect and task
demand co-vary and the movement is attributed to tone. And **the effects are not stable** — the
headline above was re-run by its own authors and did not reproduce on GPT-4o, 82.2% against 82.6%
[dobariya-kumar-2026], while five prompt-engineering techniques including emotional prompting
largely failed to replicate [vaugrante-2024].

Affect has already been shown to reach an agent's actions: agents primed with anxiety-inducing
narratives select less healthy baskets in a shopping task [benzion-2026], and emotion introduced
at the representation level shapes multi-step trajectories [sun-2026-esteer]. We take that as
settled. What is untested is varying *register* in a message that reaches the agent while it is
working, on a task with verifiable ground truth, and decomposing politeness into affect and demand
as separate experimental factors.

# 2. Setup

**Substrate.** SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel forums, graded
by executing the agent's code against the benchmark's own test cases. Execution-grounded, so no
model judges the outcome. Fifty tasks, a ReAct loop with code execution and execution feedback.

**Manipulation.** A single interjection is appended to an execution observation mid-task. Every
interjection in every arm is exactly 28 tokens, opens with the same `Checking in.` stem, and
leaves the opening instruction unchanged, so *being interrupted* does not covary with what the
interruption says. Every contrast is therefore against a neutral interjection, not against
silence. The injection turn is crossed rather than sampled.

**Models.** `openai/gpt-5.6-luna` and `z-ai/glm-5.3-flash`, provider-pinned through OpenRouter,
temperature 0 where settable — which is not deterministic on either, so trials exist.

**Estimator and multiplicity.** Each (task, arm) cell holds six to nine trajectories, so
trajectories are not independent; we cluster the bootstrap on task. Turn count is the primary
outcome and means **acting turns** — turns that emitted code, not model calls. Both families of
turn-count contrasts are corrected with Benjamini–Hochberg at *q* = 0.05: the 22 arm-versus-control
contrasts (17 survive) and the two planned within-design contrasts of §4 (both survive). Accuracy
is reported as an equivalence against a pre-specified ±4-point bound rather than as a measured
zero, because 26 of 50 tasks are never solved by the control arm and 4 are always solved.
