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

## Total spend

**$0.00 against the study's target-model budget caps.** No target model
has been called against the current roster (GPT-5.6 Luna, GLM 5.3 Flash,
DeepSeek V4 Flash, Qwen3.8 Flash -- see `harness/config.py` module
docstring for the roster rationale and the per-model OpenRouter
verification table, checked 2026-09-10). Both Gemini tiers were dropped in
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
