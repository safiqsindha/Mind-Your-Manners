"""Tests for the roster (harness/config.py's CORE_MODELS/STUDY1_MODELS) and
the Study 1 soft/hard budget-cap tiering."""
import time
from pathlib import Path

import pytest

from harness.config import (
    ALL_MODELS,
    CORE_MODELS,
    GPT_LUNA,
    GPT_LUNA_CALIBRATION,
    MODELS_BY_KEY,
    STUDY1_HARD_BUDGET_CAP_USD,
    STUDY1_MODELS,
    STUDY1_SOFT_BUDGET_CAP_USD,
    STUDY2_CORE_BUDGET_CAP_USD,
    STUDY2_PILOT_BUDGET_CAP_USD,
    with_thinking,
)
from harness.spend_tracker import BudgetExceeded, ResultRow, SpendTracker


def test_four_models_present():
    keys = {m.key for m in STUDY1_MODELS}
    assert "llama-3.3-70b" not in keys
    assert "gemini-flash" not in keys
    assert "gemini-flash-lite" not in keys
    assert keys == {"gpt-luna", "glm-current", "deepseek-current", "qwen-current"}


def test_study1_models_is_core_models():
    """Study 1 is retired and no longer pulls in an extra Gemini-Lite tier
    -- STUDY1_MODELS should just be CORE_MODELS now."""
    assert STUDY1_MODELS == CORE_MODELS


def test_no_direct_provider_integrations_in_core_roster():
    """All four roster models must route through OpenRouter -- none should
    be configured with a direct provider api_base (item 3's "single
    provider path", enforced here at the roster-definition level)."""
    for m in CORE_MODELS:
        assert m.api_base == "https://openrouter.ai/api/v1", f"{m.key} is not routed through OpenRouter"
        assert m.provider_pin, f"{m.key} has no provider_pin set"


def test_every_model_has_a_positive_price():
    for m in CORE_MODELS:
        assert m.input_price_per_1m > 0
        assert m.output_price_per_1m > 0


def test_every_pinned_model_satisfies_the_quantization_requirement():
    """Every model with provider_pin set must either have quantization_pin
    set, or explicitly acknowledge (quantization_not_exposed=True) that its
    pinned provider's real OpenRouter endpoint doesn't report one -- see
    harness/config.py's QUANTIZATION PIN section and
    harness/providers/openai_compatible.py. A model satisfying neither
    would raise ProviderError on its very first live call."""
    for m in CORE_MODELS:
        if m.provider_pin:
            assert m.quantization_pin or m.quantization_not_exposed, (
                f"{m.key}: provider_pin set but neither quantization_pin nor "
                "quantization_not_exposed=True -- this model cannot make a live call"
            )


def test_deepseek_is_not_pinned_to_the_nonexistent_deepseek_provider():
    """Regression test for the bug caught while merging the pinning PR in:
    provider_pin="DeepSeek" doesn't correspond to any real OpenRouter
    endpoint for this model_id."""
    deepseek = next(m for m in CORE_MODELS if m.key == "deepseek-current")
    assert deepseek.provider_pin != "DeepSeek"
    assert deepseek.quantization_pin  # DeepInfra's fp8 pin should still be set explicitly


def test_glm_has_a_real_quantization_pin_not_the_not_exposed_escape_hatch():
    """GLM 5.3 Flash's first-party Z.AI endpoint reports a real fp8
    quantization (unlike Luna/Qwen's first-party endpoints) -- it should be
    quantization_pin, not the quantization_not_exposed opt-out."""
    glm = next(m for m in CORE_MODELS if m.key == "glm-current")
    assert glm.quantization_pin == ["fp8"]
    assert glm.quantization_not_exposed is False


def test_glm_reasoning_effort_is_pinned_not_left_to_default():
    """GLM's reasoning is mandatory and its own default_effort is "max" (the
    most expensive level) -- reasoning_effort must be explicitly set here so
    a run never silently defaults to it."""
    glm = next(m for m in CORE_MODELS if m.key == "glm-current")
    assert glm.reasoning_effort is not None
    assert glm.reasoning_effort != "max"


def test_no_roster_model_is_pinned_to_a_moving_latest_alias():
    """OpenRouter '~'-prefixed model IDs (e.g. '~deepseek/deepseek-v4-flash-latest')
    redirect to whatever is currently newest -- a moving target that
    destroys reproducibility. None of this harness's model_ids may start
    with '~'."""
    for m in ALL_MODELS:
        assert not m.model_id.startswith("~"), f"{m.key}: model_id {m.model_id!r} is a moving '~latest' alias"


def test_no_roster_model_is_pinned_to_an_async_batch_variant():
    """OpenRouter ':batch' variants are asynchronous-only and cannot serve
    this harness's synchronous ReAct loop."""
    for m in ALL_MODELS:
        assert not m.model_id.endswith(":batch"), f"{m.key}: model_id {m.model_id!r} is an async batch-only variant"


def test_core_models_have_a_recorded_canonical_slug():
    """Every real roster model should record the dated, non-moving snapshot
    id OpenRouter's catalog reports for it, for reproducibility/audit --
    see harness/config.py module docstring."""
    for m in CORE_MODELS:
        assert m.canonical_slug, f"{m.key} has no canonical_slug recorded"
        assert not m.canonical_slug.startswith("~")


def test_calibration_arm_is_luna_with_reasoning_off_not_a_different_model():
    """The thinking arm compares one model at two reasoning settings, not
    two different models -- GPT_LUNA_CALIBRATION must share model_id with
    GPT_LUNA (not e.g. gpt-5.6-luna-pro), differing only in the reasoning
    parameter and thinking_enabled."""
    assert GPT_LUNA_CALIBRATION.model_id == GPT_LUNA.model_id
    assert GPT_LUNA_CALIBRATION.key != GPT_LUNA.key
    assert GPT_LUNA_CALIBRATION.thinking_enabled is False
    assert GPT_LUNA_CALIBRATION.reasoning_effort == "none"
    assert GPT_LUNA.thinking_enabled is True
    assert GPT_LUNA.reasoning_effort != "none"


def test_calibration_arm_not_in_core_models_but_addressable_by_key():
    assert GPT_LUNA_CALIBRATION not in CORE_MODELS
    assert MODELS_BY_KEY["gpt-luna-calibration"] is GPT_LUNA_CALIBRATION


def test_with_thinking_enabled_true_is_a_no_op_on_reasoning_effort():
    """enabled=True only re-affirms thinking_enabled -- it does not invert
    an enabled=False call, since it passes the model's current
    reasoning_effort through unchanged. Applying it to GPT_LUNA (already
    "on") is the well-defined case; it must not silently change the effort."""
    on = with_thinking(GPT_LUNA, enabled=True)
    assert on.reasoning_effort == GPT_LUNA.reasoning_effort
    assert on.thinking_enabled is True


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


def test_study2_core_budget_cap_is_150_and_above_the_pilot_cap():
    """Set generously against Luna's price uncertainty (see config.py's
    budget-cap comment) rather than tightly against a single point
    estimate -- $150, not the old $70 sized for a different roster/tone
    count."""
    assert STUDY2_CORE_BUDGET_CAP_USD == 150.0
    assert STUDY2_CORE_BUDGET_CAP_USD > STUDY2_PILOT_BUDGET_CAP_USD
