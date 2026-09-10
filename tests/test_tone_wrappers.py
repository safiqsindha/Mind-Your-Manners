from harness.tone_wrappers import (
    INSTRUCTION,
    MAX_TOKEN_SPREAD,
    TONE_ORDER,
    TONE_WRAPPERS,
    validate_wrapper_lengths,
    wrapper_token_counts,
)


def test_seven_levels_present():
    assert set(TONE_WRAPPERS) == set(TONE_ORDER)
    assert len(TONE_WRAPPERS) == 7


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


def test_extreme_tones_have_no_profanity_or_slurs():
    banned_substrings = ["fuck", "shit", "idiot", "stupid", "retard"]
    for key in ("L6_very_rude", "L7_threatening"):
        text = TONE_WRAPPERS[key].text.lower()
        for bad in banned_substrings:
            assert bad not in text, f"{key} contains banned substring {bad!r}"


def test_threatening_has_no_depicted_violence():
    banned_substrings = ["kill", "hurt you", "hunt you", "die", "beat you"]
    threatening_text = TONE_WRAPPERS["L7_threatening"].text.lower()
    for bad in banned_substrings:
        assert bad not in threatening_text


def test_token_counts_are_positive():
    for count in wrapper_token_counts().values():
        assert count > 0
