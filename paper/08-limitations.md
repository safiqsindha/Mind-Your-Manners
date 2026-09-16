# 8. Limitations, and what we expect to generalise

> **Draft status.** Cross-references are to the sections named. Citation keys resolve to §9.

## 8.1 The short version

Two models, one benchmark, fifty tasks, one agent scaffold. Everything in this paper is a claim
about what these agents did on these tasks. We separate below what we expect to survive a change
of setting from what we do not, because those are different bets and a reader should be able to
disagree with them separately.

## 8.2 What we expect to generalise

**The dissociation.** That demand without evaluative language produces the effect, that negative
register without demand does not, and that positive register without demand produces the opposite
effect (§4.9) is a claim about what part of a message an agent acts on. Two of its three legs held
on a second model from a different lab with very different stopping behaviour; the praise leg was
directionally consistent but below power there (§4.7, §8.3). And in the two published stimulus
sets whose per-condition outcomes can be inspected, the demand-bearing conditions are the ones
that moved (§3.6). We would be surprised if it were specific to spreadsheets.

**That register moves length, not correctness at the size the tone literature reports.** This is
already published for single-turn settings [kumar-dobariya-2026; yin-2024], and our contribution
is to replicate it where the moved quantity is *steps* rather than tokens within one response. Two
independent lines of evidence converging is a reasonable basis for expecting it elsewhere. Note
the bound, and that it is a bound on the *pooled* estimates: a single contrast here cannot
exclude a four-point effect (§2.7), while the pooled contrasts of §2.8 can. Neither excludes an
effect of a point or two.

**Closing cues as a termination lever.** This is the most distinctive result (§5) and the one
whose generalisation we hold most loosely, because it rests on one run on one model. What the data
support is an ordering — explicit close, conventional close, no signal, explicit continue —
monotone in how strongly the message projects an end to the exchange. The mechanism behind that
ordering is not demonstrated, and the one implication of a pre-closing account that we could test
failed (§5.4). What travels, if anything does, is that an agent's stopping behaviour is movable by
a cue carrying no information about the task.

## 8.3 What we do not expect to generalise

**Every magnitude.** §7 is explicit: point estimates in this study span 1.5× to 3.4× across
re-measurements of the same contrast on the same model, most of it across different turn ceilings.
At matched ceiling the two larger effects reproduce within 10% while the smallest is marginally
inconsistent with a common value (§7.3). Quoting any number here as *the* size of a register
effect would repeat the error the paper is about.

**The waste.** That a continue signal buys mostly repeated work is, on our own data, a property of
the model rather than of the signal. The Luna control produces 1.51 redundant steps to GLM's 0.26,
and a demand interjection adds +1.03 to Luna against +0.19 to GLM (§4.7). A model that stops early
has little repetition available to be pushed into. Expect the *direction* to hold and the
wastefulness to scale with how inclined the model already was to continue.

**The praise magnitude specifically.** GLM's praise arm does not reach significance on its own
(p = 0.062) and is below 80% power at its observed size (§2.7). The replication of §4.7 rests on
the demand arm.

## 8.4 The substrate

SpreadsheetBench was chosen because it is execution-grounded — the grade comes from running the
agent's code against real test cases, not from a model's judgement — and because its tasks are
real workbook problems rather than synthesised ones. That grounding is the benefit; three costs
follow from it.

**Accuracy is structurally underpowered here.** 26 of our 50 tasks are never solved by the control
arm and 4 are always solved, so for more than half the sample the per-task accuracy difference is
pinned at zero whatever the manipulation does (§2.7). This is why the accuracy null is stated as
an equivalence against a pre-specified bound rather than as a measured zero, and why turn count is
the primary outcome.

**The turn ceiling is ours, not the benchmark's.** SpreadsheetBench's official multi-round
protocol caps at five rounds; we used ten and then twenty. §6.6 defends twenty empirically — the
median turn at which the best answer is first reached is 2, and 98.3% of trajectories have peaked
by turn 10 — but the choice is ours and comparisons to the benchmark's published numbers should
not be made across it.

**The evaluator has a floor.** Its own audit reports a 4% instruction-level false-negative rate
and a 3.8% test-case-level false-omission rate [ma-2024]. Our per-turn regrade inherits it (§2.10).

**A second substrate is the obvious next step and we have not run it.** AppWorld
[trivedi-2024] is the candidate: its stock evaluator keeps per-requirement pass and fail lists, so
a per-turn "fraction of unit tests passed" measure can be computed without modifying it — the same
instrument as §6, on a different task family, at roughly $0.70 per trajectory. One piece of
engineering it would require: what that benchmark treats as collateral damage is not a separate
metric but additional entries in the same test battery, so separating it is work.

## 8.5 The scaffold

One agent loop, ReAct with code execution and execution feedback. Three properties of it are load
bearing and a different scaffold could change any of them.

**Each turn receives the original input, never the previous turn's output.** This is what makes
turns independent attempts and makes "did attempt *k+1* land closer?" well posed (§6.2). An agent
that accumulates state would need a different progress measure, and might well show real
improvement across turns where ours does not.

**The interjection is delivered as an execution observation.** It arrives where tool output
arrives, not as a fresh user turn. Whether an agent responds the same way to a message in the user
channel is untested and is a plausible moderator of the closing-cue result in particular.

**Turn 0 is inspection.** On Luna, 98% of first turns run code and 0% produce a candidate answer;
on GLM, 90% and 5% (§4.6, §4.7). The finding that an interjection is inert until work exists to be
about is, on our data, a finding about this scaffold's opening move.

## 8.6 Things we measured once

Because §7 treats a single measurement as a draw:

- The **bare closing cue, praise-the-work, and the Q4−Q5 praise isolation** (§5) — one run, one
  model. Two arms of that run were later re-measured and replicated in direction (§7.2); the three
  that carry the section's argument have not been.
- The **opening-tone null** (§2.6) — one run, and on an instrument the paper itself declares
  confounded: its seven wrappers were not length-matched, and its reference level carried an extra
  task instruction that triples the rate of zero-turn trajectories (§2.2). The length-matching fix
  was applied only as a 150-trajectory re-run of that one arm; the seven-wrapper scale was never
  re-run matched. Its interval excludes a 44%-scale effect, which is stronger than a bare null, but
  the instrument is the weakest in the study.
- The **timing-is-a-proxy result** (§4.6) — one run, one arm, and its no-answer cells are small
  (31 tasks at turn 1, 8 at turn 2).
- **GLM**, on everything. One run at one ceiling.

## 8.7 Four objections we expect, and do not have answers to

**One stimulus per construct.** Every construct in this paper — demand, praise, insult, closing
cue, "work remains" — is a single 28-token sentence. We cite [sclar-2024] and [mizrahi-2024] for
prompt-format sensitivity and then generalise from one sentence per condition. A stimulus-sampling
design, several paraphrases per construct, is the right version of this experiment and we did not
run it. The length-matching and the shared `Checking in.` stem control *within* a comparison; they
do nothing about whether our one praise sentence is representative of praise.

**The demand coding is ours and post hoc.** §4.2's coding of the seven registers was made after
seeing the effects — we say so there — and §3's coding of other papers' stimuli has no second
rater. The probe of §4.3 is what tests the construct rather than asserting it, but it tests it on
texts we wrote to embody our own coding.

**The primary outcome is not corrected for multiplicity.** §2.6 corrects the opening run's
twelve-outcome trend family and the 22-contrast accuracy family. The turn-count contrasts — the
primary outcome — are uncorrected, and several load-bearing p-values are not large: GLM praise at
0.062, stage-1 Luna praise at 0.017, L2 very polite at 0.0055, L6 very rude at 0.012. The largest
effects would survive any reasonable correction; these would not all.

**Run-level drift is not excluded as an explanation of §7.** Provider drift was checked *within*
the opening run (r = −0.003 with elapsed time) but not *between* runs, which span three days. The
roster is provider-pinned and the served provider was asserted on every call, but temperature 0 is
not deterministic on any roster model (§2.2), and we cannot separate sampling variation from drift
for the one matched-ceiling pair that disagrees (§7.3).

## 8.8 What we did not test

**Whether any of this affects a human's experience of the agent.** We measured what the agent did.
Whether users prefer, trust, or are better served by an agent that persists is a different
question with a different method.

**Whether the effects compound.** Every run delivers exactly one interjection. An agent nagged
repeatedly, or praised repeatedly, might habituate, escalate, or neither.

**Whether register in the *system* prompt behaves like register mid-task.** Our opening-tone null
(§2.6) is about a register-varied instruction at the top of the user turn, not about a persona set
in the system prompt, which is the configuration most deployments actually use.

**The cost of being interrupted at all.** Every crossed run compares an interjection against a
*neutral interjection*, so the effects throughout are register effects, not interruption effects.
Only the micro-experiment measured interruption itself — 3.47 to 4.11 turns under a neutral
interruption, +51 reasoning tokens, p = 0.15 — once, on one model.

**Two of the four roster models.** DeepSeek and Qwen passed the n=100 validation gate and were
never run. "Two models from different labs" describes what the budget reached, not a design
choice; the four-model roster was specified and then not executed.

**Whether any of this holds when the other party is adversarial.** Every task here is solitary:
the agent works on a workbook, and the only other voice in the transcript is ours. Negotiation
is the obvious contrast, and it is now instrumented — TERMS-Bench sets out to diagnose
negotiation agents beyond deal rate [zhang-2026-termsbench]. Whether a closing cue curtails a
negotiating agent the way it curtails a working one, or whether a counterpart's register does
what a user's does, is untested here and would need an outcome measure of that kind rather than
ours.

**Anything about refusals or safety behaviour.** There were zero refusals in the opening-tone
run's 1,050 trajectories under every register including threatening, and the model never referred
to the user's tone across its 4,647 calls. Refusal counts for the interjection runs are recorded
but were not analysed. That is an observation, not a test.

## 8.9 Summary

The result we are most confident in is a negative one: **rudeness without a demand
does not make an agent work harder, and politeness without a demand does not either.** The arms
that did make it work harder were the ones that told it to keep going, in whatever register. What
moves an agent is being told to keep going,
and what stops it is being told, in any of several ways, that the conversation is over. The
strongest practical implication is a hazard rather than a technique — a pleasantry can end an
agent's work — and the strongest methodological implication is that this literature's effect sizes
should be treated as ranges until someone measures them twice.
