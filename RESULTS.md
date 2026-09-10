# Results

**Status: NOT YET RUN.** No API keys were available in the environment this
harness was built in, and per an explicit decision with the requester, this
build stopped at "harness built and tested against a mock provider" rather
than spending real money without credentials or a live-spend confirmation.
Everything below is a template plus the honest state of each precondition —
fill in the actual numbers as each stage runs.

## Validation gate

| Study | Model | Benchmark | Observed accuracy | Published accuracy | Within tolerance? |
|---|---|---|---|---|---|
| 1 | — | MMLU-Pro | not run | — | — |
| 2 | — | SpreadsheetBench | not run | — | — |

Both gates are wired up (`harness/study1/runner.py:run_validation_gate`,
`harness/study2/runner.py:run_validation_gate`) and exercised against the
mock provider + real MMLU-Pro data during development — see the harness test
suite. They have not been run against a real model.

## Part A — Replication (Mind Your Tone, arXiv 2510.04950)

**No longer blocked; not yet run against a target model.** The 250-prompt
dataset's repo was found via the paper's full-paper extension (arXiv
2605.29027, same authors) at
`github.com/OmDobariya/AMCIS_politeness_llms` — confirmed real, cloned, and
inspected directly (see `README.md` "Dataset availability" for the full
account). `harness/study1/dataset.py`, `runner.py`, and
`answer_extraction.py` were rewritten to reproduce their real CSV schema,
their real system prompt + instruction preamble (pulled directly from
their own `code_50_que_all_llms.ipynb`, not re-derived), their NUM_RUNS=10
protocol, and their exact answer-extraction regex. A full mock-provider
pass through `run_part_a_replication` against the real cloned 250-row CSV
completes correctly end-to-end.

Original paper's own reported numbers, for reference (ChatGPT-4o only, not
yet reproduced by this harness on any model):

| Tone | Accuracy |
|---|---|
| Very Polite | 80.8% |
| Polite | 81.4% |
| Neutral | 82.2% |
| Rude | 82.8% |
| Very Rude | 84.8% |

The AMCIS 2026 full-paper extension adds a second, larger dataset (570
MMLU questions across 57 subjects, 7 tones including two new extremes —
Sycophantic and Threatening — tested on ChatGPT-4o, ChatGPT-5-nano, Gemini
2.5 Flash, and Gemini 2.5 Flash Lite) and reports tone effects as
"systematic but highly model-dependent." Not yet incorporated into this
harness — Part B's MMLU-Pro remaster already covers similar ground with
programmatic (not hand-written) wrappers, which is the more important
methodological fix; a 7-tone extension is a possible future addition, not
a blocker.

**Replication verdict: not yet determined — needs a live run against a
target model.**

## Part B — Remaster (MMLU-Pro / GPQA Diamond, programmatic tone wrappers)

Not yet run. The five tone wrappers are built, length-matched (max spread 5
tokens; see `tests/test_tone_wrappers.py`), and instruction-identical across
levels. `harness/study1/runner.py:run_part_b_remaster` applies them to
byte-identical MMLU-Pro/GPQA question text and has been smoke-tested
end-to-end against real MMLU-Pro items with the mock provider.

**Remaster verdict: not yet determined.**

## Study 2 — Agentic spreadsheet work (SpreadsheetBench)

Not yet run against a target model. Since the previous update, the dataset
loader and grader were rewritten after actually cloning
`RUCKBReasoning/SpreadsheetBench` and reading the real `evaluation.py` —
the earlier version guessed a CLI/env-var interface that does not exist.
The corrected grader imports and calls their real `compare_workbooks()`
function directly (not a subprocess/CLI guess) and reproduces their exact
soft/hard-restriction scoring. Verified on a real sample task: grading the
answer file against itself passes on all 3 test cases; grading the
unmodified input against the answer fails all 3, as expected. A full
mock-provider run through `run_condition_batch` (2 real tasks × 5 tone
levels, real cloned repo, real grader) completes without error.

**Gating check results (2026-09-10):** ran the full sample set's answer
files against themselves through `compare_workbooks()`, unmodified —
**199/200 pass**. The one failure is a real bug in the *authors'* own
`evaluation.py` (their `answer_position.split(',')` doesn't strip
whitespace, so a multi-range position with a space after the comma
resolves to a malformed cell reference and raises `AttributeError`) — not
something to patch in their code, and this harness's grader already fails
that one test case gracefully (records it as a failed comparison) rather
than crashing the batch.

Grading formula-bearing tasks requires recalculating cached values first
(LibreOffice headless conversion, same as their own `open_spreadsheet.py`).
This was **broken in this build's container and is now fixed**, along with
two further bugs the fix process surfaced:

1. `libreoffice-calc`/`libreoffice-writer` were never actually installed —
   only `libreoffice-core` was present, despite `soffice` being on PATH.
   Confirmed via `strace`: a document-loader shared library
   (`libswdlo.so`) was `ENOENT`. `apt-get install libreoffice-calc
   libreoffice-writer` fixed it.
2. This repo's own `recalculate_with_libreoffice()` converted a file to
   itself (same source and output directory), which makes LibreOffice
   print "Overwriting: ..." then silently fail the actual write to
   **stderr** with **exit code 0** — the old success check only looked at
   stdout and the return code, so it reported success while leaving the
   file un-recalculated. Confirmed directly: recalculating `=A1*A2` this
   way reported `ok=True` but the cell still read `None` afterward. Fixed
   by converting into a temp directory and moving the result back, the
   same approach their own `open_spreadsheet.py:just_open_libreoffice()`
   uses.
3. The grader only recalculated the *model's* output, never the
   ground-truth answer file — and SpreadsheetBench's own answer files can
   themselves contain uncached formulas. Confirmed on a real task (99-24):
   its answer file's own cell A33 reads `None` unrecalculated but
   recalculates to `32`, meaning a perfectly correct model output would
   have failed comparison for no fault of its own. Fixed by recalculating
   answer files too, memoized once per file (not once per grading call, to
   avoid re-running LibreOffice on the same immutable ground truth
   thousands of times across a run).

After all three fixes: the 3 tasks that failed in a 40-task recalculation
subset (99-24, CF_6540, 44389 — all hit bug #3) now pass individually
(3/3 test cases each), and `tests/test_grader_recalculation.py` locks in
both the fix and the memoization behavior against regressions. The full
200-task gold-vs-itself recalculation re-run has now completed:
**199/200 pass.** The one remaining failure (task 56637) is the
whitespace-in-multi-range bug in the authors' own `evaluation.py`
described above (not something to patch in their code), and this
harness's grader already fails that single test case gracefully rather
than crashing the batch.

The agent loop (single-round and multi-round ReAct with sandboxed Python
execution against the workbook) is built and tested end-to-end (mock
provider + real .xlsx files via openpyxl) in `tests/test_study2_scoring.py`.
Its sandbox now has real, tested network isolation via a Linux
user+network namespace (`tests/test_sandbox.py` confirms a socket connect
attempt inside it actually fails) — see README.md "Before spending real
money" for what's still not covered (filesystem access).

Grading also now correctly reflects SpreadsheetBench's actual design: each
task's 3 test cases are graded for *generalization* of one agent-produced
solution, not 3 independent agent runs — the agent sees only test case 1,
and its generated code is mechanically re-applied (no extra model calls)
to test cases 2 and 3 before grading all 3 together.

**Divergence-from-Study-1 check: not yet determined.**

## Total spend

**$0.00 against the study's target-model budget caps.** No target model
has been called against the current roster (GPT-5.6 Luna, Gemini 3.8 Flash,
Gemini 3.1 Flash-Lite, DeepSeek V4 Flash, Qwen3.8 Flash -- see
`harness/config.py` module docstring for the roster rationale and the
per-model OpenRouter verification table, checked 2026-09-10). The earlier
roster (Gemini 2.5 Flash / DeepSeek-V3 / Qwen2.5-72B / Llama 3.3 70B) has
been replaced; Llama is dropped entirely, not carried forward as a spare.

Separately, **~$0.28** was spent on real-inference *pipeline* smoke tests
using `harness/providers/claude_cli_provider.py` (local `claude` CLI,
session-authenticated) -- a handful of exploratory calls plus a 2-item x
5-tone-level run through the actual Study 1 Part B runner, confirming the
wrapper -> real call -> extraction -> scoring -> cost-tracking path works
end-to-end. This is not counted against the caps below, since it used a
non-target model purely to validate plumbing -- see README.md
"Smoke-testing with real inference."

Per-call spend logging (`results/raw/*.jsonl`) and a running total
(`results/spend_log.jsonl`) are wired up and budget-capped
(`harness/spend_tracker.py:BudgetExceeded`) for whenever a live target-model
run starts. `--live` also prints a rough spend projection and requires
confirmation before the first paid call in any run (`--yes` skips the
prompt for scripted/CI use):

| Phase | Cap |
|---|---|
| Study 1 (soft warning) | $50 |
| Study 1 (hard stop) | $75 |
| Study 2 pilot | $20 |
| Study 2 core | $70 |
| Study 2 frontier spot-check (optional, separate) | $150 |
| Study 3 (bilateral, 100 negotiations/cell) | $100 |

## What's needed to actually run this

1. **An OpenRouter API key.** All five roster models route through
   OpenRouter on one key (see README.md "Single provider path") — only
   remaining hard blocker that requires the repo owner specifically.
2. ~~The Mind Your Tone 250-prompt dataset~~ — **resolved**: found via the
   paper's AMCIS 2026 full-paper extension, `ensure_mind_your_tone_repo()`
   clones it automatically.
3. ~~A cloned `SpreadsheetBench` checkout and grader sanity check~~ —
   **resolved**: cloned, and the grader/dataset code was rewritten to match
   the real repo (see "Study 2" above). LibreOffice's formula
   recalculation, previously broken in this build's own environment, is
   also now fixed (see git history) — still worth confirming
   `libreoffice-calc`/`libreoffice-writer` are installed wherever a live
   batch actually runs.
4. ~~A better sandbox for Study 2's code execution~~ — **resolved**: real,
   tested network isolation via a Linux user+network namespace. Filesystem
   access is still unrestricted — a full container is still preferable
   where available.
5. ~~Re-verification of every model ID / price in `harness/config.py`~~ —
   **resolved for the current roster**: every model_id, price, and
   provider pin was checked directly against OpenRouter's live catalog on
   2026-09-10 (see `harness/config.py` module docstring). Re-run this
   check if it's been more than a few weeks.
6. Full `provider.only`/`allow_fallbacks`/`quantizations` enforcement, the
   served-provider assertion, response-cache-disable assertion, and
   caching instrumentation are designed and verified against OpenRouter's
   documented API (see `harness/config.py`) but not yet implemented in the
   provider layer itself — that's the next PR.
7. Study 3 (AgenticPay negotiation) is designed and gating-checked (one
   real negotiation run end-to-end against the actual AgenticPay code, via
   a throwaway `claude` CLI adapter — see PR for details) but not yet
   built as a harness module.
