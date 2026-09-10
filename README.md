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
  **Gating check (see RESULTS.md for the full write-up):** ran
  `compare_workbooks(answer, answer)` -- gold vs. itself -- across all 200
  tasks in the sample set. 199/200 passed outright; the one failure is a bug
  in the *authors'* own `evaluation.py` (their `answer_position.split(',')`
  doesn't strip whitespace, so a multi-range position like
  `"B12:B110, C12:C23, ..."` -- space after the comma -- resolves to a
  malformed cell reference), not something to patch in their code, and this
  harness's grader wrapper already fails that one test case gracefully
  rather than crashing the batch.
  LibreOffice's headless formula recalculation (required before grading any
  formula-bearing task, same as their own `open_spreadsheet.py`) was
  **broken and is now fixed**: `libreoffice-calc`/`libreoffice-writer` were
  never actually installed in this build's container (only
  `libreoffice-core` was -- confirmed via `strace`, a document-loader
  shared library was missing) -- installing them fixed it. A second, real
  bug in this repo's own `recalculate_with_libreoffice()` was found and
  fixed at the same time: converting a file to itself (same source and
  output directory) makes LibreOffice silently fail the write to stderr
  with exit code 0, which the old success check missed entirely; fixed by
  converting into a temp directory and moving the result back, matching
  their own `open_spreadsheet.py:just_open_libreoffice()`. A third bug
  found via the same check: the grader only recalculated the *model's*
  output, never the ground-truth answer file, and SpreadsheetBench's own
  answer files can themselves contain uncached formulas -- confirmed on a
  real task (99-24), where a correct answer's own cell read `None` unless
  recalculated. Fixed by recalculating answer files too (memoized once per
  file, not per grading call). **SpreadsheetBench 2** (end-to-end business
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

# Study 3: clones AgenticPay automatically, runs the full 5x5 buyer-tone x
# seller-tone matrix for one buyer/seller model pair (restricted to the
# bilateral env -- see "Dataset availability" above)
python -m harness.cli --live study3 bilateral-matrix \
  --buyer-model gemini-flash --seller-model gemini-flash --n-trials-per-cell 4
```

Run `pytest` for the test suite (all pass against the mock provider, no
network/keys required beyond `datasets`' HF pull in a couple of dataset
tests being skippable offline).

## Single provider path: OpenRouter, and how pinning is enforced

Every target model routes through OpenRouter on one API key -- no
direct-provider integrations (`harness/providers/openai_compatible.py`'s
`API_KEY_ENV_BY_BASE` still lists DeepSeek/DashScope's direct endpoints, but
nothing in the roster points `api_base` at them anymore). Free-tier
OpenRouter endpoints (`:free` model slugs) are for debugging/pilots only --
never route a real study rollout through one, and never route rollouts
through a flat-rate coding-agent subscription (a fixed monthly plan has no
meaningful per-call cost to log against the budget caps below).

Pinning a model to a specific backend requires all three of the following
together, sent as one `provider` object -- `order` alone is a priority
hint, not a pin, since OpenRouter can still fall back elsewhere:

- `provider.only` -- hard allow-list, exactly the pinned provider
- `provider.allow_fallbacks: false` -- forbids falling back off that list
- `provider.quantizations` -- locks precision, so the pinned provider can't
  quietly serve a lower-precision variant of the model

Set both `ModelConfig.provider_pin` and `ModelConfig.quantization_pin` for
any OpenRouter-routed model -- the provider layer raises `ProviderError`
before making a call if only one is set. **This roster does not satisfy
that yet** (see RESULTS.md item 5): none of the 5 current models have
`quantization_pin` set, and checking live endpoint data while merging the
enforcement code in found that several of their pinned providers
(OpenAI's own endpoint, Google AI Studio, Alibaba) report an "unknown"
quantization rather than a discrete one -- meaning `quantizations` may not
be meaningful to set for a first-party/proprietary endpoint at all, since
`provider.only` already pins to the one and only variant that provider
serves. `DEEPSEEK_CURRENT`'s pin (`provider_pin="DeepSeek"`) is a separate,
more basic problem: no provider by that name appears in OpenRouter's live
endpoint list for `deepseek/deepseek-v4-flash-0731` at all. Fixing both is
a follow-up before any live run -- see RESULTS.md.

**The pin is asserted, not assumed.** Every OpenRouter call requests
`X-OpenRouter-Metadata: enabled` and reads the actual serving provider back
from `openrouter_metadata.endpoints.endpoints[].selected` (there is no
provider field on the plain chat-completion response) -- a mismatch, or a
response with no metadata to check, raises `ProviderPinViolation` and halts
the run rather than silently mixing backends. The served provider is
recorded on every result row (`ResultRow.served_provider`).

**OpenRouter's response cache is disabled and asserted off, not just left
at its default.** This is a separate mechanism from provider-side prompt
caching (`usage.prompt_tokens_details.cached_tokens`, see below) -- it can
return a complete previously-computed response for an identical request,
zeroing out that call's token counts. Every OpenRouter call sends
`X-OpenRouter-Cache: false`; a response carrying
`X-OpenRouter-Cache-Status: HIT` raises `ResponseCacheViolation` and halts
the run, since a cached hit would silently destroy the trial-level variance
estimates this harness's repeated-trials design depends on.

**Caching and cost instrumentation is recorded on every result row**
(`harness/spend_tracker.py:ResultRow`): `prompt_tokens`, `completion_tokens`,
`reasoning_tokens`, `cached_tokens` (provider-side prompt-cache hits --
measured, not designed around; Study 1's prompts are short enough that this
is expected to read zero throughout, but it's reported either way rather
than assumed), wall-clock `latency_s`, and `cost_usd` (prefers OpenRouter's
own billed `usage.cost` when present, since it reflects what was actually
charged rather than this file's static price table). See
`tests/test_openrouter_pinning.py` for the enforcement behavior above,
verified against mocked HTTP responses shaped like OpenRouter's own
documented request/response schema (checked directly against
`openrouter.ai/docs`, not guessed, before writing the code).

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
   the optional frontier spot-check; Study 3 is a hard $100 for ~100
   negotiations/cell. `--live` prints a rough projection and asks for
   confirmation before the first paid call in every run (pass `--yes` to
   skip the prompt for scripted/CI use).
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
5. Verify `libreoffice-calc` and `libreoffice-writer` (not just
   `libreoffice-core`) are actually installed wherever a live batch runs --
   see "Dataset availability" above for how this build's container had
   `soffice` on PATH but was still missing them, and confirm
   `recalculate_with_libreoffice()` against a real formula before trusting
   any formula-based Study 2 grade.
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
