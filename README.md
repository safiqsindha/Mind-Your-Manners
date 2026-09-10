# Prompt-Tone Evaluation Harness

A reproducible harness for testing whether prompt politeness/tone affects
LLM accuracy (Study 1, single-turn QA) and agentic task quality (Study 2,
SpreadsheetBench). See `RESULTS.md` for the current results status.

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

## Running it

Every subcommand defaults to **dry-run**: it forces the mock provider
regardless of `harness/config.py`, so nothing ever costs money unless you
pass `--live`. `--live` additionally refuses to run if the API keys a
selected model needs aren't set (see `.env.example`).

```bash
pip install -r requirements.txt

# Dry-run smoke test (free, no keys needed)
python -m harness.cli study1 validation-gate --model gemini-flash --n-items 10

# Live validation gate -- must pass before spending on the full Part B run.
# --live prints a rough spend projection and asks for confirmation before
# the first paid call; pass --yes to skip the prompt for scripted use.
python -m harness.cli --live study1 validation-gate \
  --model gemini-flash --benchmark mmlu_pro --n-items 100 \
  --expected-accuracy <current published figure> --tolerance 0.05

# Defaults to all 5 Study 1 models (STUDY1_MODELS -- includes the Gemini
# Lite tier); override --models to run a subset.
python -m harness.cli --live study1 part-b --benchmark mmlu_pro --n-items 100

# Part A: clones the Mind Your Tone dataset automatically (no --dataset-path
# needed), reproduces their exact protocol including NUM_RUNS=10 repeats --
# 250 prompts x 10 runs x n models adds up fast, size --budget-cap accordingly
python -m harness.cli --live study1 part-a --models gemini-flash --n-runs 10

python -m harness.cli --live study2 validation-gate \
  --model gemini-flash --repo-dir data/spreadsheetbench \
  --expected-accuracy <current published figure>

# Study 2 defaults to CORE_MODELS (4 models -- no Gemini Lite tier)
python -m harness.cli --live study2 pilot --n-tasks 30
```

Run `pytest` for the test suite (all pass against the mock provider, no
network/keys required beyond `datasets`' HF pull in a couple of dataset
tests being skippable offline).

## Before spending real money

1. Re-verify every `model_id` in `harness/config.py` against OpenRouter's
   current model list and pricing (`GET https://openrouter.ai/api/v1/models`,
   no auth required) -- the ones there now were checked on 2026-09-10 (see
   the module docstring's verification table) but OpenRouter's catalog and
   pricing move fast; don't assume they're still current.
2. Run the validation gate for each study and confirm it passes against a
   currently-published baseline figure before running any tone condition.
3. Watch `results/spend_log.jsonl` / the CLI's printed spend summaries
   against the caps in `harness/config.py`: Study 1 has a two-tier cap
   (soft warning at $50, hard stop at $75); Study 2 is a hard $90 across its
   four core models (pilot $20 + core $70), with an independent $150 cap for
   the optional frontier spot-check; Study 3 is a hard $100. `--live` prints
   a rough projection and asks for confirmation before the first paid call
   in every run (pass `--yes` to skip the prompt for scripted/CI use).
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

## License note

If you extract data from `RUCKBReasoning/SpreadsheetBench` into this repo
(as opposed to keeping it in a git-ignored `data/` cache), it is CC BY-SA
4.0 -- keep attribution and the same license on any redistribution.
