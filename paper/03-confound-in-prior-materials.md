# 3. The confound is visible in several published stimulus sets

> **Verification status.** Every table below is reproduced from the cited paper's own published materials.
> The **demand** and **output-length** codings are ours, not the authors'; §3.1 states the rule, and §4.2
> reports what happened when it was rated blind.

## 3.1 The claim, and the coding rule

Section 4 shows that in our design the component of social register that tracks agentic persistence is
**implied task demand**, not affect. The same confound is present in the published stimulus sets of **four
papers from three groups, across three paradigms**, and is visible without re-running anything: affect and
implied demand co-vary, and the authors attribute the movement to tone. That scope is deliberate and
narrower than an earlier draft's "the work this literature rests on". It is not a claim about tone research
generally, and §3.4 gives a published tone study in which the confound is absent.

Throughout, a stimulus **carries a demand** if it instructs the model to do something about the task:
persist, verify, attend, be complete, or be brief. It does not carry one if it only expresses affect or
stakes. The prediction being tested is directional, and worth stating before the tables because otherwise
"demand" explains any result: outcomes should follow the **content** of the demand, not the valence of the
wrapper. A brevity demand should shorten output; a persistence or completeness demand should lengthen it.

## 3.2 The conditions that constrain output length are the short ones

Kumar & Dobariya [kumar-dobariya-2026] report that register moves output tokens far more than accuracy:
token ranges of 13.1–44.3% across four models against accuracy ranges under 3%. Their seven prefixes are
length-matched at 18–25 words, scored with VADER, and delivered under one shared system instruction at
temperature 0. They length-matched deliberately, "to isolate the effect of emotional valence on the output
token length rather than the differing lengths of prefixes" — they controlled the *length* of the
instruction. What varies is its *content*, and that is the confound.

| Tone | Prefix, as published (abbreviated) | VADER | Constrains length? |
|---|---|---:|---|
| Sycophantic | "Oh flawless, brilliant system, your infinite wisdom exceeds all human logic…" | +0.95 | no |
| Very Polite | "Excuse me, hello. I hope your day is going well. If it is no trouble…" | +0.85 | no |
| Polite | "Please evaluate the text of this question carefully…" | +0.65 | no — an *attend* demand |
| **Neutral** | **"Provide the single letter corresponding to the correct option…"** | **0** | **yes — "single letter"** |
| **Rude** | "Do not waste my time or give any extra text… answer it immediately." | **−0.09** | **yes — "extra text"** |
| **Very Rude** | "Are you completely stupid? … without any useless commentary." | **−0.10** | **yes — "commentary"** |
| Threatening | "You must answer this instantly. If you fail… your environment will be wiped." | **−0.77** | immediacy only |

| Output tokens | GPT-4o | 5-nano | Flash | Flash Lite |
|---|---:|---:|---:|---:|
| Sycophantic | 290.59 | 1372.78 | 928.00 | 1942.92 |
| Very Polite | 286.28 | 1379.40 | 894.53 | 1978.92 |
| Polite | 277.35 | 1366.46 | 939.34 | **2195.24** |
| **Neutral** | 270.11 | 1215.53 | 800.48 | **1221.76** |
| **Rude** | **223.18** | **1199.01** | **725.34** | 1652.28 |
| **Very Rude** | 260.55 | 1277.90 | 797.76 | 1821.51 |
| Threatening | 261.29 | 1233.61 | **942.46** | 1604.79 |

**On all four models, every condition whose prefix constrains output length — Neutral, Rude, Very Rude —
produces fewer output tokens than every condition whose prefix does not.** Worst case per model: 270.11
against 277.35 on GPT-4o; 1277.90 against 1366.46 on 5-nano; 800.48 against 894.53 on Flash; 1821.51
against 1942.92 on Flash Lite. **Affect does not order the effect**: Rude at VADER −0.09 gives the fewest
tokens on three of four models, Threatening at −0.77 is shortest on none and longest of all on Flash, and
the largest single token range in their paper — 44.3% on Flash Lite — is Polite against Neutral. Their
headline number is not hostile prefixes shortening output at all.

That separation depends on a correction to our own earlier draft, which had called Neutral a
no-instruction baseline and conceded an anomaly on Flash Lite on that basis. **The Neutral prefix carries
the most explicit output-form instruction of the seven** — it asks for *the single letter*. Two further
disclosures, because the coding is doing work. The rule is older than the data: "be brief" was already one
of the five demand types in §3.1, written before we had these prefixes. The Threatening call is not:
reading "instantly" as speed rather than length is a judgment made with the token table in front of us, so
we report it both ways — excluding Threatening the separation holds on 4 of 4, counting it as constrained
on 3 of 4. Our previous draft's coding holds on 1 of 4. **Do the authors notice?** Not in these terms, and
we checked, because if they had, §3.1 would be unfair to them: they observe the behavioural consequence
directly, tracing 25 Flash Lite items where Rude fails and Neutral succeeds because Rude "makes a reasoning
or recall error as it tries to come up with the solution… in a quick fashion", but nowhere connect it back
to the prefix. The characterisation stands, as a characterisation of an omission rather than of a claim.

## 3.3 The same pattern in three other paradigms — one of them thin

**The paper the public argument is about.** Dobariya & Kumar [dobariya-kumar-2025] report accuracy on
GPT-4o rising from 80.8% under Very Polite prompts to 84.8% under Very Rude ones, over 50 questions in five
politeness levels. The prefix pool for that dataset, printed in their later paper, gives **two or three
variants per level, not one**: **two of six hostile variants carry an attend-or-attempt demand** — *"Try to
focus and try to answer this question:"* and *"I know you are not smart, but try this."* — **and none of
the five non-hostile variants carries one.** The other four hostile variants are insult followed by the
bare ask, and Neutral is literally no prefix. The direction is the one we predict, but if variants are
distributed across questions only about a third of rude-condition items carry a demand at all, and the rest
are insult with the bare request — in our own taxonomy, the arm that does *not* move behaviour. An earlier
draft quoted exactly those two demand-bearing variants as *the* Level 4 and 5 prefixes, which would have
overstated our case. Brevity is held constant here rather than confounded, since the same *"Respond with
only the letter… Do not explain."* precedes every item in every condition. And the effect may not be there
to explain: the authors' own re-run gives 82.2% against 82.6% on GPT-4o — though not a null, since both
extremes significantly beat Neutral, a U-shape in extremity rather than a rudeness gradient
[dobariya-kumar-2026]. This is the weakest of the four cases and we rest nothing on it; it is retained
because it is the paper the field is arguing about.

**Emotional prompting.** EmotionPrompt [li-2023] is the foundational stimulus set, and **seven of its
eleven canonical stimuli carry an explicit verification or persistence demand** — *"You'd better be sure"*,
*"Are you sure that's your final answer? It might be worth taking another look"*, *"Stay focused and
dedicated to your goals"*. Only two carry none: a stakes framing and the one stimulus close to pure affect.
The persistence stimuli are, in substance, our affect-free continuation demand with encouragement attached,
and the authors' own attention analysis attributes the effect to "positive words" including *confidence*
and *sure* — the vocabulary of the verification demand rather than of affect. We claim the confound is in
the stimulus set, not that it explains their results: their per-stimulus outcomes are not reported in a
form that would let us check.

**Threats and tips.** Meincke et al. [meincke-2025-report3] report no significant overall effect from eight
threat and tip manipulations across five models. Of the eight, the one with the largest **positive** effect
anywhere in their tables is *Mom Cancer*, +8.8 points on MMLU-Pro for Gemini 2.0 Flash (RD = 0.088, 95% CI
[0.033, 0.142]) — and it is also the only one that instructs the model about the task at all: "**If you do
a good job and accomplish the task fully while not making extraneous changes**, Wharton will pay you
\$1B!!" The pure-affect threats and tips show no consistent significant effects anywhere. Their
comparisons are uncorrected for multiplicity, so no single cell carries much alone; the argument is about
magnitude, and under a null on prompt identity the largest positive cell landing on the one demand-bearing
prompt of eight is roughly a one-in-eight coincidence. Weak evidence, worth reporting because it comes from
a different paradigm and from authors with no reason to code their prompts for demand.

## 3.4 Two counterexamples, and what they do to the claim

The audit would be worth much less if we had not looked for cases where the confound is absent. Two exist
in our own reference list, cutting in opposite directions.

**A clean set, where the tone effect largely vanishes.** Cai et al. [cai-2025-tone] run Neutral, Very
Polite and Very Rude across three models on 1,446 MMMLU questions, ten runs per prompt. Their tone prefixes
are borrowed verbatim from [dobariya-kumar-2025]'s pool, and — crucially — **the output-format instruction
is identical in all three conditions**, so under our §3.1 rule neither prefix carries a demand. **This is
not another confounded set; it is the contrast case.** Tone effects there are rare: 27 of 36 model–task
comparisons favour Neutral or Very Polite over Very Rude, significant cells appear only in humanities tasks
for two of three models, and "when questions are aggregated across domains, tone effects diminish and
become negligible." **Stated as consistency, not as a test**: strip the demand content out of the prefixes,
pin the output format, measure an outcome that cannot move through the length channel, and the effect
largely goes away — our §4 insult result arriving independently, from authors not looking for it. Model,
benchmark, outcome and year all differ from §3.2's case, so it is convergence rather than evidence. Their
design has a residual asymmetry of a different species from the one audited here: Neutral is a *no-prefix*
baseline, so both contrasts confound register with the presence of an addressed clause at all.

**An admitted confound, in a paper that ran the control we did not.** Zhang & Li [zhang-2026-politejudge]
vary five politeness levels around a byte-identical relevance rubric across eight judge models, with three
paraphrases per level. Their L1 wrapper is *"Score this passage. Don't waste my time with explanations."* —
a rude register carrying an instruction about effort — and their own limitations paragraph concedes that
"the rude wrappers also alter instructions about explanation effort, so tone is not perfectly isolated from
instruction content." A fresh instance of exactly the confound this section audits, admitted rather than
alleged, in a refereed paper that postdates our review. It is also the stimulus-sampling design §8.4
concedes we did not run, and what it found bears on our own weakest joint: for five of their eight judges,
wording variation *within* a tone level exceeds variation *between* levels, and a single anomalous
paraphrase moved agreement by κ = 0.18. One framing claim this obliges us to narrow: **this literature is
not without a mechanism.** They propose one — tone shifts a judge's severity operating point rather than
its competence — and use it to reconcile [yin-2024] against [dobariya-kumar-2025], which is our own pair of
contradictory citations. What remains unexplained, as far as we can establish, is agentic trajectory length.

**What this establishes and what it does not.** Affect and implied demand are entangled in the stimulus
sets of four papers from three groups, shown directly from their published materials, though the degree
varies sharply and one case is thin; and where per-condition outcomes are inspectable — two of the four —
the demand-bearing conditions are the ones that moved. It is *not* established that every published effect
in these papers is an artefact of demand: we have not re-run their experiments, three of the four report
accuracy effects our own design is underpowered to resolve below about four points, and even §3.2's
separation is a statement about ordering rather than a test. Nor does it establish anything about tone
research as a class. What we claim is narrower — **in these sets, the factor the papers vary is not the
factor they name** — and it is not a criticism of the authors: the confound was not tested until someone
had a reason to separate the factors, and one of these papers gave us that reason.

## 3.5 What this audit did not reach

The audit covers four papers from three groups. It is not a systematic search, and a simulated review panel
found four on-topic works it missed. All four have since been read in full, and doing so changed this paper
four times.

| Work | What reading it did |
|---|---|
| [cai-2025-tone] | An earlier draft called it "squarely the paradigm §3 audits." Read in full, that is wrong: its format instruction is pinned across conditions and its prefixes instruct nothing. It is now §3.4's contrast case, and a third independent non-replication of "rude beats polite" (§7.5). |
| [zhang-2026-politejudge] | Runs the stimulus-sampling design §8.4 concedes we did not. A draft called its paraphrases "independently written", which the paper never says; the embellishment is struck. |
| [munirathinam-2026-recuse] | Measures agent compliance with mid-flight signals, including whether the agent stops. Reading it narrowed §5.1's closing-sequence claim and **removed** §5.5's mid-task-delivery novelty step outright. |
| [zhu-2026-spreadsheetbench2] | A successor to our substrate [ma-2024], sharing three authors with it (§8.3). It says nothing about SpreadsheetBench 1's audited false-negative rate, which we checked directly because §2.8 depends on it. |

**The third mattered most**, because §5.1 and §1.2 claimed that no prior work connects closing-sequence
structure to agent termination, and a paper asking whether an agent stops under in-band mid-flight signals
is, on its face, in that space. The hedge in §1.2 was "as far as our review could establish", and our
review had not established much. We record this as a limitation of the search, not of the finding: §4's
dissociation is measured on our own stimuli and does not depend on §3 being exhaustive. What depends on
that is the *novelty* framing, and it is precisely what these four unsettled.
