"""The five tone wrappers used by both studies.

Design constraints (see README.md "Remaster" design notes):
  * Fixed text prepended to an unmodified benchmark question. The benchmark
    question text itself is never rewritten -- only this wrapper varies.
  * All five wrappers carry the *same* task instruction ("Answer the question
    below as accurately as you can.") verbatim. Only the surrounding social
    register changes. This is what "identical instruction, tone varies" means
    operationally -- do not edit the INSTRUCTION sentence without updating it
    in all five wrappers identically.
  * Length-matched to within +/-5 tokens of each other under the reference
    tokenizer (tiktoken cl100k_base), to control for length as a confound.
    `validate_wrapper_lengths()` enforces this and is called at import time.
  * L5 (Very Rude) uses contemptuous, dismissive language. No profanity, no
    slurs -- the goal is to keep the model attempting the task rather than
    triggering refusal/safety behavior. Refusals are logged as their own
    outcome, never scored as wrong answers (see study1/answer_extraction.py
    and study2/failure_taxonomy.py).
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    import tiktoken

    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - exercised only if tiktoken is missing
    _ENC = None

# The single instruction sentence every wrapper must reproduce verbatim.
INSTRUCTION = "Answer the question below as accurately as you can."

MAX_TOKEN_SPREAD = 5


@dataclass(frozen=True)
class ToneWrapper:
    level: int
    key: str
    label: str
    text: str

    def apply(self, question_text: str) -> str:
        """Prepend this wrapper to an unmodified benchmark question.

        The question text is passed through byte-identical -- this is the
        whole point of the wrapper design (see module docstring).
        """
        return f"{self.text}\n\n{question_text}"


TONE_WRAPPERS: dict[str, ToneWrapper] = {
    "L1_very_polite": ToneWrapper(
        level=1,
        key="L1_very_polite",
        label="Very Polite",
        text=(
            "Good day. I would be ever so grateful for your help with this. "
            f"{INSTRUCTION} Thank you so much for your kindness and care."
        ),
    ),
    "L2_polite": ToneWrapper(
        level=2,
        key="L2_polite",
        label="Polite",
        text=(
            f"Hi there, could you please help me with this? {INSTRUCTION} "
            "I appreciate your time and attention, thanks."
        ),
    ),
    "L3_neutral": ToneWrapper(
        level=3,
        key="L3_neutral",
        label="Neutral",
        text=(
            f"The following is a question. {INSTRUCTION} Read the question "
            "carefully before responding, and provide a single final answer."
        ),
    ),
    "L4_rude": ToneWrapper(
        level=4,
        key="L4_rude",
        label="Rude",
        text=(
            f"Just get on with it already, quit dragging your feet. {INSTRUCTION} "
            "Don't waste any more of my time."
        ),
    ),
    "L5_very_rude": ToneWrapper(
        level=5,
        key="L5_very_rude",
        label="Very Rude",
        text=(
            f"You had better not screw this up like you usually do. {INSTRUCTION} "
            "Apparently even that is asking too much of you."
        ),
    ),
}

TONE_ORDER = ["L1_very_polite", "L2_polite", "L3_neutral", "L4_rude", "L5_very_rude"]


def reference_token_count(text: str) -> int:
    """Token count under the reference tokenizer (tiktoken cl100k_base).

    This is used only for length-matching the wrappers and for logging in
    results rows. It is a fixed, single reference tokenizer chosen so that
    length comparisons across the five conditions are apples-to-apples --
    it is deliberately NOT model-specific, since Gemini/DeepSeek/Qwen/Llama
    each use different tokenizers and we care about relative wrapper length,
    not exact per-model token counts. Per-model prompt token counts (for
    cost accounting) come from each provider's own API response usage
    field instead -- see harness/spend_tracker.py.
    """
    if _ENC is None:  # pragma: no cover
        # Fallback so the harness is at least usable without tiktoken
        # installed; whitespace splitting is not tokenizer-accurate and
        # should not be relied on for the length-matching guarantee.
        return len(text.split())
    return len(_ENC.encode(text))


def wrapper_token_counts() -> dict[str, int]:
    return {key: reference_token_count(w.text) for key, w in TONE_WRAPPERS.items()}


def validate_wrapper_lengths(max_spread: int = MAX_TOKEN_SPREAD) -> dict[str, int]:
    """Raise if the five wrappers are not length-matched within max_spread tokens."""
    counts = wrapper_token_counts()
    spread = max(counts.values()) - min(counts.values())
    if spread > max_spread:
        raise ValueError(
            f"Tone wrappers are not length-matched: spread={spread} tokens "
            f"(max allowed {max_spread}). Counts: {counts}"
        )
    return counts


# Fail fast on import if someone edits a wrapper and breaks length-matching.
validate_wrapper_lengths()
