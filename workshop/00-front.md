# Abstract

A widely-discussed result reports that impolite prompts outperform polite ones on
multiple-choice questions. That literature is single-turn; deployed systems are agents. We put a
coding agent on SpreadsheetBench and varied the social register of a single 28-token interjection
delivered mid-task. Every interjection is length-matched and opens with the same stem, so being
interrupted does not covary with what the interruption says.

Across six mid-task runs on two models from different labs (9,850 scheduled trajectories, 6,616 in the
primary analysis), **persistence
tracks implied task demand more closely than social register.** An affect-free "please continue
working" reproduces the increase in turns, while a length-matched insult carrying no demand does
not lengthen trajectories (−0.08 turns, 95% CI [−0.40, +0.24] at the ten-turn budget). Across six register arms the
ordering follows our demand coding rather than politeness, with polite and hostile arms on both
sides; blinded raters dispute that coding for one arm, so we report an ordering, not a clean
dichotomy. Register acts on its own in one direction only: praise carrying no task reference
*shortens* trajectories, and so does a note saying no further notes will follow (−1.44 turns). We
leave the mechanism of these shortening effects open. Per-turn regrading shows that on the main model 56–93% of each clear turn-count effect is steps
after which the graded range did not change. No accuracy effect survives correction or
replication, and pooled accuracy contrasts are equivalent within a ±4-point bound taken from the
tone literature (an exploratory analysis, not pre-registered).

The practical implication is altered control flow rather than measured lost correctness: **a
status note appended to an agent's tool output changed when it stopped, without instructing it to
stop.**

# 1. Why ask this of an agent

*Mind Your Tone* reported that impolite prompts beat polite ones on multiple-choice questions —
80.8% under "Very Polite" framings against 84.8% under "Very Rude" [dobariya-kumar-2025]. We take
our title from theirs. Emotional prompting had already reported that affect-laden additions change
what a model produces [li-2023].

Three things about that literature motivated this study. **It is almost entirely single-turn**,
while what matters for a deployed agent is how much work it does and when it stops. **The
manipulation is not the variable it is named after**: one stimulus set's Rude prefix reads "Do not
waste my time or give any extra text… answer it immediately" — an instruction about how to answer,
not only a register — while its Neutral prefix asks for "the single letter" [kumar-dobariya-2026].
§3 asks the same question of our own stimuli. And **the effects are not stable**: the headline did
not reproduce on GPT-4o when its own authors re-ran it, 82.2% against 82.6% [dobariya-kumar-2026],
and five prompt-engineering techniques including emotional prompting largely failed to replicate
[vaugrante-2024].

Affect has already been shown to reach an agent's actions, through an anxiety-inducing narrative
delivered between two runs of a shopping task [benzion-2026] and through steering hidden states
[sun-2026-esteer]; we cite the second for direction only, since it reports no intervals. What is
untested is varying *register* in a message that reaches the agent while it is working, on a task
with verifiable ground truth, and separating affect from implied demand as experimental factors.

# 2. Setup

**Substrate and agent.** SpreadsheetBench [ma-2024]: workbook-editing tasks from Excel forums,
graded by executing the agent's code against the benchmark's test cases. Our 50 tasks are a fixed
subset of a validation sample drawn, stratified by instruction type, from the benchmark's 200-task
sample, excluding every task that passes when the agent does nothing. Accuracy is the benchmark's
hard criterion: every test case must pass. The agent is a ReAct loop: each turn it emits one
Python block, run against the original workbook, or a `FINAL:` line. **The system prompt states
the turn budget, asks for a saved answer by turn N−2, and each observation ends with a
`[Turn k of N next]` marker.** Observations (stdout, stderr, marker) return as user-role messages
in this harness.

**Manipulation.** One interjection is appended, after a blank line, to the observation that
follows acting turn *k* (0-indexed). Every interjection is exactly 28 tokens under `cl100k_base`
and opens with the same `Checking in.` stem, so *being interrupted* does not covary with what the
interruption says; every contrast is against a neutral interjection, not silence. Appendix A lists
all seventeen, including where their padding clauses differ. The control says it was recorded
*partway through the task*; every treated arm replaces that clause, so each contrast also removes it.

**Turn budget and injection position.** The three Luna runs in the figures used a ten-turn budget,
the cross-model run twenty. Because the agent is told its budget, the budget is a condition it
paces against, not only a cap: the "work remains" effect is +1.85 turns at ten and +6.20 at twenty,
though only 22 of that arm's ten-turn trajectories hit the cap. We therefore compare magnitudes
only within a budget. At ten, 4.2–5.8% of analysed trajectories reach the cap. The injection turn
is crossed: turns 0–2 in the register run, 1–2 in the probe and closure runs. **We report turns 1
and 2 for the register run, a choice made after its turn-0 contrasts were seen**; none survives
correction, and pooling all three keeps the ordering of §3 (Appendix C.2). Trajectories ending
before their scheduled injection are excluded; firing precedes delivery, so it can differ by
arm only by chance (Appendix C.1). The control arm averages 4.5, 4.2 and 3.8 acting turns (SD
2.4–2.7) in the closure, probe and register runs, so a one-turn effect is a quarter of a trajectory.

**Models.** **Luna** is `openai/gpt-5.6-luna`, pinned to `openai/gpt-5.6-luna-20260709`; **GLM** is
`z-ai/glm-5.3-flash`, pinned to `z-ai/glm-5.3-flash-20260826`, both via OpenRouter. **Both figures
and every effect in turns in the body are Luna;** GLM is a cross-model replication (Appendix C.3).
Temperature is 0 where settable; outputs still vary across calls, hence trials.

**Estimator and multiplicity.** Each (task, arm) cell is scheduled for six to nine trajectories, fewer once those on which the
interjection did not fire are excluded (Appendix C.1). Point
estimates are paired within task: per task, the mean over firing trajectories in each arm, pooled
across positions, differenced, then averaged over tasks. A task with no firing trajectory in an arm
drops from that contrast (none does in Luna's, three or four in GLM's); Appendix C.2 gives
position-stratified estimates. Intervals come from a task bootstrap and
*p*-values from a task-level sign-flip permutation, **20,000 draws each, everywhere**; pooled
contrasts resample tasks jointly across runs, which share their 50 tasks. **Intervals are
within-run and exclude run-to-run variation, which §5 shows is substantial.** Turn count is the
primary outcome and means **acting turns**: turns that emitted code. **We report nominal *p*-values;
correction status comes from two Benjamini–Hochberg families**: the 22 arm-versus-control contrasts
in every run with a mid-task interjection, of which 17 survive at *q* = 0.05 (listed in Appendix
C.1 with every run), and §4's two **designed within-run contrasts** — designed, not pre-registered
— which both survive. Accuracy is an equivalence against a ±4-point bound, the gap the tone literature reports; we fixed
it during analysis, after an earlier draft's arm-specific bounds were discarded, so it is exploratory,
not pre-registered. We use equivalence because 26 of 50 tasks are never solved by the control arm
and 4 are always solved.
