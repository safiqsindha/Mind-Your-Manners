# Communications

Drafts for external write-up. **Nothing here is ready to publish**: the study
has one model of four complete, and that one is on a wrapper set since found
confounded. Each draft is written against what is currently established and
marks in-line what is still pending.

Three rules apply to every draft below, and they are not stylistic:

1. **Never quote a v1 effect size as an estimate.** The v1 wrappers carried
   two confounds. The v1 primary *null* stands. The v1 accuracy numbers do
   not, and are illustrative only.
2. **The null is the headline.** If a draft leads with the accuracy trend, it
   is leading with the weakest, most-confounded, multiplicity-exposed result
   in the study. Do not.
3. **Cite all three prior papers.** arXiv 2510.04950, arXiv 2605.29027,
   arXiv 2607.23915. This is mandatory, not courteous — the whole design is
   an extension of theirs.

---

## 1. LinkedIn post

**Status:** hold until the four-model run completes. The version below is
written for that moment and marked where numbers must be swapped in.

> Everyone has an opinion about whether you should be polite to AI. There are
> now three papers on it. All three measure the same thing: what the model
> *says*.
>
> We asked a different question. Does tone change what an agent *does*?
>
> Same seven-tone scale, from grovelling to threatening. But instead of
> answering a multiple-choice question, the model writes Python, runs it
> against a real spreadsheet, sees what happened, and tries again. It is
> graded by the benchmark's own evaluator. No string matching.
>
> [N] models. [N] runs. $[N].
>
> **The headline: tone does not change how hard the model works.** We
> pre-registered a prediction that the effect would be *larger* in an agentic
> setting than the published single-turn figure of 44%. It came in at 15%.
> Our own prediction failed, and that is in the repo in the same font as
> everything else.
>
> Three things I did not expect.
>
> **We nearly published two effects that were not there.** A threatening-tone
> effect looked solid at a fifth of the data (p = 0.028) and dissolved by the
> end (p = 0.358). An accuracy trend survived to p = 0.023 and then turned
> out to rest on two tasks and a prompt-length artifact. Both are written up
> as methodology, with the interim numbers that made them tempting.
>
> **Our "neutral" prompt was not neutral.** It was the only one of the seven
> that added "provide a single final answer." That one sentence made the
> model answer instead of work: one attempt in ten produced no action at all,
> and acting-without-looking was the most common failure. Remove the
> sentence and both effects vanish, while accuracy does not move.
>
> **Our prompts were different lengths, and length predicted the outcome
> better than tone did.** Five tokens of difference on an 800-token prompt.
> The spec allowed it. It should not have.
>
> We found all three by having the analysis reviewed independently before
> writing it up, not after. Four arithmetic errors and two design flaws.
>
> Repo, data, and every correction: [link]
>
> Building on Dobariya & Kumar's *Mind Your Tone* work — arXiv 2510.04950,
> 2605.29027, 2607.23915.

**Notes for posting**

- Swap `[N]` for the final model count, trajectory count and spend.
- Do not add "so be nice to your AI anyway" as a closer. It is the line
  everyone wants and the data does not support it.
- If the accuracy result survives replication, it gets its own post. It does
  not get smuggled into this one.

---

## 2. Blog post

**Working title:** *We nearly published two things that were not there*

**Status:** the methodology spine is written and true today. The results
section needs the four-model run.

**Angle.** Not "here is what we found about tone." The honest and more useful
angle is: here is what it takes to get a trustworthy null out of an agentic
experiment, and here are the two moments we nearly failed.

### Outline

**1. The question everyone has already answered for themselves**
Three papers, one finding, one setting. Single-turn QA. What happens when
the model has to *do* something instead of say something.

**2. The setup**
Seven tones. SpreadsheetBench. The model writes and runs Python, sees the
output, iterates. Graded by the benchmark authors' own evaluator. 50 tasks ×
7 tones × 3 trials per model. Tone order randomised per task, because
otherwise the last tone always meets the worst network conditions.

**3. The result**
Tone does not move token cost. p = 0.36. The confidence interval excludes an
effect of the published size rather than merely failing to detect one. Our
pre-registered prediction was wrong in the falsifiable direction.

**4. The first near-miss: a threatening effect that was not there**
p = 0.028 at a fifth of the data. The honest thing was to stop looking, and
we did — repeatedly checking an accumulating result and reporting when it
looks good is how this becomes a finding. It ended at 0.358.

**5. The second near-miss: an accuracy trend that was real but not what we
said it was**
p = 0.023, survived an independent re-implementation. Then: not monotonic,
fragile to dropping two tasks, one of twelve outcomes tested, and confounded
twice over.

**6. The part I would tell anyone building an eval**
Our neutral condition was not neutral. One extra sentence turned the agent
into an answerer. Our prompts differed by five tokens and length
out-predicted the manipulation. **Both were in the spec. Both passed review.
Neither was visible without someone attacking the data.**

**7. What the harness learned the hard way**
Seven bugs found during the runs, each producing a plausible wrong number
rather than a crash: the answer key reachable from the sandbox, dry runs
writing into live files, two live processes sharing one records file after a
restart that had not killed the original. A table of all seven and what each
would have done to the published numbers.

**8. What we still do not know**
Three models to go. A lead about inspection behaviour that needs
re-measuring against the fixed instrument. Whether any of this replicates.

### Things to resist while drafting

- The "be nice to your AI" hook. It is the most shareable framing and the
  least supported.
- Making the bug hunt sound heroic. Every one of them was our own mistake,
  found late.
- Implying the null is *proof* of no effect. It bounds the effect. Say that.

---

## 3. Preprint skeleton

**Target venue:** TBD — a workshop on agent evaluation is the honest fit.
**Status:** cannot be written until the roster completes. Structure below is
pre-registered in spirit; deviations get their own section, as §0.

### Title options

1. *Tone Effects Do Not Survive the Move From Answering to Acting*
2. *Mind Your Manners: Prompt Tone and Agentic Task Execution*
3. *A Null Result on Prompt Tone in Multi-Turn Agentic Work*

### Abstract skeleton

> Prior work reports that prompt tone affects LLM accuracy and output length
> in single-turn question answering [1,2,3], with output-token variation
> reaching 44.3% across a seven-level tone scale [3]. We test whether these
> effects persist when the model must *execute* rather than *answer*. Using
> SpreadsheetBench, we run [N] models across the same seven-tone scale in a
> multi-turn agentic loop where the model writes Python, observes execution
> output, and iterates, graded by the benchmark's own evaluator. Across [N]
> trajectories we find **no effect of tone on token cost** (task-clustered
> permutation trend test, p = [N]), with a confidence interval excluding
> effects of the previously reported magnitude. [Accuracy result.] We report
> two interim false positives, the analysis errors found by independent
> review, and two confounds in our own instrument, all of which are
> documented with the numbers that made them credible.

### Section plan

| § | Content | Status |
|---|---|---|
| 0 | **Deviations from pre-registration** — the wrapper change mid-study, why, and what it invalidates | Written; see RESULTS.md |
| 1 | Introduction — the three prior papers; the answering/acting distinction | Outline |
| 2 | Related work — tone effects; agentic benchmarks; TERMS-BENCH, NegotiationArena | Outline |
| 3 | Design — seven tones, length-matched exactly; SpreadsheetBench; the loop; randomisation | **Can write now** |
| 4 | Outcome measures — cost primary, accuracy secondary, the behavioural measures, why | **Can write now** |
| 5 | Results — the null; accuracy; behaviour | Needs roster |
| 6 | Threats to validity | **Mostly written** |
| 7 | The two false positives, as a methods contribution | **Can write now** |
| 8 | Limitations and future work | Outline |

### §6 Threats to validity — already enumerated

1. **Instrument confounds (v1).** Neutral wrapper carried a task instruction;
   wrapper lengths were U-shaped and out-predicted tone rank. Both fixed in
   v2; the fix's effect was measured directly (150-trajectory control arm).
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

### §7 The false positives as a contribution

This is the section most likely to be the paper's actual value. Both
near-misses are documented with interim p-values, the stopping decision, and
the test that was wrong the first time (a pooled test where a task-clustered
one was needed — same data, p = 0.81 vs p = 0.03).

### Data availability

All records committed: gate, core, and the wrapper control, with
`wrapper_set` on every row. Every table recomputes with no API access.

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

- [ ] Four-model run complete on v2 wrappers
- [ ] Every number regenerated from committed records, not transcribed
- [ ] Independent re-analysis of the final dataset, as was done for v1
- [ ] No v1 effect size quoted anywhere as an estimate
- [ ] The null leads; the accuracy result does not
- [ ] All three prior papers cited in every artifact
- [ ] Deviations section written before the results section
