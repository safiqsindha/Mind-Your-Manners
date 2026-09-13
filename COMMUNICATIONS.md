# Communications

Drafts for external write-up. **Nothing here is ready to publish**: the study
has one model of four, and the causal variable behind its one positive
finding is not yet identified. Each draft is written against what is
currently established and marks in-line what is still pending.

Four rules apply to every draft below, and they are not stylistic:

1. **Never quote a v1 effect size as an estimate.** The v1 wrappers carried
   two confounds. The v1 primary *null* stands; the v1 accuracy numbers do
   not, and are illustrative only.
2. **Do not say "rude costs more."** It is the most shareable sentence
   available and the data does not support it. The rude interruption arm is
   null (+6.7%, p = 0.13) while the *polite* arm is +28%. What predicts cost
   is whether the interruption implies the work must continue or be correct,
   not how rude it is (r = +0.88 vs +0.51 for tone rank).
3. **Two headlines, and they point opposite ways.** Tone in the opening
   prompt is null. Interruption mid-task is not. A draft that reports only
   one of these is misleading whichever one it picks.
4. **Cite all three prior papers.** arXiv 2510.04950, arXiv 2605.29027,
   arXiv 2607.23915. Mandatory, not courteous — the whole design extends
   theirs.

### The current state of the claim, in one paragraph

Opening tone does not change what the agent does (p = 0.36, effect of the
published size excluded). Interrupting the agent partway through *does*
change what it does, and has replicated twice (+27.5%, then +36.7% reasoning
tokens for a threatening interruption against a neutral one). The mechanism
is persistence rather than effort: thinking per step is flat across all seven
registers, and what moves is how many steps the agent takes before stopping.
Flattery reverses it — told mid-task that it is brilliant, the agent stops
sooner (−0.68 turns, p < 0.0001). Accuracy has never moved in any run. And
the register/demand confound means the operative variable is not yet named,
which a four-arm probe is currently testing.

---

## 1. LinkedIn post

**Status:** hold. Publishable once the demand/affect probe resolves whether
register matters at all. Marked where numbers must be swapped in.

> Everyone has an opinion about whether you should be polite to AI. There are
> now three papers on it. All three measure the same thing: what the model
> *says*.
>
> We asked a different question. Does tone change what an agent *does*?
>
> Same seven-tone scale, from grovelling to threatening. But instead of
> answering a multiple-choice question, the model writes Python, runs it
> against a real spreadsheet, sees what happened, and tries again. Graded by
> the benchmark's own evaluator. No string matching.
>
> 5,150 trajectories. One model so far. $28.
>
> **Finding one: how you open does not matter.** Rude, polite, grovelling,
> threatening — the agent works exactly as hard. Not "we could not detect a
> difference." The interval excludes an effect of the size the prior papers
> reported.
>
> **Finding two: how you interrupt does.** Say the same thing *partway
> through*, while the agent is working, and it changes behaviour. A
> threatening check-in costs about a third more thinking. That has now
> replicated twice on separate data.
>
> **Finding three is the one I did not expect.** The agent is not thinking
> harder. It is *refusing to stop*. Thinking per step does not move at all;
> the number of steps does. And flattery does the opposite — tell it that it
> is brilliant halfway through and it wraps up early.
>
> Here is the part I would rather not write. When I looked at *which*
> interruptions cost more, it was not the rude ones. Polite cost 28% more.
> Rude cost nothing measurable. What actually predicted the cost was whether
> the message implied "keep going" or "get it right."
>
> Which means my own prompts were confounded. I matched them all to the same
> length, and a *meaning* difference walked in where the length difference
> used to be. The honest headline is that nagging costs compute, and
> politeness was along for the ride.
>
> [PENDING: the four-arm probe separating demand from register.]
>
> None of it made the agent more accurate. Not once, in any run.
>
> Repo, data and the five confounds that each inverted a headline: [link]

**Do not post if:** the probe shows register is inert and the draft still
implies tone matters. Rewrite around the completion-signal framing instead.

---

## 2. Blog post

**Working title:** *The agent was not thinking harder. It was refusing to stop.*

**Status:** the methodology spine is written and true today. The results
section is now substantive rather than a null, but the causal claim waits on
the probe.

**Angle.** Not "here is what we found about tone." Two better ones, and they
can be the same piece: what it takes to get a trustworthy result out of an
agentic experiment, and the moment the interesting finding turned out to be
about something other than what we were manipulating.

### Outline

**1. The question everyone has already answered for themselves**
Three papers, one finding, one setting: single-turn QA. What happens when the
model has to *do* something instead of say something.

**2. The setup**
Seven tones. SpreadsheetBench. The model writes and runs Python, sees the
output, iterates. Graded by the benchmark authors' own evaluator. Tone order
randomised per task, because otherwise the last tone always meets the worst
network conditions.

**3. The null, and why it is a real result**
Opening tone does not move token cost. p = 0.36. The interval excludes an
effect of the published size rather than merely failing to detect one. Our
pre-registered prediction was wrong in the falsifiable direction.

**4. The thing that was not null**
Deliver the same register *mid-task* and behaviour changes. +27.5%, then
+36.7% on a second, larger, differently-designed run. The control is a
*neutral interruption*, not silence, which is what makes it a statement about
register rather than about being interrupted.

**5. Position matters more than we expected**
The same words are free at turn 0 and cost 55% more at turn 2. Our first
attempt to measure this was confounded — late injections only fire on
trajectories that last that long, which are the hard ones — and it took
crossing the turn and defining the comparison population from the control arm
to get an answer.

**6. The mechanism, which is not effort**
Thinking per step is flat across every register. Turn count is what moves.
The agent is declining to stop. And sycophancy inverts it: told it is
brilliant, it stops early. This was invisible until we stopped looking only
at tokens.

**7. The part I would rather not have found**
It was not the rude interruptions that cost more. Polite cost 28%, rude cost
nothing. Implied demand outpredicted politeness at r = +0.88 vs +0.51, with
no overlap between groups. **Our own prompts were confounded** — and it was
the same failure as an earlier one we had already fixed. We matched the
lengths exactly, and a semantic difference moved into the space the lexical
one had occupied.

**8. Five confounds, each of which inverted a headline**
A table: wrapper length outpredicting tone rank; pooled vs task-clustered
tests giving p = 0.81 vs 0.03 on identical data; injection turn confounded
with difficulty, turning p = 0.004 into p = 0.32; two concurrent arms sharing
scratch directories and corrupting 800 grades; and pooling an inert cell that
diluted every effect by a third. The lesson is not "we were careful." It is
that this instrument keeps producing effects that dissolve under a
better-specified comparison.

**9. What we still do not know**
Whether register matters at all. Three models to go. Whether any of it
replicates.

### Things to resist while drafting

- **The "be nice to your AI" hook.** Most shareable, least supported, and now
  actively contradicted: polite nagging was the expensive one.
- Making the bug hunt sound heroic. Every one was our own mistake, found
  late, and one of them was a repeat of a category we had already been burned
  by.
- Implying the null is *proof* of no effect. It bounds the effect. Say that.
- Leading with "AI works harder when threatened." It is true and it is the
  least interesting true thing here, and it invites the causal reading the
  data does not support.

---

## 3. Preprint skeleton

**Target venue:** TBD — a workshop on agent evaluation is the honest fit.
**Status:** cannot be written until the roster completes. Structure below is
pre-registered in spirit; deviations get their own section, as §0.

### Title options

1. *Interruptions, Not Instructions: Where Prompt Tone Acts on an Agent*
2. *The Agent Was Not Thinking Harder, It Was Refusing to Stop*
3. *Tone Effects Do Not Survive the Move From Answering to Acting — Except Mid-Task*
4. *Mind Your Manners: Prompt Tone and Agentic Task Execution*

Title 1 is the honest framing if the probe shows register matters; title 2 if
the mechanism is the contribution; title 3 only if the probe shows register
is inert and the effect is purely a completion signal, in which case "tone"
should leave the title entirely.

### Abstract skeleton

> Prior work reports that prompt tone affects LLM accuracy and output length
> in single-turn question answering [1,2,3], with output-token variation
> reaching 44.3% across a seven-level tone scale [3]. We test whether these
> effects persist when the model must *execute* rather than *answer*. Using
> SpreadsheetBench in a multi-turn agentic loop where the model writes
> Python, observes execution output, and iterates, graded by the benchmark's
> own evaluator, we separate two placements of the same tone scale: tone in
> the opening instruction, and tone delivered as an interruption partway
> through the trajectory. Across [N] trajectories, **opening tone has no
> effect on token cost** (task-clustered permutation trend test, p = 0.36),
> with a confidence interval excluding effects of the previously reported
> magnitude. **Mid-task interruption does**, replicating across two
> independent runs (+27.5%, +36.7% reasoning tokens for a threatening
> against a neutral interruption). The mechanism is not increased effort per
> step, which is flat across all seven registers, but increased persistence:
> the agent takes more steps before stopping. Sycophantic interruption
> reverses the effect, shortening trajectories. The effect is also
> position-dependent: an interruption after the agent's first response is
> inert, while the same text two steps later costs 55% more. **No placement
> or register changed task accuracy.** We further show that our own
> seven-level instrument confounds social register with implied task demand,
> that implied demand is the better predictor (r = +0.88 vs +0.51), and
> report a four-arm probe separating them. We document five confounds found
> during the study, each of which inverted or erased a headline result.

### Section plan

| § | Content | Status |
|---|---|---|
| 0 | **Deviations from pre-registration** — the wrapper change mid-study, why, and what it invalidates | Written; see RESULTS.md |
| 1 | Introduction — the three prior papers; the answering/acting distinction | Outline |
| 2 | Related work — tone effects; agentic benchmarks; TERMS-BENCH, NegotiationArena | Outline |
| 3 | Design — seven tones, length-matched exactly; SpreadsheetBench; the loop; randomisation | **Can write now** |
| 4 | Outcome measures — cost primary, accuracy secondary, the behavioural measures, why | **Can write now** |
| 5 | Results — the opening-tone null; the interruption effect and its replication; position dependence; the persistence mechanism; accuracy | **Can mostly write now**; roster for generality |
| 5b | The register/demand confound and the probe that separates them | Probe running |
| 6 | Threats to validity | **Mostly written** |
| 7 | The two false positives, as a methods contribution | **Can write now** |
| 8 | Limitations and future work | Outline |

### §6 Threats to validity — already enumerated

1. **Instrument confounds (v1).** Neutral wrapper carried a task instruction;
   wrapper lengths were U-shaped and out-predicted tone rank. Both fixed in
   v2; the fix's effect was measured directly (150-trajectory control arm).
1b. **Instrument confound (interjections).** The seven mid-task texts vary
   social register and implied task demand together. Demand is the better
   predictor (r = +0.88 vs +0.51) and the groups do not overlap, so the
   headline effect cannot be attributed to register on this data. A four-arm
   probe (neutral / demand-only / praise-only / insult-only, structural
   minimal pairs, all 28 tokens) separates them. **This is the same class of
   failure as (1), recurring after it was believed fixed** — lengths were
   matched and a semantic nuisance variable replaced the lexical one.
1c. **Censoring at the turn ceiling.** Turn count is the outcome the
   mechanism acts on, and the loop caps at 10 turns against a median of ~3.8.
   Threatening roughly doubles turn-limit hits, so the arms with the largest
   effects are the most censored, biasing the measured effect *downward*.
2. **Multiplicity.** Twelve outcomes each received a trend test.
3. **Fragility.** The accuracy trend rests on 19 of 50 tasks.
4. **Floor effects.** 26 of 50 tasks are never solved by the model tested.
5. **Non-determinism.** temperature=0 does not produce identical outputs on
   any roster model; measured directly, three distinct outputs from three
   byte-identical calls.
6. **Single provider.** All inference through OpenRouter with provider
   pinning enforced and asserted per call; an unpinned call to the same model
   was served by a different provider at materially different speed.
7. **Model version drift.** Moving slugs are checked against the catalog's
   dated snapshot before every live run.

### §7 The confounds as a contribution

This is the section most likely to be the paper's actual value. Five
confounds, each documented with the number it produced before it was found
and the number after:

| Confound | Before | After |
|---|---|---|
| Wrapper length outpredicted tone rank | accuracy trend p = 0.023 | withdrawn |
| Pooled test where task-clustered was needed | p = 0.81 | p = 0.03 |
| Injection turn confounded with task difficulty | timing split p = 0.004 | p = 0.32, withdrawn |
| Two concurrent arms sharing scratch directories | 800 grades corrupted | recovered by re-grading from raw logs |
| Pooling an inert cell (turn 0) | threatening +28.9% | +36.7%; sycophantic flipped from null to significant |

Plus the two interim false positives, with their p-value trajectories and the
stopping decision.

The argument is not "we were careful." It is that **four of these five
produced a plausible, publishable, wrong number rather than a crash**, and
that the same class of instrument confound recurred after being fixed once.
An agentic eval with this many researcher degrees of freedom should be
assumed to contain one until someone has attacked it.

### Data availability

All records committed: gate, core, the wrapper control, the mid-task
micro-experiment (both arms, plus clean re-grades), and the seven-level
crossed run — 5,150 graded trajectories, with `wrapper_set`, `interjection`,
`interjection_turn` and `interjection_fired` on every applicable row. Every
table recomputes with no API access.

### Author contributions

CRediT taxonomy. To be completed.

### Citations required

- [1] Dobariya & Kumar, arXiv 2510.04950
- [2] Dobariya & Kumar, arXiv 2605.29027 (AMCIS 2026)
- [3] Dobariya & Kumar, arXiv 2607.23915
- SpreadsheetBench
- TERMS-BENCH, arXiv 2605.13909
- NegotiationArena, ICML 2024

---

## Pre-publication checklist

- [ ] **Demand/affect probe resolved** — until it is, no draft may attribute
      the interruption effect to social register
- [ ] Four-model run complete, testing *interruptions* rather than opening
      tone (opening tone is null; replicating a null across models is not
      where the $50 should go)
- [ ] Every number regenerated from committed records, not transcribed
- [ ] Independent re-analysis of the final dataset, as was done for v1
- [ ] No v1 effect size quoted anywhere as an estimate
- [ ] Both headlines present: opening tone null AND interruption effect. A
      draft carrying only one is misleading whichever it picks
- [ ] Turn count reported as the mechanism, not buried under token counts
- [ ] The sentence "rude interruptions cost more" appears nowhere — the rude
      arm is null and the polite arm is +28%
- [ ] Accuracy reported as a bound, never as "no effect"
- [ ] Turn-ceiling censoring stated as a limitation on the effect size
- [ ] All three prior papers cited in every artifact
- [ ] Deviations section written before the results section
