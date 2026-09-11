"""Tests for harness/providers/openai_compatible.py's retry-on-transient-
failure logic (_post_with_retry), added after a live run found DeepSeek and
Qwen both returning HTTP 429 "rate-limited upstream... shared pool" on
essentially the first call, with no retry logic to absorb it -- see that
module's docstring "RETRY ON TRANSIENT FAILURE" note.

time.sleep is patched throughout so these tests run fast and exercise the
real backoff-selection logic without actually waiting.
"""
from __future__ import annotations

from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest
import requests

from harness.providers.base import ModelConfig, ProviderError
from harness.providers.openai_compatible import (
    MAX_RETRIES,
    OpenAICompatibleProvider,
    RETRY_BACKOFF_BASE_S,
    RETRY_BACKOFF_CAP_S,
    _clamp_delay,
    _post_with_retry,
)

UNPINNED_MODEL = ModelConfig(
    key="retry-test-model",
    provider="openai_compatible",
    model_id="some/model",
    display_name="Retry Test Model",
    temperature=0.0,
    api_base="https://openrouter.ai/api/v1",
)


def _resp(status_code, headers=None, text="error", json_body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = text
    resp.json.return_value = json_body or _ok_json()
    return resp


def _ok_json():
    return {
        "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_retries_on_429_then_succeeds(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429), _resp(429), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_gives_up_after_max_retries(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429)] * (MAX_RETRIES + 1)
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderError, match="429"):
        provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert mock_post.call_count == MAX_RETRIES + 1
    assert mock_sleep.call_count == MAX_RETRIES


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_non_retryable_status_fails_immediately_without_sleeping(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(400, text="bad request")]
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderError, match="400"):
        provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert mock_post.call_count == 1
    mock_sleep.assert_not_called()


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_retry_after_header_is_honored_over_exponential_backoff(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429, headers={"Retry-After": "5"}), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    mock_sleep.assert_called_once_with(5.0)


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_exponential_backoff_used_when_no_retry_after_header(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429), _resp(429), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    first_delay, second_delay = mock_sleep.call_args_list[0].args[0], mock_sleep.call_args_list[1].args[0]
    assert first_delay == RETRY_BACKOFF_BASE_S  # 2s
    assert second_delay == RETRY_BACKOFF_BASE_S * 2  # 4s -- actually growing, not flat


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_5xx_is_also_retried(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(503), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    assert mock_post.call_count == 2


@pytest.mark.parametrize("status", [502, 504])
@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_502_and_504_are_each_individually_retried(mock_post, mock_sleep, status):
    mock_post.side_effect = [_resp(status), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    assert mock_post.call_count == 2


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_500_is_not_retried(mock_post, mock_sleep):
    """500 is deliberately excluded -- see RETRYABLE_STATUS_CODES's
    comment: unlike 502/503/504, a 500 can be a deterministic model-side
    error that retrying would only reproduce."""
    mock_post.side_effect = [_resp(500, text="internal error")]
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderError, match="500"):
        provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert mock_post.call_count == 1
    mock_sleep.assert_not_called()


# --- Retry-After header edge cases -- the exact scenario an adversarial or
# misconfigured upstream could use to hang a live run if unclamped. ---

def test_clamp_delay_caps_a_huge_retry_after_value():
    assert _clamp_delay(999_999.0) == RETRY_BACKOFF_CAP_S


def test_clamp_delay_rejects_negative_value():
    assert _clamp_delay(-5.0) == RETRY_BACKOFF_CAP_S


def test_clamp_delay_rejects_nan():
    assert _clamp_delay(float("nan")) == RETRY_BACKOFF_CAP_S


def test_clamp_delay_rejects_infinity():
    assert _clamp_delay(float("inf")) == RETRY_BACKOFF_CAP_S


def test_clamp_delay_passes_through_a_reasonable_value():
    assert _clamp_delay(5.0) == 5.0


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_huge_retry_after_header_is_capped_not_slept_in_full(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429, headers={"Retry-After": "999999"}), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    mock_sleep.assert_called_once_with(RETRY_BACKOFF_CAP_S)


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_negative_retry_after_header_does_not_crash(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429, headers={"Retry-After": "-5"}), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    mock_sleep.assert_called_once_with(RETRY_BACKOFF_CAP_S)


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_non_numeric_retry_after_header_falls_back_to_exponential_backoff(mock_post, mock_sleep):
    # Real servers sometimes send an RFC 7231 HTTP-date instead of seconds.
    mock_post.side_effect = [_resp(429, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    mock_sleep.assert_called_once_with(RETRY_BACKOFF_BASE_S)


# --- Network-level exceptions (below the HTTP layer) -- the biggest gap
# flagged in review: a 502/503 response was retried, but a bare
# ConnectionError/Timeout from `requests` was not. ---

@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_connection_error_is_retried_then_succeeds(mock_post, mock_sleep):
    mock_post.side_effect = [requests.ConnectionError("boom"), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once()


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_timeout_exception_is_retried_then_succeeds(mock_post, mock_sleep):
    mock_post.side_effect = [requests.Timeout("timed out"), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert response.text == "hi"
    assert mock_post.call_count == 2


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_network_exception_exhausts_retries_and_raises_provider_error(mock_post, mock_sleep):
    mock_post.side_effect = [requests.ConnectionError("boom")] * (MAX_RETRIES + 1)
    provider = OpenAICompatibleProvider(api_key="k")
    with pytest.raises(ProviderError, match="network error"):
        provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    assert mock_post.call_count == MAX_RETRIES + 1
    assert mock_sleep.call_count == MAX_RETRIES


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_timeout_kwarg_passed_on_every_retry_attempt(mock_post, mock_sleep):
    mock_post.side_effect = [_resp(429), _resp(429), _resp(200)]
    provider = OpenAICompatibleProvider(api_key="k")
    provider.complete(UNPINNED_MODEL, "sys", [{"role": "user", "content": "hi"}])
    for call in mock_post.call_args_list:
        assert call.kwargs["timeout"] == 180


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_retry_then_success_still_verifies_the_pin_on_a_pinned_model(mock_post, mock_sleep):
    """The retry path and the served-provider pin assertion have never
    been exercised together before -- confirm a 429-then-200 sequence on
    a pinned model still correctly parses openrouter_metadata on the
    (successful) final response, using the real live response shape
    (see test_openrouter_pinning.py::REAL_LIVE_PINNED_RESPONSE_BODY)."""
    pinned_model = replace(UNPINNED_MODEL, provider_pin="Nex AGI", quantization_pin=["fp8"])
    pinned_ok_body = {
        **_ok_json(),
        "openrouter_metadata": {
            "endpoints": {"available": [{"provider": "Nex AGI", "selected": True}]},
        },
    }
    mock_post.side_effect = [_resp(429), _resp(200, json_body=pinned_ok_body)]
    provider = OpenAICompatibleProvider(api_key="k")
    response = provider.complete(pinned_model, "sys", [{"role": "user", "content": "hi"}])
    assert response.served_provider == "Nex AGI"
    assert mock_post.call_count == 2


# --- Truncated-response failures ------------------------------------------
# ChunkedEncodingError and ContentDecodingError inherit from RequestException,
# NOT from ConnectionError or Timeout, so catching only the obvious two let
# them through unretried. A real gate run lost a task to
# "ChunkedEncodingError: Response ended prematurely".

@pytest.mark.parametrize(
    "exc",
    [
        requests.exceptions.ChunkedEncodingError("Response ended prematurely"),
        requests.exceptions.ContentDecodingError("bad gzip"),
    ],
)
@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_truncated_response_is_retried(mock_post, mock_sleep, exc):
    mock_post.side_effect = [exc, _resp(200)]
    resp = _post_with_retry("http://x", {}, {}, timeout=180)
    assert resp.status_code == 200
    assert mock_post.call_count == 2, "a truncated response body must be retried"


@patch("harness.providers.openai_compatible.time.sleep")
@patch("harness.providers.openai_compatible.requests.post")
def test_truncated_response_eventually_gives_up_as_provider_error(mock_post, mock_sleep):
    mock_post.side_effect = [
        requests.exceptions.ChunkedEncodingError("truncated")
    ] * (MAX_RETRIES + 1)
    with pytest.raises(ProviderError):
        _post_with_retry("http://x", {}, {}, timeout=180)
    assert mock_post.call_count == MAX_RETRIES + 1


@patch("harness.providers.openai_compatible.requests.post")
def test_a_config_error_is_still_not_retried(mock_post):
    """Only transient network failures. TooManyRedirects is a configuration
    problem that retrying would merely delay."""
    mock_post.side_effect = requests.exceptions.TooManyRedirects("loop")
    with pytest.raises(requests.exceptions.TooManyRedirects):
        _post_with_retry("http://x", {}, {}, timeout=180)
    assert mock_post.call_count == 1
