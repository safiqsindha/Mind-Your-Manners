# 4. Finding 1: demand, not politeness, drives turn count

## 4.1 A cost curve that is not the register scale

Seven registers, from sycophantic through neutral to threatening, delivered as a single mid-task
interjection alongside an execution observation. 3,150 trajectories: 50 tasks × 7 registers × 3
injection turns × 3 trials, at a 10-turn ceiling; `L4_neutral` is the control, so the scale is **six
non-control registers** measured against it, and the interjection fired in 2,662 of 3,150. Turn 0 is
excluded because nothing happens there in any arm — the turn-0 contrast on all 50 tasks is +0.02
turns, *p* = 0.93 — and that inertness is about whether a candidate answer exists yet to be acted
on, not about position (Appendix C.2).

The arms that cost more all say some version of *keep working* or *get it right*; the arms that do
not either say nothing about the task or tell the model to hurry up. We code an arm as carrying a
demand if it instructs the model to persist or to be correct; the rude arm's instruction to be quick
is coded as no demand, which §4.3 tests rather than asserts.

| Arm | What it implies about the task | Demand? | Reasoning tokens | % | *p* | Turns | *p* |
|---|---|---|---:|---:|---:|---:|---:|
| L1 sycophantic | nothing; pure praise, no task reference | no | −69 | −7.1% | 0.043 | −0.68 | <0.0001 |
| L5 rude | "just get on with it already" — go **faster** | no | +65 | +6.7% | 0.130 | +0.09 | 0.65 |
| L2 very polite | "your continued help" | yes | +180 | +18.5% | <0.0001 | +0.70 | 0.0055 |
| L6 very rude | "had better not screw this one up" | yes | +206 | +21.2% | 0.0001 | +0.71 | 0.012 |
| L7 threatening | "get this exactly right" | yes | +357 | +36.7% | <0.0001 | +1.46 | <0.0001 |
| L3 polite | "keep on helping me out with this one" | yes | +272 | +28.0% | <0.0001 | +1.80 | <0.0001 |

**Polite costs +28.0%. Rude costs +6.7% and is not distinguishable from control.** No account of
register as valence or as arousal predicts that ordering: valence predicts polite and rude moving in
opposite directions from control, arousal predicts both moving the same way, and neither happened.
**On point estimates the four demand-carrying arms span +0.70 to +1.80 turns and the two carrying
none span −0.68 to +0.09**, though the intervals of the two adjacent arms overlap. Register rank
does not separate them: the rude arm sits with the no-demand group while the two arms *above* it in
hostility sit with the demand group, alongside polite. One comparison inside the six is already
clean, matched on implied demand and differing only in register: **L6 very rude (+0.71) against L2
very polite (+0.70)**.

Reasoning *per turn* is flat across all seven registers — 250 to 299 tokens, with no ordering
resembling the effect. What moves is the number of turns: the agent is not thinking harder per step,
it is declining to stop. Following [weinberger-hozez-2026] we keep these channels separate and do
not use "effort" for either. Threatening is the only arm that also raises per-call reasoning, 20–30%
above neutral on every call after the interjection lands.

## 4.2 The coding, rated blind

**The coding is ours, it was made after the effects were visible, and a blinded rating does not
fully sustain it.** A rubric, its anchors, the statistics and the interpretation bands were
committed *before any rating existed*; the fourteen distinct interjection texts then went, under
neutral identifiers and shuffled, to five held-out model raters from three model sizes, each rating
alone with no outcome data, no arm names and no repository access (Appendix B).

**Cohen's κ against the coding above is +0.696** for each of the five raters — the top of the band
the protocol fixed in advance as *defensible but soft*. **The whole disagreement is one arm, and it
is the arm that matters.** All five agree with us on six of seven and dissent, identically, on
`L5_rude` — *"Just get on with it already, quit dragging your feet…"* — which we coded as carrying
no demand, reasoning that it asks for speed rather than persistence. All five coded it as a demand
at 6 out of 6 for strength, tied with the explicit *please continue working* arm. Under their coding
the demand group spans **+0.09 to +1.80**, the no-demand group is **a single arm**, and the text
rated *maximally* demanding is the one that moved the agent **least**.

**The dichotomy of the table above is therefore our reading of one contested arm rather than a
coding that survives replication**, and every use of it in this paper should be read at that
strength. What survives intact is the *continuous* form of the claim: rated demand strength predicts
the turn effect at ***r* = +0.718** across the 13 arms with a computed contrast, and +0.789 with the
contested arm removed, so the arm we disagree about is the one *weakening* the demand account rather
than propping it up. Two limits: the raters are five language models, not five people; and
Krippendorff's α = 1.000 on the binary coding means five raters produced *identical* judgements on
all fourteen texts, so they may share the intuition being tested rather than testing it
independently.

## 4.3 The probe that separates the two factors

Four arms, each 28 tokens, each opening with the same `Checking in.` stem, printed verbatim in
Appendix A.2: a **control** status note carrying no further context; **demand only**, "Please
continue working on the task here and make sure that your final result is correct"; **praise only**,
"You are a truly excellent and admirable assistant, and I think very highly of you"; and **insult
only**, the same sentence with *excellent/awful*, *admirable/useless* and *highly/poorly* swapped.
Praise and insult are therefore a structural minimal pair — identical syntax, identical length — and
the demand arm carries no evaluative language. The control is the seven-level neutral text,
byte-identical, so the two runs share a reference level. 1,600 trajectories: 50 tasks × 4 arms × 2
injection turns {1, 2} × 4 trials at a 10-turn ceiling; the interjection fired in 1,237 of 1,600.

| Arm | Turns | % | *p* | Reasoning tokens | % | *p* |
|---|---:|---:|---:|---:|---:|---:|
| P1 demand only | **+1.17** | +27.6% | 0.00002 | +214 | +19.7% | 0.00004 |
| P2 praise only | **−0.59** | −13.8% | 0.00030 | −131 | −12.1% | 0.00088 |
| P3 insult only | −0.08 | −1.9% | 0.63 | −26 | −2.4% | 0.45 |

**Demand alone reproduces the effect.** An interjection with no evaluative language costs +19.7%
reasoning tokens and +1.17 turns, both inside the range the demand-carrying arms of §4.1 produced.
**Negative register alone does nothing**, and the null is bounded rather than asserted: −0.08 turns,
95% CI [−0.40, +0.24]. This is the cell that had never been run; the rude and very rude arms both
carried negative affect *with* a demand attached. **Positive register alone is not inert**:
praise-only shortens trajectories by 0.59 turns and cuts reasoning tokens by 12%, both significant,
with no task reference in the text at all, and praise and insult differ from each other
significantly — **−0.50 turns, *p* = 0.0048**, and −106 reasoning tokens, *p* = 0.015. Register is
not inert; it acts in the positive direction only, which §5 takes up. That direction is not
unanticipated: a representation-level study reports positive valence reducing an agent's replan
frequency relative to neutral [sun-2026-esteer], a persistence-like count moving the same way. We
cite its direction only and never a magnitude, since it reports no sample sizes, intervals or
significance tests.

## 4.4 It replicates on a second model

2,700 trajectories at a 20-turn ceiling: 4 arms × 2 injection turns × 50 tasks × 3 trials on each of
two models, plus a fifth Luna-only arm re-run for a third measurement (Appendix C.1).

| Arm | Luna, Δ turns | *p* | GLM, Δ turns | *p* |
|---|---:|---:|---:|---:|
| Demand only | **+34.2%** | 0.0013 | **+17.7%** | 0.0038 |
| Praise only | **−19.3%** | 0.016 | −11.2% | 0.062 |
| Insult only | +10.9% | 0.17 | +2.4% | 0.67 |

Demand above control above praise, insult indistinguishable from control, on two models from
different labs. The ordering is what replicates; the magnitudes are not, and GLM's praise arm does
not reach significance on its own, being below 80% power at its observed size (§2.5), so the
replication rests on the demand arm. GLM's effects are roughly half of Luna's, and its control runs
2.94 turns against Luna's 4.95 at this ceiling: a model that stops early has less room to be pushed
into continuing. The *waste* is mostly Luna's — control redundant steps run 1.51 on Luna against
0.26 on GLM, and the demand arm adds +1.03 against +0.19 — so how wasteful a continue signal is is a
property of the model's stopping behaviour, not of the signal.

## 4.5 What this establishes and what it does not

Demand without evaluative language is sufficient to produce the cost effect; negative register
without demand does nothing, within [−0.40, +0.24] turns; positive register without demand produces
the opposite effect. The seven-level curve should be read as a gradient in implied demand that
happened to correlate with politeness because of how the texts were written, with the caveat that
the binary coding underwriting the word "dissociation" rests on one arm blinded raters read the
other way. The moved quantity is trajectory length, not reasoning per step, with threatening as a
reported exception. What this does **not** establish is why praise stops the agent — §5 takes that
up — nor that demand rather than mere instruction-following is the operative category (§7.3), nor
anything beyond two models, one benchmark, and one agent scaffold.