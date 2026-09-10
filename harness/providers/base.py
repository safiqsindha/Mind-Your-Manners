"""Provider-agnostic interfaces used by both studies.

Every model call in this harness -- single-turn QA (Study 1) or a step in an
agentic trajectory (Study 2) -- goes through a `Provider.complete()` call and
produces one `ProviderResponse`. That response is what gets written, one row
per call, to results/raw/ (see harness/spend_tracker.py and study*/runner.py).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ModelConfig:
    """Pinned identity of a model + the sampling settings used for a run.

    Every field here is logged in every result row (per the task spec's
    "Record model ID, provider, temperature, and any reasoning/thinking
    settings in every result row" requirement) -- see
    harness/spend_tracker.py:ResultRow.
    """

    key: str  # short internal name, e.g. "gpt-luna"
    provider: str  # "anthropic" | "openai_compatible" | "google" | "mock"
    model_id: str  # exact pinned model ID string sent to the API
    display_name: str
    temperature: float
    seed: Optional[int] = None
    reasoning_effort: Optional[str] = None  # e.g. "low"/"medium"/"high", None if N/A
    thinking_budget_tokens: Optional[int] = None  # for models with an explicit thinking budget
    # Explicit on/off summary of whether this condition intends reasoning to
    # run at all -- distinct from reasoning_effort's granular string, since
    # e.g. reasoning_effort="low" still means thinking_enabled=True (reasoning
    # is happening, just at low effort). None where the model's reasoning
    # behavior isn't under this harness's control at all (no reasoning
    # parameter sent, provider default applies -- see config.py roster
    # docstring's per-model reasoning-control table).
    thinking_enabled: Optional[bool] = None
    canonical_slug: Optional[str] = None  # OpenRouter's dated, non-moving snapshot id for model_id, checked live at config time -- see config.py roster docstring
    api_base: Optional[str] = None  # override base URL (e.g. OpenRouter with pinned provider)
    provider_pin: Optional[str] = None  # OpenRouter provider slug for "provider.only", e.g. "Together"
    quantization_pin: Optional[list[str]] = None  # OpenRouter "provider.quantizations" lock, e.g. ["fp8"]
    # Explicit, auditable escape hatch from the "quantization_pin is
    # mandatory whenever provider_pin is set" rule -- set True ONLY after
    # checking the pinned provider's real endpoint entry (GET
    # /api/v1/models/{id}/endpoints) and confirming it reports no discrete
    # "quantization" value. Verified true for every first-party/proprietary
    # API provider checked so far (OpenAI, Google AI Studio, Alibaba) --
    # they simply don't expose this field, on any of their listed pricing
    # tiers, so there is no ambiguity for provider.only to leave unresolved
    # in the first place. Never set this to unblock a model you haven't
    # actually checked.
    quantization_not_exposed: bool = False
    input_price_per_1m: float = 0.0  # USD, for spend tracking
    output_price_per_1m: float = 0.0  # USD, for spend tracking
    max_tokens: int = 1024
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int = 0
    cached_tokens: int = 0  # provider-side prompt-cache hits (usage.prompt_tokens_details.cached_tokens);
    # measure only -- see harness/config.py module docstring on caching instrumentation.
    served_provider: Optional[str] = None  # actual backend that served this call, when reported
    latency_s: float = 0.0
    refused: bool = False
    error: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens + self.reasoning_tokens


class ProviderError(RuntimeError):
    pass


class ProviderPinViolation(ProviderError):
    """The provider that actually served a call didn't match the configured
    pin (or couldn't be determined). Must propagate uncaught and halt the
    run -- callers must not catch-and-continue on this, same convention as
    spend_tracker.BudgetExceeded."""


class ResponseCacheViolation(ProviderError):
    """OpenRouter's response cache served a cached response despite being
    asserted off. Left unswallowed, this would silently destroy
    trial-level variance estimates -- must propagate and halt the run."""


class Provider:
    """Base class for a model provider backend."""

    name = "base"

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        raise NotImplementedError

    def _timed(self, fn, *a, **kw):
        start = time.monotonic()
        result = fn(*a, **kw)
        elapsed = time.monotonic() - start
        result.latency_s = elapsed
        return result
