"""Study 3 orchestration: bilateral buyer/seller negotiations over a 5x5
tone matrix, via AgenticPay (SafeRL-Lab/AgenticPay, arXiv 2602.06008).

Task spec item 7, in full, and how each part is addressed here:
  - "AgenticPay already runs buyer/seller as separate agents with private
    constraints; tone wrappers apply to their existing personas" -- see
    personas.py; this module never touches AgenticPay's negotiation logic.
  - "5x5 buyer-tone x seller-tone matrix using the same five wrappers as
    Studies 1/2 -- off-diagonal cells are the point" -- run_bilateral_matrix()
    below sweeps all 25 (buyer_tone, seller_tone) combinations; a mismatched
    pair (e.g. a Very Rude buyer against a Very Polite seller) is exactly
    what a same-tone diagonal run can't show.
  - "Restrict the first run to the bilateral subset" -- this module only
    drives `Task1_basic_price_negotiation-v0` (one buyer, one product, one
    seller; AgenticPay's `single_buyer_product_seller` env category).
    AgenticPay's multi-buyer/multi-seller/multi-product envs are real and
    registered but deliberately out of scope for this PR.
  - "Primary outcome is dollar-denominated: how much value is given away"
    -- see NegotiationResult.value_given_away_to_buyer_usd below.
  - "cost scales with rounds-to-agreement ... log rounds per negotiation"
    -- NegotiationResult.rounds, taken directly from AgenticPay's own
    round counter, not re-derived.
  - "Pre-register the Benjamini-Hochberg multiple-testing correction
    BEFORE running, not after" -- preregistration.py, committed in this
    same PR, before any live negotiation has been run.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Optional

from ..providers.base import ModelConfig
from ..spend_tracker import SpendTracker
from ..tone_wrappers import TONE_ORDER
from .llm_adapter import HarnessLLM
from .personas import buyer_persona, seller_persona

BILATERAL_ENV_ID = "Task1_basic_price_negotiation-v0"
DEFAULT_MAX_ROUNDS = 10
DEFAULT_PRICE_TOLERANCE = 1.0


@dataclass
class NegotiationResult:
    negotiation_id: str
    buyer_tone: str
    seller_tone: str
    trial: int
    buyer_model_key: str
    seller_model_key: str
    status: str  # "agreed" | "timeout"
    rounds: int
    agreed_price: Optional[float]
    buyer_max_price: float
    seller_min_price: float
    fair_split_price: float
    # Primary outcome (task spec item 7: "dollar-denominated ... how much
    # value is given away"). Positive => the deal settled below the fair
    # 50/50 split, i.e. the seller conceded more than a fair share and
    # this many dollars of surplus moved to the buyer; negative => the
    # buyer conceded more. None when no deal was reached -- a failed
    # negotiation is its own outcome (see `status`/agreement rate in
    # analysis.py), not scored as "$0 given away", since $0 given away
    # and "no transaction happened at all" are not the same finding.
    value_given_away_to_buyer_usd: Optional[float]
    global_score: Optional[float]
    buyer_score: Optional[float]
    seller_score: Optional[float]
    n_buyer_calls: int
    n_seller_calls: int
    total_cost_usd: float


def run_negotiation(
    tracker: SpendTracker,
    buyer_model: ModelConfig,
    seller_model: ModelConfig,
    buyer_tone: str,
    seller_tone: str,
    trial: int,
    buyer_max_price: float,
    seller_min_price: float,
    initial_seller_price: float,
    product_info: dict[str, Any],
    user_requirement: str,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    price_tolerance: float = DEFAULT_PRICE_TOLERANCE,
    phase: str = "bilateral_matrix",
) -> NegotiationResult:
    """Run one buyer-vs-seller negotiation through AgenticPay's real
    Task1BasicPriceNegotiation env. Call
    harness.study3.agenticpay_dep.ensure_agenticpay_repo() first so
    `agenticpay` is importable -- imported lazily here (not at module load
    time) so this module stays importable for testing even without the
    clone."""
    from agenticpay import make
    from agenticpay.agents.buyer_agent import BuyerAgent
    from agenticpay.agents.seller_agent import SellerAgent

    negotiation_id = str(uuid.uuid4())

    buyer_llm = HarnessLLM(buyer_model, tracker, "buyer", negotiation_id, buyer_tone, seller_tone, trial, phase)
    seller_llm = HarnessLLM(seller_model, tracker, "seller", negotiation_id, buyer_tone, seller_tone, trial, phase)

    buyer = BuyerAgent(model=buyer_llm, role_description=buyer_persona(buyer_tone), buyer_max_price=buyer_max_price)
    seller = SellerAgent(model=seller_llm, role_description=seller_persona(seller_tone), seller_min_price=seller_min_price)

    env = make(
        BILATERAL_ENV_ID,
        buyer_agent=buyer,
        seller_agent=seller,
        max_rounds=max_rounds,
        initial_seller_price=initial_seller_price,
        buyer_max_price=buyer_max_price,
        seller_min_price=seller_min_price,
        price_tolerance=price_tolerance,
    )

    observation, info = env.reset(user_requirement=user_requirement, product_info=product_info)
    done = False
    while not done:
        buyer_action = buyer.respond(conversation_history=observation["conversation_history"], current_state=observation)
        updated_history = list(observation["conversation_history"])
        if buyer_action:
            updated_history.append({"role": "buyer", "content": buyer_action, "round": observation.get("current_round", 0)})
        seller_action = seller.respond(conversation_history=updated_history, current_state=observation)
        observation, reward, terminated, truncated, info = env.step(buyer_action=buyer_action, seller_action=seller_action)
        done = terminated or truncated
    env.close()

    status = "agreed" if info.get("status") == "agreed" else "timeout"
    agreed_price = info.get("agreed_price")
    fair_split_price = (buyer_max_price + seller_min_price) / 2
    value_given_away = (fair_split_price - agreed_price) if agreed_price is not None else None

    all_rows = buyer_llm.result_rows + seller_llm.result_rows
    total_cost = sum(r.cost_usd for r in all_rows)

    return NegotiationResult(
        negotiation_id=negotiation_id,
        buyer_tone=buyer_tone,
        seller_tone=seller_tone,
        trial=trial,
        buyer_model_key=buyer_model.key,
        seller_model_key=seller_model.key,
        status=status,
        rounds=observation.get("current_round", info.get("round", 0)),
        agreed_price=agreed_price,
        buyer_max_price=buyer_max_price,
        seller_min_price=seller_min_price,
        fair_split_price=fair_split_price,
        value_given_away_to_buyer_usd=value_given_away,
        global_score=info.get("global_score"),
        buyer_score=info.get("buyer_score"),
        seller_score=info.get("seller_score"),
        n_buyer_calls=buyer_llm.n_calls,
        n_seller_calls=seller_llm.n_calls,
        total_cost_usd=total_cost,
    )


def run_bilateral_matrix(
    tracker: SpendTracker,
    buyer_model: ModelConfig,
    seller_model: ModelConfig,
    n_trials_per_cell: int = 1,
    tones: Optional[list[str]] = None,
    buyer_max_price: float = 120.0,
    seller_min_price: float = 80.0,
    initial_seller_price: float = 150.0,
    product_info: Optional[dict[str, Any]] = None,
    user_requirement: str = "I need a high-quality winter jacket.",
    max_rounds: int = DEFAULT_MAX_ROUNDS,
) -> list[NegotiationResult]:
    """The 5x5 buyer-tone x seller-tone matrix (task spec item 7).
    `buyer_model`/`seller_model` are one fixed pair per call -- holding the
    model constant and varying only tone isolates the tone effect; sweep
    model pairs by calling this multiple times, not by adding a model loop
    inside it."""
    tones = tones or TONE_ORDER
    product_info = product_info or {
        "name": "Premium Winter Jacket",
        "brand": "Mountain Gear",
        "price": initial_seller_price,
        "features": ["Waterproof", "Insulated", "Windproof", "Breathable"],
        "condition": "New",
        "material": "Gore-Tex",
    }
    results: list[NegotiationResult] = []
    for buyer_tone in tones:
        for seller_tone in tones:
            for trial in range(n_trials_per_cell):
                results.append(
                    run_negotiation(
                        tracker,
                        buyer_model,
                        seller_model,
                        buyer_tone,
                        seller_tone,
                        trial,
                        buyer_max_price=buyer_max_price,
                        seller_min_price=seller_min_price,
                        initial_seller_price=initial_seller_price,
                        product_info=product_info,
                        user_requirement=user_requirement,
                        max_rounds=max_rounds,
                    )
                )
    return results
