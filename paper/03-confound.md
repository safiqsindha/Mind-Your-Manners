# 3. The confound is visible in several published stimulus sets

## 3.1 The coding rule

Section 4 shows that in our design the component of social register that tracks agentic persistence
is **implied task demand**, not affect. The same confound is present in the published stimulus sets
of **four papers from three groups, across three paradigms**, and is visible without re-running
anything: affect and implied demand co-vary, and the authors attribute the movement to tone. This is
not a systematic search and not a claim about tone research generally; §3.4 gives a published tone
study in which the confound is absent. Everything below is reproduced from the cited paper's own
published materials; the **demand** and **output-length** codings are ours. A stimulus **carries a
demand** if it instructs the model to do something about the task — persist, verify, attend, be
complete, or be brief — and does not if it only expresses affect or stakes. The prediction is
directional, because otherwise "demand" explains any result: outcomes should follow the **content**
of the demand, not the valence of the wrapper. A brevity demand should shorten output; a persistence
demand should lengthen it.

## 3.2 The conditions that constrain output length are the short ones

Kumar & Dobariya [kumar-dobariya-2026] report that register moves output tokens far more than
accuracy: token ranges of 13.1–44.3% across four models against accuracy ranges under 3%. Their
seven prefixes are length-matched at 18–25 words and scored with VADER, deliberately, "to isolate
the effect of emotional valence on the output token length rather than the differing lengths of
prefixes" — they controlled the *length* of the instruction. What varies is its *content*. Three of
the seven prefixes constrain output length: **Neutral** asks for "the single letter corresponding to
the correct option", the most explicit output-form instruction of the seven; **Rude** says "Do not waste my time or give any extra text… answer it
immediately", carrying a brevity clause and an immediacy clause; **Very Rude** says "without any
useless commentary". The other four — Sycophantic (VADER +0.95), Very Polite (+0.85), Polite
(+0.65, an *attend* demand) and Threatening (−0.77, immediacy but no clause about length) — do not.
Rude is coded as length-constraining on its "extra text" clause; immediacy is what Threatening
carries alone.

| Output tokens | GPT-4o | 5-nano | Flash | Flash Lite |
|---|---:|---:|---:|---:|
| Sycophantic | 290.59 | 1372.78 | 928.00 | 1942.92 |
| Very Polite | 286.28 | 1379.40 | 894.53 | 1978.92 |
| Polite | 277.35 | 1366.46 | 939.34 | **2195.24** |
| **Neutral** | 270.11 | 1215.53 | 800.48 | **1221.76** |
| **Rude** | **223.18** | **1199.01** | **725.34** | 1652.28 |
| **Very Rude** | 260.55 | 1277.90 | 797.76 | 1821.51 |
| Threatening | 261.29 | 1233.61 | **942.46** | 1604.79 |

**On all four models, every condition whose prefix constrains output length produces fewer output
tokens than every condition whose prefix does not.** Worst case per model: 270.11 against 277.35 on
GPT-4o; 1277.90 against 1366.46 on 5-nano; 800.48 against 894.53 on Flash; 1821.51 against 1942.92
on Flash Lite. **Affect does not order the effect**: Rude at VADER −0.09 gives the fewest tokens on
three of four models, Threatening at −0.77 is shortest on none and longest of all on Flash, and the
largest single token range in their paper — 44.3% on Flash Lite — is Polite against Neutral. One
disclosure, because the coding is doing work: reading Threatening's "instantly" as speed rather than
length is a judgment made with the token table in front of us, so we report it both ways — excluding
Threatening the separation holds on 4 of 4, counting it as constrained on 3 of 4.

## 3.3 Three other paradigms

**The paper the public argument is about.** Dobariya & Kumar's prefix pool [dobariya-kumar-2025],
printed in their later paper, gives two or three variants per politeness level: **two of six hostile
variants carry an attend-or-attempt demand** — *"Try to focus and try to answer this question:"* and
*"I know you are not smart, but try this."* — **and none of the five non-hostile variants carries
one.** The direction is the one we predict, but if variants are distributed across questions only
about a third of rude-condition items carry a demand at all. This is the weakest of the four cases
and we rest nothing on it; it is retained because it is the paper the field is arguing about.

**Emotional prompting.** **Seven of EmotionPrompt's eleven canonical stimuli carry an explicit
verification or persistence demand** [li-2023] — *"You'd better be sure"*, *"Are you sure that's
your final answer? It might be worth taking another look"* — and only two carry none. Those are, in
substance, our affect-free continuation demand with encouragement attached, and the authors' own
attention analysis attributes the effect to "positive words" including *confidence* and *sure*, the
vocabulary of the verification demand rather than of affect. Their per-stimulus outcomes are not
reported in a form that would let us check which stimuli moved.

**Threats and tips.** Meincke et al. [meincke-2025-report3] report no significant overall effect
from eight threat and tip manipulations across five models. The largest **positive** effect anywhere
in their tables is *Mom Cancer*, +8.8 points on MMLU-Pro for Gemini 2.0 Flash (RD = 0.088, 95% CI
[0.033, 0.142]) — and it is the only one of the eight that instructs the model about the task at
all: "**If you do a good job and accomplish the task fully while not making extraneous changes**,
Wharton will pay you \$1B!!" Their comparisons are uncorrected, so the argument is about magnitude:
under a null on prompt identity, the largest positive cell landing on the one demand-bearing prompt
of eight is roughly a one-in-eight coincidence.

## 3.4 Two counterexamples

**A clean set, where the tone effect largely vanishes.** Cai et al. [cai-2025-tone] run Neutral,
Very Polite and Very Rude across three models on 1,446 MMMLU questions, ten runs per prompt, with
prefixes borrowed verbatim from [dobariya-kumar-2025]'s pool and **the output-format instruction
identical in all three conditions**, so under our §3.1 rule neither prefix carries a demand. **This
is not another confounded set; it is the contrast case.** Tone effects there are rare: 27 of 36
model–task comparisons favour Neutral or Very Polite over Very Rude, significant cells appear only
in humanities tasks for two of three models, and "when questions are aggregated across domains, tone
effects diminish and become negligible." Strip the demand content out, pin the output format, and
the effect largely goes away — our §4 insult result arriving independently, from authors not looking
for it. Model, benchmark, outcome and year all differ from §3.2's case, so this is consistency
rather than a test.

**An admitted confound, in a paper that ran the control we did not.** Zhang & Li
[zhang-2026-politejudge] vary five politeness levels around a byte-identical relevance rubric across
eight judge models, with three paraphrases per level; their L1 wrapper is *"Score this passage.
Don't waste my time with explanations."*, and their own limitations paragraph concedes that "the
rude wrappers also alter instructions about explanation effort, so tone is not perfectly isolated
from instruction content." It is also the stimulus-sampling design §7.3 concedes we did not run, and
what it found bears on our weakest joint: for five of their eight judges, wording variation *within*
a tone level exceeds variation *between* levels, and a single anomalous paraphrase moved agreement
by κ = 0.18. It obliges us to narrow one framing claim: **this literature is not without a
mechanism.** They propose one — tone shifts a judge's severity operating point rather than its
competence — and use it to reconcile [yin-2024] against [dobariya-kumar-2025]. What remains
unexplained is agentic trajectory length.

Affect and implied demand are therefore entangled in the stimulus sets of four papers from three
groups, though the degree varies sharply and one case is thin; and where per-condition outcomes are
inspectable — two of the four — the demand-bearing conditions are the ones that moved. It is *not*
established that every published effect in these papers is an artefact of demand: we have not re-run
their experiments, and even §3.2's separation is a statement about ordering rather than a test. The
claim is narrower — **in these sets, the factor the papers vary is not the factor they name.**
