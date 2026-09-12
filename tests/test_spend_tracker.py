import time
from pathlib import Path

import pytest

from harness.config import MODELS_BY_KEY
from harness.spend_tracker import BudgetExceeded, ResultRow, SpendTracker, compute_cost_usd
from harness.providers.mock_provider import MockProvider


def make_row(cost_usd: float, i: int = 0) -> ResultRow:
    return ResultRow(
        row_id=f"r{i}", study="study1", phase="test", item_id=f"q{i}", tone_level="L3_neutral",
        trial=0, model_key="m", model_id="m-id", provider="mock", temperature=0.0, seed=None,
        reasoning_effort=None, thinking_budget_tokens=None, prompt_tokens=10, completion_tokens=5,
        reasoning_tokens=0, cost_usd=cost_usd, latency_s=0.0, refused=False, error=None,
        response_text="(A)", extracted_answer="A", is_correct=True, timestamp=time.time(),
    )


def test_records_rows_and_tracks_spend(tmp_path: Path):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    tracker.record(make_row(1.0, 0))
    tracker.record(make_row(2.0, 1))
    tracker.close()
    assert tracker.total_usd == pytest.approx(3.0)
    assert tracker.n_calls == 2
    lines = (tmp_path / "raw.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2


def test_budget_exceeded_raises(tmp_path: Path):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=2.0)
    tracker.record(make_row(1.5, 0))
    with pytest.raises(BudgetExceeded):
        tracker.record(make_row(1.0, 1))
    tracker.close()


def test_check_before_call_raises_before_spending(tmp_path: Path):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=1.0)
    with pytest.raises(BudgetExceeded):
        tracker.check_before_call(estimated_cost_usd=5.0)
    tracker.close()


def test_compute_cost_usd_matches_manual_calc():
    model = MODELS_BY_KEY["gpt-luna"]
    response = MockProvider().complete(model, "sys", [{"role": "user", "content": "2+2? (A) 3 (B) 4"}])
    cost = compute_cost_usd(model, response)
    # completion_tokens ALREADY includes reasoning on this route, so the
    # manual calc must not add reasoning again -- doing so was the bug (see
    # spend_tracker.compute_cost_usd and test_design_integrity section 10).
    expected = (response.prompt_tokens / 1_000_000) * model.input_price_per_1m + (
        response.completion_tokens / 1_000_000
    ) * model.output_price_per_1m
    assert cost == pytest.approx(expected)
    assert response.reasoning_tokens > 0, "fixture must actually exercise reasoning"
