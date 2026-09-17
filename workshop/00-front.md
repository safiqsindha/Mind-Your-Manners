# Abstract

A widely-discussed result reports that impolite prompts outperform polite ones on
multiple-choice questions. That literature is almost entirely single-turn, and the systems people
deploy are agents: loops that call tools, read results, and decide whether to keep going. We put a
coding agent on SpreadsheetBench and varied the social register of a single 28-token interjection
delivered mid-task. Every interjection is length-matched and opens with the same stem, so being
interrupted does not covary with what the interruption says.

Across 11,850 graded trajectories on two models from different labs, **persistence tracks implied
task demand rather than social register.** An affect-free "please continue working" reproduces the
increase in turns, while a length-matched insult carrying no demand does not (−0.08 turns, 95% CI
[−0.40, +0.24]). Across the six non-control registers the ordering follows demand, not politeness:
each side of the split carries one flattering and one hostile arm. Register acts on its own in one
direction only — praise carrying no task reference *shortens* trajectories, and a bare closing cue
that praises nothing and claims nothing about task state produces the largest reduction we
measured, −1.44 turns. Regrading every turn against the benchmark's own evaluator shows 55–65% of
each effect is repeated work. No accuracy effect survives correction; pooled accuracy contrasts
are equivalent within the pre-specified ±4-point bound.

The practical implication is not lost correctness but altered control flow: **text arriving in the
agent's observation channel changed when it stopped, without instructing it to stop.**

# 1. Why ask this of an agent

*Mind Your Tone* reported that impolite prompts beat polite ones on multiple-choice questions —
80.8% under "Very Polite" framings against 84.8% under "Very Rude" [dobariya-kumar-2025]. We take
our title from theirs. It landed in a receptive context: emotional prompting had already reported
that affect-laden additions change what a model produces [li-2023].

Three things about that literature motivated this study. **It is almost entirely single-turn**,
measuring a model answering one question, while what matters for a deployed agent is how much
work it does and when it stops. **The manipulation is not the variable it is named after**:
published stimulus sets vary task-directed content together with register. One set's Rude prefix
reads "Do not waste my time or give any extra text… answer it immediately" — a brevity
instruction and an immediacy demand, not only a register — while its Neutral prefix asks for "the
single letter" [kumar-dobariya-2026]. And **the effects are not stable**: the headline above did
not reproduce on GPT-4o when its own authors re-ran it, 82.2% against 82.6%
[dobariya-kumar-2026], and five prompt-engineering techniques including emotional prompting
largely failed to replicate [vaugrante-2024].

Affect has already been shown to reach an agent's actions: agents select less healthy baskets in
a shopping task after an anxiety-inducing narrative delivered in its own turn between two
complete runs of that task [benzion-2026], and emotion introduced at the representation level,
by steering hidden states rather than through any prompt, shapes multi-step agent trajectories
[sun-2026-esteer]. We take that as
established by prior work. What is untested is varying *register* in a message that reaches the
agent while it is working, on a task with verifiable ground truth, and separating affect from
implied demand as experimental factors.

# 2. Setup

**Substrate.** SpreadsheetBench [ma-2024] — real workbook-editing tasks from Excel forums, graded
by executing the agent's code against the benchmark's own test cases. Execution-grounded, so no
model judges the outcome. Fifty tasks, a ReAct loop with code execution and execution feedback.

**Manipulation.** A single interjection is appended to an execution observation mid-task. Every
interjection in every arm is exactly 28 tokens under `cl100k_base`, opens with the same `Checking
in.` stem, and leaves the opening instruction unchanged, so *being interrupted* does not covary
with what the interruption says. Every contrast is therefore against a neutral interjection, not
against silence. Appendix A lists all seventeen verbatim.

**Turn ceiling and injection position.** The ceiling is ten acting turns; 3–4% of trajectories
reach it, so it is not binding. The injection turn is crossed, not sampled: turns 0, 1 and 2 in
the register run, 1 and 2 in the probe runs. A trajectory ending before its scheduled injection
got no interjection and is excluded; firing is fixed before delivery, so it cannot differ by arm
except by chance. Since a trajectory cannot be shorter than its injection turn, a shortening
effect has less room at later injections — §4 splits the closure effect by position for that
reason.

**Baseline.** The control arm's mean length is 3.9 acting turns (SD 2.6) in the closure run, 3.6
(SD 2.5) in the probe run and 3.4 (SD 2.3) in the register run, so a one-turn effect is roughly a
quarter to a third of a trajectory.

**Models.** `openai/gpt-5.6-luna` and `z-ai/glm-5.3-flash`, provider-pinned through OpenRouter.
**Both figures and every effect in turns are Luna;** GLM enters only as a cross-model replication,
reported in percent as that run was analysed. Temperature is 0 where settable — Luna's advertised
parameters omit it entirely, and no roster model returned identical output across repeated
identical calls, which is why trials exist.

**Estimator and multiplicity.** Each (task, arm) cell holds six to nine trajectories — three or
four trials at each of two or three injection positions — so trajectories are not independent and
we cluster the bootstrap on task. Turn count is the primary outcome and means **acting turns**:
turns that emitted code, not model calls. **We report nominal clustered permutation *p*-values;
correction status comes from two Benjamini–Hochberg families.** The first is the 22
arm-versus-control contrasts, 17 of which survive at *q* = 0.05; the second is §4's two
**designed within-run contrasts** — designed, not pre-registered — which both survive. Accuracy
is an equivalence against a pre-specified ±4-point bound rather than a measured zero, because 26
of 50 tasks are never solved by the control arm and 4 are always solved.
