"""OpenAI-Chat-Completions-compatible provider.

Single provider path (task spec item 3): every target model in this harness
now routes through OpenRouter on one API key -- no direct-provider
integrations. `API_KEY_ENV_BY_BASE`'s DeepSeek/DashScope entries are kept
only so a locally-configured direct API still works if someone points
`api_base` at them explicitly; nothing in `harness/config.py`'s roster does
that anymore.

Pinning an OpenRouter call requires ALL THREE of the following together --
this is deliberately not configurable as a subset, because `order` alone is
a priority hint (OpenRouter can still fall back elsewhere), not a pin:

  - `provider.only`            hard allow-list: exactly the pinned provider
  - `provider.allow_fallbacks: false`   forbids falling back off that list
  - `provider.quantizations`   locks precision, so a provider can't quietly
                                serve a lower-precision variant of the model

See `ModelConfig.provider_pin` / `ModelConfig.quantization_pin`. The one
exception: `quantization_pin` is not required for a provider that
genuinely doesn't expose a discrete quantization at all (checked live
against `GET /api/v1/models/{id}/endpoints` -- true for every first-party
API provider checked so far: OpenAI, Google AI Studio, Alibaba's own
endpoint). There, `provider.only` is already maximally specific -- one
provider, one variant, nothing for `quantizations` to disambiguate -- so
`ModelConfig.quantization_not_exposed=True` is an explicit, audited
opt-out rather than a silently-missing field. When `provider_pin` is set,
`complete()` also asserts -- rather than assumes -- that the provider
OpenRouter actually used matches the pin, via the
`X-OpenRouter-Metadata: enabled` request header and the resulting
`openrouter_metadata.endpoints.endpoints[].selected` response field (there
is no such field in the plain chat-completion response body; verified
against OpenRouter's API reference before writing this). A mismatch raises
`ProviderPinViolation`, which -- like `BudgetExceeded` -- must propagate
uncaught and halt the run rather than being logged as a per-row error.

OpenRouter's response cache (a distinct mechanism from provider-side prompt
caching -- see `prompt_tokens_details.cached_tokens` below) defaults to off,
but is asserted off here rather than trusted: every OpenRouter call sends
`X-OpenRouter-Cache: false`, and a response carrying
`X-OpenRouter-Cache-Status: HIT` raises `ResponseCacheViolation`. Left
unnoticed, a cached response would silently zero out that call's token
counts and destroy trial-level variance estimates -- the exact thing this
harness's repeated-trials design depends on.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import requests

from .base import (
    ModelConfig,
    Provider,
    ProviderError,
    ProviderPinViolation,
    ProviderResponse,
    ResponseCacheViolation,
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# key -> env var holding the API key for that backend.
API_KEY_ENV_BY_BASE = {
    OPENROUTER_BASE_URL: "OPENROUTER_API_KEY",
    "https://api.deepseek.com": "DEEPSEEK_API_KEY",
    "https://dashscope.aliyuncs.com/compatible-mode/v1": "DASHSCOPE_API_KEY",
}


class OpenAICompatibleProvider(Provider):
    name = "openai_compatible"

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

    def _resolve_key(self, model: ModelConfig) -> Optional[str]:
        if self._explicit_key:
            return self._explicit_key
        env_var = API_KEY_ENV_BY_BASE.get(model.api_base or "", "OPENROUTER_API_KEY")
        return os.environ.get(env_var)

    def available(self, model: ModelConfig) -> bool:
        return bool(self._resolve_key(model))

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        api_key = self._resolve_key(model)
        if not api_key:
            raise ProviderError(f"No API key found for base_url={model.api_base!r}")

        base_url = (model.api_base or OPENROUTER_BASE_URL).rstrip("/")
        is_openrouter = base_url == OPENROUTER_BASE_URL
        full_messages = [{"role": "system", "content": system}] + messages

        body: dict[str, Any] = {
            "model": model.model_id,
            "messages": full_messages,
            "temperature": model.temperature,
            "max_tokens": model.max_tokens,
        }
        if model.seed is not None:
            body["seed"] = model.seed
        if tools:
            body["tools"] = tools
        if model.reasoning_effort:
            body["reasoning"] = {"effort": model.reasoning_effort}

        headers = {"Authorization": f"Bearer {api_key}", "content-type": "application/json"}

        if is_openrouter:
            # Disable response caching on every OpenRouter call -- see module
            # docstring. Applies regardless of whether a provider is pinned.
            headers["X-OpenRouter-Cache"] = "false"
            if model.provider_pin:
                if not model.quantization_pin and not model.quantization_not_exposed:
                    raise ProviderError(
                        f"{model.key}: provider_pin={model.provider_pin!r} is set but "
                        "quantization_pin is not, and quantization_not_exposed is not True. "
                        "OpenRouter pinning requires provider.only, allow_fallbacks:false, AND "
                        "provider.quantizations together UNLESS the pinned provider genuinely "
                        "doesn't expose a discrete quantization (checked live, then "
                        "quantization_not_exposed=True) -- see this module's docstring and "
                        "README 'Single provider path'."
                    )
                body["provider"] = {"only": [model.provider_pin], "allow_fallbacks": False}
                if model.quantization_pin:
                    body["provider"]["quantizations"] = model.quantization_pin
                # Needed to get openrouter_metadata.endpoints back in the
                # response body so the served-provider assertion below has
                # something to check against.
                headers["X-OpenRouter-Metadata"] = "enabled"

        resp = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=180,
        )
        if resp.status_code >= 400:
            raise ProviderError(f"{base_url} API error {resp.status_code}: {resp.text[:2000]}")

        if is_openrouter and resp.headers.get("X-OpenRouter-Cache-Status", "").upper() == "HIT":
            raise ResponseCacheViolation(
                f"{model.key}: OpenRouter served this response from its response cache "
                "(X-OpenRouter-Cache-Status: HIT) despite X-OpenRouter-Cache: false -- "
                "halting rather than silently zeroing this call's token counts."
            )

        data = resp.json()

        choice = data["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""
        finish_reason = choice.get("finish_reason", "")
        refused = finish_reason in ("content_filter", "refusal")

        tool_calls = []
        for tc in message.get("tool_calls") or []:
            fn = tc.get("function", {})
            tool_calls.append({"id": tc.get("id"), "name": fn.get("name"), "arguments": fn.get("arguments")})

        usage = data.get("usage", {})
        completion_details = usage.get("completion_tokens_details") or {}
        reasoning_tokens_reported = isinstance(completion_details, dict) and "reasoning_tokens" in completion_details
        reasoning_tokens = 0
        if isinstance(completion_details, dict):
            reasoning_tokens = completion_details.get("reasoning_tokens", 0) or 0

        cached_tokens = 0
        prompt_details = usage.get("prompt_tokens_details") or {}
        if isinstance(prompt_details, dict):
            cached_tokens = prompt_details.get("cached_tokens", 0) or 0

        served_provider = None
        if is_openrouter:
            metadata = data.get("openrouter_metadata") or {}
            endpoints = ((metadata.get("endpoints") or {}).get("endpoints")) or []
            selected = next((e for e in endpoints if e.get("selected")), None)
            served_provider = (selected or {}).get("provider")

            if model.provider_pin:
                if not served_provider:
                    raise ProviderPinViolation(
                        f"{model.key}: could not determine the served provider from the "
                        "response (openrouter_metadata missing/empty) -- can't verify the "
                        f"provider.only pin ({model.provider_pin!r}) was honored; failing "
                        "closed rather than assuming it was."
                    )
                if served_provider != model.provider_pin:
                    raise ProviderPinViolation(
                        f"{model.key}: pinned provider {model.provider_pin!r} via "
                        "provider.only/allow_fallbacks, but OpenRouter served this call "
                        f"via {served_provider!r} instead -- halting rather than silently "
                        "mixing backends mid-run."
                    )

        return ProviderResponse(
            text=text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            reasoning_tokens=reasoning_tokens,
            reasoning_tokens_reported=reasoning_tokens_reported,
            cached_tokens=cached_tokens,
            served_provider=served_provider,
            refused=refused,
            raw=data,
            tool_calls=tool_calls,
        )
