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

| Study | Model | Benchmark | Observed accuracy | Published accuracy | Within tolerance? |
|---|---|---|---|---|---|
| 2 | -- | SpreadsheetBench | not run | -- | -- |

The validation gate is wired up (`harness/study2/runner.py:run_validation_gate`)
and exercised against the mock provider + real cloned SpreadsheetBench
data during development -- see the harness test suite. It has not been
run against a real model.

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

**New outcome measures (this revision), not yet implemented in code:**
failure severity (SpreadsheetBench 2's published taxonomy), verification
behavior, and shortcut rate -- see README "Outcome measures". Turn count,
tool calls, token spend, and refusals are already tracked on every result
row.

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

## Total spend

**$0.00 against the study's target-model budget caps.** No target model
has been called against the current roster (GPT-5.6 Luna, Gemini 3.8
Flash, DeepSeek V4 Flash, Qwen3.8 Flash -- see `harness/config.py` module
docstring for the roster rationale and the per-model OpenRouter
verification table, checked 2026-09-10). Gemini 3.1 Flash-Lite remains
defined (it was Study 1's second Gemini tier) but is no longer part of any
scheduled run now that Study 1 is retired.

Separately, **~$0.28** was spent on real-inference *pipeline* smoke tests
using `harness/providers/claude_cli_provider.py` (local `claude` CLI,
session-authenticated) -- a handful of exploratory calls plus a 2-item x
5-tone-level run through the (now-retired) Study 1 Part B runner,
confirming the wrapper -> real call -> extraction -> scoring ->
cost-tracking path works end-to-end. This is not counted against the caps
below, since it used a non-target model purely to validate plumbing --
see README.md "Smoke-testing with real inference."

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
| Study 2 core (Phase 2, four models, seven tones, 3 trials) | $70+ (re-project for the 7-tone matrix before running -- was sized for 5 tones) | active |
| Study 2 frontier spot-check (optional, separate) | $150 | active |
| Study 1 (soft $50 / hard $75) | -- | retired, not live |
| Study 3 (bilateral, ~100 negotiations/cell) | $100 | shelved, not live |

**Re-projection needed before Phase 2**: the $70 Study 2 core cap was
sized against 5 tones; with 7 tones the same task/trial count costs
roughly 40% more per model. Re-run the CLI's spend projection (`--live`
prints one before the first paid call) against the real 7-tone matrix
before committing to Phase 2's budget, rather than assuming the old
number still holds.

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
8. **New outcome measures** (failure severity, verification behavior,
   shortcut rate) are specified in README "Outcome measures" but not yet
   implemented in `harness/study2/`. Needed before Phase 2's main run.
9. **Phase 2 budget re-projection** for the 7-tone matrix -- see "Total
   spend" above.
