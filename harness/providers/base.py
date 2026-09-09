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

    key: str  # short internal name, e.g. "gemini-flash"
    provider: str  # "anthropic" | "openai_compatible" | "google" | "mock"
    model_id: str  # exact pinned model ID string sent to the API
    display_name: str
    temperature: float
    seed: Optional[int] = None
    reasoning_effort: Optional[str] = None  # e.g. "low"/"medium"/"high", None if N/A
    thinking_budget_tokens: Optional[int] = None  # for models with an explicit thinking budget
    api_base: Optional[str] = None  # override base URL (e.g. OpenRouter with pinned provider)
    provider_pin: Optional[str] = None  # e.g. OpenRouter "provider" routing field
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
