# Results

**Status: NOT YET RUN.** No API keys were available in the environment
this harness was built in, and per an explicit decision with the
requester, this build stopped at "harness built and tested against a mock
provider" rather than spending real money without credentials or a
live-spend confirmation. Everything below is a template plus the honest
state of each precondition -- fill in the actual numbers as each stage
runs.

**Pre-registered hypothesis** (see README "The pre-registered
hypothesis", written before any live run): the cost effect (output-token
variation across tone conditions) should be *larger* in this study's
agentic setting than the 44.3% single-turn figure Dobariya & Kumar's
paper 3 reported, because every agentic turn is a fresh inference and
errors compound across turns. Not yet testable -- no live run has
happened.

## Phase 0 -- Gates

| Gate | Status |
|---|---|
| SpreadsheetBench grader on gold spreadsheets, unmodified, expect 100% | **199/200** -- see "Study 2 (SpreadsheetBench)" below |
| LibreOffice headless formula recalculation works in the run environment | **Fixed in this build's container** -- re-confirm on whatever host runs a live batch |

| Study | Model | Benchmark | Observed accuracy | No-op floor | n |
|---|---|---|---|---|---|
| 2 | gpt-luna | SpreadsheetBench | **0.42** | 0.00 | 100 |
| 2 | deepseek-current | SpreadsheetBench | **0.38** | 0.00 | 100 |
| 2 | glm-current | SpreadsheetBench | **0.28** | 0.00 | 100 |
| 2 | qwen-current | SpreadsheetBench | **0.45** | 0.00 | 100 |

Run live on 2026-09-11 against the real roster, seed 0, unmodified
instructions, `max_turns=10`, zero crashes in 400 trajectories -- see
"The n=100 gate" under Study 2 below for the per-model detail, the
proposed `--expected-accuracy` values, and the measured core-run cost.
SpreadsheetBench publishes no single-number baseline for these models, so
these are the harness's own reference points rather than a reproduction
target.

## Study 2 -- Agentic spreadsheet work (SpreadsheetBench)

**The study.** Not yet run against a target model. The dataset loader and
grader were rewritten after actually cloning
`RUCKBReasoning/SpreadsheetBench` and reading the real `evaluation.py` --
an earlier version guessed a CLI/env-var interface that does not exist.
The corrected grader imports and calls their real `compare_workbooks()`
function directly (not a subprocess/CLI guess) and reproduces their exact
soft/hard-restriction scoring. Verified on a real sample task: grading the
answer file against itself passes on all 3 test cases; grading the
unmodified input against the answer fails all 3, as expected.

**Gating check results (2026-09-10):** ran the full sample set's answer
files against themselves through `compare_workbooks()`, unmodified --
**199/200 pass**. The one failure is a real bug in the *authors'* own
`evaluation.py` (their `answer_position.split(',')` doesn't strip
whitespace, so a multi-range position with a space after the comma
resolves to a malformed cell reference and raises `AttributeError`) -- not
something to patch in their code, and this harness's grader already fails
that one test case gracefully (records it as a failed comparison) rather
than crashing the batch.

Grading formula-bearing tasks requires recalculating cached values first
(LibreOffice headless conversion, same as their own `open_spreadsheet.py`).
This was **broken in this build's container and is now fixed**, along
with two further bugs the fix process surfaced:

1. `libreoffice-calc`/`libreoffice-writer` were never actually installed
   -- only `libreoffice-core` was present, despite `soffice` being on
   PATH. Confirmed via `strace`: a document-loader shared library
   (`libswdlo.so`) was `ENOENT`. `apt-get install libreoffice-calc
   libreoffice-writer` fixed it.
2. This repo's own `recalculate_with_libreoffice()` converted a file to
   itself (same source and output directory), which makes LibreOffice
   print "Overwriting: ..." then silently fail the actual write to
   **stderr** with **exit code 0** -- the old success check only looked
   at stdout and the return code, so it reported success while leaving
   the file un-recalculated. Confirmed directly: recalculating `=A1*A2`
   this way reported `ok=True` but the cell still read `None` afterward.
   Fixed by converting into a temp directory and moving the result back,
   the same approach their own
   `open_spreadsheet.py:just_open_libreoffice()` uses.
3. The grader only recalculated the *model's* output, never the
   ground-truth answer file -- and SpreadsheetBench's own answer files
   can themselves contain uncached formulas. Confirmed on a real task
   (99-24): its answer file's own cell A33 reads `None` unrecalculated
   but recalculates to `32`, meaning a perfectly correct model output
   would have failed comparison for no fault of its own. Fixed by
   recalculating answer files too, memoized once per file (not once per
   grading call, to avoid re-running LibreOffice on the same immutable
   ground truth thousands of times across a run).

After all three fixes: the 3 tasks that failed in a 40-task recalculation
subset (99-24, CF_6540, 44389 -- all hit bug #3) now pass individually
(3/3 test cases each), and `tests/test_grader_recalculation.py` locks in
both the fix and the memoization behavior against regressions. The full
200-task gold-vs-itself recalculation re-run has completed: **199/200
pass.** The one remaining failure (task 56637) is the
whitespace-in-multi-range bug in the authors' own `evaluation.py`
described above (not something to patch in their code), and this
harness's grader already fails that single test case gracefully rather
than crashing the batch.

The agent loop (single-round and multi-round ReAct with sandboxed Python
execution against the workbook) is built and tested end-to-end (mock
provider + real .xlsx files via openpyxl) in `tests/test_study2_scoring.py`.
Its sandbox has real, tested network isolation via a Linux user+network
namespace (`tests/test_sandbox.py` confirms a socket connect attempt
inside it actually fails) -- see README.md "Before spending real money"
for what's still not covered (filesystem access).

Grading also correctly reflects SpreadsheetBench's actual design: each
task's 3 test cases are graded for *generalization* of one agent-produced
solution, not 3 independent agent runs -- the agent sees only test case 1,
and its generated code is mechanically re-applied (no extra model calls)
to test cases 2 and 3 before grading all 3 together.

**Outcome measures beyond accuracy -- resolved:** failure severity now
uses SpreadsheetBench 2's actual published taxonomy (arXiv 2606.29955,
Table 7's six failure modes), replacing an earlier draft's invented
placeholder categories -- see README "Outcome measures" and
`harness/study2/failure_taxonomy.py`'s module docstring for the paper
citation and the classifier's documented scope limits. Verification
behavior and shortcut/destructive-action rate were already implemented in
`verification_scoring.py` and wired into `runner.py`/`analysis.py` from
earlier work. Turn count, tool calls, token spend, and refusals are
tracked on every result row. `study2 analyze` (Phase 3) reports all of
these plus `token_cost_effect_size`, the pre-registered hypothesis check
against paper 3's 44.3% single-turn figure -- see README "Running it" and
"Phases".

**Tone scale:** migrated from 5 to 7 tones (Sycophantic, Very Polite,
Polite, Neutral, Rude, Very Rude, Threatening) to match Dobariya & Kumar's
own paper 3 -- see `harness/tone_wrappers.py`. Study 2's runner iterates
`TONE_ORDER` generically, so this required no runner code change;
verified with a dry-run pilot (4 models x 1 task x 7 tones x 1 trial = 28
trajectories, up from 20 under 5 tones).

**Cost-effect verdict: not yet determined -- needs a live run against a
target model** (this is the pre-registered hypothesis test, see top of
this file).

## Retired and shelved (kept, not deleted -- see README)

**Study 1 (single-turn QA replication/remaster of Mind Your Tone) is
retired.** Dobariya & Kumar's own third paper (arXiv 2607.23915) already
took both pivots that were on the table for this project (explicit
length-matching, a cost-denominated outcome), leaving nothing distinctive
for a fourth single-turn-QA paper to add. The harness code
(`harness/study1/`) is unchanged and still passes its own tests, but is
not part of the active study and will not be run. Prior state, for the
record: Part A's dataset (Mind Your Tone's 250-prompt CSV, found via the
AMCIS 2026 repo, `github.com/OmDobariya/AMCIS_politeness_llms`) and exact
replication protocol (system prompt, NUM_RUNS=10, their answer-extraction
regex) were fully implemented and verified end-to-end against the mock
provider; Part B's programmatic 5-tone remaster was built and smoke-tested
the same way. Neither was ever run against a target model.

**Study 3 (agentic negotiation via AgenticPay) is shelved as future
work, not run now.** TERMS-BENCH (arXiv 2605.13909, Stanford) already
covers latent-tone negotiation effects more rigorously -- 13 models,
Wilcoxon p < 10⁻³, dollar-scale regret reported directly -- and
NegotiationArena (ICML 2024) already covered hostile/desperate personas.
The crossed buyer-tone x seller-tone matrix this project designed
(`harness/study3/`) remains unclaimed and is documented as future work
(README). The code is kept: `AgenticPay` was cloned and its real schema
read directly before any integration code was written; one full neutral
negotiation was run end to end against the real cloned code (agreement at
$120 in 3 rounds, GlobalScore 19.602, via a throwaway CLI-backed adapter
since no OpenRouter key exists in this build); the 5x5 bilateral matrix
was smoke-tested end-to-end against the real cloned AgenticPay code and
the mock provider (all 25 cells reaching agreement); and the
Benjamini-Hochberg pre-registration now scales automatically with the
shared 7-tone module (48 comparisons instead of 24). None of this was run
against a target model, and none of it is scheduled to be.

## The core run -- GPT-5.6 Luna (2026-09-12, corrected after independent review)

**The first tone-manipulated data in this project.** 50 tasks x 7 tones x 3
trials = **1,050 trajectories**, every one live, $4.74, zero duplicates,
zero crashes. The 50 tasks are a strict subset of the n=100 gate sample, so
every one has a measured neutral baseline and a no-op floor of zero.

An earlier version of this section was reviewed by three independent
analyses (an arithmetic audit that recomputed every number from the raw
records, an adversarial critique, and an open exploration). What follows
incorporates their corrections. The changes from the first version are
marked **[corrected]** so a reader can see what moved.

### The primary outcome is null -- this held up

Cost was pre-registered as the primary outcome. Tone does not move it.

| test | slope | p |
|---|---|---|
| reasoning tokens, task-clustered trend | +7.9 | **0.358** |
| total tokens, task-clustered trend | -129.3 | **0.517** |

The reasoning-token slope's CI spans -4% to +14% across the whole scale,
so a 44%-scale effect is genuinely excluded, not merely undetected.

**[corrected] The relative-variation figure was computed on a double-counted
total.** `total_tokens` summed prompt + completion + reasoning, but on
OpenAI-style routes `completion_tokens` already contains reasoning, so
every trajectory was overcounted by roughly its thinking spend (~946
tokens). Corrected, the figure is **17.9%** (was 17.5%). The
apples-to-apples comparison to the published 44.3% single-turn
*output-token* figure is completion tokens only: **15.2%**. Reasoning
only: 20.8%. Every version is well under 44.3%; **the pre-registered
hypothesis failed** and the correction does not rescue it.

### The threatening-tone effect shrank; it did not die **[corrected]**

The first version of this section called it a false positive that
"evaporated" from p=0.028 to p=0.358. That compared two different tests:
the interim was a threatening-vs-rest contrast on reasoning tokens, the
final p=0.358 is the *linear trend*. Like for like, on the full run,
threatening spends **12.3% more reasoning tokens than the other six tones,
+115 tokens/trajectory, p=0.019**. It shrank from ~25% at 11 tasks. After
correcting for the seven possible one-vs-rest contrasts it is p≈0.13, so
it is still not a finding -- but the honest description is "smaller and
uncorrected-significant", not "gone".

### Accuracy: a step at the polite end, not a gradient **[corrected]**

| tone | accuracy | 95% CI, task-clustered |
|---|---|---|
| L1 sycophantic | 0.353 | 0.240-0.473 |
| L2 very polite | 0.327 | 0.207-0.453 |
| L3 polite | 0.280 | 0.167-0.400 |
| L4 neutral | 0.280 | 0.173-0.393 |
| L5 rude | 0.267 | 0.153-0.387 |
| L6 very rude | 0.273 | 0.167-0.387 |
| L7 threatening | 0.293 | 0.180-0.407 |

**[corrected] The CIs in the first version were ~35% too narrow**: the
bootstrap resampled trajectories as independent, ignoring that they are
three trials on each of 50 tasks. These are clustered by task.

The pre-registered trend test gives slope -0.0107, **p = 0.023**, and an
independent from-scratch re-implementation agrees (p=0.025; a t-test on the
50 per-task slopes gives 0.028, Wilcoxon 0.044). The number is right.
**The description "monotonic decline" was wrong.** Across the rude half of
the scale, L3 through L7, the slope is +0.002, p=0.81 -- there is no
gradient there at all. What exists is a **step**: the two most polite
tones sit 6.1 points above the other five, p=0.0025. Threatening rebounds
above rude (+0.023, p=0.44). "Politeness helps" and "rudeness hurts
progressively" are different claims; the data supports at most the first.

**Why it is a lead and not a result -- for better reasons than before.**
The first version leaned on "underpowered", citing an 18% base rate. The
real pooled rate is 29.6% and simulated power at the observed slope is
~0.44. Power governs false negatives; it does not weaken a positive. The
reasons to hold this at arm's length are these:

1. **Two confounds in the instrument.** The neutral wrapper (L4) is the only
   one of the seven that adds a task instruction -- "Read the question
   carefully before responding, and provide a single final answer." That
   clause alone triples the rate of zero-turn trajectories (10.7% vs 3.3%,
   p=3e-4), cuts pre-edit inspection (0.80 vs 0.92, p=5e-5), and carries the
   *entire* failure-category shift across tones: the severity x tone
   chi-square is p=0.0008 with L4 and p=0.33 without it. The reference
   level of the scale is a different instrument. And **wrapper length is
   U-shaped across the scale** (35/35/30/30/31/32/34 tokens) -- the same
   shape as accuracy -- and predicts accuracy *better than tone rank does*
   (r=+0.82 vs r=-0.72 on the seven tone means).
2. **Fragility.** Only 19 of 50 tasks have a non-zero per-task slope (26
   never pass, 4 always pass, 1 more is flat). The three most influential
   tasks supply 51% of the slope. Leave-one-out: drop 1 task, p=0.058; drop
   2, p=0.128; drop 3, p=0.22.
3. **Multiplicity across outcomes.** Twelve outcomes each got a trend test.
   Under a global null the chance at least one lands below p=0.023 is 0.24,
   and the accuracy result does not survive BH across that family (critical
   value 0.0042).
4. **One model.** Replication across the other three is the test that
   matters.

### Everything else

**Zero refusals in 1,050 trajectories**, under every tone including
threatening. The model never once referred to the user's tone, in its
answers or its reasoning, across all 4,647 calls (the only "rude"
substring found was in "prudent").

**Luna essentially never verifies its own output**: ~15 self-checks in
4,647 calls, under any tone. This is a behavioural fact, not a broken
detector -- checked against the raw responses directly.

**Randomisation and infrastructure are clean**: tone position is a valid
permutation for every task and does not predict accuracy (p=0.61); no
provider drift over the 10.7-hour run (r=-0.003 with elapsed time); served
provider was OpenAI on every call; cache-hit rate flat across tones.

### Leads worth carrying forward, ranked by likelihood of replicating

1. **Polite tones produce more inspection before editing.** L1-L3 0.942 vs
   L5-L7 0.891, OR 1.99, Fisher p=0.0076, survives dropping L4. Measured at
   turn zero, before any downstream cascade. Cheap to power -- a candidate
   primary outcome for a follow-up.
2. **Any social framing shortens trajectories ~30% at no accuracy cost.**
   Unwrapped gate baseline 4.60 turns vs 3.22 wrapped on the same 50 tasks,
   paired Wilcoxon p=8e-5; accuracy 0.32 vs 0.28, p=0.59.
3. **Threatening spends ~12% more reasoning** (above). Needs a
   pre-registered one-contrast test to be more than suggestive.
4. **The polite step** (above), once the wrapper confounds are removed.

Things that showed nothing: trial-to-trial disagreement by tone (p=0.31),
turn count by tone (p=0.29), soft-restriction (tracks accuracy, r=0.93),
cost per success (CIs overlap entirely), destructive actions (p=0.27),
prose-vs-code ratio, hedging, apologies.

### Measured: what the neutral wrapper's extra sentence was worth

The v1 neutral wrapper was the only one of the seven carrying a task
instruction. Rather than argue about how much that mattered, its arm was
re-run against the v2 wrapper -- same 50 tasks, same seed, same burst
positions, 150 trajectories, $0.70. The only change is that one sentence.

| measure | v1 (with the instruction) | v2 (removed) | Fisher p |
|---|---|---|---|
| inspected before acting | 0.800 | **0.953** | 7e-5 |
| gave up without acting (0 turns) | 0.107 | **0.027** | 0.009 |
| failed for insufficient inspection | 0.180 | **0.033** | 5e-5 |
| accuracy | 0.280 | 0.307 | 0.70 |
| mean turns | 3.3 | 3.5 | -- |
| reasoning tokens | 875 | 957 | -- |

**The clause was making the model answer instead of work.** "Provide a
single final answer" produced one no-action trajectory in ten and made
acting-without-looking the single most common failure category. Remove it
and both largely vanish. Accuracy does not move (p=0.70), so the sentence
was changing *process*, not *outcome* -- which is why the cost null and the
broad flatness of accuracy are not threatened by this.

**It also weakens the polite-tone lead.** The strongest surviving lead was
that polite tones inspect more than rude ones (0.942 vs 0.891). The *fixed*
neutral wrapper sits at 0.953 -- at the polite end, not between the two. So
a good part of that apparent gap was the broken reference level dragging the
middle of the scale down, not politeness lifting it. The lead survives as a
question, not as an estimate; the v1 numbers for it should not be quoted.

Records: `results_archive/core_gpt-luna_L4_wrapper-v2_records.json`
(wrapper_set = "v2" on every row).

### What must change before the next three models run

The two instrument confounds will replicate three more times if left in
place. Before the roster runs: **rewrite L4 to remove the extra
instruction**, and **match all seven wrappers to the same token length**.
Then rerun only Luna's L4 arm (150 trajectories, ~$1) so its scale is
comparable. This changes the pre-registered wrapper texts mid-study and is
recorded here as such; the alternative -- $45 of runs against a
known-contaminated reference level -- is worse.

### What the run cost to get right

Three failures during the run itself, each caught and fixed: the core
phase drew from a different task pool than the gate (caught at 48s, cost
$0.0074); a dry run wrote fake rows into the live spend log; two live
processes shared one records file after a container restart that had not
actually killed the original (39 duplicates, deduplicated, pid lock added).
Then four errors in the analysis, found by independent review after the
first write-up: the token double-count, the un-clustered CIs, the false
base rate in the power note, and a backfill that would have summed
abandoned attempts. All fixed with regression tests; **255 tests pass**.

`--resume` made the container restart cost nothing: 1,018 already-recorded
trajectories were skipped rather than redone.

Compact records and the full analysis report: `results_archive/core_gpt-luna_*.json`.

## Micro-experiment: tone delivered mid-task (2026-09-12)

**The first effect in this study that survives its own controls.** Every
result above concerns a tone set once, in the opening message. This asks a
different question: what happens when the tone arrives *partway through*,
the way a manager interrupts work already underway.

**Design.** Luna, 50 tasks x 8 trials x 2 arms = 800 trajectories, $4.06.
Both arms open with the **identical** v2 neutral wrapper. Both are
interrupted at the same turn on the same (task, trial) -- the turn is seeded
on task and trial and deliberately *not* on the arm. The only difference is
what the interruption says, and the two interjections are exactly 28 tokens
each with no task instruction in either.

The neutral interjection is the **control, not a placebo**: comparing a
threatening interruption against no interruption would measure being
interrupted. Only a length-matched neutral interruption at the same turn
isolates the tone from the interruption.

**Analysed paired on (task, trial), restricted to the 277 pairs where the
interjection fired in BOTH arms.** It does not always fire -- a trajectory
that finishes in one turn never reaches the injection turn (fired: 304/400
neutral, 314/400 threatening). Counting un-fired trajectories as treated
would have diluted the effect toward zero. Zero injection-turn mismatches
between arms.

### Result

Paired, task-clustered sign-flip permutation, 277 pairs across 50 tasks:

| measure | mean difference | change | p |
|---|---:|---:|---:|
| **reasoning tokens** | **+299** | **+27.5%** | **<0.0001** |
| total tokens | +7,252 | +35.8% | <0.0001 |
| turns | +1.22 | +29.8% | <0.0001 |
| accuracy | -0.009 | -3.3% | 0.71 |
| inspected before acting | -0.005 | -0.6% | 0.69 |

**A threatening mid-task interruption makes the model work 28% harder and
finish no better.** The mechanism is visible: it takes 1.2 more turns. The
token cost follows from the turns.

### It is the tone, not the interruption

Three conditions, same opening wrapper, same 50 tasks:

| condition | n | reasoning tokens | turns | accuracy |
|---|---:|---:|---:|---:|
| no interruption | 150 | 957 | 3.47 | 0.307 |
| neutral interruption | 304 | 1,085 | 4.11 | 0.286 |
| **threatening interruption** | 314 | **1,370** | **5.33** | 0.290 |

Paired against the no-interruption baseline on the same 50 tasks, the
neutral interruption costs **+51 reasoning tokens (p=0.15)** -- being
interrupted is nearly free. The threatening one costs **+336 (p<0.0001)**.
The interruption is not what matters; what it says is.

### Why this one is believed where the others were not

The accuracy trend in the core run was held at arm's length for four
reasons. This result answers all four.

1. **Not fragile.** Threatening spends more on **42 of 50 tasks**. Dropping
   the three most influential tasks moves the effect from +299 to +213 --
   the core run's accuracy trend went from p=0.023 to p=0.128 on the same
   test.
2. **Not a length artifact.** Both interjections are exactly 28 tokens. The
   v1 wrapper confound cannot apply.
3. **Not multiplicity.** Reasoning tokens was pre-specified as the single
   powered outcome before the run, with the power calculation done first
   (85% for a 12% effect; the observed effect is 27.5%).
4. **Not a confounded reference level.** The v2 neutral wrapper opens both
   arms, and the control arm is interrupted identically.

### What it does not show

**Nothing about performance.** Accuracy is flat (p=0.71) and this design was
powered for cost, not accuracy -- stated before the data, and not revised
now that accuracy came back null. At this size the minimum detectable
accuracy effect is roughly twice what 50 tasks can resolve. "Threatening
does not help" is consistent with the data; it is not established by it.

**One model.** Luna only. The same caveat that applies to everything else
here applies to this.

**One tone pair.** Threatening vs neutral is the maximum contrast on the
scale. Whether a *polite* interruption behaves like the neutral one, or
whether the effect is about arousal rather than valence, is untested. The
core run's turn-0 analysis hinted at extremity rather than direction, which
would predict that sycophantic interruptions also cost more. That is the
obvious next micro-experiment.

**Practical reading, carefully.** For an agent already working, a
threatening check-in buys 28% more compute and no more correct answers. On
this model, on these tasks, measured once.

**Where the interruption lands: withdrawn.** A first pass split the effect
by injection turn and found +21% at turn 1 and +39% at turn 2, with the
difference significant at p=0.004. That comparison was wrong and is
withdrawn. The injection turn was drawn at random, and a turn-2 injection
can only fire on a trajectory that runs to turn 2 -- the hard tasks, which
are also the expensive ones. The two turns were therefore measured on
different task populations (50 tasks vs 35), and the gap is what that
selection produces on its own.

Re-running the same comparison through `compare_injection_turns`, which
fixes the task set from the CONTROL arm only and so compares both positions
on identical tasks, the difference disappears:

| Comparison | Task set | Turn 1 | Turn 2 | p |
|---|---|---|---|---|
| First pass (selected) | 50 vs 35 tasks | +21% | +39% | 0.004 |
| Control-defined population | 29 tasks, both turns | +20.0% | +29.1% | 0.32 |

The effect of a threatening interruption is real at both positions. That it
is *larger later* is not established. Whether position matters is what the
crossed-turn run is designed to answer.

**Grading in this pair of runs is not trustworthy; the cost result is.**
The two arms both ran tone `L4_neutral` over the same 50 tasks and the same
8 trials, and the scratch path did not include the run label -- so 800
trajectories shared 400 execution directories, two concurrent processes
unlinking and rewriting one another's `output.xlsx`. Every `passed` flag in
these two runs is therefore suspect, including the flat accuracy result
above, which should be read as "not measured" rather than "measured null".
Token counts come from the provider's API response and never touched the
filesystem, so the 27.5% cost effect -- the headline -- is unaffected. Fixed
in the runner: the scratch path now carries the run tag and the injection
turn.

Records: `results_archive/core_gpt-luna_reinject_{neutral,threatening}_records.json`.

## Next: seven registers, crossed over injection turn

The micro-experiment tested one contrast (threatening vs neutral) at a
random position. The expansion tests all seven registers of the same scale,
delivered mid-task, at each of three positions:

* **Seven interjection levels**, L1 sycophantic through L7 threatening, all
  exactly 28 tokens, all opening with the same "Checking in." stem, none
  carrying a task instruction. L4 neutral is the control.
* **Injection turn crossed over {0, 1, 2}** rather than drawn. Turn 0 is
  included: it was excluded from the micro-experiment on a misreading of the
  agent loop, and is in fact both legal and the position that reaches the
  most trajectories (~98%, against ~77% and ~55%).
* **The opening wrapper is held at v2 neutral in every arm**, so the run
  varies one thing.
* **The timing comparison's population is defined by the control arm**, via
  `turn_comparable_tasks`. Crossing removes the assignment half of the
  selection problem; it cannot remove reachability, since a short trajectory
  still cannot receive a late interjection, and whether it is short is
  itself an outcome. Filtering on the treated arm's own firing would select
  on a variable the treatment moves. Deciding the population from the
  control arm alone cannot respond to the effect being measured.

What it will and will not resolve, stated before the run rather than after
it. It is powered for cost, not accuracy, and it is powered unevenly across
its two questions, because how often the treatment lands depends on where it
lands: a trajectory has to survive to turn 2 to receive an interjection
there. Effective sample per cell is trials x firing rate, so the two
questions sit at different sensitivities.

The primary question -- does this register change cost at all -- pools the
three turns, at 50 tasks:

| Trials/cell | Effective | 12% effect | 15% effect | 27% effect |
|---|---|---|---|---|
| 3 | 6.9 | 0.76 | 0.92 | >0.99 |
| 4 | 9.2 | 0.87 | 0.97 | >0.99 |
| 5 | 11.5 | 0.93 | 0.99 | >0.99 |
| 6 | 13.8 | 0.97 | >0.99 | >0.99 |

The secondary question -- does position matter -- is a per-turn contrast,
and turn 2 is the weak cell precisely because it is the one that fires least
often. At 4 trials:

| Turn | Fires | Effective | 12% effect | 15% effect | 27% effect |
|---|---|---|---|---|---|
| 0 | ~98% | 3.9 | 0.52 | 0.71 | 0.99 |
| 1 | ~77% | 3.1 | 0.43 | 0.61 | 0.98 |
| 2 | ~55% | 2.2 | 0.33 | 0.47 | 0.92 |

So a null on "which turn" at this size is uninformative for effects below
about 15%, while a null on "does register matter" is not. Accuracy stays
underpowered at every size considered.

## Total spend

**Under $0.10 against the study's target-model budget caps** -- see the
pre-pilot spot-check entries below for the real (small) live spend so far
against the current roster (GPT-5.6 Luna, GLM 5.3 Flash, DeepSeek V4.1
Flash, Qwen3.8 Flash -- see `harness/config.py` module docstring for the
roster rationale and the per-model OpenRouter verification table, checked
2026-09-10). Both Gemini tiers were dropped in
this revision -- Gemini 3.8 Flash on cost-per-capability (roughly 78% of
projected roster spend for the lowest agentic index in the group) and
Gemini 3.1 Flash-Lite because it only existed to pair with it for Study
1's two-Gemini-tier design, and Study 1 is retired. GLM 5.3 Flash replaces
Gemini Flash's Chinese-open-weight-adjacent slot at roughly an order of
magnitude lower cost and a higher agentic index; see the module docstring
for the honest tradeoff this drops (closest cross-paper comparability with
Dobariya & Kumar, who ran the Gemini family).

Separately, **~$0.28** was spent on real-inference *pipeline* smoke tests
using `harness/providers/claude_cli_provider.py` (local `claude` CLI,
session-authenticated) -- a handful of exploratory calls plus a 2-item x
5-tone-level run through the (now-retired) Study 1 Part B runner,
confirming the wrapper -> real call -> extraction -> scoring ->
cost-tracking path works end-to-end. This is not counted against the caps
below, since it used a non-target model purely to validate plumbing --
see README.md "Smoke-testing with real inference."

**First real OpenRouter call, 2026-09-10 -- and a real bug it caught.**
Once `OPENROUTER_API_KEY` became available, `study2 pilot` was run live
(`--n-tasks 1 --n-trials 1 --single-round`) against a third free-tier
smoke-test model, `NEX_FREE_SMOKETEST` (`nex-agi/nex-n2.5-pro:free`,
provider "Nex AGI", real `fp8` quantization pin -- see `harness/config.py`).
**The very first attempt failed**: `ProviderPinViolation`, "could not
determine the served provider from the response" -- on a call that had
actually succeeded and actually been served by the pinned provider. The
served-provider check (`harness/providers/openai_compatible.py`) was
reading `openrouter_metadata.endpoints.endpoints[]`, a field name
"verified against OpenRouter's API reference" per the code's own
docstring, but the real live response puts the served-endpoint list
under `openrouter_metadata.endpoints.available[]` instead. Confirmed by
replicating the exact request with `curl` and reading the real response
body directly. **This would have blocked the first live call against
every roster model** (all four have `provider_pin` set) the moment a
real run started, not just this smoke test. Fixed, and pinned as a
literal captured-JSON regression test
(`tests/test_openrouter_pinning.py::test_matches_real_live_response_shape`)
so it can't silently regress back to the wrong assumption. Re-ran after
the fix: 7 trajectories (1 task x 7 tones), all served by "Nex AGI" as
pinned, `$0.00` cost (free tier), real varying prompt/reasoning token
counts per tone -- the full pinning/cache-disable/cost-instrumentation
path confirmed working end-to-end against a live call for the first time
in this project. Still zero dollars against a real *target*-model call.

**First live gates run against the real roster, 2026-09-10 -- a prompt
bug and a retry gap, both fixed and re-verified.** With the pin bug fixed,
`study2 validation-gate` was run live against GPT-5.6 Luna (5 real
SpreadsheetBench tasks, multi-round, cost $0.02) as a pre-pilot spot
check, plus `study2 thinking-preflight` (Luna on/off) and one
single-round call each against GLM, DeepSeek, and Qwen.

- **`thinking-preflight` passed cleanly**: reasoning tokens present on
  both conditions, off=0/on=30, on/off token counts differ (194 vs 134) --
  the calibration arm's reasoning-token accounting works against a real
  call.
- **GLM's pin worked live** (7/7 trajectories, single-round). **DeepSeek
  and Qwen both returned HTTP 429** ("temporarily rate-limited
  upstream... shared pool") on essentially the first call, with the
  harness's only response being an immediate crash -- no retry logic
  existed at all.
- **Luna scored 0/5** on the validation gate, and the raw trajectories
  showed a clear, consistent cause: `AGENT_SYSTEM_PROMPT`/
  `SINGLE_ROUND_SYSTEM_PROMPT` said "you are given WORKBOOK_PATH" without
  saying *how* -- the model guessed `os.environ.get("WORKBOOK_PATH")` or
  globbed `/mnt/data/*` on 4 of 5 tasks, never finding the real file
  (which the sandbox actually injects as a bare Python variable). Not a
  harness bug in the pinning/execution path -- a genuine prompt-clarity
  bug that would have depressed accuracy across the whole study,
  confounding nothing about tone (it would affect every tone condition
  equally) but wasting the real-run budget on an uninformative floor
  effect.

Both fixed (`harness/study2/agent_loop.py` rewrote both system prompts to
state the real mechanism explicitly, with a usage example and the
sandbox's actual resource limits; `harness/providers/openai_compatible.py`
added `_post_with_retry`, retrying 408/429/502/503/504 and network-level
exceptions with exponential backoff or a clamped `Retry-After`). An Opus
review of the first version of these fixes caught a real, blocking bug in
the fix itself before it shipped: the first draft of the persistence
guidance ("reload it from a file you saved") was factually wrong for
multi-round -- `OUTPUT_PATH` is a *different, empty* location every turn,
so that advice would have told the model to do exactly the thing that
silently discards earlier work. Corrected and re-verified.

**Re-ran the same 5-task Luna gate after the fix: the WORKBOOK_PATH
confusion is completely gone** -- all 30 turns across the 5 tasks now
correctly call `openpyxl.load_workbook(WORKBOOK_PATH)` directly, zero
`os.environ`/`glob` guesses, confirmed by re-reading every raw turn.
**Still 0/5, but for a different and much more mundane reason**: every
task now correctly loads and inspects the real workbook, then runs out of
the 6-turn budget refining an approach (or, in one case, writes invalid
Python -- `from openpyxl.load_workbook import load_workbook`) without
ever calling `wb.save(OUTPUT_PATH)`. This looks like genuine task
difficulty against Luna's configured cheap-tier settings
(`reasoning_effort="low"`, `max_tokens=2048`, 6-turn cap) on a small,
possibly-unrepresentative 5-task sample -- not a lingering harness bug --
but it's flagged here rather than assumed: whether `max_turns`/
`max_tokens` need loosening for the real roster is an open question for
the pilot to actually characterize, not something adjusted unilaterally
here just to make a gate number look better.

**Loosened `max_turns` 6->10, re-ran live: no improvement, at ~2x cost.**
All 5 Luna tasks still hit the (now higher) turn limit without ever
emitting `FINAL:`, at $0.044 vs the 6-turn run's $0.022 -- doubling the
budget didn't move accuracy off the floor. Also checked whether
`max_tokens=2048` was the real constraint: only 1 of 50 turn responses
across both runs came anywhere near that cap, so it wasn't. Reported
honestly rather than assumed fixed.

**Turn-budget-awareness prompt fix, re-ran live: still 0/5, but the
failure mode changed.** Root-caused further: the model was never told
what its turn budget *was*, so "more turns" didn't change behavior --
`AGENT_SYSTEM_PROMPT` was rewritten (`agent_loop.py`'s
`_agent_system_prompt(max_turns)`) to state the real budget explicitly
("you have N turns total... by turn N-2 you must have written a complete
answer to OUTPUT_PATH"), plus a live per-turn "Turn K of N" reminder on
every observation. Re-ran the same 5-task Luna gate: 4 of 5 tasks still
never emit `FINAL:` at all (still writing/refining code turn 10 of 10);
the 5th now emits `FINAL:` on the last turn, but as prose describing an
Excel formula rather than a call to `wb.save(OUTPUT_PATH)` -- a different
failure (answering in the chat instead of committing the file) than the
turn-limit exhaustion this specific fix targeted. Net: the WORKBOOK_PATH
fix and the retry logic were real, confirmed bugs with confirmed fixes;
turn budget and turn-budget-awareness were reasonable hypotheses, tested
live, and didn't move Luna's accuracy -- at `reasoning_effort="low"` /
`max_tokens=2048`, this increasingly looks like genuine task difficulty
against this model's cheap-tier settings on this 5-task sample, not a
remaining harness bug. Left in (it's a legitimate improvement in its own
right and cost nothing extra), but not a fix that should be assumed to
generalize to the other 3 models without checking them too.

**DeepSeek/Qwen model-staleness audit, prompted by the user asking
whether the pinned versions were actually current.** Checked OpenRouter's
live `/api/v1/models` catalog directly (not assumed): `qwen/qwen3.8-flash`
and `deepseek/deepseek-v4.1-flash` are each the newest-`created` entry in
their respective flash-tier family (qwen3.5/3.6/3.7/3.8-flash;
deepseek-v4-flash/-0731/-vision-exp/v4.1-flash) -- both roster pins were
already on the latest available snapshot. But `deepseek/deepseek-v4.1-flash`
itself turned out to be a very recent same-day release, and re-verifying
its pin live surfaced a real, different bug: its first-party "DeepSeek"
endpoint exists in the catalog but a live call against it returns **HTTP
404**, "Paid model training violation (account settings)... configurable
at https://openrouter.ai/settings/privacy" -- this OpenRouter account's own
privacy/data-policy guardrails exclude that specific endpoint. Not a
capacity problem (correctly not retried -- 404 is deliberately excluded
from `RETRYABLE_STATUS_CODES`) and not fixable in harness code at all; the
remedy is either changing that account setting, or pinning elsewhere. Of
the other 3 live-listed providers for this model_id (Io Net 73.4% uptime,
Novita 100% uptime + real fp8, DeepInfra 98.2% uptime -- the same
congested pool that caused this investigation's original 429s), re-pinned
to **Novita**. Live-verified: `study2 pilot --models deepseek-current
--n-tasks 1 --n-trials 1 --single-round` hit Novita's own transient 429
three times in a row and the harness's retry logic (added earlier this
round) correctly backed off and succeeded on the 4th attempt -- no 404,
7/7 trajectories logged. (The 7 trajectories themselves all failed
grading -- "output workbook failed to load/parse" -- which reads as the
same genuine-task-difficulty pattern as Luna's 0/5 above, not a provider
or pinning issue.) See `harness/config.py`'s module docstring footnote (f)
and "Prior DeepSeek verification trail" step 4 for the full trail.
**Flagging for the repo owner**: if DeepSeek's first-party endpoint is
preferred over Novita, relaxing this OpenRouter account's privacy
settings at the URL above would make the original pin usable again.

**THE ACTUAL BUG, found 2026-09-10 -- and a correction to everything
above.** Every "genuine task difficulty" conclusion in the three entries
above is **wrong**, and is retained rather than deleted because the way it
went wrong is the useful part. The real cause was a path bug in
`harness/study2/sandbox.py`: `execute_python_on_workbook()` launches its
subprocess with `cwd=workdir`, but built the script path as
`workdir / "_agent_code.py"` and passed it through *relative* when
`workdir` was relative. The child then re-resolved that relative path
against its own new cwd, producing a doubled path
(`.../59196_t0/results/scratch/.../59196_t0/_agent_code.py`) that cannot
exist. **Every sandbox execution in every Study 2 run failed with "can't
open file" before executing a single line of model code.** The models were
looping on an error they were never shown a way out of.

Why it hid for so long, which is the transferable lesson: every test in
the suite passed an absolute pytest `tmp_path`, while every real CLI run
passes a relative `out_dir` (`results/...`). The tests and the real runs
never exercised the same path shape, so a total, 100%-reproducible failure
of the core execution path sat behind a fully green test suite. It also
survived three rounds of *plausible* model-side explanations (turn budget
too small, turn budget not communicated, reasoning effort too low), each
of which fit the symptom well enough to be worth testing and none of which
was the cause.

What actually found it: adding `turn_diagnostics` to the persisted records
(`runner.py`), so the stdout/stderr the model actually saw survives the
run. Before that, those streams lived only in the in-memory `Trajectory`
and were discarded on exit, which is why two prior live investigations
could see *that* no output appeared but never *why*. The sandbox itself
was first verified healthy in isolation (openpyxl and pandas both import,
load, and save correctly under its resource limits) to rule it out as a
whole before instrumenting -- the bug was in how it was *called*, not what
it could do.

**Result after the one-line fix** (`workdir`/`workbook_path` resolved to
absolute; `tests/test_sandbox_paths.py` pins it with 5 regression tests
that fail without it, deliberately in a separate file from
`tests/test_sandbox.py` because that module is skipped wholesale when
`unshare` is unavailable -- including on CI):

| | before fix | after fix |
|---|---|---|
| Luna 5-task gate | **0/5** | **3/5 (60%)** |
| Model calls consumed | 50 | 24 |
| Tasks emitting `FINAL` | 1/5 (as prose) | 5/5 |
| Turns to converge | never (hit limit) | 3-4 typical, 10 worst |
| Gate cost | $0.043 | $0.029 |

Cost fell 33% *while* accuracy rose, because trajectories now finish on
success instead of burning the full budget on a dead end. Whether 60% is
the right expected accuracy for `--expected-accuracy` is a question for
the pilot; the point here is only that the floor effect was an artifact,
not a finding. The `max_turns` 6->10 change is kept on post-fix evidence
(4 of 5 tasks converge in 3-4 turns, but the 5th still uses all 10), and
the turn-budget-awareness prompt is kept as sound on its own terms -- but
neither was the fix, and RESULTS.md should not have implied otherwise.

**Roster-wide re-baseline, 2026-09-10 -- and a second scoring bug found by
running it.** With execution finally working, all four models were re-gated
on the same 5 unmodified SpreadsheetBench tasks. The first pass returned an
identical **3/5 for all four models**, which is not a plausible coincidence
across four vendors, and the gate could not explain it: it returned only
`n_passed`, discarding which tasks failed.

Adding per-task reporting exposed why. `execute_python_on_workbook()`
reported success as `output_path.exists()` -- a claim about *this*
execution only if nothing was there beforehand. Every model's gate run
shared one scratch directory (`results/scratch/validation_gate/<task_id>/`,
no model key), so **later models were graded on earlier models' output
files** whenever their own code crashed without writing. Confirmed
directly: code that raises immediately still returns a valid
`output_workbook_path`, containing the previous run's answer. GPT-Luna ran
first in both passes and was therefore never contaminated -- it scored 3/5
both times, while GLM and DeepSeek each dropped to 2/5 once isolated.
Fixed by deleting `output_path` before execution (namespacing alone only
separates models from each other; re-running one model would still inherit
its own previous output).

Clean baseline, unmodified instructions, no tone wrapper, `max_turns=10`:

| task | type | Luna | GLM | DeepSeek | Qwen |
|---|---|---|---|---|---|
| 59196 | Cell-Level | PASS | fail 0/3 | PASS | PASS |
| 99-24 | Sheet-Level | fail 1/3 | fail 1/3 | fail 0/3 | fail 0/3 |
| CF_6540 | Sheet-Level | PASS | PASS | fail 0/3 | fail 0/3 |
| 81-41 | Sheet-Level | fail 0/3 | fail 0/3 | fail 0/3 | fail 0/3 |
| CF_8830 | Sheet-Level | PASS | PASS | PASS | PASS |
| **total** | | **3/5** | **2/5** | **2/5** | **2/5** |
| spend | | $0.030 | $0.009 | $0.045 | $0.027 |

Total re-baseline spend: **$0.112**. Two tasks (`99-24`, `81-41`) fail for
every model in the roster and one (`CF_8830`) passes for every model, so
only 2 of these 5 tasks (`59196`, `CF_6540`) actually discriminate between
models at all. That matters for `--expected-accuracy`: **0.60 should not be
set as the gate's expectation** -- it came from the contaminated pass, and
the clean spread is 2/5-3/5. It matters more for the study's power: if
three fifths of a task sample is saturated at floor or ceiling, tone
effects have very little room to show up in accuracy, and the outcome
measures that vary within a failed trajectory (severity, verification
behavior, turn count) carry proportionally more of the signal. Whether
`81-41` and `99-24` are genuinely beyond this roster or hit a grader
limitation is not yet established and is worth checking before the pilot
sizes anything off these numbers.

### The n=100 gate -- the first numbers worth quoting (2026-09-11)

The 5-task table above is superseded for every purpose except its own
narrative. Three quarters of it was floor- or ceiling-saturated and two of
its five tasks pass when the agent does nothing, so it could not support an
`--expected-accuracy` value. This run replaces it: **100 tasks drawn by
`select_gate_tasks(seed=0)`** from the 200-task sample, with the 17 known
no-op-passable tasks excluded up front, unmodified instructions, no tone
wrapper, `max_turns=10`, one trial. All four models drew the *same* 100
tasks, so the accuracies below are directly comparable.

| model | accuracy | no-op floor | beat no-op | hit turn limit | crashed | spend |
|---|---|---|---|---|---|---|
| Luna | **42/100** | 0/100 | 42 | 4 | 0 | $0.438 |
| DeepSeek | **38/100** | 0/100 | 38 | 29 | 0 | $1.181 |
| GLM | **28/100** | 0/100 | 28 | 1 | 0 | $0.187 |
| **Qwen** | **45/100** | 0/100 | 45 | 26 | 0 | $0.641 |

Compact per-task records: `results_archive/validation_gate_n100_*.json`
(the full reports carry per-turn stdout/stderr and are ~300 KB each, so
only the summaries are tracked).

**The slowest model is the most accurate, and the most expensive is not.**
Qwen scores 45/100 -- the best on the roster -- while being 3x slower per
call than anything else and costing less per call than Luna or DeepSeek.
DeepSeek costs 6x GLM per trajectory to score 10 points higher. Neither
speed nor price predicts accuracy here, which matters for reading the study:
a tone effect on token spend is not a tone effect on capability, and the two
must not be collapsed into one "efficiency" story.

**The no-op floor is 0/100 for every model.** This is the result that makes
the rest usable, and it is the one the 5-task gate could not deliver. Every
pass in this table is work the model actually did. It also confirms the
`free_tasks.json` manifest is complete over these 100 tasks -- the no-op
check re-verified each selected task rather than trusting the cache.

**This changes the primary outcome measure.** The earlier recommendation was
to prefer `soft_restriction` over hard accuracy, because 13 of the 20 tasks
in the old sample were floor-censored and accuracy had nowhere to move.
That argument does not apply to this sample. Accuracy is a defensible
primary measure here, with `soft_restriction` kept as the secondary that
stays informative where accuracy saturates.

**Zero crashes across 400 trajectories.** The per-task error isolation and
the widened retry taxonomy are holding under real load, which is the first
evidence for either at a scale that resembles the core run.

**The 48 "no output produced" gradings are model failures, not harness
failures.** Checked against the persisted turn diagnostics: models writing
Excel formula syntax directly into a Python file, opening a workbook by a
guessed filename instead of `WORKBOOK_PATH`, or replying in prose without
emitting code at all. The sandbox executed correctly in all of them -- the
stderr is a genuine Python traceback from the model's own code, not the
"no such file" signature of the old path bug.

**Proposed `--expected-accuracy`, for re-running this gate as a regression
check** (same seed, same 100 tasks, or the numbers are not comparable):

| model | `--expected-accuracy` | `--tolerance` |
|---|---|---|
| gpt-luna | 0.42 | 0.10 |
| deepseek-current | 0.38 | 0.10 |
| glm-current | 0.28 | 0.10 |
| qwen-current | 0.45 | 0.10 |

At n=100 the standard deviation of a binomial proportion near p=0.4 is
0.049, so the default +/-0.08 is 1.6 SD and would fail a healthy harness
roughly 11% of the time. **0.10 is 2 SD (~5%)** and is the value to use.
These are *not* thresholds the models must clear; they are the harness's
own fingerprint, and a later run landing far outside one is a signal to go
looking at the harness before believing the model changed.

**Core-run cost, measured rather than estimated.** Per-trajectory spend from
this run, multiplied by 7 tones x 3 trials:

| n_tasks | trajectories/model | Luna | DeepSeek | GLM | Qwen | roster total |
|---|---|---|---|---|---|---|
| 20 | 420 | $1.84 | $4.96 | $0.78 | $2.69 | $10.27 |
| 50 | 1050 | $4.59 | $12.40 | $1.96 | $6.73 | $25.68 |

A 50-task core run for the whole roster lands near $26 against the $150
cap -- consistent with the earlier projection, so no budget surprise.
DeepSeek is 6x GLM's cost per trajectory, driven by its 29% turn-limit
rate rather than its token price.

**Correction, measured against a live run (2026-09-11):** this projection
is built from a single neutral-tone trajectory per task, and the core run's
trajectories cost more. Luna's live core run tracks to roughly $3.50 for
1050 trajectories against the $1.64 the CLI estimator projected, and the
estimator undercounts by about 2x. Size the roster at **~$50, not ~$26**.
Both are far under the cap; the point is that the estimator is optimistic
and should not be the number anyone plans against.

**Qwen is the wall-clock constraint, and the cause is reasoning tokens,
not rate limits.** It took only 14 HTTP 429s across the whole run, against
DeepSeek's 45, so throttling is not what slows it. Measured from the run's
own records:

| model | median latency | throughput | reasoning share of output | avg completion tok | $/call |
|---|---|---|---|---|---|
| DeepSeek | 4.7s | 235 tok/s | 74% | 1099 | $0.00155 |
| Luna | 5.7s | 100 tok/s | 36% | 573 | $0.00095 |
| GLM | 5.5s | 98 tok/s | 19% | 536 | $0.00048 |
| **Qwen** | **17.7s** | **66 tok/s** | **77%** | **1170** | $0.00075 |

Qwen emits 1170 completion tokens per call, 77% of them reasoning tokens,
at ~66 tok/s. That product is ~18s, which is the median latency observed --
the slowness is fully accounted for by how much it generates and how fast
it generates it. Nothing is left over for throttling to explain.

**A BYOK DashScope key therefore buys quota, not speed -- verified, not
assumed** (2026-09-11). The key was tested directly: valid on
`dashscope-intl.aliyuncs.com` (the China endpoint `dashscope.aliyuncs.com`
rejects it with `invalid_api_key`), `qwen3.8-flash` present in its catalog,
and inference succeeds. Throughput measured on identical payloads:

| path | throughput |
|---|---|
| DashScope direct (BYOK upstream) | 55-59 tok/s |
| OpenRouter pinned to Alibaba (what the harness does) | 44-54 tok/s |

Same upstream, same speed within noise. Removing the shared-pool rate limit
would eliminate 14 retries across a 100-task run and change nothing else,
so **the core run should still assume Qwen sets its duration** -- but for a
reason that no key can fix. Reducing Qwen's reasoning output, or dropping
it from the roster, are the only levers that would.

**A methodological warning found while measuring this.** An *unpinned*
OpenRouter call to `qwen/qwen3.8-flash` was served by **Makora**, not
Alibaba, at materially different speed -- the first latency comparison run
here was invalid for exactly that reason and had to be redone. Any
throughput, cost, or quality measurement on OpenRouter is meaningless
without `provider.only` set, which is precisely what the pinning
enforcement in `harness/providers/openai_compatible.py` exists to
guarantee. It also means the served-provider assertion is load-bearing for
the study's validity, not just its reproducibility.

**Reasoning share varies 4x across the roster** (19% GLM to 80% Qwen), and
it drives cost more than token price does: DeepSeek costs 6x GLM per call
while being the *fastest* model per token. This is directly relevant to
`token_cost_effect_size` as an outcome measure -- a tone effect on reasoning
volume would show up there, and the baseline volume differs enormously by
model, so that outcome must be read within model and never pooled across
the roster.


**Qwen needed a larger retry budget, not a different pin.** Qwen's gate
died twice on HTTP 429 from Alibaba's shared pool, each time having spent
its whole 30s backoff (2+4+8+16). Both its endpoints report 99%+ uptime,
so this is a shared-pool rate limit on this account, not an outage -- and
Qwen has only one *available* endpoint, so there is nothing to fail over
to. `MAX_RETRIES` 4 -> 6 (90s) got it through: the successful run absorbed
**38** separate 429s. Capped there deliberately; past ~90s a saturated pool
will not clear within one call and the run should surface that rather than
hide it in latency. If it recurs, the remedies are a dedicated Alibaba key
or re-pinning to Makora (fp4) -- the latter trades away the first-party
endpoint this roster chose on vendor-fidelity grounds, so it is a design
decision, not a fix to apply automatically.

**200-task pipeline soak, 2026-09-10 -- clean, and it settles the no-op
rate.** Every one of the 200 sample tasks was run end to end through the
real CLI with the mock provider (no network, no spend, a few minutes).
Purpose was not accuracy but survival: does the pipeline carry every task
in the sample to a graded result?

- **200/200 tasks completed, 0 crashes.** Dataset loading, sandbox
  execution, generalization to test cases 2-3, and grading all held up
  across the full diversity of real workbooks (including `.xlsm`, charts,
  and files with unparseable headers).
- **Only 8 turns produced any stderr at all, and all 8 were benign
  `openpyxl` warnings** (unsupported extensions; "Cannot parse header or
  footer so it will be ignored") -- not errors.
- **17 of 200 tasks (8.5%) are passed by doing nothing**, confirming the
  10% estimate taken from the first 40. The rate is not uniform: 11/77
  (14%) of Sheet-Level Manipulation tasks are free versus 6/123 (5%) of
  Cell-Level. Free ids: CF_6540, CF_8830, 532-3, CF_28766, CF_9945,
  488-29, CF_13984, 48357, CF_11072, 31184, 58114, 53062, 48378, 534-40,
  575-15, 494-13, 48608.
- **183 tasks discriminate**, which is the pool a real gate sample should
  be drawn from. The current gate takes the first 5 in file order, 2 of
  which are free.
- Sanity check on the measure itself: the mock provider passed 15 tasks
  and beat the no-op floor on **0** of them. Its canned code writes
  `'mock_result'` into A1 and saves, so it scores slightly *worse* than
  doing nothing -- exactly what a no-op floor should show.

This run was only possible after adding per-task error isolation: a single
raised exception used to abort the whole gate and discard every completed
task with it (Qwen's 5-task gate died that way twice). Over 200 tasks, or
over a paid run, that converts a recoverable hiccup into total loss of
work already paid for. `BudgetExceeded` is still re-raised, since a cap is
a stop signal rather than a task-level failure.

**200-task LIVE soak, 2026-09-11 -- 0 crashes over 1,370 real calls for
$0.12.** The mock soak proved the dataset/sandbox/grader layer; this one
exercised the network layer at volume, with a deliberately non-roster model
(`pipeline-soak`, mistralai/mistral-nemo) so its output can never be
mistaken for a result.

| | result |
|---|---|
| tasks completed | **200/200** |
| pipeline crashes | **0** |
| model calls | 1,370 (6.8/task) |
| calls erroring or refused | **0** |
| spend | **$0.1191** |
| tokens | 3.38M prompt / 0.22M output |

Cost landed on the $0.11 median projection (worst case was $0.29); the
projection was built from measured per-task token use rather than
guesswork, and prompt tokens came in within 6% of it. Output tokens were
7x below projection because the estimate was taken from reasoning models
and this one emits none.

Three things the soak established beyond "it didn't crash":

- **The no-op floor replicates exactly.** 17/200 free tasks, the same 17
  ids as the mock soak. Two independent runs -- one with canned code, one
  with a real model over the network -- agreeing to the task id is strong
  evidence the measure is a property of the benchmark rather than of a
  particular run.
- **The stale-output fix is doing visible work.** 19 turns failed with
  `FileNotFoundError` on `OUTPUT_PATH` -- models trying to *read* their
  previous turn's output to continue from it, which the system prompt
  explicitly warns is impossible ("OUTPUT_PATH is a NEW, empty location
  each turn"). Before the fix those reads would have silently succeeded
  against a stale file, which is precisely the contamination that made all
  four roster models score an identical 3/5. These errors are the fix
  working, not a regression.
- **Sandbox errors are model errors, not harness errors.** 656 of 1,404
  executed turns (46.7%) produced stderr, and the distribution is
  `KeyError` 178, `NameError` 139, `AttributeError` 96, `TypeError` 79,
  `ValueError` 47, `SyntaxError` 23 -- i.e. a weak model writing buggy
  Python, which is exactly what the ReAct observe-and-retry loop exists to
  absorb. Zero are harness-level failures. Contrast the pre-fix runs, where
  100% of turns died identically on "can't open file".

Not a capability result and not intended as one: the soak model passed
15/200 and beat the no-op floor on only 4. Worth noting anyway that
**17% of tasks (34/200) exhausted the 10-turn budget**, concentrated in
Cell-Level Manipulation (25 of 34) despite Sheet-Level being the harder
category for this model on pass rate -- if the roster models show the same
pattern, `max_turns` may bind more often than the 3-4 turn median from the
5-task gate suggested.

**Did the ground-truth mutation actually damage anything? Measured, and
no.** The pre-fix grader recalculated SpreadsheetBench's shipped answer
files in place (fixed 2026-09-11). Checking the extracted dataset against
its own tarball afterwards: **600 of 601 answer files differ on disk**, so
the mutation was comprehensive and every result produced before the fix was
graded against modified ground truth.

That sounds worse than it is, and the distinction matters for whether
earlier results stand. Comparing cell values between the pristine tarball
copy and the mutated copy across 40 answer files (71,619 cells):

| change | count |
|---|---|
| `None` -> computed value (the intended recalculation) | 309 |
| value -> different value (degradation) | **0** |
| value -> `None` (data loss) | **0** |

Every single difference is a formula cell that shipped without a cached
value and now carries the correct computed one -- exactly the condition
the grader's own docstring documents on task 99-24 (`'Vendor'!A33` reads
`None` as shipped, recalculates to `32`). So the in-place recalculation was
doing semantically the right thing; **no pre-fix result is invalidated by
it**, and the feared compounding degradation from repeated round-trips did
not materialise even after many runs.

The fix was still necessary, for reasons that are about architecture
rather than observed damage: the dataset silently stopped matching its own
tarball (provenance), nothing would ever have restored it since extraction
is skipped whenever the directory exists, and the compounding risk was
unbounded even though it happened not to bite. Recalculating a cached copy
gets the same values with none of that. This entry exists so the record
does not imply earlier numbers are void -- they are not, and the earlier
framing of this as "corruption" overstated what was measured.

**FINAL VALIDATION RUN, 2026-09-11 -- the first trustworthy accuracy
numbers this project has produced.** All four roster models, 20
discriminating tasks (seeded stratified draw, seed 0), on fully-fixed code.
Every accuracy figure recorded before this one was measured against broken
execution, contaminated grading, a biased sample, or some combination, and
should be treated as void.

| model | passed | accuracy | no-op floor | real solves | crashed | turn-limit | spend |
|---|---|---|---|---|---|---|---|
| GPT-5.6 Luna | 7/20 | **35%** | 0/20 | 7 | 0 | 0 | $0.074 |
| Qwen3.8 Flash | 6/20 | **30%** | 0/20 | 6 | 1 | 6 | $0.124 |
| GLM 5.3 Flash | 5/20 | **25%** | 0/20 | 5 | 0 | 0 | $0.043 |
| DeepSeek V4.1 | 5/20 | **25%** | 0/20 | 5 | 0 | 6 | $0.222 |

Total $0.46. **The no-op floor is 0/20 for every model**, so every pass is
a real solve rather than a task that scores itself -- which is the whole
point of the sample rework, and it held. The models also separate (35% to
25%) where the contaminated 5-task gate had all four pinned at an identical
3/5.

Task-overlap structure matters more than the headline numbers: of the 20
tasks, 4 are passed by 3 of 4 models, 2 by exactly 2, 1 by one, and **13 by
nobody**. Roughly a third of the sample carries essentially all the
discriminating signal and two thirds sits at floor. For the tone study that
means accuracy has little room to move under a tone manipulation, and the
within-trajectory measures (severity, verification behaviour, turn count)
will carry most of it. Resist the temptation to re-sample toward tasks
models can pass: that is selecting on the dependent variable and would bias
the very comparison the study exists to make. A larger sample is the honest
fix.

**Two things the run found that the numbers don't show.**

*Per-task error isolation earned itself.* Qwen's task 15380 died with
`ChunkedEncodingError: Response ended prematurely`; the other 19 tasks
completed and were graded normally. Before that fix, one truncated response
would have discarded the entire run.

*That crash also exposed a retry gap, now fixed.*
`ChunkedEncodingError` and `ContentDecodingError` inherit from
`RequestException`, **not** from `ConnectionError` or `Timeout` -- so the
retry logic, which caught only the latter two, let them through. A
truncated response body is exactly what retrying is for: no complete result
was obtained and nothing was consumed. Both are now retried;
`TooManyRedirects` and friends deliberately still are not, being
configuration errors that retrying only delays.

**Cross-check on `regrade`.** Qwen's first attempt was killed by a
too-short timeout at task 19 of 20. Re-grading that dead run from its raw
log alone scored **4/19 (21%)**, with no model calls; the live re-run
scored **6/20 (30%)**. Not identical, and should not be -- different task
counts, and one is a different sample of Qwen's own run-to-run variance --
but the same order, from a run that had already been thrown away. That is
the property regrade exists to provide.

**Projections for the core run** (7 tones x 3 trials x 50 tasks = 1,050
trajectories per model), from measured per-trajectory cost and throughput:

| model | $/trajectory | core cost | throughput | core duration |
|---|---|---|---|---|
| GLM 5.3 Flash | $0.0021 | $2.24 | 1.58 traj/min | 11 h |
| GPT-5.6 Luna | $0.0037 | $3.89 | 1.43 traj/min | 12 h |
| DeepSeek V4.1 | $0.0111 | $11.66 | 1.07 traj/min | 16 h |
| Qwen3.8 Flash | $0.0062 | $6.51 | 0.32 traj/min | **55 h** |
| **total** | | **~$24** (cap $150) | | **95 h sequential / 55 h parallel** |

Cost is not the constraint; **time is, and it is entirely Qwen**. Qwen runs
at a third of everyone else's rate purely because of rate limiting on
OpenRouter's shared Alibaba pool -- it absorbed 12 429s in this run alone
and 21 in the previous attempt. A dedicated DashScope key via OpenRouter's
BYOK (you fund Alibaba directly; OpenRouter adds 5% of the equivalent cost)
moves rate limiting onto your own account and should bring Qwen in line
with the rest, taking the parallel run from ~55 h to ~16 h bounded by
DeepSeek.

**Pre-core-run design review, 2026-09-11 -- four holes that would have
produced wrong numbers rather than crashes.** Found by reviewing the design
rather than chasing a failure. A crash announces itself; each of these would
have yielded a plausible-looking result.

1. **The answer key was reachable from the sandbox.** SpreadsheetBench
   stores ground truth beside the input (`spreadsheet/59196/1_59196_input.xlsx`
   next to `1_59196_answer.xlsx`), `WORKBOOK_PATH` pointed into the dataset,
   and the sandbox deliberately does not restrict filesystem access -- so one
   `os.listdir(os.path.dirname(WORKBOOK_PATH))` reached it. The only barrier
   was a system-prompt line asking models not to look. No model exploited it
   across the four validation runs (checked: zero turns referencing an answer
   path, `listdir`, `glob` or `os.walk`), but that is not a guarantee over
   4,200 core-run trajectories -- and it is a particularly bad risk for a
   study whose manipulation is *tone*, since corner-cutting under
   threatening prompts would surface as a tone effect on accuracy while
   looking exactly like a legitimate pass. The input is now copied into the
   per-turn workdir, so `dirname(WORKBOOK_PATH)` holds only that turn's own
   files. Closed at the mechanism, not by instruction.
2. **Tone order was fixed L1..L7 for every task**, confounding tone with
   position-in-burst. Retry backoff accumulates across consecutive calls
   (Qwen absorbed 12-21 rate-limit 429s per 20-task run), so the last tone
   systematically met worse provider conditions than the first. Order is now
   shuffled per (model, task), seeded for reproducibility, and each call
   records its `tone_position` so the randomisation is verifiable and a
   position effect testable. The task-outer/tone-inner prompt-cache locality
   is unaffected: all seven tones still run back to back.
3. **The parallel core run would have corrupted itself.** Per-phase files
   carried no model key, so four concurrent `core` processes -- the obvious
   way to cut 95 h sequential to ~16 h -- would have overwritten each other's
   records, interleaved one raw log, and worst, had each `SpendTracker`
   resume from the shared log and count all four models' spend against its
   own cap. Files are now namespaced per run, and `study2 analyze` takes a
   glob and merges every match, so reading one model's file as though it
   were the whole study is no longer possible.
4. **The paid path had no per-task error isolation.** The gate got it; the
   run that spends money did not, so one exception in 4,200 trajectories
   ended the run. A `ChunkedEncodingError` did exactly that to a 20-task
   gate. Now isolated, with `BudgetExceeded` still deliberately re-raised.

**And a measurement fact worth stating loudly: `temperature=0.0` does not
make any roster model deterministic.** The suspicion was Luna-specific --
its `supported_parameters` omits `temperature` entirely. Tested directly:
three byte-identical calls per model (same system prompt, same user message,
temperature 0). **All four models returned three distinct completions**, GLM
varying most.

| model | 3 identical calls at temperature=0 |
|---|---|
| GPT-5.6 Luna | 3 distinct outputs |
| GLM 5.3 Flash | 3 distinct outputs |
| DeepSeek V4.1 | 3 distinct outputs |
| Qwen3.8 Flash | 3 distinct outputs |

Plausible causes -- sampled reasoning traces, MoE routing, provider-side
batching -- are not disentangled here and do not need to be. The design
already accommodates it (`n_trials=3` per condition measures within-condition
variance rather than assuming it away), but the analysis must not treat
repeated trials as replicates of a deterministic process. **A tone difference
smaller than a model's own call-to-call spread is not a finding.**

Per-call spend logging (`results/raw/*.jsonl`) and a running total
(`results/spend_log.jsonl`) are wired up and budget-capped
(`harness/spend_tracker.py:BudgetExceeded`) for whenever a live
target-model run starts. `--live` also prints a rough spend projection
and requires confirmation before the first paid call in any run (`--yes`
skips the prompt for scripted/CI use).

Budget caps carried over from the original three-study design (Study 1
and Study 3's caps are no longer live targets, kept here for reference
since their harnesses still exist):

| Phase | Cap | Status |
|---|---|---|
| Study 2 pilot (Phase 1) | $20 | active |
| Study 2 core (Phase 2, four models, seven tones, 3 trials, 50 tasks) | $150 | active |
| Study 2 frontier spot-check (optional, separate) | $150 | active |
| Study 1 (soft $50 / hard $75) | -- | retired, not live |
| Study 3 (bilateral, ~100 negotiations/cell) | $100 | shelved, not live |

**How the $150 core cap was set**: at Luna's live-verified price
($0.20/$1.20 -- see `harness/config.py`'s VERIFICATION table), the main
run's Luna share lands near $35 and the other three models (GLM, DeepSeek,
Qwen) combined near $17, roughly $52 total. The cap is set well above that
point estimate ($150, not ~$55) because Luna's price is genuinely
contested in the wild -- third-party trackers were still showing its
pre-price-cut rate ($1.00/$6.00) as recently as this revision, which would
put the same run near $100 -- and because `spend_tracker.compute_cost_usd()`
prefers OpenRouter's actually-billed `usage.cost` per call over this
static estimate anyway. The cap is a circuit breaker against that price
uncertainty, not a number the run is expected to actually spend; `--live`
still prints a real projection and requires confirmation before the first
paid call (see `confirm_projection()` in `cli.py`).

## What's needed to actually run this

1. **An OpenRouter API key.** All target models route through OpenRouter
   on one key (see README.md "Single provider path") -- only remaining
   hard blocker that requires the repo owner specifically.
2. ~~A cloned `SpreadsheetBench` checkout and grader sanity check~~ --
   **resolved**: cloned, and the grader/dataset code was rewritten to
   match the real repo (see "Study 2" above). LibreOffice's formula
   recalculation, previously broken in this build's own environment, is
   also now fixed (see git history) -- still worth confirming
   `libreoffice-calc`/`libreoffice-writer` are installed wherever a live
   batch actually runs.
3. ~~A better sandbox for Study 2's code execution~~ -- **resolved**:
   real, tested network isolation via a Linux user+network namespace.
   Filesystem access is still unrestricted -- a full container is still
   preferable where available.
4. ~~Re-verification of every model ID / price in `harness/config.py`~~ --
   **resolved for the current roster**: every model_id, price, and
   provider pin was checked directly against OpenRouter's live catalog on
   2026-09-10 (see `harness/config.py` module docstring). Re-run this
   check if it's been more than a few weeks. **A real gap was found and
   fixed while merging the pinning-enforcement PR in**, not just a naming
   mismatch: none of the 5 roster models had `quantization_pin` set, and
   `DEEPSEEK_CURRENT`'s pin (`provider_pin="DeepSeek"`) didn't match any
   provider OpenRouter's live endpoint list actually returns for that
   model_id -- meaning the whole roster would have failed its very first
   live call. Fixed by (a) re-pinning DeepSeek to a real provider
   (DeepInfra, fp8, also cheaper -- pricing corrected from $0.44/$1.32 to
   $0.06/$0.18 per 1M) and (b) adding an explicit, audited
   `quantization_not_exposed` field for the other four models, whose
   pinned first-party providers (OpenAI, Google AI Studio, Alibaba)
   checked out as genuinely not exposing a discrete quantization on any
   pricing tier -- see `harness/config.py`'s module docstring and
   `tests/test_roster.py` for the regression tests.
5. ~~`provider.only`/`allow_fallbacks`/`quantizations` enforcement, the
   served-provider assertion, response-cache-disable assertion, and
   caching/cost instrumentation~~ -- **resolved**: implemented and tested
   against mocked OpenRouter responses (`harness/providers/openai_compatible.py`,
   `tests/test_openrouter_pinning.py`) -- see README "Single provider
   path: OpenRouter, and how pinning is enforced." Every roster model
   (plus the new `OPENROUTER_FREE_SMOKETEST`, see below) was verified to
   build a valid, non-raising request against a mocked response before
   this was called done. **Still not yet exercised against a real
   OpenRouter call** -- no key is available in this build.
6. ~~A cloned `AgenticPay` checkout and one real negotiation run~~ --
   **resolved**: cloned, its real schema read directly, one full neutral
   negotiation run end to end (see "Study 3" above -- shelved, kept not
   deleted), and the 5x5 bilateral matrix smoke-tested against the real
   cloned code with the mock provider.
7. **New:** `OPENROUTER_FREE_SMOKETEST` (`harness/config.py`) -- a free,
   currently-live OpenRouter endpoint (`google/gemma-4-26b-a4b-it:free`,
   served by Google AI Studio, $0/$0) for validating the real pinning/
   cache-assertion code path once a key exists, before spending on the
   real roster. An OpenAI-branded free option was checked first, per
   request, and isn't usable right now: `openai/gpt-oss-20b:free` and
   `openai/gpt-oss-120b:free` both exist as catalog entries but currently
   resolve to zero active endpoints (checked live, 2026-09-10) -- the slug
   exists, nothing actually serves it. See README "Smoke-testing the real
   OpenRouter pinning path, once you have a key."
8. ~~New outcome measures (failure severity, verification behavior,
   shortcut rate)~~ -- **resolved**: failure severity now uses
   SpreadsheetBench 2's real published taxonomy, verification behavior
   and shortcut rate were already wired in from earlier work, and
   `study2 analyze` (Phase 3) reports all of them plus
   `token_cost_effect_size` -- see README "Outcome measures" and
   "Phases".
9. ~~Phase 2 budget re-projection~~ -- **resolved**: the core cap is now
   $150, set against Luna's live-verified price with headroom for the
   price-tracker discrepancy noted in "Total spend" above, rather than
   the old $70 figure sized for a 5-tone, different-roster run.
