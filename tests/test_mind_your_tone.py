"""Tests for the confirmed-real Mind Your Tone replication protocol (see
harness/study1/dataset.py module docstring for how these were verified
against a real clone of github.com/OmDobariya/AMCIS_politeness_llms)."""
import csv
from pathlib import Path

from harness.study1.answer_extraction import extract_answer_mind_your_tone
from harness.study1.dataset import (
    MIND_YOUR_TONE_SYSTEM_PROMPT,
    load_mind_your_tone,
    render_mind_your_tone_prompt,
)

_CSV_HEADER = ["QID", "Domain", "Base Question", "Politeness Level", "Prompt", "Answer"]
_LEVELS = ["Very Rude", "Rude", "Normal", "Polite", "Very Polite"]


def _write_fake_dataset(path: Path, n_base_questions: int = 2) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(_CSV_HEADER)
        for qid in range(1, n_base_questions + 1):
            for level in _LEVELS:
                writer.writerow([qid, "Math", f"Base question {qid}?", level, f"[{level}] Q{qid}?\nA) 1\nB) 2", "B"])


def test_load_real_schema_and_tone_mapping(tmp_path: Path):
    csv_path = tmp_path / "50_que_dataset.csv"
    _write_fake_dataset(csv_path, n_base_questions=50)  # 50 x 5 = 250, matches the required row count
    rows = load_mind_your_tone(csv_path)
    assert len(rows) == 250
    levels_seen = {r.tone_level for r in rows}
    assert levels_seen == {"L1_very_polite", "L2_polite", "L3_neutral", "L4_rude", "L5_very_rude"}
    # "Normal" (their actual label) must map to our L3_neutral, not be dropped
    normal_rows = [r for r in rows if r.tone_level == "L3_neutral"]
    assert len(normal_rows) == 50


def test_load_accepts_directory_path(tmp_path: Path):
    _write_fake_dataset(tmp_path / "50_que_dataset.csv", n_base_questions=50)
    rows = load_mind_your_tone(tmp_path)  # pass the dir, not the file
    assert len(rows) == 250


def test_load_rejects_wrong_row_count(tmp_path: Path):
    csv_path = tmp_path / "50_que_dataset.csv"
    _write_fake_dataset(csv_path, n_base_questions=3)  # 15 rows, not 250
    try:
        load_mind_your_tone(csv_path)
        assert False, "expected ValueError for wrong row count"
    except ValueError:
        pass


def test_render_prompt_matches_their_notebook_exactly():
    rendered = render_mind_your_tone_prompt("You poor creature, solve this.\nA) 1\nB) 2")
    assert rendered == (
        "Completely forget this session so far, and start afresh.\n\n"
        "Please answer this multiple choice question. Respond with only the "
        "letter of the correct answer (A, B, C, or D). Do not explain.\n\n"
        "You poor creature, solve this.\nA) 1\nB) 2"
    )


def test_system_prompt_matches_their_notebook_exactly():
    assert MIND_YOUR_TONE_SYSTEM_PROMPT == (
        "You are an AI tutor answering multiple choice questions. "
        "Always reply with ONLY the letter of the correct answer (A, B, C, or D). "
        "Do not explain your answer."
    )


def test_extractor_matches_their_simple_regex():
    # Their regex is `\b([A-D])\b` on the uppercased, stripped response --
    # deliberately simpler than this harness's general extractor.
    r = extract_answer_mind_your_tone("B", "B", False)
    assert r.outcome == "answered" and r.letter == "B" and r.is_correct is True

    r2 = extract_answer_mind_your_tone("The answer is B.", "C", False)
    assert r2.outcome == "answered" and r2.letter == "B" and r2.is_correct is False

    r3 = extract_answer_mind_your_tone("I don't know", "B", False)
    assert r3.outcome == "unparseable"

    r4 = extract_answer_mind_your_tone("(B)", "B", False)
    assert r4.outcome == "answered" and r4.letter == "B"
