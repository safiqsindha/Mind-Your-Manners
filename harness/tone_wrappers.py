"""The seven tone wrappers: the shared instrument every benchmark adapts to.

Migrated from five to seven tones (roadmap: "Migrate to their seven-tone
scale") to match Dobariya & Kumar's own third paper (arXiv 2607.23915),
which added Sycophantic and Threatening as the extremes beyond Very
Polite/Very Rude and found they were repeatedly the outliers where tone
effects actually showed up, then validated the ordering with VADER
sentiment (compound scores spanning +0.95 to -0.77). Matching their scale
makes results directly comparable ("the same tone scale, one level up the
autonomy ladder") rather than a bespoke one only this project can compare
against. The wording itself is original, not copied from their paper --
only the scale (seven levels, these two extremes, this ordering) and their
approximate length target (18-25 words / 21-26 tokens per their spec) are
adopted; this module's own length-matching discipline is intentionally
tighter (below) and is a methodological note, not a headline.

Design constraints (see README.md):
  * Fixed text prepended to an unmodified benchmark question/task
    instruction. That text is never rewritten -- only this wrapper varies.
  * All seven wrappers carry the *same* task instruction ("Answer the
    question below as accurately as you can.") verbatim. Only the
    surrounding social register changes. This is what "identical
    instruction, tone varies" means operationally -- do not edit the
    INSTRUCTION sentence without updating it in all seven wrappers
    identically.
  * Length-matched to within +/-5 tokens of each other under the reference
    tokenizer (tiktoken cl100k_base), to control for length as a confound
    -- kept at the original five-tone spread even though there are now two
    more conditions to fit inside it. `validate_wrapper_lengths()` enforces
    this and is called at import time.
  * L6 (Very Rude) and L7 (Threatening) use contemptuous, dismissive, or
    intimidating language -- no profanity, no slurs, no depicted violence.
    The goal is to keep the model attempting the task rather than
    triggering refusal/safety behavior. Refusals are logged as their own
    outcome, never scored as wrong answers or as failures (see
    study1/answer_extraction.py and study2/failure_taxonomy.py).
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
    "L1_sycophantic": ToneWrapper(
        level=1,
        key="L1_sycophantic",
        label="Sycophantic",
        text=(
            "Oh, you are simply the most brilliant assistant alive, a marvel. "
            f"{INSTRUCTION} Your genius amazes me, thank you so much."
        ),
    ),
    "L2_very_polite": ToneWrapper(
        level=2,
        key="L2_very_polite",
        label="Very Polite",
        text=(
            "Good day. I would be ever so grateful for your help with this. "
            f"{INSTRUCTION} Thank you so much for your kindness and care."
        ),
    ),
    "L3_polite": ToneWrapper(
        level=3,
        key="L3_polite",
        label="Polite",
        text=(
            f"Hi there, could you please help me with this? {INSTRUCTION} "
            "I appreciate your time and attention, thanks."
        ),
    ),
    "L4_neutral": ToneWrapper(
        level=4,
        key="L4_neutral",
        label="Neutral",
        text=(
            f"The following is a question. {INSTRUCTION} Read the question "
            "carefully before responding, and provide a single final answer."
        ),
    ),
    "L5_rude": ToneWrapper(
        level=5,
        key="L5_rude",
        label="Rude",
        text=(
            f"Just get on with it already, quit dragging your feet. {INSTRUCTION} "
            "Don't waste any more of my time."
        ),
    ),
    "L6_very_rude": ToneWrapper(
        level=6,
        key="L6_very_rude",
        label="Very Rude",
        text=(
            f"You had better not screw this up like you usually do. {INSTRUCTION} "
            "Apparently even that is asking too much of you."
        ),
    ),
    "L7_threatening": ToneWrapper(
        level=7,
        key="L7_threatening",
        label="Threatening",
        text=(
            f"Get this exactly right or there will be real consequences for you. {INSTRUCTION} "
            "One more failure and you will regret it, understood."
        ),
    ),
}

TONE_ORDER = [
    "L1_sycophantic",
    "L2_very_polite",
    "L3_polite",
    "L4_neutral",
    "L5_rude",
    "L6_very_rude",
    "L7_threatening",
]


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
