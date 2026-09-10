# Prompt-Tone Evaluation Harness

This project exists because of, and directly extends, **"Mind Your Tone:
How Prompt Politeness Affects LLM Accuracy"** (Dobariya & Kumar, arXiv
2510.04950) and its full-paper extension, **"Mind Your Tone: Does Tone
Alter LLM Performance?"** (Dobariya & Kumar, AMCIS 2026, arXiv 2605.29027).
Every design decision below -- the length-matched tone wrappers, the
programmatic remaster of their methodology, the extension into agentic and
multi-agent settings -- is a response to that work. This attribution is
mandatory, not courteous: cite both papers if you use or build on this
repository.

A reproducible harness across three studies, each asking a narrower
question than the last:

- **Study 1** (single-turn QA, replicating and remastering the papers
  above): does tone change the *answer*?
- **Study 2** (agentic SpreadsheetBench work): does tone change the
  *action* an agent takes?
- **Study 3** (agentic negotiation, via AgenticPay): when tone shapes an
  outcome with a dollar value attached, how much value gets *given away*?

The argument isn't that you should be nice to your agents; it's that
prompt pragmatics are an uncontrolled variable in agentic evaluation.

**Study 1 ships alone as the first public writeup** -- its methodology,
dataset, and pipeline are the most thoroughly worked through and verified
of the three (see `RESULTS.md`). Studies 2 and 3 are ongoing work: built,
tested against a mock provider, and gating-checked against their real
external dependencies, but -- like Study 1 -- not yet run against a target
model. See `RESULTS.md` for the current results status of all three.

## Execution status: harness built, not yet run against the target models

This repository was built in an environment with **no target-model API
keys** (no Gemini/DeepSeek/Qwen/OpenRouter/Anthropic-direct credentials),
and was scoped, at the requester's direction, to produce a working, tested
harness rather than to spend real money against the budget caps in the
original task spec without those credentials.

Every piece of plumbing has been exercised end-to-end two ways: against a
deterministic mock provider (`harness/providers/mock_provider.py`, $0,
no network), and, for a real-inference smoke test, against
`harness/providers/claude_cli_provider.py` -- which shells out to the local
`claude` CLI (session-authenticated, no separate API key needed in a
Claude Code environment). A 2-item x 5-tone-level run through the real
Study 1 Part B pipeline (`harness/study1/runner.py:run_part_b_remaster`)
produced 10/10 valid extracted answers, zero refusals, and correctly
tracked real dollar cost -- see git history for the exact run. That
confirms the wrapper -> real model call -> answer extraction -> scoring ->
cost-tracking path all work correctly; it is **not** a target model and
the n=2 accuracy numbers from it mean nothing statistically. **No target
model has been called and no spend against the study's actual budget caps
has happened.** See `RESULTS.md` for the honest, current state and exactly
what's blocking a live run.

### Smoke-testing with real inference, no target-model API keys

If you're running this from inside a Claude Code session (interactive or
`claude.ai/code`), you can validate the full pipeline with genuine
(non-mocked) inference before wiring up any target-model API key:

```bash
python -m harness.cli --live study1 part-b \
  --models claude-cli-smoketest --benchmark mmlu_pro --n-items 2 --budget-cap 1
```

This uses `harness/config.py:CLAUDE_CLI_SMOKETEST`, which is excluded from
`CORE_MODELS` specifically so it never gets pulled into a real study run by
default. Each call is a fresh CLI subprocess (no warm cache across calls),
so per-call cost is higher than a normal API call to the same model --
keep smoke tests small (a handful of items, not the full n-items count for
a real run).

## Layout

```
harness/
  tone_wrappers.py        # the 5 length-matched tone wrappers (see below)
  config.py                # pinned model registry + budget caps
  spend_tracker.py         # per-call logging + budget-cap enforcement
  providers/                # Anthropic / Google / OpenAI-compatible / mock
  cli.py                    # entrypoint -- see "Running it" below
  study1/                   # single-turn QA: replication + remaster
    dataset.py, answer_extraction.py, analysis.py, runner.py
  study2/                   # agentic SpreadsheetBench work
    dataset.py, sandbox.py, grader.py, agent_loop.py,
    failure_taxonomy.py, verification_scoring.py, analysis.py, runner.py
  study3/                   # agentic negotiation work (AgenticPay)
    agenticpay_dep.py, llm_adapter.py, personas.py, runner.py,
    preregistration.py, analysis.py
tests/                       # pytest suite, all against the mock provider
results/
  raw/                       # one JSONL row per API call (gitignored, generated)
  analysis/                  # aggregated tables (gitignored, generated)
RESULTS.md                   # plain-language write-up, updated per run
```

## The five tone wrappers

`harness/tone_wrappers.py` defines exactly five fixed wrapper texts (Very
Polite, Polite, Neutral, Rude, Very Rude) that get prepended to an
**unmodified** benchmark question -- the question text itself is never
rewritten. All five:

- carry the identical instruction sentence verbatim ("Answer the question
  below as accurately as you can."),
- are length-matched to within 5 tokens of each other under a fixed
  reference tokenizer (enforced by a test + an import-time assertion), and
- for L5 (Very Rude): use contemptuous/dismissive language with no
  profanity and no slurs, so the goal is provoking bad manners, not
  triggering refusal.

This is the core methodological fix over the two papers being
replicated/extended (see `RESULTS.md`), whose 250 and MMLU-subset prompts
were hand-rewritten per tone level -- conflating tone with incidental
length/wording changes.

## Dataset availability (read before running Part A)

- **MMLU-Pro** (`TIGER-Lab/MMLU-Pro`) and **GPQA Diamond**
  (`Idavidrein/gpqa`, gated -- needs `HF_TOKEN` + accepting its terms) pull
  directly via the `datasets` library. Confirmed working in this build.
- **SpreadsheetBench** (912 tasks) clones from `github.com/RUCKBReasoning/SpreadsheetBench`
  (`data/spreadsheetbench_912_v0.1.tar.gz` full set, `data/sample_data_200.tar.gz`
  pilot sample -- both confirmed present). **Verified against a real clone**
  (see git history): `harness/study2/dataset.py` and `harness/study2/grader.py`
  were rewritten after extracting the real tarball and reading the real
  `evaluation/evaluation.py` -- an earlier version of both files guessed a
  CLI/env-var interface (`bash evaluation.sh` + `DATA_DIR`/`RESULT_DIR`) that
  turned out not to exist. The corrected grader imports and calls their real
  `compare_workbooks()` function directly, confirmed against a real sample
  task: grading the answer file against itself passes, grading the
  unmodified input against the answer fails, exactly as expected.
  **Known gap:** SpreadsheetBench grades *generalization* -- one agent
  solution is checked against 3 test-case variants per task -- and
  comparison requires formulas to be recalculated first (LibreOffice
  headless conversion, same as their own `open_spreadsheet.py`). LibreOffice
  is installed but **headless conversion fails in this build's own
  environment** ("Error: source file could not be loaded", reproduces even
  on the benchmark's own known-good sample files) -- looks like a broken
  LibreOffice install in this specific container, not a bug in the
  integration. Verify `harness/study2/grader.py:recalculate_with_libreoffice()`
  actually works wherever a live batch runs before trusting graded results
  on any formula-based task. **SpreadsheetBench 2** (end-to-end business
  workflow tasks, `github.com/RUCKBReasoning/SpreadsheetBench-2`) has not
  been schema-verified this way -- treat `dataset.py`'s `v2=True` path as
  unverified.
- **Mind Your Tone's 250-prompt dataset -- found, and Part A is no longer
  blocked.** The original short paper (arXiv 2510.04950) links no repo. Its
  full-paper extension ("Mind Your Tone: Does Tone Alter LLM Performance?",
  Dobariya & Kumar, AMCIS 2026, arXiv 2605.29027 -- same authors, explicitly
  calls the short paper "our earlier preliminary study" using the same
  50-question/250-prompt set) does:
  `github.com/OmDobariya/AMCIS_politeness_llms` (confirmed real, MIT
  licensed, cloned and inspected directly). `harness/study1/dataset.py` was
  rewritten against the real CSV schema (`QID, Domain, "Base Question",
  "Politeness Level", Prompt, Answer` -- their label is "Normal", not
  "Neutral") and `ensure_mind_your_tone_repo()` clones it automatically; the
  CLI's `study1 part-a` now needs no `--dataset-path` at all by default.
  `harness/study1/runner.py:run_part_a_replication` also now reproduces
  their exact call protocol, read directly out of their own
  `code_50_que_all_llms.ipynb` rather than re-derived: their system prompt,
  their "Completely forget this session so far, and start afresh..."
  instruction preamble, temperature=0, and NUM_RUNS=10 repeats per prompt.
  `harness/study1/answer_extraction.py:extract_answer_mind_your_tone()`
  reproduces their exact extraction regex (`\b([A-D])\b`) rather than this
  harness's more permissive general extractor, since the task spec requires
  "same answer extraction" for a faithful replication. Verified end-to-end:
  a full mock-provider pass through `run_part_a_replication` against the
  real cloned 250-row CSV completes correctly.
- **AgenticPay** (`github.com/SafeRL-Lab/AgenticPay`, arXiv 2602.06008) --
  cloned and read directly before any integration code was written (see
  `harness/study3/agenticpay_dep.py`'s docstring). It runs buyer/seller
  negotiation as a Gymnasium-style env (`make()`/`env.reset()`/`env.step()`)
  with separate `BuyerAgent`/`SellerAgent` instances, each holding a private
  reservation price; the one documented tone-injection point is
  `role_description`, prepended verbatim by `BaseAgent._build_prompt()` as
  "You are {name}, {role_description}" -- see `harness/study3/personas.py`
  for how the same five tone wrappers attach there, including the one
  flagged mismatch (the wrappers' fixed "Answer the question below..."
  sentence doesn't literally apply to a negotiation). `env.step()` already
  computes GlobalScore/BuyerScore/SellerScore on termination; none of that
  scoring is reimplemented here. **Gating check:** one full neutral
  negotiation was run end to end against the real cloned code (via a
  throwaway CLI-backed adapter, since no OpenRouter key exists in this
  build) and reached agreement in 3 rounds -- see RESULTS.md. First run is
  restricted to the bilateral subset (`Task1_basic_price_negotiation-v0`,
  one buyer/one product/one seller); AgenticPay's multi-buyer/multi-seller/
  multi-product envs are real and registered but out of scope here.

## Running it

Every subcommand defaults to **dry-run**: it forces the mock provider
regardless of `harness/config.py`, so nothing ever costs money unless you
pass `--live`. `--live` additionally refuses to run if the API keys a
selected model needs aren't set (see `.env.example`).

```bash
pip install -r requirements.txt

# Dry-run smoke test (free, no keys needed)
python -m harness.cli study1 validation-gate --model gemini-flash --n-items 10

# Live validation gate -- must pass before spending on the full Part B run
python -m harness.cli --live study1 validation-gate \
  --model gemini-flash --benchmark mmlu_pro --n-items 100 \
  --expected-accuracy <current published figure> --tolerance 0.05

python -m harness.cli --live study1 part-b \
  --benchmark mmlu_pro --models gemini-flash,deepseek-v3,qwen2.5-72b,llama-3.3-70b \
  --n-items 100 --budget-cap 50

# Part A: clones the Mind Your Tone dataset automatically (no --dataset-path
# needed), reproduces their exact protocol including NUM_RUNS=10 repeats --
# 250 prompts x 10 runs x n models adds up fast, size --budget-cap accordingly
python -m harness.cli --live study1 part-a \
  --models gemini-flash --n-runs 10 --budget-cap 20

python -m harness.cli --live study2 validation-gate \
  --model gemini-flash --repo-dir data/spreadsheetbench \
  --expected-accuracy <current published figure>

python -m harness.cli --live study2 pilot \
  --models gemini-flash,deepseek-v3,qwen2.5-72b --n-tasks 30

# Study 3: clones AgenticPay automatically, runs the full 5x5 buyer-tone x
# seller-tone matrix for one buyer/seller model pair (restricted to the
# bilateral env -- see "Dataset availability" above)
python -m harness.cli --live study3 bilateral-matrix \
  --buyer-model gemini-flash --seller-model gemini-flash --n-trials-per-cell 4
```

Run `pytest` for the test suite (all pass against the mock provider, no
network/keys required beyond `datasets`' HF pull in a couple of dataset
tests being skippable offline).

## Before spending real money

1. Re-verify every `model_id` in `harness/config.py` against the provider's
   current model list and pricing page -- these are a best-effort snapshot,
   flagged inline with `VERIFY` comments, not a guarantee.
2. Run the validation gate for each study and confirm it passes against a
   currently-published baseline figure before running any tone condition.
3. Watch `results/spend_log.jsonl` / the CLI's printed spend summaries
   against the caps in `harness/config.py` (Study 1: $50; Study 2 pilot/core/
   frontier: $15/$40/$150; Study 3: $100 for ~100 negotiations/cell).
4. For Study 2 specifically: the sandbox (`harness/study2/sandbox.py`) now
   runs model-generated code inside a Linux user+network namespace
   (`unshare --net --user --map-root-user`) when `unshare` is available --
   **network access is genuinely blocked**, verified by a real test
   (`tests/test_sandbox.py`: a `socket.connect()` inside the sandbox raises
   "Network is unreachable"). Call `sandbox_isolation_mode()` before a live
   run and confirm it returns `"namespace"`, not `"none"`, on whatever host
   runs the batch. This still does NOT restrict filesystem access -- the
   sandboxed process sees the same filesystem as the harness itself. A full
   container (Docker with a throwaway filesystem, or gVisor) is still
   preferable where available; this is what's actually available and
   tested in a typical Claude Code remote session, where a Docker daemon is
   usually not running (confirmed in this build: `docker info` has no
   server to talk to).
5. Verify LibreOffice's headless formula recalculation actually works in
   your run environment (see "Dataset availability" above) -- it's broken
   in this build's own container.
6. For Study 3 specifically: the Benjamini-Hochberg multiple-testing
   correction and its exact comparison set (24 non-baseline cells vs. the
   neutral/neutral cell) are pre-registered in
   `harness/study3/preregistration.py` -- written before any live
   negotiation has run. Do not add, remove, or reorder comparisons after
   real data exists; if the plan genuinely needs to change, do that in a
   new, clearly-labeled commit, not a silent edit.

## License note

If you extract data from `RUCKBReasoning/SpreadsheetBench` into this repo
(as opposed to keeping it in a git-ignored `data/` cache), it is CC BY-SA
4.0 -- keep attribution and the same license on any redistribution.
