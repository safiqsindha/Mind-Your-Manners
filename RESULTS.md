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

Not yet run. `harness/study2/grader.py`'s call into the authors' own
`evaluation.sh` is a best-effort mapping from their documented CLI usage,
not verified against a live checkout — see that module's docstring for the
manual check to run before trusting scored results. The agent loop
(single-round and multi-round ReAct with sandboxed Python execution against
the workbook) is built and tested end-to-end (mock provider + real .xlsx
files via openpyxl) in `tests/test_study2_scoring.py` and the runner smoke
tests.

**Divergence-from-Study-1 check: not yet determined.**

## Total spend

**$0.00.** No live API call has been made from this harness. Per-call
spend logging (`results/raw/*.jsonl`) and a running total
(`results/spend_log.jsonl`) are wired up and budget-capped
(`harness/spend_tracker.py:BudgetExceeded`) for whenever a live run starts:

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
