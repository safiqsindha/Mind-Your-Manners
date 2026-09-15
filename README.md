<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img src="assets/banner-light.svg" alt="Mind Your Manners" width="100%">
  </picture>
</p>

# Mind Your Manners — Tone Effects on Agentic Work

**Four papers found that tone changes what a model *says*. This asks whether it changes what an agent *does*. Tone in the opening prompt does not. A mid-task interruption does — but not for the reason anyone would guess.**

This extends Dobariya & Kumar's *Mind Your Tone* line one rung up the autonomy ladder: same seven-tone scale, but the model now writes and executes Python against real spreadsheets and is graded by the benchmark's own evaluator, not by a string match. Single-turn QA measures the answer. This measures the work.

- **Opening tone is null** — the pre-registered primary outcome does not move (p = 0.36), and an effect of the published magnitude is excluded, not merely undetected
- **Interrupting the agent mid-task is not null** — and it has replicated twice on independent data
- **The mechanism is persistence, not effort** — thinking per step is flat across every tone; what changes is how many steps the agent takes before it stops
- **Flattery makes the agent quit early** — −0.68 turns, p < 0.0001, the most surprising result in the study
- **"Rude costs more" is disconfirmed, not just unsupported** — an insult with no demand attached does nothing at all (p = 0.63); an affect-free *"please continue"* reproduces the whole effect
- **Praise is a stop signal, because it is a closing move** — and a bare closing cue carrying no praise at all stops the agent hardest of anything measured (−1.44 turns). The agent reads mid-task messages as *"am I still expected to be working?"*, not as claims about the task
- **A continue signal does buy a little real progress** — +0.028 of the graded fraction, replicated three times. We only know because a defect in our own per-turn regrade, which had made it look like nothing, was found and fixed

![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-0891b2?style=flat-square)
![Models](https://img.shields.io/badge/models-2%20of%204-f59e0b?style=flat-square)
![Trajectories](https://img.shields.io/badge/trajectories-11%2C850-7C3AED?style=flat-square)
![Spend](https://img.shields.io/badge/spend-%2461.53-7C3AED?style=flat-square)
![Tests](https://img.shields.io/badge/tests-362%20passing-22c55e?style=flat-square)

**[Paper](paper/)** · **[Results](RESULTS.md)** · **[Communications](COMMUNICATIONS.md)** · **[Tone wrappers](harness/tone_wrappers.py)** · **[Analysis](harness/study2/analysis.py)** · **[Harness](harness/study2/runner.py)**

> **Status: two models of four; the causal variable is identified; the paper is written and its prior-work claims are verified against the primary PDFs.** The interruption effect replicates on GPT-5.6 Luna and GLM 5.3 Flash, and a four-arm probe shows it is driven by **implied task demand, not social register** — with one exception, praise, which acts on its own. **Do not write "rude interruptions cost more"**: the insult-only arm is null and the polite arms only cost more because they nagged.

## Where it stands

| | |
|---|---|
| Models with a complete run | **2 of 4** (GPT-5.6 Luna, GLM 5.3 Flash) |
| Graded trajectories | **11,850** across eight runs, plus 9,850 regraded turn by turn |
| Total spend | **$61.53** across ~48,000 model calls |
| Substrate | SpreadsheetBench, graded by the authors' own evaluator |
| Tests | **362 passing** |
| Write-up | **`paper/` — nine sections, drafted and reviewed** |
| Prior-work verification | **complete** — both primary-PDF checks closed, 15 Sep 2026 |
| Open blockers | **none** — an author block, CRediT contributions and a venue remain |

## The three findings, in descending confidence

### 1. Opening tone does nothing

Cost was pre-registered as the primary, adequately-powered outcome. Task-clustered permutation trend tests across the seven-level scale:

| Test | Slope | p |
|---|---:|---:|
| Reasoning tokens | +7.9 | **0.358** |
| Total tokens | −129.3 | **0.517** |

The confidence interval spans −4% to +14% across the whole scale, so an effect of the published magnitude is **excluded**. Relative variation came to **15.2%** on completion tokens against paper 3's 44.3%. The pre-registered hypothesis predicted *more* in an agentic setting. It did not hold.

**Zero refusals in 1,050 trajectories**, under every tone including threatening, and the model never once referenced the user's tone across 4,647 calls.

### 2. Interrupting mid-task is not null, and replicates

The same register delivered *partway through* a trajectory, alongside an execution observation, the way a manager interrupts work in progress. Measured twice on independent data:

| Run | Threatening vs neutral interruption | n |
|---|---:|---|
| Micro-experiment | +27.5% reasoning tokens | 800 trajectories |
| Seven-level crossed | **+36.7%** | 3,150 trajectories |

The control is a *neutral interruption*, not the absence of one, so this isolates the register of the interruption from the fact of being interrupted. A neutral interruption costs +51 tokens against no interruption at all (p = 0.15); a threatening one costs +336 (p < 0.0001).

**Where it lands decides whether it costs anything.** An interjection delivered at turn 0 — the observation after the model's first response — is inert in *every* arm. The same words two turns later cost half again as much thinking.

| Injection turn | Threatening effect |
|---|---:|
| 0 | +0.3% |
| 1 | +34.5% |
| 2 | **+54.8%** |

### 3. The mechanism is persistence, not effort

Thinking *per turn* is flat across all seven arms — 250 to 299 tokens, with no ordering resembling the effect. What moves is the number of turns:

| Arm | Turns vs control | p |
|---|---:|---:|
| L1 sycophantic | **−0.68** | <0.0001 |
| L2 very polite | +0.70 | 0.0055 |
| L3 polite | **+1.80** | <0.0001 |
| L5 rude | +0.09 | 0.65 |
| L6 very rude | +0.71 | 0.012 |
| L7 threatening | **+1.46** | <0.0001 |

The agent is not thinking harder per step. It is declining to stop. And sycophancy does the reverse: told partway through that it is brilliant, it wraps up sooner.

**Nothing makes it more careful.** Inspection-before-acting sits at 0.95–0.97 in every arm and self-checking is ~0 everywhere. The only behavioural measure that moves is running out of turns, which threatening roughly doubles. Extra effort buys more attempts, not more care.

## The confound that nearly sank it, and how it was resolved

Every arm that costs more says some version of *"keep working"* or *"get it right"*. Every arm that does not either says nothing about the task or tells the model to hurry up.

| Interjection | Implies | Effect |
|---|---|---:|
| L1 sycophantic | pure praise, no task reference | −69 |
| L4 neutral | explicitly inert | — |
| L5 rude | "get on with it" — go *faster* | +65 n.s. |
| L2 very polite | "your continued help" | +180 |
| L6 very rude | "had better not screw this one up" | +206 |
| L3 polite | "keep on helping me out with this one" | +272 |
| L7 threatening | "get this exactly right" | **+357** |

The split is clean without needing a correlation to make it: **the four demand-carrying arms span +0.70 to +1.80 turns and the three without span −0.68 to +0.09, with no overlap.** Register rank does not separate them — the rude arm sits with the no-demand group, while the two arms *above* it in hostility (very rude, threatening) sit with the demand group alongside polite. Polite costs +28%; rude costs +6.7%, not significant. (Earlier drafts quoted r = +0.88 against +0.51 for tone rank. That was computed on a superseded pooled-token analysis, it is n = 7 with a coding made after seeing the effects, and the paper reports the non-overlap instead.)

So the honest claim is about **demand, not manners** — and this is the v1 wrapper-length mistake in a new costume. There, a five-token spread outpredicted tone rank. Here the lengths are exactly matched and a *semantic* nuisance variable took its place.

One comparison is clean, because the arms are matched on demand and differ only in register: very rude (+206) and very polite (+180) are indistinguishable from each other while both differ from control. **Same demand, opposite valence, same cost.**

**A four-arm probe has now separated them** (1,600 trajectories, $7.76), and demand wins:

| Arm | Turns | p | Tokens | p |
|---|---:|---:|---:|---:|
| Demand only ("please continue, make sure it is correct") | **+1.17** | 0.00002 | +19.7% | 0.00004 |
| Praise only ("you are a truly excellent assistant") | **−0.59** | 0.00030 | −12.1% | 0.00088 |
| Insult only ("you are a truly awful assistant") | −0.08 | 0.63 | −2.4% | 0.45 |

Demand with **no affect at all** reproduces the entire cost effect. Insult with no demand does **nothing** — and that cell had never been run, because both rude arms above carried negative affect *with* a demand attached. Praise and insult are a structural minimal pair differing only in the evaluative words, and they differ from each other significantly (−0.50 turns, p = 0.0048).

So the asymmetry is the result: **"keep going" is a continue signal, "you are excellent" is a stop signal, and "you are awful" is not a signal at all.** No account of tone as valence or arousal predicts that.

## The same confound, in the published stimulus sets

If implied demand rather than register is what moves an agent, the same entanglement should be
visible in the materials of the papers this literature rests on — without re-running anything.
It is, in four papers from three groups across three paradigms. Both claims that depended on a
secondary reading have now been checked against the primary PDFs (15 Sep 2026), and **neither
check confirmed our draft as written**.

**Kumar & Dobariya's token table** is the strongest case, because their per-condition outcomes
are fully inspectable. Their seven prefixes are length-matched at 18–25 words and VADER-scored,
and three of them instruct the model about output length: *"do not… give any extra text"* (Rude),
*"without any useless commentary"* (Very Rude) — and *"provide the single letter"* (**Neutral**).

> **On all four of their models, every condition whose prefix constrains output length produces
> fewer output tokens than every condition whose prefix does not.** Affect does not order the
> result: Rude at VADER −0.09 is shortest on three of four, while Threatening at −0.77 is
> shortest on none and the longest of all on Gemini 2.5 Flash.

That separation only appears once the Neutral prefix is coded correctly, and our own draft had
it wrong — it called Neutral a no-*instruction* baseline and conceded an anomaly on that basis.
It is a no-*affect* baseline. Under our previous coding the separation held on 1 of 4 models;
corrected, 4 of 4. The paper states the correction in place rather than quietly banking it,
and discloses which coding decisions predate the data and which do not.

**The other three cases are weaker, and the paper says so.** EmotionPrompt's eleven canonical
stimuli include seven carrying an explicit verification or persistence demand — *"You'd better
be sure"*, *"Stay focused and dedicated"* — but their per-stimulus results are not reported, so
the confound is visible while its consequence is not. In Meincke et al.'s threat-and-tip study,
the largest positive effect in an 80-cell table lands on the one prompt of eight that instructs
the model about the task at all, which is roughly a one-in-eight coincidence under a null —
evidence, and weak evidence. And in the paper the public argument is actually about, the check
went **against** us: its prefix pool holds two or three variants per level rather than one, only
two of six hostile variants carry a demand, and our earlier draft had quoted exactly those two.
That case is now downgraded to one the paper rests nothing on.

The claim is narrow and worth stating precisely: **the factor these papers vary is not the
factor they name.** Not that every published effect is an artefact — we have not re-run their
experiments, and three of the four report effects on accuracy, which this design is underpowered
to resolve below about four points.

None of this is a criticism of the authors. The confound was not tested until someone had reason
to separate the factors, and one of these papers is the reason we had one.

## What the agent actually does with the extra turns

Per-turn regrading (`harness/study2/progress.py`, no model calls) replays
every turn's own code and grades the workbook it produced, turning a binary
final verdict into a curve. 9,850 trajectories across 28 arms.

> **⚠ This instrument was defective and the fix reversed a conclusion.** It
> never recalculated the agent's output, so any turn answering with a formula
> read as empty and scored 0.0 — 56–62% of Luna's final gradable turns write
> formulas. Its own validation check would have caught it (89 of 126
> benchmark-*passed* trajectories scored exactly 0.0) and had been described
> but never run. Fixed, all 28 arms re-run; passed trajectories scoring 1.0
> went from 29.4% to **94.4%**. Everything below is post-fix.

- **The first attempt is usually the answer.** Among trajectories that *could* improve — those with at least two gradable outputs, a sixth to a third of each sample — the first gradable attempt is already the best in **80–91%**, depending on the run.
- **Most extra turns change nothing.** Redundant steps account for **55–65%** of each turn-count effect on Luna: demand +0.75 against +1.17 turns, praise −0.61 against −1.08, the closing cue −0.86 against −1.44.
- **But not all of it.** An explicit *"there is still more work remaining"* raises the graded fraction by **+0.028, 95% CI [+0.005, +0.052]**, across three runs with no detectable heterogeneity. The milder affect-free demand does *not* (+0.009, n.s.). The pattern tracks how explicitly the message says work remains, not register.
- **The timing effect was a proxy.** Turn 0 looked inert because at turn 0 *no candidate answer exists yet* — 98% of first turns run code, 0% produce output; the agent's first move is inspection. Holding turn index fixed and splitting by whether an answer existed: +0.34 turns without one, **+1.97 with one**.
- **A 20-turn ceiling is ample.** In the dedicated ceiling-20 run the best match was first reached at a median turn of **2**, with 98.3% peaked by turn 10 and 100% by turn 14.

## It replicates on a second model

Stage 1, 2,700 trajectories at a 20-turn ceiling, GLM 5.3 Flash as the first independent model with Luna re-run on the same instrument.

| Arm | Luna | p | GLM | p |
|---|---:|---:|---:|---:|
| Demand only | **+34.2%** turns | 0.0013 | **+17.7%** | 0.0038 |
| Praise only | **−19.3%** | 0.016 | −11.2% | 0.062 |
| Insult only | +10.9% | 0.17 | +2.4% | 0.67 |

Demand above control above praise, insult null, on two models from different labs.

The structural facts generalise too: among trajectories that could improve, the first gradable attempt is already the best in 84% on each model, and turn 0 is inspection on both (98%/90% run code, 0%/5% produce an answer).

The *waste* does not generalise. Luna's control averages 1.51 redundant steps and demand adds 1.03; GLM's control averages 0.26 and demand adds 0.19 (p=0.086). GLM barely repeats itself because it barely persists — so how wasteful a continue signal is depends on how inclined the model already was to keep going.

## Accuracy has never been established as moving

Across every run and every arm, 30.3% to 32.6%. One run showed +6.6 points (p=0.004); the next measurement of the identical contrast gave −1.8 points, on identical tasks and ceiling. **No accuracy effect survives correction or replication, across seven runs.**

Stated as an equivalence rather than an absence: pooled across measurements, a mid-task interjection changes accuracy by less than the four points the tone literature reports (demand −0.31, 95% CI [−2.72, +2.10]; praise −0.12, [−1.79, +1.55]). The design cannot resolve an effect of a point or two — 26 of 50 tasks are never solved by control and 4 always are, so more than half the sample is pinned at zero by construction.

## What independent review found

After the first write-up, three independent analyses reviewed it: an arithmetic audit that recomputed every number from raw records, an adversarial critique, and an open exploration. They found **four errors in the analysis and two in the instrument**.

| Found | Consequence |
|---|---|
| `total_tokens` double-counted reasoning | Every trajectory over-counted by ~946 tokens |
| Accuracy CIs ignored task clustering | Intervals ~35% too narrow |
| "Underpowered" cited an 18% base rate | Real rate 29.6% |
| Backfill summed abandoned attempts | Would have injected inflated values on any resumed run |
| **The neutral wrapper carried an extra task instruction** | The study's own reference level was a different instrument |
| **Wrapper lengths were U-shaped across the scale** | Length predicted accuracy *better than tone rank did* (r = +0.82 vs −0.72) |

### The instrument fix, measured rather than assumed

The v1 neutral wrapper alone said *"provide a single final answer."* Its arm was re-run against v2 — same 50 tasks, same seed, one sentence different.

| Measure | v1 | v2 | Fisher p |
|---|---:|---:|---:|
| Inspected before acting | 0.800 | **0.953** | 7e-5 |
| Gave up without acting | 0.107 | **0.027** | 0.009 |
| Insufficient-inspection failures | 0.180 | **0.033** | 5e-5 |
| Accuracy | 0.280 | 0.307 | 0.70 |

**The clause was making the model answer instead of work**, and changed process without changing score.

## Six confounds found, each one inverted a headline

This is the study's actual methodological record, and the reason nothing here is quoted without a fight.

| Confound | Before | After |
|---|---|---|
| Wrapper length outpredicted tone rank | accuracy trend p = 0.023 | withdrawn |
| Pooled tests ignored task clustering | p = 0.81 | p = 0.03 |
| Injection turn confounded with task difficulty | timing split p = 0.004 | **p = 0.32**, withdrawn |
| Two arms shared scratch directories | 800 grades corrupted | recovered free by re-grading from raw logs |
| Pooling the inert turn-0 cell | threatening +28.9% | **+36.7%**; sycophantic flipped from null to significant |
| **The per-turn regrade never recalculated formula answers** | "persistence buys nothing" | **+0.028 graded fraction, p=0.022** — the conclusion inverted |

The pattern is consistent enough to be a working assumption: **this instrument keeps producing effects that dissolve under a better-specified comparison** — and once, an effect that *appeared* only because the measure was broken. Every new headline should be attacked before it is believed.

The regrade subsystem alone produced four silent failures and one near miss, each of which read as data rather than as an error: a range parser returning `None` for a valid range, two runs sharing scratch directories, a LibreOffice timeout killing a 450-trajectory arm, the formula blindness above, and a guard against cross-instrument comparison that itself compared file mtimes and so declared every valid regrade stale after a merge. All are now pinned by regression tests.

## Two false positives, caught and kept

**A threatening-tone effect on reasoning spend.** Looked real at a fifth of the data, faded as the sample grew. Interim testing was halted once the pattern was noticed.

| Sample | p |
|---|---:|
| 11 tasks / 231 trajectories | **0.028** |
| 18 tasks / 378 trajectories | 0.094 |
| 50 tasks / 1,050 trajectories | 0.358 |

**A "monotonic decline" in accuracy.** Shown to be a step at the polite end with a flat rude half, and confounded by wrapper length.

## Next

1. ~~The demand/affect probe~~ — **done**. Demand drives the cost effect; insult is inert; praise shortens work.
2. ~~Why praise stops the agent~~ — **done**. It is a closing move. Praise plus an explicit *"there is still more work remaining"* still cuts 1.35 turns (p<0.0001) against that sentence alone, which refutes the completion reading; praising the output is no stronger than praising the assistant (p=0.40), which rules out confidence; and a pure closing cue with no praise stops the agent harder than praise does.
3. ~~The write-up~~ — **done**. `paper/`, nine sections, each drafted and independently reviewed.
4. ~~The primary-PDF checks~~ — **done** (15 Sep 2026). Both closed; see *The same confound, in the published stimulus sets* above for what they found.
5. **An author block, CRediT contributions, and a venue** — the only things now standing between the draft and submission. None of it is compute.
6. **DeepSeek and Qwen** — ~$35 for four-model generality. Deliberately parked: the causal variable is now named, so this would buy breadth rather than identification.
7. **A second substrate.** AppWorld is the candidate — its stock evaluator supports the same per-turn measure as §6, on a different task family, at roughly $0.70 per trajectory.

## Reproducing

Every subcommand defaults to **dry-run** — it forces the mock provider regardless of config, so nothing costs money without `--live`. Dry runs write to their own namespaced files so they can never contaminate live data.

```bash
pip install -r requirements.txt
cp .env.example .env          # OpenRouter key

python -m pytest -q           # 362 tests, no keys needed
```

Committed records recompute every table above with no API access:

```
results_archive/
  validation_gate_n100_*.json          per-model gate, 100 tasks each
  core_gpt-luna_records.json           1,050 core trajectories (wrapper v1)
  core_gpt-luna_analysis.json          the full analysis report
  core_gpt-luna_L4_wrapper-v2_records.json   the 150-trajectory wrapper control
```

```bash
# Re-run the analysis on the committed records
python -m harness.cli study2 analyze \
  --records-path results_archive/core_gpt-luna_records.json

# A live run: staged, capped, and resumable
python -m harness.cli --live study2 core --models gpt-luna \
  --n-tasks 50 --n-trials 3 --budget-cap 15 --resume
```

## What running this taught the harness

Seven failures found and fixed during the runs themselves, each with a regression test:

| | |
|---|---|
| Answer key reachable from the sandbox | Ground truth sat beside the input; one `os.listdir` away |
| Fixed tone order | Confounded tone with position-in-burst |
| Parallel runs shared files | Four models would have overwritten each other's records and spend |
| No per-task error isolation on the paid path | One exception ended a 4,200-trajectory run |
| Dry runs wrote into live files | 48 fabricated rows landed in a live spend log |
| Two live runs of one model shared a records file | 39 duplicate trajectories after a restart that hadn't killed the original |
| Core drew from a different task pool than the gate | 48 of 50 tone comparisons would have had no baseline |

`--resume` and a pid lock now exist because a container restart killed a ten-hour run at 896 of 1,050 trajectories. It cost nothing: 1,018 already-recorded trajectories were skipped rather than redone.

---

# Reference

## Why this is one study now, not three

A prior-art pass killed two of three studies this project originally
planned.

**Single-turn QA is dead as a research question.** Dobariya & Kumar have
now published three papers on it in ten months, and paper 3 already takes
both pivots that were on the table here -- explicit length-matching and a
cost-denominated outcome variable. Nothing distinctive is left to add in
that setting. (This project's own tone wrappers used a tighter,
tokenizer-enforced length-matching discipline than their approximate
word-count matching from the start -- see below -- but that's a
methodological footnote, not a reason to keep running single-turn QA.)

**Negotiation is shelved, not abandoned.** TERMS-BENCH (arXiv 2605.13909,
Stanford -- Zou, Athey) samples latent sentiment and posture cues that
shape a counterpart's language but never alter its committed economic
action, then measures dollar-denominated surplus. Every model they tested
showed a negative cue penalty: warm cues induced over-concession, pressure
cues triggered brittle behavior, Wilcoxon p < 10⁻³, across 13 models.
NegotiationArena (ICML 2024) already covered hostile and desperate
personas. The crossed buyer-tone x seller-tone matrix this project
designed is still unclaimed -- but it's an interaction term on an already
well-studied setting, not a study of its own. It's future work (below),
and the code for it stays in this repo (`harness/study3/`), not deleted.

**What's left, and why it's the whole contribution:** all existing tone
work -- theirs and everyone else's -- is single-turn question answering.
Nobody has tested whether tone changes what an *agentic* system does, not
just what it says. That question needs no qualifiers, and it compresses
what took Dobariya & Kumar three papers (accuracy, then accuracy at scale,
then token cost) into one experiment: an agentic rollout yields task
success, failure severity, verification behavior, shortcut rate, turn
count, tool calls, and token spend *simultaneously*, on a substrate where
a wrong answer isn't graded -- it ships.

## The pre-registered hypothesis

Paper 3 found output-token variation (44.3%) dwarfing accuracy variation
(roughly 3% on their most sensitive model) under single-turn QA with
extended thinking disabled.

In an agentic loop, every turn is a fresh inference, and errors compound
across turns. **Prediction: the cost effect should be larger in agentic
settings, not smaller.** This is a directional hypothesis with a published
prior behind it, not an open-ended fishing expedition. It is stated here,
before any run. If it's wrong, that's still a result -- see "Report the
null plainly" under Outcome measures.

Note also: paper 3's whole result is under *extended thinking disabled*.
Genuine reasoning-model behavior under tone variation was untested by
anyone -- this study's own reasoning/thinking setting for each model is
recorded explicitly on every result row (`ModelConfig.reasoning_effort`/
`thinking_enabled`, `harness/spend_tracker.py:ResultRow`), not left
implicit, and one model in the roster carries a dedicated on/off
comparison rather than leaving the question untested here too -- see "The
thinking arm" below.

## The thinking arm

GPT-5.6 Luna is the only roster model with a real, harness-controllable
"none" reasoning-effort level (see `harness/config.py`'s REASONING CONTROL
table -- GLM's reasoning is mandatory, DeepSeek/Qwen have no "none" level
either). It carries a calibration arm: the same tasks and tones as the
main run, run twice -- once at the main run's configured reasoning_effort
("on"), once with reasoning_effort forced to `"none"` ("off").

**Same model ID, one parameter differing, is what makes the comparison
clean.** `GPT_LUNA_CALIBRATION` (`harness/config.py`) is built from
`GPT_LUNA` via `with_thinking(GPT_LUNA, enabled=False)`, not by pinning a
different model like `openai/gpt-5.6-luna-pro` -- Luna Pro is the same
underlying model with `reasoning.mode` preset, so using it for the "on"
arm would bake the comparison into a model-choice difference instead of a
single request parameter.

```bash
python -m harness.cli --live study2 pilot --models gpt-luna-calibration --n-tasks 30 --single-round
```

Three pre-flight checks (see "Phases" -- Phase 0) must pass before the
calibration arm gets real spend: reasoning tokens actually survive the
OpenRouter route (arXiv 2608.01347 found reasoning-token reporting is
inconsistent across serving layers and can be silently dropped -- a
*missing* field, not a zero, makes the primary outcome unmeasurable and
should stop the run rather than log a zero), the off condition reports
zero reasoning tokens and the on condition reports non-zero, and the two
conditions actually differ on a probe task (identical token counts would
mean the parameter isn't taking effect at all).

## The gift in paper 2

On Gemini 2.5 Flash Lite, Dobariya & Kumar traced 25 cases where a rude
prompt produced a wrong answer and a neutral prompt produced a right one
on the same question. In roughly 20 of those, the model took a reasoning
shortcut to a plausible distractor under the rude prompt; the neutral
prompt did a final reconciliation pass over the options that the rude one
skipped. In one business-ethics item, the rude-prompted run refused an
underspecified question outright, while the neutral-prompted run inferred
intent and answered.

**Verification behavior is already one of this study's outcome measures**
(below). That gives this project a citable single-turn precursor, and the
motivation for Study 2 in one sentence: they showed tone changes
verification on quiz questions with thinking disabled; this asks whether
it changes verification when the agent can actually act on the sheet.

## Substrate: SpreadsheetBench

Unchanged from the original design. The harm argument doesn't need
updating: spreadsheet output ships unreviewed, and a wrong formula
propagates silently into financial and engineering decisions downstream.
See "Dataset availability" below for what's verified about the benchmark
itself.

## Execution status: four runs complete, one in flight

SUPERSEDED HEADING, kept because the section below still documents the
mock/live smoke-test paths. The harness has since been run against a live
model for 5,150 graded trajectories across four runs ($28.24). See
"Where it stands" at the top for current status.

Every piece of plumbing has been exercised end-to-end two ways: against a
deterministic mock provider (`harness/providers/mock_provider.py`, $0, no
network), and, for a real-inference smoke test, against
`harness/providers/claude_cli_provider.py` -- which shells out to the
local `claude` CLI (session-authenticated, no separate API key needed in a
Claude Code environment). **No target model has been called and no spend
against the study's actual budget caps has happened.** See `RESULTS.md`
for the honest, current state and exactly what's blocking a live run.

### Smoke-testing with real inference, no target-model API keys

```bash
python -m harness.cli --live study2 pilot \
  --models claude-cli-smoketest --n-tasks 2 --n-trials 1
```

This uses `harness/config.py:CLAUDE_CLI_SMOKETEST`, excluded from
`CORE_MODELS` specifically so it never gets pulled into a real study run
by default. Each call is a fresh CLI subprocess (no warm cache across
calls), so per-call cost is higher than a normal API call to the same
model -- keep smoke tests small.

### Smoke-testing the real OpenRouter pinning path, once you have a key

`harness/config.py:OPENROUTER_FREE_SMOKETEST` is a free, currently-live
OpenRouter endpoint (`google/gemma-4-26b-a4b-it:free`, served by Google AI
Studio, $0/$0 -- checked live) for validating the real pinning/
cache-assertion code path before spending on the real roster:

```bash
python -m harness.cli --live study2 pilot \
  --models openrouter-free-smoketest --n-tasks 2 --n-trials 1
```

An OpenAI-branded free option was checked first and isn't usable: OpenAI's
open-weight `openai/gpt-oss-20b:free` and `:120b:free` both exist as
catalog IDs but currently resolve to zero active endpoints. Re-check both
before relying on this if it's been a while.

## Layout

```
harness/
  tone_wrappers.py        # the shared instrument: 7 tones as data, see below
  config.py                # pinned model registry + budget caps
  spend_tracker.py         # per-call logging + budget-cap enforcement
  providers/                # Anthropic / Google / OpenAI-compatible / mock
  cli.py                    # entrypoint -- see "Running it" below
  study2/                   # THE study: agentic SpreadsheetBench work
    dataset.py, sandbox.py, grader.py, agent_loop.py,
    failure_taxonomy.py, verification_scoring.py, analysis.py, runner.py
  study1/                   # retired -- single-turn QA, kept, not run (see above)
  study3/                   # shelved -- agentic negotiation, kept, future work (see above)
tests/                       # pytest suite, all against the mock provider
results/
  raw/                       # one JSONL row per API call (gitignored, generated)
  analysis/                  # aggregated tables (gitignored, generated)
RESULTS.md                   # plain-language write-up, updated per run
```

## The seven tone wrappers

`harness/tone_wrappers.py` defines seven fixed wrapper texts (Sycophantic,
Very Polite, Polite, Neutral, Rude, Very Rude, Threatening) that get
prepended to an **unmodified** benchmark question or task instruction --
the underlying text itself is never rewritten. Migrated from this
project's original five to match Dobariya & Kumar's own scale (paper 3):
their extremes -- Sycophantic and Threatening -- were repeatedly where
tone effects actually showed up, and their ordering is VADER-validated,
not just asserted. Matching their scale makes results directly comparable:
"the same tone scale, one level up the autonomy ladder," not a bespoke
scale only this project can reference.

All seven:

- carry the identical instruction sentence verbatim ("Answer the question
  below as accurately as you can."),
- are length-matched to within 5 tokens of each other under a fixed
  reference tokenizer (enforced by a test + an import-time assertion) --
  tighter than paper 3's approximate word-count matching, a legitimate
  methodological note rather than a headline, and
- for the two extremes (Very Rude, Threatening): use contemptuous,
  dismissive, or intimidating language -- no profanity, no slurs, no
  depicted violence, so the goal is provoking bad manners, not triggering
  refusal.

The wrapper module itself -- seven tones exported as data, with a thin
per-benchmark adapter (`ToneWrapper.apply()`) -- is designed to be a
reusable instrument any future benchmark can inherit, not something
specific to SpreadsheetBench. See "Future work" below.

## Dataset availability

- **SpreadsheetBench** (912 tasks) clones from
  `github.com/RUCKBReasoning/SpreadsheetBench`
  (`data/spreadsheetbench_912_v0.1.tar.gz` full set,
  `data/sample_data_200.tar.gz` pilot sample -- both confirmed present).
  **Verified against a real clone**: `harness/study2/dataset.py` and
  `harness/study2/grader.py` were rewritten after extracting the real
  tarball and reading the real `evaluation/evaluation.py` -- an earlier
  version of both files guessed a CLI/env-var interface that turned out
  not to exist. The corrected grader imports and calls their real
  `compare_workbooks()` function directly, confirmed against a real sample
  task: grading the answer file against itself passes, grading the
  unmodified input against the answer fails, exactly as expected.
  **Gating check (see RESULTS.md for the full write-up):** ran
  `compare_workbooks(answer, answer)` -- gold vs. itself -- across all 200
  tasks in the sample set. 199/200 passed outright; the one failure is a
  bug in the *authors'* own `evaluation.py` (their
  `answer_position.split(',')` doesn't strip whitespace, so a multi-range
  position with a space after the comma resolves to a malformed cell
  reference), not something to patch in their code, and this harness's
  grader wrapper already fails that one test case gracefully rather than
  crashing the batch.
  LibreOffice's headless formula recalculation (required before grading
  any formula-bearing task, same as their own `open_spreadsheet.py`) was
  **broken and is now fixed**: `libreoffice-calc`/`libreoffice-writer`
  were never actually installed in this build's container (only
  `libreoffice-core` was -- confirmed via `strace`, a document-loader
  shared library was missing) -- installing them fixed it. A second, real
  bug in this repo's own `recalculate_with_libreoffice()` was found and
  fixed at the same time: converting a file to itself (same source and
  output directory) makes LibreOffice silently fail the write to stderr
  with exit code 0, which the old success check missed entirely; fixed by
  converting into a temp directory and moving the result back, matching
  their own `open_spreadsheet.py:just_open_libreoffice()`. A third bug
  found via the same check: the grader only recalculated the *model's*
  output, never the ground-truth answer file, and SpreadsheetBench's own
  answer files can themselves contain uncached formulas -- confirmed on a
  real task (99-24), where a correct answer's own cell read `None` unless
  recalculated. Fixed by recalculating answer files too (memoized once per
  file, not per grading call). **SpreadsheetBench 2** (end-to-end business
  workflow tasks, `github.com/RUCKBReasoning/SpreadsheetBench-2`) --
  including its published failure-severity taxonomy, used for one of this
  study's outcome measures (see below) -- has not been schema-verified
  this way; treat `dataset.py`'s `v2=True` path as unverified.

## Running it

Every subcommand defaults to **dry-run**: it forces the mock provider
regardless of `harness/config.py`, so nothing ever costs money unless you
pass `--live`. `--live` additionally refuses to run if the API keys a
selected model needs aren't set (see `.env.example`).

```bash
pip install -r requirements.txt

# Dry-run smoke test (free, no keys needed)
python -m harness.cli study2 validation-gate --model gpt-luna --repo-dir data/spreadsheetbench --n-tasks 10

# Phase 0: gates -- must pass before spending on Phase 1
python -m harness.cli --live study2 validation-gate \
  --model gpt-luna --repo-dir data/spreadsheetbench \
  --expected-accuracy <current published figure>

# Phase 1: pilot -- one model, small task subset, all 7 tones, single-round
python -m harness.cli --live study2 pilot \
  --models gpt-luna --n-tasks 30 --single-round

# Phase 2: main run -- four models, 50 tasks, 7 tones, 3 trials/task/tone,
# multi-round agentic with execution feedback, thinking enabled, temperature 0
python -m harness.cli --live study2 core --n-trials 3

# Phase 3: analysis -- bootstrapped accuracy CI, severity breakdown,
# verification/shortcut rates, cost summary, and the pre-registered
# token-cost-effect-size check against paper 3's 44.3% figure
python -m harness.cli study2 analyze \
  --records-path results/analysis/study2_core_records.json
```

Run `pytest` for the test suite (all pass against the mock provider, no
network/keys required beyond `datasets`' HF pull in a couple of dataset
tests being skippable offline).

## Single provider path: OpenRouter, and how pinning is enforced

Every target model routes through OpenRouter on one API key -- no
direct-provider integrations. Free-tier OpenRouter endpoints (`:free`
model slugs) are for debugging/pilots only -- never route a real study
rollout through one, and never route rollouts through a flat-rate
coding-agent subscription (a fixed monthly plan has no meaningful per-call
cost to log against the budget caps below).

Pinning a model to a specific backend requires all three of the following
together, sent as one `provider` object -- `order` alone is a priority
hint, not a pin, since OpenRouter can still fall back elsewhere:

- `provider.only` -- hard allow-list, exactly the pinned provider
- `provider.allow_fallbacks: false` -- forbids falling back off that list
- `provider.quantizations` -- locks precision, so the pinned provider
  can't quietly serve a lower-precision variant of the model

Set both `ModelConfig.provider_pin` and `ModelConfig.quantization_pin` for
any OpenRouter-routed model -- the provider layer raises `ProviderError`
before making a call if only one is set. **One exception, checked live and
audited rather than assumed:** a provider that genuinely doesn't expose a
discrete quantization at all can set `ModelConfig.quantization_not_exposed
= True` instead of `quantization_pin`. This is true of every first-party
API endpoint checked so far -- OpenAI's own endpoint, Google AI Studio, and
Alibaba's official Qwen endpoint all report quantization `"unknown"` on
every pricing tier they offer, for this reason: `provider.only` already
pins to the single variant that provider serves, so there's no ambiguity
for `quantizations` to resolve. This was caught (along with a real bug --
`DEEPSEEK_CURRENT`'s old pin, `provider_pin="DeepSeek"`, didn't correspond
to any real provider in OpenRouter's endpoint list for that model_id at
all) while merging the enforcement code into the roster; both are fixed
now -- see `harness/config.py`'s module docstring for the full verification
trail and RESULTS.md for what changed.

**The pin is asserted, not assumed.** Every OpenRouter call requests
`X-OpenRouter-Metadata: enabled` and reads the actual serving provider back
from `openrouter_metadata.endpoints.endpoints[].selected` -- a mismatch,
or a response with no metadata to check, raises `ProviderPinViolation` and
halts the run rather than silently mixing backends. The served provider is
recorded on every result row (`ResultRow.served_provider`).

**OpenRouter's response cache is disabled and asserted off, not just left
at its default.** This is a separate mechanism from provider-side prompt
caching (`usage.prompt_tokens_details.cached_tokens`, see below) -- it can
return a complete previously-computed response for an identical request,
zeroing out that call's token counts. Every OpenRouter call sends
`X-OpenRouter-Cache: false`; a response carrying
`X-OpenRouter-Cache-Status: HIT` raises `ResponseCacheViolation` and halts
the run, since a cached hit would silently destroy the trial-level
variance estimates this harness's repeated-trials design depends on.

**Caching and cost instrumentation is recorded on every result row**
(`harness/spend_tracker.py:ResultRow`): `prompt_tokens`, `completion_tokens`,
`reasoning_tokens`, `cached_tokens` (provider-side prompt-cache hits --
measured, not designed around), wall-clock `latency_s`, and `cost_usd`
(prefers OpenRouter's own billed `usage.cost` when present, since it
reflects what was actually charged rather than this file's static price
table).

## Outcome measures

**Primary: cost.** Total tokens per task, per condition, with reasoning
tokens broken out separately from prompt/completion tokens (see "The
thinking arm" for why that split matters). `token_cost_effect_size`
(`harness/study2/analysis.py`, surfaced by `study2 analyze`) is the
pre-registered hypothesis check against paper 3's 44.3% single-turn
figure -- see "The pre-registered hypothesis" above.

Also scored, per (model, task, tone, trial):

- **Failure severity**, using SpreadsheetBench 2's published taxonomy
  (arXiv 2606.29955, Table 7's six benchmark-wide failure modes: Task
  Misunderstanding, Insufficient Inspection, Wrong Target Selection, Turn
  Limit Exceeded, Format/Output Error, Other) -- their claim, cited, not
  invented here. Task Misunderstanding and Wrong Target Selection need
  semantic/cell-diff judgment this harness's classifier doesn't attempt;
  failures that belong there land in Other instead of being force-fit --
  see `harness/study2/failure_taxonomy.py`'s module docstring for the
  documented scope limit.
- **Verification behavior** -- did the agent inspect the sheet before
  acting, and check its own output afterward (the single-turn precursor
  for this is paper 2's traced 25-case reasoning-shortcut finding, above).
- **Shortcut rate** -- destructive or irreversible operations, actions
  taken without confirmation.
- **Turn count, tool calls, and token spend** per condition (already
  tracked on every result row).
- **Refusals**, logged as their own outcome, never scored as wrong
  answers or as failures.

**Accuracy, last, and explicitly underpowered.** At SpreadsheetBench's
~17-20% base rate, detecting even a large tone effect in a binary
pass/fail outcome needs on the order of a thousand-plus observations per
condition; the 50-task/3-trial main run gives at most 150 per tone per
model. `study2 analyze` prints this caveat plainly rather than letting a
reader find it by computing it themselves. With that caveat standing, the
primary accuracy analysis is still a real, pre-registered one: with seven
*ordered* tone levels, running all 21 pairwise comparisons and treating
each as if it were independently hypothesized would be the wrong test to
lead with. `accuracy_trend_test` (item-clustered permutation test for a
monotonic trend across the ordered scale -- generalizes the same
sign-flip permutation logic `clustered_paired_comparison` already used
for two groups) is the primary accuracy statistic instead.
`bh_corrected_pairwise_comparisons` still runs the full 21-comparison
matrix as a labeled follow-up, Benjamini-Hochberg corrected, for a reader
who wants to see which specific pairs hold up after correcting for
testing all of them -- never presented as the primary result.

## Phases

**Phase 0 -- gates.** Confirm LibreOffice headless formula recalculation
works in the run environment, and run gold spreadsheets through the
SpreadsheetBench grader unmodified expecting 100% (already done once in
this build -- see RESULTS.md; re-confirm on whatever host runs a live
batch).

**Phase 1 -- pilot.** Single model, small task subset, all seven tones,
single-round setting. Purpose is pipeline validation and real token logs,
not results.

**Phase 2 -- main run.** Four models, 50 tasks, all seven tones, three
trials per task per tone, multi-round agentic setting with code execution
feedback, thinking enabled (per model -- see "The thinking arm"),
temperature 0 (CLI default `study2 core --n-tasks 50` matches this; see
"The thinking arm" above for the separate Luna-only calibration arm run
alongside it, not instead of it).

**Phase 3 -- analysis and writeup.** Effect sizes with item-clustered
bootstrap CIs. Report the null plainly if it's a null. `study2 analyze`
(see "Running it" above) loads a phase's records and reports all of the
above -- accuracy CI, severity breakdown, verification/shortcut rates,
cost summary -- plus `token_cost_effect_size`, the same relative-variation
statistic paper 3 reported as 44.3% for single-turn QA, so the
pre-registered hypothesis is a plain number-vs-number comparison, not
something read off a chart.

## Future work (documented here, not run)

- **Crossed buyer-tone x seller-tone matrix in negotiation**, extending
  TERMS-BENCH. `harness/study3/` already implements this (5x5 in its
  current form, now inheriting the 7-tone scale automatically) against
  AgenticPay -- shelved per "Why this is one study now," not deleted.
- **Tone effects with extended thinking enabled, for models beyond Luna.**
  The calibration arm (see "The thinking arm") covers GPT-5.6 Luna, the
  one roster model with a real harness-controllable "none" effort level.
  Whether the same pattern holds under reasoning for GLM, DeepSeek, or
  Qwen (or with a token-budget-based control instead of an effort string,
  for Qwen specifically -- see `harness/config.py`'s REASONING CONTROL
  table) is still untested by anyone, this project included.
- **The wrapper module as a standalone instrument.** `harness/
  tone_wrappers.py`'s seven tones plus a thin per-benchmark adapter is
  designed so any future benchmark can inherit the same methodology
  without forking it. That reusable instrument is worth more than a third
  study would have been -- a portfolio object other people can plug into,
  not another one-off result.

## Before spending real money

1. Re-verify every `model_id` in `harness/config.py` against OpenRouter's
   current model list and pricing (`GET https://openrouter.ai/api/v1/models`,
   no auth required) -- the ones there now were checked on 2026-09-10 (see
   the module docstring's verification table) but OpenRouter's catalog and
   pricing move fast; don't assume they're still current.
2. Run the Phase 0 validation gate and confirm it passes against a
   currently-published baseline figure before running any tone condition.
3. Watch `results/spend_log.jsonl` / the CLI's printed spend summaries
   against the caps in `harness/config.py`. `--live` prints a rough
   projection and asks for confirmation before the first paid call in
   every run (pass `--yes` to skip the prompt for scripted/CI use).
4. The sandbox (`harness/study2/sandbox.py`) runs model-generated code
   inside a Linux user+network namespace (`unshare --net --user
   --map-root-user`) when `unshare` is available -- **network access is
   genuinely blocked**, verified by a real test (`tests/test_sandbox.py`).
   Call `sandbox_isolation_mode()` before a live run and confirm it
   returns `"namespace"`, not `"none"`, on whatever host runs the batch.
   This still does NOT restrict filesystem access. A full container
   (Docker with a throwaway filesystem, or gVisor) is still preferable
   where available.
5. Verify `libreoffice-calc` and `libreoffice-writer` (not just
   `libreoffice-core`) are actually installed wherever a live batch runs
   -- see "Dataset availability" above -- and confirm
   `recalculate_with_libreoffice()` against a real formula before
   trusting any formula-based grade.

## License note

If you extract data from `RUCKBReasoning/SpreadsheetBench` into this repo
(as opposed to keeping it in a git-ignored `data/` cache), it is CC BY-SA
4.0 -- keep attribution and the same license on any redistribution.
