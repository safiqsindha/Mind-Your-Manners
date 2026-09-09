# Prompt-Tone Evaluation Harness

A reproducible harness for testing whether prompt politeness/tone affects
LLM accuracy (Study 1, single-turn QA) and agentic task quality (Study 2,
SpreadsheetBench). See `RESULTS.md` for the current results status.

## Execution status: harness built, not yet run live

This repository was built in an environment with **no LLM provider API
keys** and was scoped, at the requester's direction, to produce a working,
tested harness rather than to spend real money against the budget caps in
the original task spec. Every piece of plumbing below has been exercised
end-to-end against a deterministic mock provider (`harness/providers/mock_provider.py`)
and a real pull of MMLU-Pro from Hugging Face, but **no real model has been
called and $0 has been spent.** See `RESULTS.md` for the honest, current
state and exactly what's blocking a live run.

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
- **SpreadsheetBench** (912 tasks) and **SpreadsheetBench 2** clone from
  `github.com/RUCKBReasoning/SpreadsheetBench{,-2}` (confirmed real repos,
  `data/all_data_912.tar.gz` / `data/sample_data_200.tar.gz`). Not yet
  cloned or run against in this build -- `harness/study2/grader.py`'s exact
  subprocess invocation of their `evaluation.sh` is a best-effort mapping
  from their README, not something exercised against a live checkout.
  Validate it manually (see the module docstring) before trusting scored
  results.
- **Mind Your Tone's own 250-prompt dataset** (arXiv 2510.04950) has **no
  discoverable public repository** -- searched arXiv, the paper text, and
  common secondary sources; no GitHub/anonymous.4open.science link exists in
  the published paper. Part A replication is blocked until this file is
  obtained directly from the authors (Om Dobariya, Akhil Kumar) or from ACL
  Anthology supplementary materials. `harness/study1/dataset.py:load_mind_your_tone()`
  takes a local file path for exactly this reason -- don't route around it
  with a guessed URL.

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

python -m harness.cli --live study2 validation-gate \
  --model gemini-flash --repo-dir data/spreadsheetbench \
  --expected-accuracy <current published figure>

python -m harness.cli --live study2 pilot \
  --models gemini-flash,deepseek-v3,qwen2.5-72b --n-tasks 30
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
   frontier: $15/$40/$150).
4. For Study 2 specifically: the sandbox (`harness/study2/sandbox.py`) that
   executes model-generated code is process-level isolation only. Put it in
   a real container (network disabled, throwaway filesystem) before a live
   run -- see that module's docstring.

## License note

If you extract data from `RUCKBReasoning/SpreadsheetBench` into this repo
(as opposed to keeping it in a git-ignored `data/` cache), it is CC BY-SA
4.0 -- keep attribution and the same license on any redistribution.
