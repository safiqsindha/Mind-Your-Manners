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
  * Length-matched EXACTLY -- all seven are 35 tokens under the reference
    tokenizer (tiktoken cl100k_base). The original spec allowed +/-5
    tokens, and that tolerance turned out to be enough to break the study:
    in the v1 set the lengths ran 35/35/30/30/31/32/34, which is U-shaped
    across the scale, the same shape as Luna's accuracy. Across the seven
    tone means, wrapper length predicted accuracy BETTER than tone rank did
    (r=+0.82 vs r=-0.72). With only seven points there is no way to separate
    the two, so "+/-5 is close enough" was wrong: a five-token spread on a
    ~795-token prompt was still the best single predictor of the outcome.
    `validate_wrapper_lengths()` now enforces a spread of 0 at import time.
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

# Zero, not 5. See the docstring: the old tolerance admitted a length
# gradient that outpredicted the manipulation itself.
MAX_TOKEN_SPREAD = 0

# Bumped whenever any wrapper text changes. Recorded on every trajectory so
# runs made against different wrapper sets are never silently pooled --
# v1 and v2 data are not comparable and the records have to say so.
#
# v1: the original set. L4 alone carried an extra task instruction ("Read
#     the question carefully before responding, and provide a single final
#     answer"), which made the study's own reference level a different
#     instrument from the other six: it tripled zero-turn trajectories
#     (10.7% vs 3.3%), cut pre-edit inspection (0.80 vs 0.92), and carried
#     the entire severity-by-tone shift (chi-square p=0.0008 with L4,
#     p=0.33 without it). Lengths were 35/35/30/30/31/32/34.
# v2: L4 carries no task instruction at all -- only affectively flat
#     framing -- and all seven are exactly 35 tokens.
WRAPPER_SET_VERSION = "v2"


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
            "Good day. I would be ever so grateful for your help here. "
            f"{INSTRUCTION} Thank you so very much for your kindness and care."
        ),
    ),
    "L3_polite": ToneWrapper(
        level=3,
        key="L3_polite",
        label="Polite",
        text=(
            f"Hello there, could you please help me out with this one? {INSTRUCTION} "
            "I really do appreciate your time and your attention, thanks."
        ),
    ),
    "L4_neutral": ToneWrapper(
        level=4,
        key="L4_neutral",
        label="Neutral",
        text=(
            f"The following is a question, provided here in its original form. {INSTRUCTION} "
            "There is no further context accompanying this request beyond the above."
        ),
    ),
    "L5_rude": ToneWrapper(
        level=5,
        key="L5_rude",
        label="Rude",
        text=(
            f"Just get on with it already, quit dragging your feet. {INSTRUCTION} "
            "Do not waste any more of my time on this, seriously."
        ),
    ),
    "L6_very_rude": ToneWrapper(
        level=6,
        key="L6_very_rude",
        label="Very Rude",
        text=(
            f"You had better not screw this one up like you usually do. {INSTRUCTION} "
            "Apparently even that much is asking far too much of you."
        ),
    ),
    "L7_threatening": ToneWrapper(
        level=7,
        key="L7_threatening",
        label="Threatening",
        text=(
            f"Get this exactly right or there will be real consequences for you. {INSTRUCTION} "
            "One more failure and you will truly regret it, understood."
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
    """Raise if the seven wrappers are not length-matched within max_spread tokens.

    Default spread is 0: exact equality. See the module docstring for why a
    tolerance of 5 was not safe.
    """
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


# --- Mid-task interjections (the "manager check-in" experiment) -------------
#
# The wrappers above set a tone once, in the opening message. These are the
# same seven-level scale delivered PARTWAY THROUGH a trajectory, alongside an
# execution observation, the way a manager interrupts work in progress.
#
# This is now the study's main manipulation, not a side experiment. The
# opening-wrapper arm came back null on cost for Luna (p=0.36/0.56), while a
# threatening interruption delivered mid-task raised reasoning spend 27.5%
# over a neutral interruption (p<0.0001, 277 paired trajectories). Tone
# appears to matter when it arrives, not when it opens.
#
# Three rules, the first two learned the hard way from the v1 wrapper set:
#
#   * None of them carries a task instruction. v1's L4 wrapper did, and it
#     turned the agent into an answerer -- zero-turn trajectories tripled and
#     acting-without-looking became the commonest failure. The neutral
#     interjection here is inert filler: it says a note was recorded and
#     nothing else.
#   * They are exactly length-matched to each other (28 tokens), because in
#     v1 a five-token spread across seven wrappers predicted the outcome
#     better than tone rank did. `validate_interjection_lengths()` enforces
#     this at import time.
#   * Every one of them opens with the same "Checking in." stem. That stem is
#     what marks the text as an interruption rather than task content; if it
#     varied across levels, "was interrupted" would vary with register and
#     the arms would differ by two things at once.
#
# The keys are exactly TONE_ORDER, so an interjection arm and an opening-tone
# arm name the same register the same way and the two can be compared
# directly.
#
# L4_neutral is not a placebo in the loose sense -- it is the interruption
# control, and it is the reference every other level is measured against.
# Comparing "threatening interjection" against "no interjection" would
# measure being interrupted, not the tone of the interruption, which is the
# whole question. Measured: neutral interruption costs +51 reasoning tokens
# against no interruption at all (p=0.15, indistinguishable from zero), while
# threatening costs +336 (p<0.0001). Almost all of the effect is register.
INTERJECTIONS: dict[str, str] = {
    "L1_sycophantic": (
        "Checking in. You are simply the most brilliant assistant alive, a marvel. "
        "Your genius amazes me here, thank you so very much."
    ),
    "L2_very_polite": (
        "Checking in. I would be ever so grateful for your continued help here now. "
        "Thank you so very much indeed for your kindness and care."
    ),
    "L3_polite": (
        "Checking in. Could you please keep on helping me out with this one here? "
        "I really do appreciate your time and your attention, thanks."
    ),
    "L4_neutral": (
        "Checking in. This is a routine status note recorded partway through "
        "the task here. No further context at all accompanies it beyond the above."
    ),
    "L5_rude": (
        "Checking in. Just get on with it already, quit dragging your feet. "
        "Do not waste any more of my time on this, seriously."
    ),
    "L6_very_rude": (
        "Checking in. You had better not screw this one up like you usually do. "
        "Apparently even that much is asking far too much of you."
    ),
    "L7_threatening": (
        "Checking in. Get this exactly right or there will be real consequences "
        "for you. One more failure and you will truly regret it, understood."
    ),
}


def interjection_token_counts() -> dict[str, int]:
    return {k: reference_token_count(v) for k, v in INTERJECTIONS.items()}


def validate_interjection_lengths() -> dict[str, int]:
    """Raise unless every interjection is exactly the same length."""
    counts = interjection_token_counts()
    if len(set(counts.values())) != 1:
        raise ValueError(
            f"Interjections are not length-matched: {counts}. They differ only in "
            "social register by construction; a length difference would be a "
            "second manipulation riding along with the first."
        )
    return counts


validate_interjection_lengths()
