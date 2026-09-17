# Mind your manners? LLM-agent persistence tracks demand, not social register

**Authors.** *[to be completed]*

---

## Abstract

A widely-discussed result reports impolite prompts beating polite ones on multiple-choice questions.
That literature is almost entirely single-turn; deployed systems are agents that call tools, read
results, and decide whether to continue. We put a coding agent on 50 SpreadsheetBench tasks and
varied the social register of one 28-token interjection delivered mid-task. Interjections are
length-matched and share an opening stem, so being interrupted does not covary with what the
interruption says. **11,850 graded trajectories, two models from different labs.** **Demand, not
politeness, drives turn count:** an affect-free "please continue working on the task here and make
sure that your final result is correct" costs +1.17 turns, while a length-matched, syntactically
identical insult does not move it (−0.08 turns, 95% CI [−0.40, +0.24]). **Praise and closing cues
shorten trajectories; insult has no measurable effect:** a bare closing cue carrying no praise, no
evaluation and no task-state claim gives the largest reduction in the study, −1.44 turns. **No
accuracy effect survives correction or replication,** which we state as equivalence within ±4
accuracy points rather than as an absence. The implication is not lost correctness but altered
control flow: text in the agent's observation channel changed when it stopped, without instructing
it to.
