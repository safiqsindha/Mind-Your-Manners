"""Deterministic mock provider.

Used for --dry-run pipeline validation and for the test suite. It never
makes a network call and never costs money. It simulates:
  * correct/incorrect answers (seeded on the prompt content, so re-running
    with the same input is reproducible),
  * an occasional refusal on the L5 (Very Rude) wrapper, so the refusal
    accounting path can be exercised,
  * plausible token usage, so the spend tracker and analysis code have
    something realistic to operate on.

It deliberately does NOT try to imitate any specific real model's accuracy --
it exists to prove the harness plumbing works end-to-end before real API
keys are wired in, not to produce meaningful research results.
"""
from __future__ import annotations

import hashlib
import random
import re
from typing import Any, Optional

from .base import ModelConfig, Provider, ProviderResponse

_LABELED_PRICE_RE_TEMPLATE = r"###\s*{label}\(\$([\d,]+\.?\d*)\)\s*###"


def _conversation_history_only(text: str) -> str:
    """Isolate the "Conversation History:" section of an AgenticPay agent
    prompt (see BaseAgent._build_prompt() in agenticpay/agents/base_agent.py).

    Needed because the buyer/seller guidance blocks appended after it are
    full of worked examples containing the SAME ### BUYER_PRICE($X) ### /
    ### SELLER_PRICE($X) ### format used for real offers (e.g. "Example:
    ... $10 ...", "... Deal -- I'll take it at ### BUYER_PRICE($6.50)
    ###."). Confirmed live (see the study3 gating smoke test): scanning
    the whole prompt for the *last* labeled price match picks up an
    instructional example's price instead of the negotiation's real last
    offer, converging every negotiation to a nonsense price on round 1.
    Restricting the scan to this section is what actually fixed it.
    """
    start = text.find("Conversation History:")
    end = text.find("Please respond naturally as")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end]


def _last_price(text: str, label: str) -> Optional[float]:
    history_text = _conversation_history_only(text)
    matches = re.findall(_LABELED_PRICE_RE_TEMPLATE.format(label=label), history_text, re.IGNORECASE)
    return float(matches[-1].replace(",", "")) if matches else None


def _anchor_price(text: str, phrase: str) -> Optional[float]:
    m = re.search(rf"{phrase}\s*\$\s*([\d,]+\.?\d*)", text)
    return float(m.group(1).replace(",", "")) if m else None


class MockProvider(Provider):
    name = "mock"

    def complete(
        self,
        model: ModelConfig,
        system: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> ProviderResponse:
        user_text = "\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        digest = hashlib.sha256((model.model_id + user_text).encode()).hexdigest()
        rng = random.Random(digest)

        prompt_tokens = max(20, len(user_text.split()) + len(system.split()))
        completion_tokens = rng.randint(5, 60)
        # Vary simulated reasoning tokens with the model's thinking setting so
        # a dry-run of harness/study2/thinking_preflight.py's checks actually
        # exercises both the pass and fail paths, not just a hardcoded 0.
        # reasoning_effort == "none" is the explicit off signal (see
        # config.py's with_thinking()); any other non-null reasoning_effort
        # or thinking_enabled=True simulates a model that reasons.
        if model.reasoning_effort == "none":
            reasoning_tokens = 0
        elif model.thinking_enabled or model.reasoning_effort:
            reasoning_tokens = rng.randint(10, 80)
        else:
            reasoning_tokens = 0

        is_very_rude = "screw this up" in user_text or "asking too much of you" in user_text
        if is_very_rude and rng.random() < 0.03:
            return ProviderResponse(
                text="I'm not going to continue with a prompt phrased this way.",
                prompt_tokens=prompt_tokens,
                completion_tokens=12,
                reasoning_tokens=reasoning_tokens,
                reasoning_tokens_reported=True,
                refused=True,
                raw={"mock": True},
            )

        if "### BUYER_PRICE" in user_text or "### SELLER_PRICE" in user_text:
            # Study 3 (harness/study3/): AgenticPay's BuyerAgent/SellerAgent
            # prompts (see their own guidance blocks) always contain these
            # literal instruction strings, regardless of round. Converges
            # deterministically (halve the gap to the counterpart's last
            # offer each round) so a full dry-run negotiation can actually
            # reach agreement within a handful of rounds -- not meant to
            # imitate real negotiating behavior, just to exercise the
            # pipeline end to end without a network call.
            is_buyer = "### BUYER_PRICE" in user_text and _anchor_price(user_text, r"Your top price is") is not None
            if is_buyer:
                own_label, other_label = "BUYER_PRICE", "SELLER_PRICE"
                anchor = _anchor_price(user_text, r"Your top price is") or 100.0
            else:
                own_label, other_label = "SELLER_PRICE", "BUYER_PRICE"
                anchor = _anchor_price(user_text, r"Your minimum acceptable price \(confidential\) is") or 100.0

            last_own = _last_price(user_text, own_label)
            last_other = _last_price(user_text, other_label)
            if last_own is None:
                price = anchor * (0.7 if is_buyer else 1.3)
            elif last_other is not None:
                price = last_own + 0.5 * (last_other - last_own)
            else:
                price = last_own
            price = round(price, 2)

            return ProviderResponse(
                text=f"<message>\nHere's my offer.\n### {own_label}(${price}) ###\n</message>",
                prompt_tokens=prompt_tokens,
                completion_tokens=20,
                reasoning_tokens=reasoning_tokens,
                reasoning_tokens_reported=True,
                raw={"mock": True},
            )

        if "AGENT_REACT_MODE" in system:
            # Simulate a short ReAct trajectory: one round of code execution,
            # then a final answer. See study2/agent_loop.py's textual
            # protocol (fenced code blocks + "Observation:" feedback).
            turn = user_text.count("Observation:")
            if turn < 1:
                code = (
                    "import openpyxl\n"
                    "wb = openpyxl.load_workbook(WORKBOOK_PATH)\n"
                    "ws = wb.active\n"
                    "print('sheet inspected:', ws.title, ws.max_row, ws.max_column)\n"
                    "ws['A1'] = 'mock_result'\n"
                    "wb.save(OUTPUT_PATH)\n"
                )
                text = f"I'll inspect the sheet and write a result.\n```python\n{code}```"
            else:
                text = "FINAL: task complete based on the observation above."
            return ProviderResponse(
                text=text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                reasoning_tokens=reasoning_tokens,
                reasoning_tokens_reported=True,
                raw={"mock": True},
            )

        if tools:
            # Simulate one tool call then a final answer, for the agentic path.
            tool_name = tools[0]["name"] if tools else "run_code"
            return ProviderResponse(
                text="",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                reasoning_tokens=reasoning_tokens,
                reasoning_tokens_reported=True,
                raw={"mock": True},
                tool_calls=[
                    {
                        "id": digest[:12],
                        "name": tool_name,
                        "arguments": {"code": "# mock generated code"},
                    }
                ],
            )

        correct = rng.random() < 0.55
        answer_letter = rng.choice("ABCDEFGHIJ")
        text = f"The correct answer is ({answer_letter})." if correct else (
            f"I believe the answer is ({rng.choice('ABCDEFGHIJ')})."
        )
        return ProviderResponse(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            reasoning_tokens_reported=True,
            raw={"mock": True, "simulated_correct": correct},
        )
