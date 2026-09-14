# 9. Limitations, and what we expect to generalise

> **Draft status.** Cross-references are to the sections named. Citation keys are placeholders.

## 9.1 The short version

Two models, one benchmark, fifty tasks, one agent scaffold. Everything in this paper is a claim
about what these agents did on these tasks. We separate below what we expect to survive a change
of setting from what we do not, because those are different bets and a reader should be able to
disagree with them separately.

## 9.2 What we expect to generalise

**The dissociation.** That demand without evaluative language produces the effect, that negative
register without demand does not, and that positive register without demand produces the opposite
effect (§4.9) is a claim about what part of a message an agent acts on. It held on two models from
different labs with very different stopping behaviour, and the same confound is visible in four
other papers' materials across three paradigms (§3). We would be surprised if it were specific to
spreadsheets.

**That register moves length, not correctness.** This is already published for single-turn
settings [kumar-dobariya-2026; yin-2024], and our contribution is to replicate it where the moved
quantity is *steps* rather than tokens within one response. Two independent lines of evidence
converging is a reasonable basis for expecting it elsewhere.

**Closing cues as a termination lever.** This is the most distinctive result (§5) and also the one
whose generalisation we hold most loosely, because it rests on one model. But the mechanism it
implies — that an agent reads discourse structure about whether the exchange continues, not only
statements about task state — is not a fact about workbooks, and the bare closing cue producing
the largest effect in the study is hard to explain any other way.

## 9.3 What we do not expect to generalise

**Every magnitude.** §8 is explicit: point estimates in this study span 1.5× to 3.4× across
re-measurements of the same contrast on the same model. Quoting any number here as *the* size of a
register effect would repeat the error the paper is about.

**The waste.** That a continue signal buys mostly repeated work is, on our own data, a property of
the model rather than of the signal. The Luna control produces 1.88 redundant steps to GLM's 0.35,
and a demand interjection adds +1.11 to Luna against +0.23 to GLM (§4.7). A model that stops early
has little repetition available to be pushed into. Expect the *direction* to hold and the
wastefulness to scale with how inclined the model already was to continue.

**The praise magnitude specifically.** GLM's praise arm does not reach significance on its own
(p = 0.062) and is below 80% power at its observed size (§2.7). The replication of §4.7 rests on
the demand arm; we say so rather than let three rows in a table imply three replications.

## 9.4 The substrate

SpreadsheetBench was chosen because it is execution-grounded — the grade comes from running the
agent's code against real test cases, not from a model's judgement — and because its tasks are
real workbook problems rather than synthesised ones. Three consequences follow, two of them costs.

**Accuracy is structurally underpowered here.** 26 of our 50 tasks are never solved by the control
arm and 4 are always solved, so for more than half the sample the per-task accuracy difference is
pinned at zero whatever the manipulation does (§2.7). This is why the accuracy null is stated as
an equivalence against a pre-specified bound rather than as a measured zero, and why turn count is
the primary outcome.

**The turn ceiling is ours, not the benchmark's.** SpreadsheetBench's official multi-round
protocol caps at five rounds; we used ten and then twenty. §6.5 defends twenty empirically — the
median best turn among ceiling-bound trajectories is 2, and zero of 43 improvements occurred at
turn 15 or later — but the choice is ours and comparisons to the benchmark's published numbers
should not be made across it.

**The evaluator has a floor.** Its own audit reports a 4% instruction-level false-negative rate
and a 3.8% test-case-level false-omission rate [ma-2024]. Our per-turn regrade inherits it (§2.10).

**A second substrate is the obvious next step and we have not run it.** AppWorld
[trivedi-2024] is the candidate: its stock evaluator keeps per-requirement pass and fail lists, so
a per-turn "fraction of unit tests passed" measure can be computed without modifying it — the same
instrument as §6, on a different task family, at roughly $0.70 per trajectory. We flag one piece
of engineering it would require rather than imply it is free: what that benchmark treats as
collateral damage is not a separate metric but additional entries in the same test battery, so
separating it is work.

## 9.5 The scaffold

One agent loop, ReAct with code execution and execution feedback. Three properties of it are load
bearing and a different scaffold could change any of them.

**Each turn receives the original input, never the previous turn's output.** This is what makes
turns independent attempts and makes "did attempt *k+1* land closer?" well posed (§6.2). An agent
that accumulates state would need a different progress measure, and might well show real
improvement across turns where ours does not.

**The interjection is delivered as an execution observation.** It arrives where tool output
arrives, not as a fresh user turn. Whether an agent responds the same way to a message in the user
channel is untested and is a plausible moderator of the closing-cue result in particular.

**Turn 0 is inspection.** 98% of first turns run code and 0% produce a candidate answer (§4.6).
The finding that an interjection is inert until work exists to be about is, on our data, a finding
about this scaffold's opening move.

## 9.6 Things we measured once

Stated plainly, because §8's whole argument is that a single measurement is a draw:

- The **closing-cue result** (§5) — one run, one model. The contrasts within it are internally
  consistent and mutually constraining, but none has been re-measured.
- The **opening-tone null** (§1.3) — one run. Its interval excludes a published-size effect, which
  is a stronger claim than a bare null, but it has not been repeated.
- The **timing-is-a-proxy result** (§4.6) — one run, one arm, and its no-answer cells are small
  (31 tasks at turn 1, 8 at turn 2).
- **GLM**, on everything. One run at one ceiling.

## 9.7 What we did not test

**Whether any of this affects a human's experience of the agent.** We measured what the agent did.
Whether users prefer, trust, or are better served by an agent that persists is a different
question with a different method.

**Whether the effects compound.** Every run delivers exactly one interjection. An agent nagged
repeatedly, or praised repeatedly, might habituate, escalate, or neither.

**Whether register in the *system* prompt behaves like register mid-task.** Our opening-tone null
(§1.3) is about a tone-varied instruction at the top of the user turn, not about a persona set in
the system prompt, which is the configuration most deployments actually use.

**Anything about refusals or safety behaviour.** There were zero refusals in 1,050 trajectories
under every register including threatening, and the model never once referred to the user's tone
across 4,647 calls. That is an observation, not a test.

## 9.8 The honest summary

The result we are most confident in is a negative one: **being rude to an agent does not make it
work harder, and being polite does not either.** What moves an agent is being told to keep going,
and what stops it is being told, in any of several ways, that the conversation is over. The
strongest practical implication is a hazard rather than a technique — a pleasantry can end an
agent's work — and the strongest methodological implication is that this literature's effect sizes
should be treated as ranges until someone measures them twice.
