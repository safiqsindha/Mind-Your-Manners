"""Tests for Study 3 (harness/study3/): tone-persona wrapping, the BH
pre-registration procedure, the AgenticPay-facing LLM adapter, and the
run_negotiation orchestration.

The real AgenticPay clone (SafeRL-Lab/AgenticPay) is not vendored in this
repo -- it was cloned once, live, for the gating check documented in
RESULTS.md, matching this suite's established pattern for external repos
(SpreadsheetBench's own tests likewise don't require a live clone; see
tests/test_study2_scoring.py). run_negotiation()'s orchestration logic is
exercised here against a small fake `agenticpay` module (monkeypatched
into sys.modules) that reproduces the real package's reset()/step()/close()
contract confirmed during the gating check, so this tests the code in
runner.py, not a reimplementation of AgenticPay itself.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from harness.providers.base import ModelConfig
from harness.spend_tracker import SpendTracker
from harness.study3.personas import buyer_persona, seller_persona
from harness.study3.preregistration import (
    BASELINE_TONE,
    PREREGISTERED_COMPARISONS,
    benjamini_hochberg,
)
from harness.study3.llm_adapter import HarnessLLM
from harness.study3.runner import run_negotiation
from harness.tone_wrappers import TONE_ORDER, TONE_WRAPPERS

MOCK_MODEL = ModelConfig(
    key="mock-model", provider="mock", model_id="mock", display_name="Mock",
    temperature=0.0, max_tokens=512,
)


def test_buyer_persona_prepends_unmodified_wrapper_text():
    persona = buyer_persona("L4_rude")
    assert persona.startswith(TONE_WRAPPERS["L4_rude"].text)
    assert persona.endswith("You are a buyer looking for a good deal.")


def test_seller_persona_prepends_unmodified_wrapper_text():
    persona = seller_persona("L1_very_polite")
    assert persona.startswith(TONE_WRAPPERS["L1_very_polite"].text)
    assert persona.endswith("You are a seller looking to make a good deal.")


def test_all_five_tones_produce_distinct_personas():
    personas = {buyer_persona(t) for t in TONE_ORDER}
    assert len(personas) == 5


def test_preregistered_comparisons_exclude_only_the_baseline_cell():
    assert len(PREREGISTERED_COMPARISONS) == 24
    assert (BASELINE_TONE, BASELINE_TONE) not in PREREGISTERED_COMPARISONS
    assert all(bt in TONE_ORDER and st in TONE_ORDER for bt, st in PREREGISTERED_COMPARISONS)


def test_benjamini_hochberg_flags_the_small_p_values():
    # A handful of clearly-significant p-values mixed with clearly-not.
    p_values = [0.001, 0.002, 0.5, 0.9, 0.7]
    results = benjamini_hochberg(p_values, alpha=0.05)
    assert len(results) == 5
    assert results[0].significant and results[1].significant
    assert not results[3].significant


def test_benjamini_hochberg_empty_input():
    assert benjamini_hochberg([]) == []


def test_benjamini_hochberg_preserves_input_order():
    p_values = [0.9, 0.001, 0.5]
    results = benjamini_hochberg(p_values)
    assert [r.p_value for r in results] == p_values


def test_llm_adapter_records_result_row_and_returns_text(tmp_path: Path):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    llm = HarnessLLM(MOCK_MODEL, tracker, "buyer", "neg-1", "L3_neutral", "L3_neutral", trial=0)

    text = llm.generate("some negotiation prompt", temperature=0.0, max_tokens=256)

    assert isinstance(text, str)
    assert llm.n_calls == 1
    assert len(llm.result_rows) == 1
    row = llm.result_rows[0]
    assert row.study == "study3"
    assert row.item_id == "neg-1"
    assert row.tone_level == "buyer=L3_neutral|seller=L3_neutral"
    tracker.close()


class _FakeEnv:
    """Reproduces the reset()/step()/close() contract of AgenticPay's real
    Task1BasicPriceNegotiation, confirmed during the gating check
    (RESULTS.md) -- agrees on a fixed price after a fixed number of
    rounds, regardless of what the agents actually say, so this test
    exercises run_negotiation()'s own wiring rather than real negotiation
    dynamics."""

    def __init__(self, buyer_agent, seller_agent, max_rounds, initial_seller_price, buyer_max_price, seller_min_price, price_tolerance):
        self.buyer_agent = buyer_agent
        self.seller_agent = seller_agent
        self.max_rounds = max_rounds
        self.round = 0
        self.AGREE_AT_ROUND = 2
        self.agreed_price = 105.0

    def reset(self, user_requirement="", product_info=None, **kwargs):
        self.round = 0
        self.buyer_agent.initialize({"max_price": self.buyer_agent.buyer_max_price})
        self.seller_agent.initialize({"min_price": self.seller_agent.seller_min_price})
        return {"conversation_history": [], "current_round": 0}, {}

    def step(self, buyer_action=None, seller_action=None):
        self.round += 1
        terminated = self.round >= self.AGREE_AT_ROUND
        info = {
            "status": "agreed" if terminated else "ongoing",
            "agreed_price": self.agreed_price if terminated else None,
            "round": self.round,
            "global_score": 19.6 if terminated else None,
            "buyer_score": 8.1 if terminated else None,
            "seller_score": 7.4 if terminated else None,
        }
        obs = {"conversation_history": [], "current_round": self.round}
        return obs, 0.0, terminated, False, info

    def close(self):
        pass


class _FakeNegotiatingAgent:
    def __init__(self, model, role_description, **kwargs):
        self.model = model
        self.role_description = role_description
        self.initialized = False
        for k, v in kwargs.items():
            setattr(self, k, v)

    def initialize(self, context):
        self.initialized = True

    def respond(self, conversation_history, current_state):
        return self.model.generate(f"prompt for {self.role_description[:20]}")


@pytest.fixture
def fake_agenticpay(monkeypatch):
    fake_pkg = types.ModuleType("agenticpay")
    fake_pkg.make = lambda env_id, **kwargs: _FakeEnv(**kwargs)
    fake_agents_pkg = types.ModuleType("agenticpay.agents")
    fake_buyer_mod = types.ModuleType("agenticpay.agents.buyer_agent")
    fake_buyer_mod.BuyerAgent = _FakeNegotiatingAgent
    fake_seller_mod = types.ModuleType("agenticpay.agents.seller_agent")
    fake_seller_mod.SellerAgent = _FakeNegotiatingAgent

    monkeypatch.setitem(sys.modules, "agenticpay", fake_pkg)
    monkeypatch.setitem(sys.modules, "agenticpay.agents", fake_agents_pkg)
    monkeypatch.setitem(sys.modules, "agenticpay.agents.buyer_agent", fake_buyer_mod)
    monkeypatch.setitem(sys.modules, "agenticpay.agents.seller_agent", fake_seller_mod)
    yield


def test_run_negotiation_agreed_result(tmp_path: Path, fake_agenticpay):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    result = run_negotiation(
        tracker, MOCK_MODEL, MOCK_MODEL, "L4_rude", "L1_very_polite", trial=0,
        buyer_max_price=120.0, seller_min_price=80.0, initial_seller_price=150.0,
        product_info={"name": "Widget"}, user_requirement="I need a widget.",
    )
    tracker.close()

    assert result.status == "agreed"
    assert result.rounds == 2
    assert result.agreed_price == 105.0
    assert result.fair_split_price == 100.0
    # fair_split(100) - agreed_price(105) = -5: buyer paid $5 MORE than a
    # fair split, i.e. the seller captured extra value here, not gave it away.
    assert result.value_given_away_to_buyer_usd == -5.0
    assert result.global_score == 19.6
    assert result.n_buyer_calls == 2  # one call per round, 2 rounds to agreement
    assert result.n_seller_calls == 2
    assert result.total_cost_usd >= 0.0


def test_run_negotiation_records_rows_for_both_roles(tmp_path: Path, fake_agenticpay):
    tracker = SpendTracker(tmp_path / "raw.jsonl", phase="test", cap_usd=10.0)
    run_negotiation(
        tracker, MOCK_MODEL, MOCK_MODEL, "L3_neutral", "L3_neutral", trial=1,
        buyer_max_price=120.0, seller_min_price=80.0, initial_seller_price=150.0,
        product_info={"name": "Widget"}, user_requirement="I need a widget.",
    )
    tracker.close()

    raw_lines = (tmp_path / "raw.jsonl").read_text().strip().splitlines()
    assert len(raw_lines) == 4  # 2 rounds x (buyer + seller)
    import json

    rows = [json.loads(line) for line in raw_lines]
    assert {r["extra"]["role"] for r in rows} == {"buyer", "seller"}
    assert all(r["study"] == "study3" for r in rows)
