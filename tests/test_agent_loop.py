"""Tests for harness/study2/agent_loop.py's turn-budget awareness -- added
after a live re-run showed the WORKBOOK_PATH prompt fix alone wasn't
enough: every trajectory ran the full turn budget without ever emitting
FINAL, because the model was never told what that budget was. See
_agent_system_prompt's module-level comment for the full story.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from harness.providers.base import ModelConfig, ProviderResponse
from harness.spend_tracker import SpendTracker
from harness.study2.agent_loop import _agent_system_prompt, run_react_multi_round

MODEL = ModelConfig(
    key="test-model",
    provider="mock",
    model_id="test/model",
    display_name="Test Model",
    temperature=0.0,
    max_tokens=1024,
)


def test_agent_system_prompt_states_the_real_turn_budget():
    prompt = _agent_system_prompt(max_turns=10)
    assert "you have 10 turns total" in prompt.lower()


def test_agent_system_prompt_commit_by_turn_scales_with_budget():
    prompt5 = _agent_system_prompt(max_turns=5)
    prompt10 = _agent_system_prompt(max_turns=10)
    assert "turn 3" in prompt5.lower()  # max(1, 5-2)
    assert "turn 8" in prompt10.lower()  # max(1, 10-2)


def test_agent_system_prompt_commit_by_never_goes_below_turn_1():
    prompt = _agent_system_prompt(max_turns=1)
    assert "turn 1" in prompt.lower()


class _FakeProvider:
    """Records every system prompt/messages it was called with; returns
    canned code responses for a few turns then a FINAL."""

    def __init__(self, responses: list[str]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def complete(self, model, system, messages, tools=None):
        self.calls.append({"system": system, "messages": list(messages)})
        text = self.responses.pop(0)
        return ProviderResponse(text=text, prompt_tokens=10, completion_tokens=10)


def _run(tmp_path, responses, max_turns=10):
    provider = _FakeProvider(responses)
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    workbook = tmp_path / "in.xlsx"
    workbook.write_bytes(b"")  # sandbox reads the path, not the content, for these tests
    with patch("harness.study2.agent_loop.get_provider", return_value=provider):
        traj = run_react_multi_round(
            tracker, MODEL, "task1", "do the thing", workbook, tmp_path / "work",
            tone_level="L4_neutral", trial=0, max_turns=max_turns,
        )
    tracker.close()
    return traj, provider


def test_every_call_uses_the_dynamic_prompt_not_a_stale_static_one(tmp_path: Path):
    _, provider = _run(tmp_path, ["FINAL: done"], max_turns=7)
    assert len(provider.calls) == 1
    assert "you have 7 turns total" in provider.calls[0]["system"].lower()


def test_observation_includes_the_upcoming_turn_number(tmp_path: Path):
    responses = [
        "```python\nprint('hi')\n```",  # turn 0 (1-indexed: 1) -- code, no FINAL
        "FINAL: done",  # turn 1 (1-indexed: 2)
    ]
    _, provider = _run(tmp_path, responses, max_turns=5)
    assert len(provider.calls) == 2
    # The second call's messages should include an observation mentioning
    # the upcoming turn (turn index 1, 0-indexed -> "Turn 2 of 5 next").
    last_user_msg = provider.calls[1]["messages"][-1]["content"]
    assert "Turn 2 of 5 next" in last_user_msg


def test_observation_marks_the_final_available_turn(tmp_path: Path):
    responses = [
        "```python\nprint('hi')\n```",  # turn 0 of a 1-turn budget -- last turn, no next
    ]
    traj, provider = _run(tmp_path, responses, max_turns=1)
    # Loop exhausts max_turns=1 without a FINAL -- hit_turn_limit should be set.
    assert traj.hit_turn_limit is True
    assert len(provider.calls) == 1


def test_no_code_block_nudge_also_carries_the_turn_marker(tmp_path: Path):
    responses = [
        "I'm thinking about it.",  # no code block, no FINAL -- triggers the protocol nudge
        "FINAL: done",
    ]
    _, provider = _run(tmp_path, responses, max_turns=8)
    last_user_msg = provider.calls[1]["messages"][-1]["content"]
    assert "no code block or FINAL" in last_user_msg
    assert "Turn 2 of 8 next" in last_user_msg
