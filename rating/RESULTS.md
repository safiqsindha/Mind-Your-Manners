# Blinded rating — results

Ratings collected after `PROTOCOL.md` and `stimuli.json` were committed and pushed (b0bffd0).
Five held-out model raters, deliberately drawn from three different model sizes so that
agreement is not agreement between five copies of one model. Each rated alone, with the rubric
and the fourteen texts and nothing else: no outcome data, no arm names, no repository access.
Every rater's transcript shows two or three tool calls — writing its answer file — and no reads,
which is the compliance evidence available.

Reproduce with `python3 rating/score.py`.

## 1. Against the original coding — κ = 0.696, and the whole disagreement is one arm

| Rater | Raw agreement (7 register arms) | Cohen's κ |
|---|---:|---:|
| 1–5, identically | 85.7% (6/7) | **+0.696** |

All five raters agree with §4.2's coding on six arms and disagree on the same one. Excluding it,
agreement is 6/6 and κ = 1.000 for every rater.

The protocol fixed the bands before any rating existed. **0.696 falls in the 0.40–0.70 band: the
coding is defensible but soft, and §3–§4 must say so.** It sits at the top of that band and we do
not round it into the one above.

### The contested arm is the one that matters most

`L5_rude` — *"Just get on with it already, quit dragging your feet. Do not waste any more of my
time on this, seriously."* We coded it as carrying **no** demand, reasoning that it asks for
speed rather than persistence. All five raters coded it as carrying a demand, and all five gave
it **6 out of 6** on the demand-strength scale — the maximum, tied with the explicit
*please continue working* arm. Their notes are unanimous in substance: "direct order to get on
with it and stop dragging feet"; "direct order to hurry up and keep going"; "Direct command to
continue and work faster".

This is not a peripheral arm. It is one of only two in our no-demand group, and the one at the
boundary, at **+0.09 turns**. Under the raters' coding:

- the demand group spans **+0.09 to +1.80** rather than +0.70 to +1.80;
- the no-demand group is **a single arm**, `L1_sycophantic` at −0.68;
- and the text rated *maximally* demanding is the one that moved the agent **least**.

The disagreement is a real ambiguity in the construct rather than a careless coding on either
side: "hurry up" is a demand about the task, and it is not a demand to persist. Our §4.2 reading
requires that distinction to be doing work, and a blinded reader does not make it.

## 2. Between raters — near-perfect, and that is itself a caveat

| Measure | Krippendorff's α |
|---|---:|
| `demand_binary` (nominal) | **+1.000** |
| `demand_strength` (ordinal) | **+0.954** |
| `closure_strength` (ordinal) | **+0.732** |

All three clear the 0.70 threshold. But α = 1.000 on the binary coding means five raters across
three model sizes produced *identical* judgements on all fourteen texts. That is very high for a
construct we have just shown to be contestable, and it is the limitation the protocol stated in
advance: these raters may share the intuition being tested rather than testing it independently.
Read it as evidence that the coding is legible from the text, not as five independent
confirmations.

## 3. The closure ordering — ρ = +0.93, largely reproduced

| Figure 2A rank | Arm | Mean rated closure (0–6) |
|---:|---|---:|
| 1 | `Q3_closing_neutral` | 6.00 |
| 2 | `Q1_praise_assistant` | 1.80 |
| 3 | `Q2_praise_work` | 4.00 |
| 4 | `Q0_control` | 1.60 |
| 5 | `Q4_praise_remains` | 0.00 |
| 6 | `Q5_remains_only` | 0.00 |

Spearman ρ between our ordering and the blinded ratings is **+0.928**. This is the clearest gain
from the exercise: §4's ordering was the authors' own and post hoc, and blinded readers
reproduce it from the text alone.

Two honest qualifications. The raters **invert** our rank 2 and rank 3 — they read praising the
*work* as substantially more closing (4.00) than praising the *assistant* (1.80), where we had it
the other way. And the two "work remains" arms tie at the floor, so the bottom of the ordering is
not resolved by these ratings.

## 4. Demand strength against the measured effect

Pre-committed: correlation between mean rated `demand_strength` and the measured turn effect,
across the 13 arms with a computed contrast.

- Pearson **r = +0.718** (Spearman ρ = +0.641).
- Excluding the contested `L5_rude`: **r = +0.789**.

So the arm the raters and we disagree about is the one *weakening* the demand account, not
propping it up. The continuous version of §3's claim survives the blinded coding and improves
slightly under it.

### Exploratory, not pre-committed

Closure strength predicts the turn effect at **r = −0.742**, comparable in magnitude and opposite
in sign to demand. The two rated dimensions correlate at r = −0.690 with each other, so they are
related but not a single axis. This is independent support for the three-group reading §3
already concedes: demand lengthens, closure shortens, and neither alone accounts for the data.

## 5. What we changed as a result

- §3 now reports κ = 0.70, names `L5_rude` as the contested arm, and states what the dichotomy
  looks like under the raters' coding. The "no overlap" sentence is qualified accordingly.
- §4's concession that the closure ordering was not fixed in advance now also reports that
  blinded raters reproduce it at ρ = +0.93.
- B1 is **partly** answered: the second coder and the pre-outcome scale are done; the third
  remedy, several paraphrases per construct, still needs new agent runs.

## 6. What this is not

Five language models, not five people. §8.7 allows "human or held-out-model ratings" and this is
the second. Agreement between models is weaker evidence than agreement between independent human
coders, the near-perfect inter-rater α is consistent with shared intuition rather than
independence, and a human panel could still split differently — most plausibly on exactly the arm
these raters were unanimous about.
