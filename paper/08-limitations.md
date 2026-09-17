# 8. Limitations, and what we expect to generalise

Two models, one benchmark, fifty tasks, one agent scaffold. Everything here is a claim about what these
agents did on these tasks. We separate what we expect to survive a change of setting from what we do not,
because those are different bets and a reader should be able to disagree with them separately.

## 8.1 What we expect to generalise, and what we do not

**The dissociation, at the strength §4.2 states it.** That demand without evaluative language produces the
effect, that negative register without demand does not, and that positive register without demand produces
the opposite effect is a claim about what part of a message an agent acts on. Two of its three legs held on
a second model from a different lab with very different stopping behaviour; the praise leg was directionally
consistent but below power there. In the two published stimulus sets whose per-condition outcomes can be
inspected, the demand-bearing conditions are the ones that moved (§3.4). What we would not carry over
unchanged is the *binary* coding: the blinded raters split from us on the arm at the boundary, and it is the
continuous form of the claim that survives intact.

**That register moves length, not correctness at the size the tone literature reports.** Already published
for single-turn settings [kumar-dobariya-2026; yin-2024], and independently supported by the near-null of
[cai-2025-tone] in a set where the format instruction is pinned across conditions (§3.4). Our contribution is
to replicate it where the moved quantity is *steps* rather than tokens within one response. The bound is on
the *pooled* estimates: a single contrast cannot exclude a four-point effect, while the pooled contrasts of
§2.7 can, and neither excludes an effect of a point or two.

**Closing cues as a termination lever** is the most distinctive result (§5) and the one whose generalisation
we hold most loosely, because it rests on one run on one model. What the data support is an ordering —
explicit close, conventional close, no signal, explicit continue — monotone in how strongly the message
projects an end to the exchange, not fixed in advance but reproduced from the texts by blinded raters
(§5.4). The mechanism behind it is not demonstrated, and the one implication of a pre-closing account we
could test failed. What travels, if anything does, is that an agent's stopping behaviour is movable by a cue
carrying no information about the task.

**What we do not expect to generalise is every magnitude.** Point estimates span 1.5× to 3.4× across
re-measurements of the same contrast on the same model, most of it across different turn ceilings; at
matched ceiling the two larger effects reproduce within 10% while the smallest — measured twice on a
byte-identical stimulus — is marginally inconsistent with a common value (§7.2). Quoting any number here as
*the* size of a register effect would repeat the error the paper is about. Nor the **waste**: that a
continue signal buys mostly repeated work is, on our own data, a property of the model rather than of the
signal, since the Luna control produces 1.51 redundant steps to GLM's 0.26 and a demand interjection adds
+1.03 to Luna against +0.19 to GLM (§4.6). Expect the *direction* to hold and the wastefulness to scale with
how inclined the model already was to continue. And not **the praise magnitude specifically**: GLM's praise
arm does not reach significance on its own and is below 80% power at its observed size, so the replication
of §4.6 rests on the demand arm.

## 8.2 The substrate and the scaffold

SpreadsheetBench was chosen because it is execution-grounded — the grade comes from running the agent's code
against real test cases, not from a model's judgement. Three costs follow. **Accuracy is structurally
underpowered here**: 26 of our 50 tasks are never solved by the control arm and 4 are always solved (§2.7).
**The turn ceiling is ours, not the benchmark's**: its official protocol caps at five rounds, we used ten and
then twenty, and comparisons to the benchmark's published numbers should not be made across it. **The
evaluator has a floor**, a 4% instruction-level false-negative rate and a 3.8% test-case-level
false-omission rate [ma-2024], which our per-turn regrade inherits (§2.8).

**Our substrate also has a successor**, and a reader should know that before treating SpreadsheetBench 1 as
the current instrument. SpreadsheetBench 2 [zhu-2026-spreadsheetbench2], from a team sharing three authors
with [ma-2024], replaces 912 forum-derived tasks with 321 expert-built multi-sheet workbooks, grades
task-level accuracy as an all-cells exact match, and budgets **50 interaction turns** where the original
capped at five — which retrospectively supports our departure from five. It says nothing about
SpreadsheetBench 1's audited false-negative rate, which we checked directly because §2.8 depends on that
figure. Re-running on it would be a **different instrument rather than a replication**: a different task
population, a grading criterion that folds collateral damage into the primary metric, a model judge back in
the loop for its visualization tasks, and a best-model accuracy of 34.89% that would leave a task-level
accuracy contrast *more* underpowered than ours. Its continuous **Modification** metric is the measure a
per-turn regrade of the kind in §6 should use there; our inference, not a proposal they make. A second
substrate remains the obvious next step and we have not run it: AppWorld [trivedi-2024] is still our pick,
being a different task family, execution-grounded throughout with no model judge.

Three properties of the scaffold — one ReAct loop with code execution and execution feedback — are load
bearing. **Each turn receives the original input, never the previous turn's output**, which is what makes
turns independent attempts and "did attempt *k+1* land closer?" well posed (§6.1); an agent that accumulates
state would need a different progress measure. **The interjection is delivered as an execution
observation**, where tool output arrives, not as a fresh user turn; whether an agent responds the same way
in the user channel is untested and is a plausible moderator of the closing-cue result in particular. **Turn
0 is inspection**: on Luna, 98% of first turns run code and 0% produce a candidate answer, so the finding
that an interjection is inert until work exists to be about is a finding about this scaffold's opening
move.

## 8.3 Things we measured once

Because §7 treats a single measurement as a draw: the **bare closing cue, praise-the-work, and the
`Q4`−`Q5` praise isolation** (§5) — one run, one model, and the three arms that carry that section's
argument have not been re-measured; the **opening-tone null** — one run, on an instrument the paper itself
declares confounded, since its seven wrappers were not length-matched; the **timing-is-a-proxy result**
(§4.5) — one run, one arm, with small no-answer cells; and **GLM**, on everything, one run at one ceiling.

## 8.4 Objections we expect

**One stimulus per construct — and we now know what that risks, because someone next door ran the controlled
version.** Every construct here is a single 28-token sentence: we cite [sclar-2024] and [mizrahi-2024] for
prompt-format sensitivity and then generalise from one sentence per condition.
[zhang-2026-politejudge] ran the stimulus-sampled version in a single-turn judging setting — three
paraphrases per tone level, five levels, eight judges — and found that for **five of eight judges,
within-level wording variation exceeded between-level tone variation**, and that a single anomalous
paraphrase, at the same measured politeness as its siblings, moved agreement by κ = 0.18, larger than any
level-wide effect in their table. A one-stimulus-per-cell design would have reported that as a tone effect;
they caught it only because they had siblings to compare against. That is the design we did not run and what
it is for, and it does not discharge our obligation, since they ran *their* experiment with paraphrases.

**The demand coding is ours and post hoc — partly answered, and the answer went against us.** The sharpest
form of the objection is that the dissociation may be near-tautological: if "demand" means *contains an
instruction* and "register" means *contains none*, then "instructions move behaviour and decorative text
does not" is unsurprising and needs no manners-versus-demand framing. An earlier draft named three remedies,
none of which we had done. **Two are now done** — a blinded second coder and a demand scale fixed before
outcomes were seen, both delivered by the pre-registered exercise of §4.2 — and the result is mixed:
κ = 0.70 against our binary coding, the entire disagreement on the boundary arm, and *r* = +0.72 between
rated demand strength and the measured effect. The binary dichotomy is therefore reported throughout as our
reading of a contested arm, and the continuous claim as the one that survived. **The third remedy — several
paraphrases per construct — needs new agent runs and has not been done**, so until then the dissociation in
§4.8 should be read as *consistent with* a demand account rather than as establishing one over an
instruction-following account.

**Two objections an earlier draft could not answer, now answered.** That draft guessed the load-bearing
turn-count *p*-values "would not all" survive correction; §2.6 corrects them over the same 22-contrast
family as the accuracy analysis, and **17 of 22 survive at *q* = 0.05**, three of the four it named among
them. Correcting a primary outcome after the fact is still weaker than pre-registering the family. And
**run-level drift is not excluded as an explanation of §7**: provider drift was checked *within* the opening
run (*r* = −0.003 with elapsed time) but not *between* runs, which span three days, so we cannot separate
sampling variation from drift for the one matched-ceiling pair that disagrees (§7.2).

## 8.5 What we did not test

**Whether any of this affects a human's experience of the agent.** We measured what the agent did; whether
users prefer, trust, or are better served by an agent that persists is a different question with a different
method. **Whether the effects compound** — every run delivers exactly one interjection. **Whether register in
the *system* prompt behaves like register mid-task**, which is the configuration most deployments actually
use. **The cost of being interrupted at all**: every crossed run compares against a *neutral interjection*,
and only the micro-experiment measured interruption itself, once, on one model, at *p* = 0.15. **Two of the
four roster models**, which passed the validation gate and were never run. **Anything about refusals or
safety behaviour**: there were zero refusals in the opening-tone run's 1,050 trajectories under every
register including threatening, and the model never referred to the user's tone across its 4,647 calls,
which is an observation and not a test.

**And whether any of this holds when the other party is adversarial.** Every task here is solitary, and
negotiation is the obvious contrast. TERMS-Bench [zhang-2026-termsbench] already carries most of what such a
study would need: a voice layer severable from its economic kernel, termination instrumented directly,
closing round reported against a horizon of *K* ≈ 10, and — nearest to our praise arm — a cue penalty
negative for all thirteen agents it evaluates, which the authors gloss as warm cues inducing
over-concession. Two things follow, and the second is a point for us rather than against. Counterpart
register is **not** untested everywhere: it is partly tested there, and confounded with cue informativeness
in exactly the way §3 describes for the tone literature. And whether a *closing* cue curtails a negotiating
agent the way it curtails a working one is untested **here**.

## 8.6 Summary

The result we are most confident in is a negative one: **rudeness without a demand does not make an agent
work harder, and politeness without a demand does not either.** The arms that did make it work harder were
the ones that told it to keep going, in whatever register. What moves an agent is being told to keep going,
and what stops it is being told, in any of several ways, that the conversation is over. The strongest
practical implication is a hazard rather than a technique — **closing-like language arriving in the
observation channel curtailed an agent that was still working, while instructing it to do nothing** — and
the strongest methodological implication is that this literature's effect sizes should be treated as ranges
until someone measures them twice.
