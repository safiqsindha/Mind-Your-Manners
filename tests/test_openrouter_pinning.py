"""Tests for the OpenRouter enforcement layer (task spec item 3: mandatory
provider.only + allow_fallbacks:false + provider.quantizations triple-pin,
with a served-provider assertion; item 4: response-cache disabled and
asserted off; item 5: caching/latency instrumentation on every call).

All HTTP is mocked -- no network, no API key needed. Verified request/response
field names (provider.only/quantizations, openrouter_metadata.endpoints,
X-OpenRouter-Cache*, usage.prompt_tokens_details.cached_tokens, usage.cost)
came from OpenRouter's own docs, not guessed -- see
harness/providers/openai_compatible.py's module docstring and
harness/config.py's QUANTIZATION PIN section for the verification trail.
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
                "endpoints": [
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
