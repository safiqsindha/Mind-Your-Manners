"""Tests for the OpenRouter enforcement layer (task spec item 3: mandatory
provider.only + allow_fallbacks:false + provider.quantizations triple-pin,
with a served-provider assertion; item 4: response-cache disabled and
asserted off; item 5: caching/latency instrumentation on every call).

All HTTP is mocked -- no network, no API key needed. Verified request/response
field names (provider.only/quantizations, X-OpenRouter-Cache*,
usage.prompt_tokens_details.cached_tokens, usage.cost) came from
OpenRouter's own docs. `openrouter_metadata.endpoints.available` (NOT
`.endpoints`, despite what an earlier version of this file and of
openai_compatible.py assumed from docs) was corrected against a real
live response instead -- see openai_compatible.py's module docstring
"CORRECTED 2026-09-10" note and test_matches_real_live_response_shape
below, which pins the actual captured JSON so this can't silently regress.
"""
from __future__ import annotations

from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest

from harness.providers.base import ModelConfig, ProviderError, ProviderPinViolation, ResponseCacheViolation
from harness.providers.openai_compatible import OpenAICompatibleProvider

PINNED_MODEL = ModelConfig(
    key="test-model",
    provider="openai_compatible",
    model_id="meta-llama/llama-3.3-70b-instruct",
    display_name="Test Model",
    temperature=0.0,
    api_base="https://openrouter.ai/api/v1",
    provider_pin="Nebius",
    quantization_pin=["fp8"],
    input_price_per_1m=0.13,
    output_price_per_1m=0.40,
)


def _fake_response(status_code=200, headers=None, json_body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = "error text"
    resp.json.return_value = json_body or {}
    return resp


def _ok_body(served_provider="Nebius", cached_tokens=0, reasoning_tokens=0, cost=None):
    usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "prompt_tokens_details": {"cached_tokens": cached_tokens},
        "completion_tokens_details": {"reasoning_tokens": reasoning_tokens},
    }
    if cost is not None:
        usage["cost"] = cost
    return {
        "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
        "usage": usage,
        "openrouter_metadata": {
            "endpoints": {
                # Real key, confirmed live 2026-09-10 -- see
                # openai_compatible.py's module docstring "CORRECTED"
                # note. Was wrongly "endpoints" here (and in the code)
                # before that.
                "available": [
                    {"provider": "DeepInfra", "selected": False},
                    {"provider": served_provider, "selected": True},
                ]
            }
        },
    }


@patch("harness.providers.openai_compatible.requests.post")
def test_triple_pin_sent_together(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body())
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])

    body = mock_post.call_args.kwargs["json"]
    assert body["provider"] == {"only": ["Nebius"], "allow_fallbacks": False, "quantizations": ["fp8"]}


@patch("harness.providers.openai_compatible.requests.post")
def test_cache_disable_and_metadata_headers_sent(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body())
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["X-OpenRouter-Cache"] == "false"
    assert headers["X-OpenRouter-Metadata"] == "enabled"


@patch("harness.providers.openai_compatible.requests.post")
def test_quantization_pin_is_mandatory_alongside_provider_pin(mock_post):
    unquantized = replace(PINNED_MODEL, quantization_pin=None)
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderError, match="quantization_pin"):
        provider.complete(unquantized, "sys", [{"role": "user", "content": "hi"}])
    mock_post.assert_not_called()


@patch("harness.providers.openai_compatible.requests.post")
def test_quantization_not_exposed_bypasses_the_requirement(mock_post):
    """A provider that genuinely has no discrete quantization (e.g. a
    first-party API like OpenAI/Google AI Studio -- see harness/config.py's
    GPT_LUNA/GEMINI_FLASH) can opt out via quantization_not_exposed=True
    instead of being permanently uncallable."""
    not_exposed = replace(PINNED_MODEL, quantization_pin=None, quantization_not_exposed=True)
    mock_post.return_value = _fake_response(json_body=_ok_body())
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(not_exposed, "sys", [{"role": "user", "content": "hi"}])

    body = mock_post.call_args.kwargs["json"]
    assert body["provider"] == {"only": ["Nebius"], "allow_fallbacks": False}
    assert "quantizations" not in body["provider"]


@patch("harness.providers.openai_compatible.requests.post")
def test_response_cache_hit_raises_and_halts(mock_post):
    mock_post.return_value = _fake_response(
        headers={"X-OpenRouter-Cache-Status": "HIT"}, json_body=_ok_body()
    )
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ResponseCacheViolation):
        provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])


@patch("harness.providers.openai_compatible.requests.post")
def test_response_cache_miss_does_not_raise(mock_post):
    mock_post.return_value = _fake_response(
        headers={"X-OpenRouter-Cache-Status": "MISS"}, json_body=_ok_body()
    )
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"


@patch("harness.providers.openai_compatible.requests.post")
def test_served_provider_mismatch_raises_pin_violation(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body(served_provider="DeepInfra"))
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderPinViolation, match="DeepInfra"):
        provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])


@patch("harness.providers.openai_compatible.requests.post")
def test_missing_metadata_fails_closed(mock_post):
    body = _ok_body()
    body["openrouter_metadata"] = {}
    mock_post.return_value = _fake_response(json_body=body)
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderPinViolation, match="could not determine"):
        provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])


@patch("harness.providers.openai_compatible.requests.post")
def test_served_provider_match_succeeds_and_is_recorded(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body(served_provider="Nebius"))
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.served_provider == "Nebius"


# Real response body, captured live 2026-09-10 via a direct curl replicating
# this harness's exact pinned request against nex-agi/nex-n2.5-pro:free
# (trimmed to the fields this code path reads). This is what caught the
# "endpoints.endpoints" vs "endpoints.available" bug -- pinned here as a
# literal fixture, not reconstructed by hand, so a regression to the wrong
# key shape fails this test against the actual shape OpenRouter sends,
# not against a mock built from the same wrong assumption as the bug.
REAL_LIVE_PINNED_RESPONSE_BODY = {
    "id": "gen-1789054151-qshwPuRko7zoc8YozB1U",
    "model": "nex-agi/nex-n2.5-pro:free",
    "provider": "Nex AGI",
    "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "OK"}}],
    "usage": {
        "prompt_tokens": 15,
        "completion_tokens": 5,
        "total_tokens": 20,
        "cost": 0,
        "prompt_tokens_details": {"cached_tokens": 0},
        "completion_tokens_details": {"reasoning_tokens": 1},
    },
    "openrouter_metadata": {
        "requested": "nex-agi/nex-n2.5-pro:free",
        "strategy": "direct",
        "summary": "available=1, selected=Nex AGI",
        "endpoints": {
            "total": 1,
            "available": [
                {"provider": "Nex AGI", "model": "nex-agi/nex-n2.5-pro-20260907:free", "selected": True}
            ],
        },
    },
}


@patch("harness.providers.openai_compatible.requests.post")
def test_matches_real_live_response_shape(mock_post):
    model = replace(PINNED_MODEL, provider_pin="Nex AGI")
    mock_post.return_value = _fake_response(json_body=REAL_LIVE_PINNED_RESPONSE_BODY)
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(model, "sys", [{"role": "user", "content": "hi"}])
    assert response.served_provider == "Nex AGI"


@patch("harness.providers.openai_compatible.requests.post")
def test_cached_tokens_extracted_from_usage(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body(cached_tokens=7))
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.cached_tokens == 7


@patch("harness.providers.openai_compatible.requests.post")
def test_reasoning_tokens_still_extracted(mock_post):
    mock_post.return_value = _fake_response(json_body=_ok_body(reasoning_tokens=42))
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(PINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.reasoning_tokens == 42


@patch("harness.providers.openai_compatible.requests.post")
def test_unpinned_openrouter_model_still_gets_cache_disable_header(mock_post):
    unpinned = replace(PINNED_MODEL, provider_pin=None, quantization_pin=None)
    mock_post.return_value = _fake_response(json_body=_ok_body())
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(unpinned, "sys", [{"role": "user", "content": "hi"}])

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["X-OpenRouter-Cache"] == "false"
    assert "provider" not in mock_post.call_args.kwargs["json"]


@patch("harness.providers.openai_compatible.requests.post")
def test_non_openrouter_base_untouched(mock_post):
    direct = replace(
        PINNED_MODEL, api_base="https://api.deepseek.com", provider_pin=None, quantization_pin=None
    )
    mock_post.return_value = _fake_response(json_body=_ok_body())
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(direct, "sys", [{"role": "user", "content": "hi"}])

    headers = mock_post.call_args.kwargs["headers"]
    assert "X-OpenRouter-Cache" not in headers
    assert "X-OpenRouter-Metadata" not in headers
