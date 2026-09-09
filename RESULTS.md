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

**Blocked.** The original 250-prompt dataset has no discoverable public
repository (searched the arXiv abstract, PDF, HTML mirror, and secondary
sources — see `README.md` "Dataset availability"). The paper text does not
link a repo, and no `anonymous.4open.science`/GitHub link for it exists in
the published version. Replication cannot proceed without this file coming
from the authors or ACL Anthology supplementary materials.

Original paper's own reported numbers, for reference (ChatGPT-4o only, not
yet reproduced by this harness on any model):

| Tone | Accuracy |
|---|---|
| Very Polite | 80.8% |
| Polite | 81.4% |
| Neutral | 82.2% |
| Rude | 82.8% |
| Very Rude | 84.8% |

**Replication verdict: not yet determined — dataset unobtained.**

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

**Known gap, discovered while verifying:** grading requires formulas to be
recalculated first (LibreOffice headless conversion), and LibreOffice's
headless conversion is broken in this build's own container — it fails
even on the benchmark's own known-good sample files. This must be
confirmed working in whatever environment runs a live batch before any
formula-based task's grade can be trusted.

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
(Gemini/DeepSeek/Qwen/Llama/frontier spot-check) has been called.

Separately, **~$0.28** was spent on real-inference *pipeline* smoke tests
using `harness/providers/claude_cli_provider.py` (local `claude` CLI,
session-authenticated) -- a handful of exploratory calls plus a 2-item x
5-tone-level run through the actual Study 1 Part B runner, confirming the
wrapper -> real call -> extraction -> scoring -> cost-tracking path works
end-to-end. This is not counted against the $50/$15/$40/$150 caps below,
since it used a non-target model purely to validate plumbing -- see
README.md "Smoke-testing with real inference."

Per-call spend logging (`results/raw/*.jsonl`) and a running total
(`results/spend_log.jsonl`) are wired up and budget-capped
(`harness/spend_tracker.py:BudgetExceeded`) for whenever a live target-model
run starts:

| Phase | Cap |
|---|---|
| Study 1 (Part A + Part B combined) | $50 |
| Study 2 pilot | $15 |
| Study 2 core | $40 |
| Study 2 frontier spot-check | $150 |

## What's needed to actually run this

1. API keys for at least: Google (Gemini Flash-tier), DeepSeek, Qwen
   (DashScope), OpenRouter (Llama/Gemma-tier) — see `.env.example`.
2. The Mind Your Tone 250-prompt dataset, obtained directly from the
   authors, for Part A only (Part B does not need it).
3. A cloned `SpreadsheetBench` checkout (`harness/study2/dataset.py:ensure_repo`)
   and one manual grader sanity check before trusting Study 2's scored
   output.
4. A container-level sandbox for Study 2's code execution step before any
   live/spend run (see `harness/study2/sandbox.py` docstring) — the current
   subprocess-level isolation is a development-time floor, not production
   isolation for arbitrarily adversarial model-generated code.
5. Re-verification of every model ID / price in `harness/config.py` against
   current provider docs (flagged inline with `VERIFY` comments).
