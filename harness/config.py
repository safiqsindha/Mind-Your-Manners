"""Model registry and run configuration for both studies.

IMPORTANT -- read before a live run: the exact model ID strings, their
availability, and their prices below are a best-effort snapshot and are NOT
guaranteed current. Model catalogs and pricing change frequently and this
harness has never made a live call (see README.md "Execution status").
Before spending any money, run `harness/cli.py --check-catalog` (calls each
provider's model-list endpoint, where one exists, and fails loudly on any
model_id that isn't currently servable) and cross-check prices against the
providers' current pricing pages. Update this file, don't route around it.

Every ModelConfig.key below is referenced by name from study1/study2 run
configs, so keep keys stable once a run has started (results rows are keyed
by model.key, not by model_id, precisely so a mid-run model_id fix doesn't
silently fragment the dataset).
"""
from __future__ import annotations

from .providers.base import ModelConfig

# ---------------------------------------------------------------------------
# Target model set (task spec: "adjust to what is available").
# ---------------------------------------------------------------------------
# One Gemini Flash-tier model, direct API.
GEMINI_FLASH = ModelConfig(
    key="gemini-flash",
    provider="google",
    model_id="gemini-2.5-flash",  # VERIFY against https://ai.google.dev/gemini-api/docs/models before a live run
    display_name="Gemini 2.5 Flash",
    temperature=0.0,
    max_tokens=2048,
    input_price_per_1m=0.30,
    output_price_per_1m=2.50,
)

# Two Chinese open-weight models: DeepSeek and Qwen tiers, direct APIs
# (both are OpenAI-Chat-Completions-compatible).
DEEPSEEK_CHAT = ModelConfig(
    key="deepseek-v3",
    provider="openai_compatible",
    model_id="deepseek-chat",  # DeepSeek-V3 family; VERIFY at https://api-docs.deepseek.com/quick_start/pricing
    display_name="DeepSeek-V3 (deepseek-chat)",
    temperature=0.0,
    api_base="https://api.deepseek.com",
    max_tokens=2048,
    input_price_per_1m=0.27,
    output_price_per_1m=1.10,
)

QWEN_72B = ModelConfig(
    key="qwen2.5-72b",
    provider="openai_compatible",
    model_id="qwen2.5-72b-instruct",  # VERIFY at https://help.aliyun.com/zh/model-studio/ (DashScope pricing)
    display_name="Qwen2.5-72B-Instruct",
    temperature=0.0,
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    max_tokens=2048,
    input_price_per_1m=0.56,
    output_price_per_1m=1.68,
)

# One Western open-weight model (Llama/Gemma tier), routed through
# OpenRouter with the backend provider pinned explicitly so it cannot
# silently swap mid-run (task spec requirement).
LLAMA_70B = ModelConfig(
    key="llama-3.3-70b",
    provider="openai_compatible",
    model_id="meta-llama/llama-3.3-70b-instruct",  # VERIFY current OpenRouter slug + pin before a live run
    display_name="Llama 3.3 70B Instruct",
    temperature=0.0,
    api_base="https://openrouter.ai/api/v1",
    provider_pin="Together",  # pin explicitly; do not leave OpenRouter free to route
    max_tokens=2048,
    input_price_per_1m=0.60,
    output_price_per_1m=0.60,
)

# Optional frontier spot-check.
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

CORE_MODELS: list[ModelConfig] = [GEMINI_FLASH, DEEPSEEK_CHAT, QWEN_72B, LLAMA_70B]
ALL_MODELS: list[ModelConfig] = CORE_MODELS + [FRONTIER_SPOTCHECK]

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
# Budget caps (task spec, hard stops -- enforced by harness/spend_tracker.py)
# ---------------------------------------------------------------------------
STUDY1_BUDGET_CAP_USD = 50.0

STUDY2_PILOT_BUDGET_CAP_USD = 15.0
STUDY2_CORE_BUDGET_CAP_USD = 40.0
STUDY2_FRONTIER_BUDGET_CAP_USD = 150.0
