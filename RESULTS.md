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

## Study 3 — Negotiation (AgenticPay, arXiv 2602.06008)

Not yet run against a target model. `harness/study3/` was built after
cloning `SafeRL-Lab/AgenticPay` and reading its real code directly (not
guessed) -- see `harness/study3/agenticpay_dep.py`'s docstring for exactly
what was verified: the `BaseLLM.generate(prompt, temperature, max_tokens,
**kwargs)` interface, `role_description` as the one documented
tone-injection point, the `<message>`/`### BUYER_PRICE($X) ###` extraction
contract, and that `env.step()` already computes GlobalScore/BuyerScore/
SellerScore on termination (none of that scoring is reimplemented).

**Gating check:** one full neutral negotiation was run end to end against
the real cloned code (buyer max $120, seller min $80, initial ask $150),
using a throwaway `claude` CLI-backed `BaseLLM` adapter since no
OpenRouter key exists in this build. Result: agreement at $120 in 3
rounds, GlobalScore 19.602. This adapter is not part of the shipped
Study 3 code -- real runs go through `harness/study3/llm_adapter.py`,
which routes through this harness's own OpenRouter-based Provider.

The 5x5 buyer-tone x seller-tone matrix (`run_bilateral_matrix`,
restricted to the bilateral env `Task1_basic_price_negotiation-v0` per the
task spec) was smoke-tested end-to-end against the real cloned AgenticPay
code and the mock provider: `python -m harness.cli study3
bilateral-matrix` completes all 25 cells, all reaching agreement. Getting
a full dry run to actually converge (rather than erroring or looping to
timeout) surfaced one real bug worth recording: the mock provider's
negotiation responder initially scanned the *entire* prompt for the last
`### BUYER_PRICE($X) ###` / `### SELLER_PRICE($X) ###` match to simulate
"the previous offer" -- but AgenticPay's own agent prompts are full of
worked examples using that exact format (e.g. "Deal -- I'll take it at
### BUYER_PRICE($6.50) ###."), so every simulated negotiation immediately
"agreed" at whatever price happened to appear last in the *instructions*,
not the conversation. Fixed by restricting the scan to the prompt's actual
"Conversation History:" section (`harness/providers/mock_provider.py:
_conversation_history_only()`). Mock-only bug -- does not affect real
model calls -- but a good reminder that "read the real prompt text before
trusting a regex against it" applies recursively, not just to the
benchmark's own schema.

The Benjamini-Hochberg multiple-testing correction and its exact
comparison set (24 of the 25 cells vs. the L3_neutral/L3_neutral baseline)
are pre-registered in `harness/study3/preregistration.py`, committed
before any live negotiation has run -- see README.md "Before spending real
money."

**Value-given-away verdict: not yet determined -- needs a live run
against a target model.**

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
| Study 3 (bilateral, ~100 negotiations/cell) | $100 |

## What's needed to actually run this

1. **API keys** for at least: Google (Gemini Flash-tier), DeepSeek, Qwen
   (DashScope), OpenRouter (Llama/Gemma-tier) — see `.env.example`. Only
   remaining hard blocker that requires the repo owner specifically.
2. ~~The Mind Your Tone 250-prompt dataset~~ — **resolved**: found via the
   paper's AMCIS 2026 full-paper extension, `ensure_mind_your_tone_repo()`
   clones it automatically.
3. ~~A cloned `SpreadsheetBench` checkout and grader sanity check~~ —
   **resolved**: cloned, and the grader/dataset code was rewritten to match
   the real repo (see "Study 2" above). One gap remains: LibreOffice's
   formula recalculation is broken in this build's own environment —
   confirm it works wherever a live batch actually runs.
4. ~~A better sandbox for Study 2's code execution~~ — **resolved**: real,
   tested network isolation via a Linux user+network namespace. Filesystem
   access is still unrestricted — a full container is still preferable
   where available.
5. Re-verification of every model ID / price in `harness/config.py` against
   current provider docs (flagged inline with `VERIFY` comments) — not yet
   done.
6. ~~A cloned `AgenticPay` checkout and one real negotiation run~~ —
   **resolved**: cloned, its real schema read directly, one full neutral
   negotiation run end to end (see "Study 3" above), and the 5x5 bilateral
   matrix smoke-tested against the real cloned code with the mock provider.
