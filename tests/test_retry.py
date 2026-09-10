"""Tests for harness/providers/openai_compatible.py's retry-on-transient-
failure logic (_post_with_retry), added after a live run found DeepSeek and
Qwen both returning HTTP 429 "rate-limited upstream... shared pool" on
essentially the first call, with no retry logic to absorb it -- see that
module's docstring "RETRY ON TRANSIENT FAILURE" note.

time.sleep is patched throughout so these tests run fast and exercise the
real backoff-selection logic without actually waiting.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from harness.providers.base import ModelConfig, ProviderError
from harness.providers.openai_compatible import (
    MAX_RETRIES,
    OpenAICompatibleProvider,
    RETRY_BACKOFF_BASE_S,
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
