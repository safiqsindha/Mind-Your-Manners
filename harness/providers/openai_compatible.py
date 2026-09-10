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
`openrouter_metadata.endpoints.available[].selected` response field (there
is no such field in the plain chat-completion response body). A mismatch
raises `ProviderPinViolation`, which -- like `BudgetExceeded` -- must
propagate uncaught and halt the run rather than being logged as a
per-row error.

CORRECTED 2026-09-10 against a real live call, not docs: this was
originally written as `openrouter_metadata.endpoints.endpoints[]` --
plausible-looking, "verified against OpenRouter's API reference" per the
comment that used to be here, but wrong. A live call (first one made
against a real OpenRouter endpoint since this code was written) came back
with the served provider under `openrouter_metadata.endpoints.available[]`
instead, which meant the old code always read an empty list and the pin
assertion above would raise ProviderPinViolation ("could not determine
the served provider") on every single live call with a provider_pin set,
regardless of whether the pin actually held -- a false-negative that
would have blocked every live run of the real roster the first time
anyone tried one. Caught by running `study2 pilot` against a real free
OpenRouter model (`nex-agi/nex-n2.5-pro:free`) and reading the actual
response body directly with curl, not by re-reading documentation.

OpenRouter's response cache (a distinct mechanism from provider-side prompt
caching -- see `prompt_tokens_details.cached_tokens` below) defaults to off,
but is asserted off here rather than trusted: every OpenRouter call sends
`X-OpenRouter-Cache: false`, and a response carrying
`X-OpenRouter-Cache-Status: HIT` raises `ResponseCacheViolation`. Left
unnoticed, a cached response would silently zero out that call's token
counts and destroy trial-level variance estimates -- the exact thing this
harness's repeated-trials design depends on.

RETRY ON TRANSIENT FAILURE (`_post_with_retry`, added 2026-09-10): also
found live, the same day as the pin-key bug above -- DeepSeek and Qwen
(both routed through third-party/shared-pool-style OpenRouter endpoints)
returned HTTP 429 "temporarily rate-limited upstream... shared pool" on
essentially the first call of a small smoke test, with no retry logic at
all, crashing the run immediately. `_post_with_retry` retries
RETRYABLE_STATUS_CODES (408/429/502/503/504) and network-level exceptions
(connection error/timeout below the HTTP layer -- an Opus review of this
fix flagged that gap before it shipped) up to MAX_RETRIES times, honoring
a `Retry-After` response header when present (clamped against a negative
or non-finite value, which would otherwise crash `time.sleep()`) and
falling back to exponential backoff (2s/4s/8s/16s, capped) otherwise.
Every other status (400/401/403/404/422/500/etc.) still fails immediately,
unretried -- see RETRYABLE_STATUS_CODES's comment for why 500 specifically
is excluded despite being a 5xx. See that same comment for a known,
accepted limitation: retrying a 502/504 can duplicate upstream generation
cost that never reaches SpendTracker.
"""
from __future__ import annotations

import math
import os
import time
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

# Statuses worth retrying: 408/429 (request timeout / rate limited) and
# 502/503/504 (upstream/gateway trouble) are transient infrastructure
# conditions, not something a retry of the identical request can't fix.
# Everything else (400 bad request, 401/403 auth, 404 unknown model, 422
# unprocessable, etc.) is a config problem retrying won't solve -- fail
# immediately on those, same as before. 500 is deliberately NOT included:
# unlike 502/503/504 (which are OpenRouter's own gateway/pool reporting
# trouble reaching a backend), a 500 can just as easily be a deterministic
# model-side error that a retry would only reproduce -- the status code
# alone doesn't distinguish the two, so it's left to fail immediately
# rather than assumed transient. Confirmed live 2026-09-10: DeepSeek and
# Qwen (both third-party/shared-pool-style endpoints) hit 429 "temporarily
# rate-limited upstream... shared pool" on essentially the first call of a
# smoke test -- with no retry, that crashed the whole run instantly and
# would recur at any real pilot/main-run scale.
#
# KNOWN LIMITATION, not fixed here: a 502/504 specifically can mean
# OpenRouter's gateway lost the response AFTER the upstream provider
# already generated (and billed) a completion -- retrying in that case
# sends a second request whose upstream cost never reaches
# compute_cost_usd/SpendTracker (only the response actually returned to
# us gets logged), a small, real undercount against the $150 cap.
# OpenRouter's API doesn't expose an idempotency key to prevent this;
# 429 has no such risk (rejected before any generation happens).
RETRYABLE_STATUS_CODES = {408, 429, 502, 503, 504}
# Raised 4 -> 6 on evidence, not preference: Qwen's validation gate died twice
# in a row on HTTP 429 from Alibaba's shared pool, having spent its whole
# backoff budget (2+4+8+16 = 30s). OpenRouter's own remedy text for that error
# is "retry shortly", and Qwen is pinned to a single available endpoint, so
# there is nothing to fail over to -- 30s was simply mis-sized for the
# condition. Six retries give 2+4+8+16+30+30 = 90s. Deliberately not larger:
# past roughly a minute and a half a saturated pool is not going to clear
# within one call, and the run should surface that rather than hide it in
# latency.
MAX_RETRIES = 6  # up to 6 retries (7 attempts total) per call
RETRY_BACKOFF_BASE_S = 2.0  # exponential: 2s, 4s, 8s, 16s, then capped at 30s
RETRY_BACKOFF_CAP_S = 30.0


def _clamp_delay(delay: float) -> float:
    """A Retry-After header is untrusted input -- a negative value would
    make time.sleep() raise, and so would NaN (parses fine as a float but
    fails the sleep call). Clamp both to the cap rather than let either
    crash a live run."""
    if not math.isfinite(delay) or delay < 0:
        return RETRY_BACKOFF_CAP_S
    return min(delay, RETRY_BACKOFF_CAP_S)


def _post_with_retry(url: str, headers: dict, json_body: dict, timeout: int) -> requests.Response:
    """POST with retry-on-transient-failure. Honors a Retry-After header
    (seconds) when the server sends one; falls back to exponential backoff
    otherwise. Also retries on a network-level exception (connection
    error/timeout below the HTTP layer) -- these are at least as likely
    against a flaky shared inference pool as a 502/503 response, and were
    otherwise the biggest gap in this retry logic. Raises ProviderError
    directly if a network exception exhausts all retries (there is no
    response object to return in that case); for an HTTP-level failure it
    raises nothing itself on a persistent failure -- returns the last
    response so the caller's existing status-code check produces the same
    ProviderError it always has."""
    attempt = 0
    while True:
        try:
            resp = requests.post(url, headers=headers, json=json_body, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as exc:
            if attempt >= MAX_RETRIES:
                raise ProviderError(
                    f"{url}: network error after {attempt + 1} attempts, giving up: {exc}"
                ) from exc
            delay = _clamp_delay(RETRY_BACKOFF_BASE_S * (2**attempt))
            print(
                f"WARNING: {url} network error (attempt {attempt + 1}/{MAX_RETRIES + 1}) "
                f"-- retrying in {delay:.1f}s: {exc}"
            )
            time.sleep(delay)
            attempt += 1
            continue

        if resp.status_code not in RETRYABLE_STATUS_CODES or attempt >= MAX_RETRIES:
            return resp

        retry_after = resp.headers.get("Retry-After")
        if retry_after is not None:
            try:
                delay = _clamp_delay(float(retry_after))
            except ValueError:
                delay = _clamp_delay(RETRY_BACKOFF_BASE_S * (2**attempt))
        else:
            delay = _clamp_delay(RETRY_BACKOFF_BASE_S * (2**attempt))

        print(
            f"WARNING: {url} returned {resp.status_code} (attempt {attempt + 1}/{MAX_RETRIES + 1}) "
            f"-- retrying in {delay:.1f}s: {resp.text[:300]}"
        )
        time.sleep(delay)
        attempt += 1


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

        resp = _post_with_retry(f"{base_url}/chat/completions", headers, body, timeout=180)
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
            # Real key is "available", not "endpoints" -- see this module's
            # docstring for how that was found (a live call returned an
            # empty served-provider on every real request until this was
            # fixed, which would have made the pin assertion below fail
            # closed on every live call, always, regardless of whether the
            # pin actually held).
            endpoints = ((metadata.get("endpoints") or {}).get("available")) or []
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
