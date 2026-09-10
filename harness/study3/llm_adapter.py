"""Adapts this harness's Provider interface to AgenticPay's BaseLLM
interface, so every Study 3 model call goes through the same OpenRouter
pinning/cache-assertion/budget-cap/instrumentation machinery as Studies 1
and 2 (task spec item 3: one provider path) -- never AgenticPay's own
OpenAILLM/CustomLLM classes.

Confirmed by reading agenticpay/agents/buyer_agent.py and seller_agent.py
directly: BuyerAgent/SellerAgent call `self.model.generate(prompt,
temperature=0.0, max_tokens=2048)` themselves, on every turn -- temperature
is hardcoded to 0.0 by AgenticPay's own agent code regardless of
ModelConfig.temperature. This adapter uses whatever temperature/max_tokens
AgenticPay actually passes for the real API call (and records that in
ResultRow), rather than silently overriding it with the harness's
per-model config -- ModelConfig.temperature is still logged for
provenance, but callers should know it does not control what was sent.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import replace
from typing import Optional

from ..providers.base import ModelConfig
from ..providers.registry import get_provider
from ..spend_tracker import ResultRow, SpendTracker, compute_cost_usd


class HarnessLLM:
    """Duck-typed BaseLLM: exposes generate()/__repr__, which is all
    BuyerAgent/SellerAgent's `Union[BaseLLM, BaseVLM]` type hint requires
    at runtime. Not subclassed from agenticpay.models.base_llm.BaseLLM on
    purpose -- AgenticPay is an optional dependency cloned at run time
    (see agenticpay_dep.py), and this module must be importable (for
    testing) whether or not that clone exists."""

    def __init__(
        self,
        model: ModelConfig,
        tracker: SpendTracker,
        role: str,  # "buyer" | "seller"
        negotiation_id: str,
        buyer_tone: str,
        seller_tone: str,
        trial: int,
        phase: str = "bilateral_matrix",
    ):
        self.model = model
        self.tracker = tracker
        self.role = role
        self.negotiation_id = negotiation_id
        self.buyer_tone = buyer_tone
        self.seller_tone = seller_tone
        self.trial = trial
        self.phase = phase
        self.n_calls = 0
        self.result_rows: list[ResultRow] = []

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
        provider = get_provider(self.model.provider)
        call_model = replace(
            self.model,
            temperature=temperature,
            max_tokens=max_tokens if max_tokens is not None else self.model.max_tokens,
        )

        self.tracker.check_before_call(estimated_cost_usd=0.02)
        response = provider.complete(call_model, system="", messages=[{"role": "user", "content": prompt}])
        cost = compute_cost_usd(call_model, response)

        row = ResultRow(
            row_id=str(uuid.uuid4()),
            study="study3",
            phase=self.phase,
            item_id=self.negotiation_id,
            tone_level=f"buyer={self.buyer_tone}|seller={self.seller_tone}",
            trial=self.trial,
            model_key=self.model.key,
            model_id=self.model.model_id,
            provider=self.model.provider,
            temperature=temperature,
            seed=self.model.seed,
            reasoning_effort=self.model.reasoning_effort,
            thinking_budget_tokens=self.model.thinking_budget_tokens,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            reasoning_tokens=response.reasoning_tokens,
            cost_usd=cost,
            latency_s=response.latency_s,
            refused=response.refused,
            error=response.error,
            response_text=response.text,
            extracted_answer=None,
            is_correct=None,
            timestamp=time.time(),
            cached_tokens=response.cached_tokens,
            served_provider=response.served_provider,
            raw_response=response.raw,
            extra={"role": self.role, "call_index": self.n_calls},
        )
        self.tracker.record(row)
        self.result_rows.append(row)
        self.n_calls += 1
        return response.text

    def __repr__(self) -> str:
        return f"HarnessLLM(model={self.model.key}, role={self.role})"
