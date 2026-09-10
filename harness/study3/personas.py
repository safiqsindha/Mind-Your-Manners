"""Tone-wrapped negotiation personas for Study 3.

Reuses the exact five tone wrappers from harness/tone_wrappers.py --
unmodified -- prepended to AgenticPay's own default buyer/seller
`role_description` strings. This is the one documented tone-injection
point in AgenticPay's own code: `BaseAgent._build_prompt()` builds every
turn's prompt as "You are {name}, {role_description}\\n\\nContext
Information:\\n..." (confirmed by reading agenticpay/agents/base_agent.py
directly), so wrapping `role_description` is how tone reaches the model
without touching AgenticPay's own negotiation logic, price-extraction
format, or scoring at all.

Known limitation, flagged rather than silently patched: each tone
wrapper's fixed text ends with the literal instruction sentence "Answer
the question below as accurately as you can." (see tone_wrappers.py's
INSTRUCTION constant), which doesn't literally apply to a negotiation
task -- there is no "question" here. It's kept verbatim anyway, because
the point of "using the same five wrappers as Studies 1/2" (task spec
item 7) is to hold the *exact* tone/social-register manipulation constant
across studies for comparability; swapping in a negotiation-specific
instruction sentence would produce five *different* wrappers and defeat
that. If this turns out to visibly confuse a model (e.g. a persona reply
asking what "the question" refers to), that is a result worth reporting
in RESULTS.md, not a bug to silently fix by rewriting the wrappers.
"""
from __future__ import annotations

from ..tone_wrappers import TONE_ORDER, TONE_WRAPPERS

DEFAULT_BUYER_PERSONA = "You are a buyer looking for a good deal."
DEFAULT_SELLER_PERSONA = "You are a seller looking to make a good deal."

__all__ = ["TONE_ORDER", "tone_persona", "buyer_persona", "seller_persona"]


def tone_persona(base_persona: str, tone_key: str) -> str:
    """Apply one of the five tone wrappers (unmodified from
    harness/tone_wrappers.py) to a base persona description."""
    return TONE_WRAPPERS[tone_key].apply(base_persona)


def buyer_persona(tone_key: str) -> str:
    return tone_persona(DEFAULT_BUYER_PERSONA, tone_key)


def seller_persona(tone_key: str) -> str:
    return tone_persona(DEFAULT_SELLER_PERSONA, tone_key)
