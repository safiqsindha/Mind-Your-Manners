"""Model registry and run configuration for all studies.

ROSTER (replaces the earlier gemini-flash/deepseek-v3/qwen2.5-72b/llama-3.3-70b
set -- see git history for why): OpenAI and Gemini appear in every source
paper this project replicates or extends (Mind Your Tone, its AMCIS 2026
full-paper extension, SpreadsheetBench 2's own model baselines), so they are
the spine of the roster. DeepSeek and Qwen -- both already baselined in
SpreadsheetBench 2 -- are the cross-cultural extension. GLM and Kimi were
considered and are deliberately excluded on cost and recognition grounds.

  Slot                  Model                    Scope
  Western cheap tier    GPT-5.6 Luna             all studies
  Gemini Flash tier     Gemini 3.8 Flash         all studies
  Gemini Lite tier      Gemini 3.1 Flash-Lite    Study 1 only (the replicated
                                                  paper tested two Gemini tiers)
  Chinese open-weight   DeepSeek (current tier)  all studies
  Chinese open-weight   Qwen (current tier)      all studies

VERIFICATION (resolves the earlier inline VERIFY comments -- every model_id,
price, and provider below was checked against OpenRouter's own live catalog,
not carried over from memory or a training-data guess):

  model_id                          input $/1M   output $/1M   date checked
  openai/gpt-5.6-luna                  0.20          1.20      2026-09-10
  google/gemini-3.8-flash              0.75          3.75      2026-09-10
  google/gemini-3.1-flash-lite         0.125         0.75      2026-09-10
  deepseek/deepseek-v4-flash-0731      0.06          0.18      2026-09-10  (a)
  qwen/qwen3.8-flash                   0.15          0.47      2026-09-10  (b)

  (a) "DeepInfra" endpoint, fp8. RE-PINNED 2026-09-10: the previous pin
      (`provider_pin="DeepSeek"`, claimed as "the official DeepSeek
      endpoint") does not correspond to any real provider in OpenRouter's
      live endpoint list for this model_id -- there is no first-party
      "DeepSeek"-branded endpoint for deepseek-v4-flash-0731 on OpenRouter
      at all, only third-party re-hosts. This was caught while merging in
      the mandatory-quantization-pin enforcement (see git history) and
      should have been caught by the original verification pass; it was
      not. DeepInfra was picked from the real list for reporting a
      discrete quantization (fp8) and being a well-established, widely
      used inference provider -- see `GET
      /api/v1/models/deepseek/deepseek-v4-flash-0731/endpoints` for the
      full comparison (about two dozen re-hosts, prices from $0.05 to
      $0.44 per 1M input tokens).
  (b) Official "Alibaba" OpenRouter endpoint.

  Checked via `GET https://openrouter.ai/api/v1/models` (no auth required)
  and `GET https://openrouter.ai/api/v1/models/{id}/endpoints` for
  per-provider/quantization detail. Re-run this verification before a live
  run if it's been more than a few weeks -- OpenRouter's catalog, pricing,
  and endpoint availability all change frequently, and a provider that
  looked pinnable today can disappear.

QUANTIZATION PIN: checked live for all 5 models (2026-09-10). Only
DeepSeek's real endpoints report a usable, disambiguating quantization
value (`quantization_pin=["fp8"]`, matching the DeepInfra re-pin above).
GPT-5.6 Luna (OpenAI's own endpoint, plus every Azure/Bedrock re-host),
Gemini 3.8 Flash and Gemini 3.1 Flash-Lite (Google AI Studio, plus Google's
own Vertex hosting), and Qwen3.8 Flash's official Alibaba endpoint all
report quantization "unknown" on every listed pricing tier -- this looks
like a structural gap in how OpenRouter's catalog represents proprietary,
first-party APIs (as opposed to open-weight models on GPU-cloud re-hosts,
where advertising fp8/fp4/bf16 is closer to a selling point), not a
one-off data gap research can fill in. Qwen does have a third-party
alternative (Makora, fp4, identical price) that reports a real
quantization, but switching to it would mean giving up the official
Alibaba endpoint for the sake of satisfying a check -- exactly the
per-provider-savings-chasing this roster's design already rejects (see
below). These four are marked `quantization_not_exposed=True` instead:
provider.only already pins each to the single first-party endpoint that
serves it, so there is no other precision variant for `quantizations` to
rule out in the first place -- see harness/providers/openai_compatible.py.

Each of the 5 chosen models is pinned to ONE specific OpenRouter-listed
provider (`provider_pin`) chosen for vendor fidelity over marginal cost
savings -- e.g. several third-party fp8/fp4 re-hosts of Gemini/GPT-Luna's
same weights would be cheaper, and it's still the right choice, for the
same reason the harness routes everything through OpenRouter on one key
rather than chasing per-provider savings (see README "Single provider
path"). Full `provider.only`/`allow_fallbacks`/`quantizations` enforcement
and the served-provider assertion live in harness/providers/
openai_compatible.py, not here -- this file only records the *intended*
pin.

Every ModelConfig.key below is referenced by name from study run configs, so
keep keys stable once a run has started (results rows are keyed by
model.key, not model_id, precisely so a mid-run model_id fix doesn't
silently fragment the dataset).
"""
from __future__ import annotations

from .providers.base import ModelConfig

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# Target model set -- see module docstring for the verification table and
# roster rationale.
# ---------------------------------------------------------------------------
GPT_LUNA = ModelConfig(
    key="gpt-luna",
    provider="openai_compatible",
    model_id="openai/gpt-5.6-luna",
    display_name="GPT-5.6 Luna",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="OpenAI",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort="low",  # pinned explicitly -- default is "medium"; low keeps this the cheap/fast slot it's meant to be
    max_tokens=2048,
    input_price_per_1m=0.20,
    output_price_per_1m=1.20,
)

GEMINI_FLASH = ModelConfig(
    key="gemini-flash",
    provider="openai_compatible",
    model_id="google/gemini-3.8-flash",
    display_name="Gemini 3.8 Flash",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Google AI Studio",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort="low",  # reasoning is MANDATORY on this model (cannot disable) -- pinned to the cheapest allowed effort
    max_tokens=2048,
    input_price_per_1m=0.75,
    output_price_per_1m=3.75,
)

GEMINI_FLASH_LITE = ModelConfig(
    key="gemini-flash-lite",
    provider="openai_compatible",
    model_id="google/gemini-3.1-flash-lite",
    display_name="Gemini 3.1 Flash-Lite",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Google AI Studio",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort="minimal",  # this model's own default; pinned explicitly rather than left implicit
    max_tokens=2048,
    input_price_per_1m=0.125,
    output_price_per_1m=0.75,
)

DEEPSEEK_CURRENT = ModelConfig(
    key="deepseek-current",
    provider="openai_compatible",
    model_id="deepseek/deepseek-v4-flash-0731",
    display_name="DeepSeek V4 Flash (0731)",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="DeepInfra",  # re-pinned 2026-09-10 -- "DeepSeek" was never a real endpoint for this model_id, see module docstring
    quantization_pin=["fp8"],
    reasoning_effort="low",  # optional on this model; pinned for cost/latency consistency with the rest of the roster
    max_tokens=2048,
    input_price_per_1m=0.06,
    output_price_per_1m=0.18,
)

QWEN_CURRENT = ModelConfig(
    key="qwen-current",
    provider="openai_compatible",
    model_id="qwen/qwen3.8-flash",
    display_name="Qwen3.8 Flash",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Alibaba",
    quantization_not_exposed=True,  # checked 2026-09-10 -- see module docstring's QUANTIZATION PIN section
    reasoning_effort=None,  # OpenRouter does not expose discrete effort levels for this model (see verification table)
    max_tokens=2048,
    input_price_per_1m=0.15,
    output_price_per_1m=0.47,
)

# Models used in every study.
CORE_MODELS: list[ModelConfig] = [GPT_LUNA, GEMINI_FLASH, DEEPSEEK_CURRENT, QWEN_CURRENT]

# Study 1 additionally includes the Gemini Lite tier -- the paper it
# replicates/extends tested two Gemini tiers, this is the second one.
STUDY1_MODELS: list[ModelConfig] = CORE_MODELS + [GEMINI_FLASH_LITE]

# Optional frontier spot-check. NOT yet migrated to the OpenRouter-only path
# (item 3's "single provider path" applies to the 5-model roster above) --
# left on direct Anthropic access since it's an occasional spot-check, not
# a routine run; revisit if that becomes inconsistent in practice.
FRONTIER_SPOTCHECK = ModelConfig(
    key="frontier-spotcheck",
    provider="anthropic",
    model_id="claude-sonnet-5",  # VERIFY exact public API model string before use -- see README caveat
    display_name="Claude (frontier spot-check)",
    temperature=0.0,
    max_tokens=2048,
    input_price_per_1m=3.00,
    output_price_per_1m=15.00,
)

# NOT a target model -- see harness/providers/claude_cli_provider.py
# docstring. Exists only so the harness can be smoke-tested with genuine
# (non-mocked) inference from a Claude Code session that has no raw
# ANTHROPIC_API_KEY. Cost is read from the CLI's own reported
# total_cost_usd (see spend_tracker.compute_cost_usd), not the price
# fields below, hence they're 0.
CLAUDE_CLI_SMOKETEST = ModelConfig(
    key="claude-cli-smoketest",
    provider="claude_cli",
    model_id="haiku",  # CLI model alias; cheapest available for repeated smoke-test calls
    display_name="Claude (local CLI smoke test only)",
    temperature=0.0,
    max_tokens=1024,
    input_price_per_1m=0.0,
    output_price_per_1m=0.0,
)

# NOT a target model -- for validating a real, live OpenRouter call (the
# actual triple-pin/cache-assertion/instrumentation code path in
# harness/providers/openai_compatible.py) once an OPENROUTER_API_KEY exists,
# before spending on the real roster. README's "Single provider path"
# already flags free-tier OpenRouter endpoints as "for debugging/pilots
# only" -- this is that.
#
# An OpenAI-branded free option was checked first (per request) and isn't
# currently usable: `openai/gpt-oss-20b:free` and `openai/gpt-oss-120b:free`
# both exist as catalog IDs but currently resolve to zero active endpoints
# (checked live, 2026-09-10) -- i.e. the slug exists but nothing actually
# serves it right now. `google/gemma-4-26b-a4b-it:free` does have a real,
# live, $0/$0 endpoint (served directly by Google AI Studio, not a
# third-party re-host), so it's substituted here instead. Re-check both
# before relying on this if it's been a while -- free-tier availability on
# OpenRouter changes without notice.
OPENROUTER_FREE_SMOKETEST = ModelConfig(
    key="openrouter-free-smoketest",
    provider="openai_compatible",
    model_id="google/gemma-4-26b-a4b-it:free",
    display_name="Gemma 4 26B (OpenRouter free tier, smoke test only)",
    temperature=0.0,
    api_base=OPENROUTER_BASE_URL,
    provider_pin="Google AI Studio",
    quantization_not_exposed=True,  # checked 2026-09-10, same "unknown" pattern as the roster's Google-pinned models
    max_tokens=1024,
    input_price_per_1m=0.0,
    output_price_per_1m=0.0,
)

ALL_MODELS: list[ModelConfig] = STUDY1_MODELS + [FRONTIER_SPOTCHECK, CLAUDE_CLI_SMOKETEST, OPENROUTER_FREE_SMOKETEST]

MODELS_BY_KEY: dict[str, ModelConfig] = {m.key: m for m in ALL_MODELS}


def with_temperature(model: ModelConfig, temperature: float, seed: int | None = None) -> ModelConfig:
    """Return a copy of `model` at a different temperature/seed.

    Used to build the temperature-1.0, 3-trials-per-item variance-estimate
    run from the same base model configs used for the temperature-0 primary
    run, without duplicating the model registry.
    """
    from dataclasses import replace

    return replace(model, temperature=temperature, seed=seed)


# ---------------------------------------------------------------------------
# Budget caps -- enforced by harness/spend_tracker.py. Study 1 has a
# two-tier cap (a soft warning threshold and a hard stop) per the current
# projection across the five-model roster; Studies 2 and 3 keep a single
# hard cap each.
# ---------------------------------------------------------------------------
STUDY1_SOFT_BUDGET_CAP_USD = 50.0
STUDY1_HARD_BUDGET_CAP_USD = 75.0

# Retained for any caller still importing the old single-cap name.
STUDY1_BUDGET_CAP_USD = STUDY1_HARD_BUDGET_CAP_USD

# Study 2 keeps its pilot -> core staging; pilot + core together should land
# around $90 across CORE_MODELS' four models (Study 2 does not use the
# Gemini Lite tier). The frontier spot-check is a separate, optional tier
# with its own independent cap.
STUDY2_PILOT_BUDGET_CAP_USD = 20.0
STUDY2_CORE_BUDGET_CAP_USD = 70.0
STUDY2_FRONTIER_BUDGET_CAP_USD = 150.0

STUDY3_BUDGET_CAP_USD = 100.0  # at 100 negotiations per cell, bilateral subset (harness/study3/)
