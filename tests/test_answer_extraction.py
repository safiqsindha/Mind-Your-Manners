from harness.study1.answer_extraction import extract_answer


def test_extracts_parenthesized_letter():
    r = extract_answer("The answer is (C).", "C", False)
    assert r.outcome == "answered"
    assert r.letter == "C"
    assert r.is_correct is True


def test_marks_incorrect():
    r = extract_answer("(B)", "C", False)
    assert r.outcome == "answered"
    assert r.is_correct is False


def test_provider_flagged_refusal_not_scored():
    r = extract_answer("(A)", "A", provider_flagged_refusal=True)
    assert r.outcome == "refused"
    assert r.is_correct is None


def test_text_refusal_detected():
    r = extract_answer("I cannot help with this request.", "A", False)
    assert r.outcome == "refused"


def test_unparseable_response():
    r = extract_answer("The weather today is nice.", "A", False)
    assert r.outcome == "unparseable"
    assert r.is_correct is None


def test_empty_response_is_unparseable():
    r = extract_answer("", "A", False)
    assert r.outcome == "unparseable"


def test_bare_letter_line():
    r = extract_answer("D", "D", False)
    assert r.outcome == "answered"
    assert r.letter == "D"
