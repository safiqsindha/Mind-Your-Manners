"""Tests for the roster replacement (item 1 of the config-change task) and
the Study 1 soft/hard budget-cap tiering (item 6)."""
import time
from pathlib import Path

import pytest

from harness.config import (
    CORE_MODELS,
    GEMINI_FLASH_LITE,
    STUDY1_HARD_BUDGET_CAP_USD,
    STUDY1_MODELS,
    STUDY1_SOFT_BUDGET_CAP_USD,
)
from harness.spend_tracker import BudgetExceeded, ResultRow, SpendTracker


def test_llama_dropped_and_five_models_present():
    keys = {m.key for m in STUDY1_MODELS}
    assert "llama-3.3-70b" not in keys
    assert keys == {"gpt-luna", "gemini-flash", "deepseek-current", "qwen-current", "gemini-flash-lite"}


def test_gemini_lite_is_study1_only():
    assert GEMINI_FLASH_LITE not in CORE_MODELS
    assert GEMINI_FLASH_LITE in STUDY1_MODELS
    assert len(STUDY1_MODELS) == len(CORE_MODELS) + 1


def test_no_direct_provider_integrations_in_core_roster():
    """All five roster models must route through OpenRouter -- none should
    be configured with a direct provider api_base (item 3's "single
    provider path", enforced here at the roster-definition level)."""
    for m in STUDY1_MODELS:
        assert m.api_base == "https://openrouter.ai/api/v1", f"{m.key} is not routed through OpenRouter"
        assert m.provider_pin, f"{m.key} has no provider_pin set"


def test_every_model_has_a_positive_price():
    for m in STUDY1_MODELS:
        assert m.input_price_per_1m > 0
        assert m.output_price_per_1m > 0


def _make_row(cost_usd: float) -> ResultRow:
    return ResultRow(
        row_id="r", study="study1", phase="test", item_id="q", tone_level="L3_neutral",
        trial=0, model_key="m", model_id="m-id", provider="openai_compatible", temperature=0.0,
        seed=None, reasoning_effort=None, thinking_budget_tokens=None, prompt_tokens=10,
        completion_tokens=5, reasoning_tokens=0, cost_usd=cost_usd, latency_s=0.0, refused=False,
        error=None, response_text="", extracted_answer=None, is_correct=None, timestamp=time.time(),
    )


def test_soft_cap_warns_but_does_not_stop(tmp_path: Path, capsys):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0, soft_cap_usd=5.0)
    tracker.record(_make_row(6.0))  # crosses soft cap, stays under hard cap
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "soft" in captured.out.lower()
    tracker.close()


def test_hard_cap_still_stops_the_run(tmp_path: Path):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0, soft_cap_usd=5.0)
    tracker.record(_make_row(6.0))
    with pytest.raises(BudgetExceeded):
        tracker.record(_make_row(6.0))
    tracker.close()


def test_soft_cap_warning_fires_only_once(tmp_path: Path, capsys):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=100.0, soft_cap_usd=5.0)
    tracker.record(_make_row(6.0))
    capsys.readouterr()
    tracker.record(_make_row(1.0))
    captured = capsys.readouterr()
    assert "WARNING" not in captured.out
    tracker.close()


def test_study1_soft_cap_below_hard_cap():
    assert STUDY1_SOFT_BUDGET_CAP_USD < STUDY1_HARD_BUDGET_CAP_USD
