"""Tests for harness/study2/thinking_preflight.py's three gate checks."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from harness.config import GPT_LUNA, GPT_LUNA_CALIBRATION
from harness.providers.base import ProviderResponse
from harness.spend_tracker import SpendTracker
from harness.study2.thinking_preflight import run_thinking_preflight


def _mock(model):
    return replace(model, provider="mock")


def test_passes_against_the_mock_provider_with_real_roster_configs(tmp_path: Path):
    """Dry-run smoke test: the mock provider varies reasoning_tokens with
    thinking_enabled/reasoning_effort (see mock_provider.py), so this
    should pass all three checks against the real GPT_LUNA/
    GPT_LUNA_CALIBRATION configs forced onto the mock provider."""
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    report = run_thinking_preflight(tracker, _mock(GPT_LUNA), _mock(GPT_LUNA_CALIBRATION))
    tracker.close()

    assert report.passed, [(-c.name, c.detail) for c in report.checks if not c.passed]
    assert report.off_reasoning_tokens == 0
    assert report.on_reasoning_tokens > 0


def _patched_provider(on_response: ProviderResponse, off_response: ProviderResponse):
    calls = {"n": 0}

    class _FakeProvider:
        def complete(self, model, system, messages, tools=None):
            calls["n"] += 1
            return on_response if calls["n"] == 1 else off_response

    return _FakeProvider()


def test_fails_when_reasoning_tokens_field_is_missing(tmp_path: Path):
    on = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=5, reasoning_tokens_reported=False)
    off = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=0, reasoning_tokens_reported=True)
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    with patch("harness.study2.thinking_preflight.get_provider", return_value=_patched_provider(on, off)):
        report = run_thinking_preflight(tracker, GPT_LUNA, GPT_LUNA_CALIBRATION)
    tracker.close()

    assert not report.passed
    check = next(c for c in report.checks if c.name == "reasoning_tokens_field_present")
    assert not check.passed
    assert "missing" in check.detail.lower()


def test_fails_when_off_condition_is_not_actually_zero(tmp_path: Path):
    on = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=5, reasoning_tokens_reported=True)
    off = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=3, reasoning_tokens_reported=True)
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    with patch("harness.study2.thinking_preflight.get_provider", return_value=_patched_provider(on, off)):
        report = run_thinking_preflight(tracker, GPT_LUNA, GPT_LUNA_CALIBRATION)
    tracker.close()

    assert not report.passed
    check = next(c for c in report.checks if c.name == "off_zero_on_nonzero")
    assert not check.passed


def test_fails_when_on_and_off_produce_identical_token_counts(tmp_path: Path):
    on = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=0, reasoning_tokens_reported=True)
    off = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=0, reasoning_tokens_reported=True)
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    with patch("harness.study2.thinking_preflight.get_provider", return_value=_patched_provider(on, off)):
        report = run_thinking_preflight(tracker, GPT_LUNA, GPT_LUNA_CALIBRATION)
    tracker.close()

    assert not report.passed
    check = next(c for c in report.checks if c.name == "on_off_differ_on_probe")
    assert not check.passed
    # also correctly fails off_zero_on_nonzero, since "on" reported 0 too
    assert not next(c for c in report.checks if c.name == "off_zero_on_nonzero").passed


def test_passes_when_all_three_conditions_are_satisfied(tmp_path: Path):
    # completion_tokens has to CONTAIN the 40 reasoning tokens: on this
    # route reasoning is reported as a breakdown of completion, so a fixture
    # with completion=10 and reasoning=40 describes a response no provider
    # can emit -- and it was that impossible fixture, not the check, that
    # made the old prompt+completion+reasoning total look like it separated
    # the two conditions. See test_design_integrity section 10.
    on = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=50, reasoning_tokens=40, reasoning_tokens_reported=True)
    off = ProviderResponse(text="x", prompt_tokens=10, completion_tokens=10, reasoning_tokens=0, reasoning_tokens_reported=True)
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    with patch("harness.study2.thinking_preflight.get_provider", return_value=_patched_provider(on, off)):
        report = run_thinking_preflight(tracker, GPT_LUNA, GPT_LUNA_CALIBRATION)
    tracker.close()

    assert report.passed
    assert all(c.passed for c in report.checks)
