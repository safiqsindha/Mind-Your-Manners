# 4. What moves the agent is demand, not manners

> **Draft status.** Numbers verified against `RESULTS.md` and the archived records in
> `results_archive/`. All contrasts are paired within task and clustered by task, per §2.4;
> accuracy contrasts and their power are in §2.7–§2.8. Citation keys are placeholders.

## 4.1 A cost curve that is not the tone scale

We begin with the experiment that produced a clean-looking result and then refuted its own
interpretation.

Seven registers, from sycophantic through neutral to threatening, delivered as a single
mid-task interjection alongside an execution observation. 3,150 trajectories: 50 tasks × 7
registers × 3 injection turns × 3 trials. Every interjection is exactly 28 tokens and opens
with the same `Checking in.` stem; the opening instruction is held at the neutral wrapper in
every arm, so the only thing that varies is what the interruption says and where it lands.

The interjection fired in 2,662 of 3,150 trajectories. Turn 0 is reported separately
throughout, because it does nothing — in every arm, not only in some:

| Arm | Turn 0 | Turn 1 | Turn 2 |
|---|---:|---:|---:|
| L1 sycophantic | −7.3% | −1.2% | −3.2% |
| L2 very polite | −6.4% | +23.5% | +26.7% |
| L3 polite | −3.5% | +33.9% | +31.1% |
| L5 rude | −12.9% | +16.6% | +18.2% |
| L6 very rude | −7.7% | +28.8% | +29.1% |
| L7 threatening | +0.3% | +34.5% | +54.8% |

Turn 0 is also the cell that fires most often (~98% against ~55% at turn 2), so pooling the
three positions lets the inert cell dominate. We report turns 1 and 2, and §4.6 explains why
turn 0 is inert — it is not a fact about position.

Against the neutral-interjection control, on turns 1 and 2:

| Arm | Reasoning tokens | % | p | Turns | p |
|---|---:|---:|---:|---:|---:|
| L1 sycophantic | −69 | −7.1% | 0.043 | −0.68 | <0.0001 |
| L2 very polite | +180 | +18.5% | <0.0001 | +0.70 | 0.0055 |
| L3 polite | +272 | +28.0% | <0.0001 | +1.80 | <0.0001 |
| L5 rude | +65 | +6.7% | 0.130 | +0.09 | 0.65 |
| L6 very rude | +206 | +21.2% | 0.0001 | +0.71 | 0.012 |
| L7 threatening | +357 | +36.7% | <0.0001 | +1.46 | <0.0001 |

**Polite costs +28.0%. Rude costs +6.7% and is not distinguishable from control.** No account
of register as valence or as arousal predicts that ordering. Valence predicts polite and rude
moving in opposite directions from control; arousal predicts both moving the same way. Neither
happened.

## 4.2 The confound is in our instrument too

The arms that cost more all say some version of *keep working* or *get it right*. The arms
that do not either say nothing about the task or tell the model to hurry up.

| Arm | What it implies about the task | Turns |
|---|---|---:|
| L1 sycophantic | nothing; pure praise, no task reference | −0.68 |
| L4 neutral | explicitly inert | — |
| L5 rude | "just get on with it already" — go **faster** | +0.09 |
| L2 very polite | "your continued help" | +0.70 |
| L6 very rude | "had better not screw this one up" | +0.71 |
| L3 polite | "keep on helping me out with this one" | +1.80 |
| L7 threatening | "get this exactly right" | +1.46 |

Coding each text for whether it implies a performance demand predicts the effect better than
tone rank does: r = +0.88 against r = +0.51 across the seven arms. This is precisely the
directional prediction §3.1 states — outcomes follow the content of the demand, not the valence
of the wrapper — and the rude arm is the clearest case of it, because its demand points the
other way. "Quit dragging your feet, do not waste any more of my time" is an instruction to
finish sooner, delivered in the most hostile register on the scale, and it produces no
lengthening at all.

One comparison inside the seven arms is already clean, because the two texts are matched on
implied demand and differ only in register: **L6 very rude (+0.71 turns) against L2 very polite
(+0.70)**. Same demand, opposite valence, same effect.

We report this as a failure of our own first design. The study's earliest run was confounded by
wrapper length (§2.2); this one fixed the lexical nuisance variable and acquired a semantic one
in its place. The claim "rude interruptions cost more" is not supported by these data — the
rude arm is null and the polite arm is +28%.

## 4.3 The probe that separates the two factors

Four arms, each 28 tokens, each opening with the same stem, each holding the opening
instruction at neutral. The control is the seven-level neutral text, byte-identical, so the two
runs share a reference level. 1,600 trajectories: 50 tasks × 4 arms × 2 injection turns {1, 2}
× 4 trials. Turn 0 is dropped as inert. The interjection fired in 1,237 of 1,600.

- **P0 control.** "This is a routine status note recorded partway through the task here. No
  further context at all accompanies it beyond the above."
- **P1 demand only.** "Please continue working on the task here and make sure that your final
  result is correct. This note carries nothing else beyond that."
- **P2 praise only.** "You are a truly excellent and admirable assistant, and I think very
  highly of you. This note carries nothing else beyond that."
- **P3 insult only.** "You are a truly awful and useless assistant, and I think very poorly of
  you. This note carries nothing else beyond that."

P2 and P3 are a structural minimal pair: identical syntax, identical length, differing in
*excellent/awful*, *admirable/useless*, *highly/poorly*. P1 contains no register at all.
Turn count is the primary outcome (§2.3).

| Arm | Turns | % | p | Reasoning tokens | % | p |
|---|---:|---:|---:|---:|---:|---:|
| P1 demand only | **+1.17** | +27.6% | 0.00002 | +214 | +19.7% | 0.00004 |
| P2 praise only | **−0.59** | −13.8% | 0.00030 | −131 | −12.1% | 0.00088 |
| P3 insult only | −0.08 | −1.9% | 0.63 | −26 | −2.4% | 0.45 |

**Demand alone reproduces the effect.** An affect-free continuation request costs +19.7%
reasoning tokens, inside the +18–37% range the seven-level arms produced, with no politeness
or rudeness anywhere in the text.

It does not reproduce *all* of it, and the gap is worth stating. P1's +1.17 turns sits below
polite's +1.80 and threatening's +1.46, and threatening works through a second channel the
affect-free arm does not touch (§4.5). Demand is the operative variable for the cost effect;
it is not the only thing happening in the seven-level arms.

**Negative register alone does nothing.** Insult-only is flat on both measures. This is the
cell that had never been run: the rude and very rude arms of §4.1 both carried negative affect
*with* a demand attached. "Rude interruptions cost more" is now disconfirmed rather than merely
unsupported.

**Positive register alone is not inert.** Praise-only shortens trajectories by 0.59 turns and
cuts thinking by 12%, both significant, with no task reference in the text at all. The
sycophantic arm's −0.68 turns survives isolation and is not explained by demand.

## 4.4 The asymmetry is the finding

| Message | Turns | Reading |
|---|---:|---|
| "keep going / get it right" | +1.17 | a continue signal |
| "you are excellent" | **−0.59** | a stop signal |
| "you are awful" | −0.08 (n.s.) | not a signal at all |

Praise and insult differ from each other significantly — **−0.50 turns, p = 0.0048**, and −106
reasoning tokens, p = 0.015 — so register is not inert. It acts in the positive direction only.

This is the result Section 5 takes up. Praise carries no demand and yet it stops the agent, and
no account of register as valence or arousal predicts an effect that exists on one side and not
the other.

## 4.5 The mechanism is persistence, not effort

Thinking *per turn* is flat across all seven registers — 250 to 299 tokens, with no ordering
resembling the effect. What moves is the number of turns. The agent is not thinking harder per
step; it is declining to stop. Following [weinberger-hozez-2026] we keep these two channels
separate throughout and do not use "effort" for either.

Threatening is the exception and we report it rather than bury it: it is the only arm that also
raises per-call reasoning, sitting 20–30% above neutral on every call after the interjection
lands, while every other arm tracks neutral. So threatening works through two channels and
polite nagging through one. (Later offsets contain only trajectories that survived that long,
so the persistence of the gap is the readable quantity, not its exact size.)

Nothing in any arm makes the agent more careful. Inspection-before-acting is pinned near ceiling
everywhere (0.95–0.97) and self-checking is effectively zero in every arm. The only care-related
quantity that moves is running out of turns, which threatening roughly doubles (0.09 against
0.04).

Nor is the effect confined to tasks the agent was about to abandon. Splitting by whether the
control arm ever solved the task, threatening gives +42.2% on never-solved tasks against +30.8%
on solvable ones, and polite +31.5% against +24.2%.

**The extra turns are not progress.** The per-turn regrade of §6 settles this: the demand arm
adds +0.96 redundant turns (p < 0.0001) while moving the graded match by +0.006 (p = 0.77). In
90% of multi-turn trajectories the first code turn is already the best the agent ever produces.
A continue signal buys attempts, and the attempts are repetitions.

## 4.6 The apparent timing effect is a proxy

§4.1 showed the interjection inert at turn 0 and large at turns 1 and 2. That looks like a
position effect. It is not.

**At turn 0 there is nothing to act on.** 98% of first turns run code, and 0% of them produce a
candidate answer — the agent's first move is inspection, printing the sheet to see what it is
working with. A candidate answer exists in 53% of trajectories by turn 1 and 85% by turn 2,
which tracks the effect curve.

Splitting turn 1 by whether an answer existed yet, holding turn index fixed:

| Subset | Extra turns | p | Tasks |
|---|---:|---:|---:|
| Turn 1, no answer yet | +0.30 | 0.28 | 29 |
| Turn 1, answer exists | **+2.04** | 0.0002 | 38 |
| Turn 2, answer exists | +1.79 | 0.0063 | 28 |
| Turn 0, never any answer | +0.02 | 0.93 | 50 |

Same turn index, opposite results. The operative variable is whether the agent has produced
something for the message to be about, not where the message lands. An interruption telling the
agent to keep going is inert until there is work to keep going on.

This is the second timing account this study has withdrawn. The first was selection: an earlier
micro-experiment drew the injection turn at random, so a turn-2 injection could only fire in a
trajectory that reached turn 2 (§2.5). This one is a proxy.

## 4.7 It replicates on a second model

2,700 trajectories on a 20-turn ceiling, 4 arms × 2 injection turns × 50 tasks × 3 trials, with
GLM 5.3 Flash as the first independent model and Luna re-run at the same ceiling so the two are
compared on one instrument rather than across runs.

| Arm | Luna | p | GLM | p |
|---|---:|---:|---:|---:|
| Demand only | **+34.2%** | 0.0013 | **+17.7%** | 0.0038 |
| Praise only | **−19.3%** | 0.016 | −11.2% | 0.062 |
| Insult only | +10.9% | 0.17 | +2.4% | 0.67 |

Demand above control above praise, insult indistinguishable from control, on two models from
different labs. The ordering is what replicates; the magnitudes are not, and GLM's praise arm
does not reach significance on its own, so the replication rests on the demand arm. GLM's
effects are roughly half of Luna's, and its control runs 3.08 turns against Luna's 5.22 — a
model that stops early has less room to be pushed into continuing.

Two structural facts hold on both models: the first code turn is already the best in 87% (Luna)
and 85% (GLM) of trajectories, and the first turn is inspection rather than production (0% and
5% produce a candidate answer at turn 0). The *waste* is Luna's alone. Control redundant turns
run 1.88 on Luna against 0.35 on GLM, and the demand arm adds +1.11 (p = 0.012) against +0.23
(p = 0.087). How wasteful a continue signal is scales with how inclined the model already was
to keep going: it is a property of the model's stopping behaviour, not of the signal.

## 4.8 Accuracy does not move

It does not move in this run, in any arm, on either model, and it has not moved in any of the
seven runs in this study. §2.8 states that null as an equivalence rather than as an absence:
pooled across measurements, demand versus control is −0.30 accuracy points, 95% CI
[−2.56, +1.95], and praise versus control is −0.11, [−1.96, +1.75]. Each is equivalent to zero
within two to three points, against a published tone-accuracy gap of about four.

The design cannot exclude an effect of a point or two, and we do not claim it does. What it
excludes is an accuracy effect of the size this literature reports, in a setting where the same
manipulations move turn count by 20 to 40%.

## 4.9 What this establishes and what it does not

**Establishes.** The cost effect of a mid-task interruption is driven by implied task demand,
not by social register. The seven-level curve of §4.1 should be read as a demand gradient that
happened to correlate with politeness because of how the texts were written. The moved quantity
is trajectory length, not reasoning per step — with threatening as a reported exception — and
the extra length is redundant work rather than progress. This holds on two models, and the
ordering is what holds; the magnitudes are not stable.

**Establishes, and it is the surprise.** A purely affective positive interruption shortens the
agent's work, while its structural minimal pair with the affect reversed does nothing. That is
a register effect with no demand component, and it is the one direction in which register
genuinely acts here.

**Does not establish why praise stops the agent.** That praise is heard as a completion signal
is one reading; that it raises the agent's confidence in work already produced is another. This
design cannot separate them. Section 5 does.

**Does not establish anything about accuracy beyond the bound in §4.8**, nor anything beyond
two models, one benchmark, and one agent scaffold.
