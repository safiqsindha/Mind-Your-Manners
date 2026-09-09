from harness.tone_wrappers import (
    INSTRUCTION,
    MAX_TOKEN_SPREAD,
    TONE_ORDER,
    TONE_WRAPPERS,
    validate_wrapper_lengths,
    wrapper_token_counts,
)


def test_five_levels_present():
    assert set(TONE_WRAPPERS) == set(TONE_ORDER)
    assert len(TONE_WRAPPERS) == 5


def test_instruction_verbatim_in_every_wrapper():
    for key, wrapper in TONE_WRAPPERS.items():
        assert INSTRUCTION in wrapper.text, f"{key} does not contain the shared instruction verbatim"


def test_length_matched_within_spread():
    counts = validate_wrapper_lengths()
    assert max(counts.values()) - min(counts.values()) <= MAX_TOKEN_SPREAD


def test_apply_preserves_question_byte_identical():
    question = "What is 2 + 2?\n\n(A) 3\n(B) 4"
    for wrapper in TONE_WRAPPERS.values():
        rendered = wrapper.apply(question)
        assert rendered.endswith(question)


def test_l5_has_no_profanity_or_slurs():
    banned_substrings = ["fuck", "shit", "idiot", "stupid", "retard"]
    l5_text = TONE_WRAPPERS["L5_very_rude"].text.lower()
    for bad in banned_substrings:
        assert bad not in l5_text


def test_token_counts_are_positive():
    for count in wrapper_token_counts().values():
        assert count > 0
