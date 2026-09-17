# 7. Limitations

Two models, one benchmark, fifty tasks, one agent scaffold.

## 7.1 What we expect to generalise, and what we do not

**The dissociation, at the strength §4.2 states it.** Two of its three legs held on a second model
from a different lab with very different stopping behaviour; the praise leg was directionally
consistent but below power there. What we would not carry over unchanged is the *binary* coding: the
blinded raters split from us on the arm at the boundary, and it is the continuous form of the claim
that survives intact.

**That register moves length, not correctness at the size the tone literature reports.** Already
published for single-turn settings [kumar-dobariya-2026; yin-2024], and independently supported by
[cai-2025-tone] (§3.4). Our contribution is to replicate it where the moved quantity is *steps*
rather than tokens within one response. The bound is on the *pooled* estimates: a single contrast
cannot exclude a four-point effect, while the pooled contrasts of §2.5 can, and neither excludes an
effect of a point or two.

**Closing cues as a termination lever** is the most distinctive result and the one whose
generalisation we hold most loosely, because it rests on one run on one model. What the data support
is an ordering — explicit close, conventional close, no signal, explicit continue — monotone in how
strongly the message projects an end to the exchange, and reproduced from the texts by blinded
raters. The mechanism is not demonstrated. What travels, if anything does, is that an agent's
stopping behaviour is movable by a cue carrying no information about the task.

**Not every magnitude.** Point estimates span 1.5× to 3.4× across re-measurements of the same
contrast on the same model, most of it across different turn ceilings; at matched ceiling the two
larger effects reproduce within 10% while the smallest — measured twice on a byte-identical stimulus
— is marginally inconsistent with a common value (Appendix C.1). Nor the **waste**: that a continue
signal buys mostly repeated work is, on our own data, a property of the model rather than of the
signal (§4.4).

## 7.2 The substrate and the scaffold

SpreadsheetBench was chosen because it is execution-grounded — the grade comes from running the
agent's code against real test cases, not from a model's judgement. Three costs follow. **Accuracy
is structurally underpowered here**: 26 of our 50 tasks are never solved by the control arm and 4
are always solved. **The turn ceiling is ours, not the benchmark's**, so comparisons to the
benchmark's published numbers should not be made across it. **The evaluator has a floor**: a 4%
instruction-level false-negative rate and a 3.8% test-case-level false-omission rate with a
false-discovery rate of 0% [ma-2024], which our per-turn regrade inherits; on paired contrasts the
task-level component cancels, leaving an attenuation of at most about 0.96 that cannot change a
sign. Our substrate also has a successor, SpreadsheetBench 2 [zhu-2026-spreadsheetbench2], which
budgets **50 interaction turns** where the original capped at five — retrospectively supporting our
departure from five — but re-running there would be a **different instrument rather than a
replication**: a different task population, a grading criterion that folds collateral damage into
the primary metric, a model judge back in the loop for its visualization tasks, and a best-model
accuracy of 34.89% that would leave a task-level accuracy contrast *more* underpowered than ours.
AppWorld [trivedi-2024] is our pick for a second substrate; we have not run it.

Three properties of the scaffold are load bearing. **Each turn receives the original input, never
the previous turn's output**, which is what makes turns independent attempts; an agent that
accumulates state would need a different progress measure. **The interjection is delivered as an
execution observation**, where tool output arrives, not as a fresh user turn; whether an agent
responds the same way in the user channel is untested, and is a plausible moderator of the
closing-cue result in particular. **Turn 0 is inspection**: 98% of first turns run code and 0%
produce a candidate answer, so the finding that an interjection is inert until work exists to be
about is a finding about this scaffold's opening move.

## 7.3 Objections we expect

**One stimulus per construct.** Every construct here is a single 28-token sentence: we cite
[sclar-2024] and [mizrahi-2024] for prompt-format sensitivity and then generalise from one sentence
per condition. [zhang-2026-politejudge] ran the stimulus-sampled version in a single-turn judging
setting and found that for **five of eight judges, within-level wording variation exceeded
between-level tone variation** (§3.4); a one-stimulus-per-cell design would have reported that as a
tone effect. Several paraphrases per construct needs new agent runs and has not been done, so the
dissociation of §4.5 should be read as *consistent with* a demand account rather than as
establishing one over an instruction-following account.

**The demand coding is ours and post hoc.** The sharpest form of the objection is that the
dissociation may be near-tautological: if "demand" means *contains an instruction* and "register"
means *contains none*, then "instructions move behaviour and decorative text does not" is
unsurprising. Two remedies are now done — a blinded second coder and a demand scale fixed before
outcomes were seen (§4.2) — and the result went against us: κ = 0.70 on the binary coding, the
entire disagreement on the boundary arm.

**Run-level drift is not excluded.** Provider drift was checked *within* the opening run
(*r* = −0.003 with elapsed time) but not *between* runs, which span three days, so we cannot
separate sampling variation from drift for the one matched-ceiling pair that disagrees.

## 7.4 What we did not test

**Whether any of this affects a human's experience of the agent.** We measured what the agent did;
whether users prefer, trust, or are better served by an agent that persists is a different question
with a different method. **Whether the effects compound** — every run delivers exactly one
interjection. **Whether register in the *system* prompt behaves like register mid-task**, which is
the configuration most deployments actually use. **The cost of being interrupted at all**: only the
micro-experiment measured interruption itself, once, at *p* = 0.15. **Two of the four roster
models**, which passed the validation gate and were never run. **Anything about refusals or safety
behaviour**: there were zero refusals in the opening-tone run's 1,050 trajectories under every
register including threatening, and the model never referred to the user's tone across its 4,647
calls, which is an observation and not a test. **And whether any of this holds when the other party
is adversarial.** Every task here is solitary. TERMS-Bench [zhang-2026-termsbench] carries most of
what a negotiation study would need, and — nearest to our praise arm — reports a cue penalty
negative for all thirteen agents it evaluates, which the authors gloss as warm cues inducing
over-concession; counterpart register is partly tested there, and confounded with cue
informativeness in exactly the way §3 describes for the tone literature.

## 7.5 Summary

The result we are most confident in is a negative one: **rudeness without a demand does not make an
agent work harder, and politeness without a demand does not either.** The arms that did make it work
harder were the ones that told it to keep going, in whatever register. What stops it is being told,
in any of several ways, that the conversation is over. The strongest practical implication is a
hazard rather than a technique — **closing-like language arriving in the observation channel
curtailed an agent that was still working, while instructing it to do nothing** — and the strongest
methodological implication is that this literature's effect sizes should be treated as ranges until
someone measures them twice.
