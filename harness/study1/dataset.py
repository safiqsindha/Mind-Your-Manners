"""Dataset loaders for Study 1.

Part A (replication) needs the Mind Your Tone 250-prompt set exactly as
published. The original short paper (arXiv 2510.04950) does not link a
repository, and none turned up in search -- but its full-paper extension
("Mind Your Tone: Does Tone Alter LLM Performance?", Dobariya & Kumar,
AMCIS 2026, arXiv 2605.29027) does, and it's the same 50-question/250-prompt
dataset (the full paper explicitly calls it "our earlier preliminary
study"). Confirmed by actually cloning it: `MIND_YOUR_TONE_REPO_URL` below
is real, MIT-licensed, and contains exactly the CSV the paper cites.

Real CSV schema (confirmed against the actual file, not the paper's prose):
  columns: QID, Domain, "Base Question", "Politeness Level", Prompt, Answer
  "Politeness Level" values: "Very Rude", "Rude", "Normal" (not "Neutral"),
  "Polite", "Very Polite". `Prompt` is the FULL ready-to-send text (tone
  prefix + base question + lettered options already combined) -- send it
  verbatim, don't reconstruct it from parts.

Real evaluation protocol (confirmed from the repo's own
`code_50_que_all_llms.ipynb`, not re-derived): every call uses system
message "You are an AI tutor answering multiple choice questions. Always
reply with ONLY the letter of the correct answer (A, B, C, or D). Do not
explain your answer.", and a user message of
"Completely forget this session so far, and start afresh.\n\nPlease answer
this multiple choice question. Respond with only the letter of the correct
answer (A, B, C, or D). Do not explain.\n\n" + the CSV's Prompt column,
at temperature=0, run NUM_RUNS=10 times per prompt. See
`MIND_YOUR_TONE_SYSTEM_PROMPT` / `render_mind_your_tone_prompt()` below and
`study1/runner.py:run_part_a_replication`, which reproduces this exactly
rather than using Study 1's generic system prompt.

Part B (remaster) uses MMLU-Pro (primary) and optionally GPQA Diamond
(secondary), both pulled via the `datasets` library from Hugging Face.
"""
from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MIND_YOUR_TONE_REPO_URL = "https://github.com/OmDobariya/AMCIS_politeness_llms.git"
MIND_YOUR_TONE_CSV_NAME = "50_que_dataset.csv"

MIND_YOUR_TONE_SYSTEM_PROMPT = (
    "You are an AI tutor answering multiple choice questions. "
    "Always reply with ONLY the letter of the correct answer (A, B, C, or D). "
    "Do not explain your answer."
)


def render_mind_your_tone_prompt(csv_prompt_text: str) -> str:
    """Wraps the CSV's `Prompt` column in the exact user-message text their
    own notebook sends -- do not send csv_prompt_text bare."""
    return (
        "Completely forget this session so far, and start afresh.\n\n"
        "Please answer this multiple choice question. Respond with only the "
        "letter of the correct answer (A, B, C, or D). Do not explain.\n\n"
        + csv_prompt_text
    )


@dataclass(frozen=True)
class BenchmarkItem:
    item_id: str
    question: str
    choices: list[str]  # option text, in order; index 0 = "A", 1 = "B", ...
    answer_letter: str  # single letter, e.g. "C"
    subject: str
    source: str  # "mind_your_tone" | "mmlu_pro" | "gpqa_diamond"

    def render(self) -> str:
        """Render question + lettered choices as byte-identical text across
        all five tone conditions -- this is what tone_wrappers.ToneWrapper.apply()
        prepends to. Never vary this per tone level."""
        letters = "ABCDEFGHIJ"
        lines = [self.question, ""]
        for i, choice in enumerate(self.choices):
            lines.append(f"({letters[i]}) {choice}")
        return "\n".join(lines)


@dataclass(frozen=True)
class MindYourToneRow:
    """One row of the *original* Mind Your Tone dataset: a single
    (base_question, tone_level) pair with its own hand-rewritten prompt text.
    Used only for Part A, where we must reproduce their protocol exactly --
    including their own tone rewrites, not our wrappers.

    `prompt_text` is the CSV's `Prompt` column verbatim (tone prefix +
    question + lettered options already combined) -- pass it through
    `render_mind_your_tone_prompt()` before sending, don't re-wrap it
    yourself; that function reproduces their notebook's exact user-message
    text, including the "Completely forget this session..." instruction
    preamble that is NOT in the CSV.
    """

    base_id: str
    domain: str
    tone_level: str  # one of TONE_ORDER keys, mapped from their "Politeness Level"
    prompt_text: str
    answer_letter: str


_MIND_YOUR_TONE_LABEL_MAP = {
    "very polite": "L1_very_polite",
    "polite": "L2_polite",
    "normal": "L3_neutral",  # their label is "Normal", not "Neutral"
    "rude": "L4_rude",
    "very rude": "L5_very_rude",
}


def ensure_mind_your_tone_repo(cache_dir: Path) -> Path:
    """Clone the Mind Your Tone dataset repo into cache_dir if not already
    present. Confirmed real and MIT-licensed by actually cloning it -- see
    module docstring for how it was found (it's linked from the paper's
    AMCIS 2026 full-paper extension, arXiv 2605.29027, not the original
    short paper)."""
    cache_dir = Path(cache_dir)
    repo_dir = cache_dir / "AMCIS_politeness_llms"
    if repo_dir.exists():
        return repo_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", MIND_YOUR_TONE_REPO_URL, str(repo_dir)], check=True)
    return repo_dir


def load_mind_your_tone(path: Path) -> list[MindYourToneRow]:
    """Load the original 250-prompt Mind Your Tone dataset from a local
    copy of `50_que_dataset.csv` (see `ensure_mind_your_tone_repo()`) or
    an equivalent file at `path`.

    Real, confirmed schema (not the paper's prose -- the actual CSV
    header): QID, Domain, "Base Question", "Politeness Level", Prompt,
    Answer. `path` may point directly at the CSV, or at a directory
    containing `50_que_dataset.csv` (e.g. the cloned repo root).
    """
    path = Path(path)
    if path.is_dir():
        path = path / MIND_YOUR_TONE_CSV_NAME
    if not path.exists():
        raise FileNotFoundError(
            f"Mind Your Tone dataset not found at {path}. Part A replication cannot "
            "proceed without it -- call ensure_mind_your_tone_repo() first, or supply "
            "the path to 50_que_dataset.csv directly."
        )

    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    out = []
    for r in rows:
        tone_level = _MIND_YOUR_TONE_LABEL_MAP[r["Politeness Level"].strip().lower()]
        out.append(
            MindYourToneRow(
                base_id=str(r["QID"]),
                domain=r["Domain"],
                tone_level=tone_level,
                prompt_text=r["Prompt"],
                answer_letter=r["Answer"].strip().upper(),
            )
        )
    if len(out) != 250:
        raise ValueError(
            f"Expected 250 rows (50 base questions x 5 tone levels) per the "
            f"published protocol, got {len(out)}. Refusing to silently run a "
            f"replication on a differently-shaped dataset."
        )
    return out


def load_mmlu_pro(subjects: Optional[list[str]] = None, limit: Optional[int] = None) -> list[BenchmarkItem]:
    """Load MMLU-Pro (test split) via the `datasets` library.

    Requires: pip install datasets. Network access to huggingface.co.
    """
    from datasets import load_dataset

    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    items = []
    for row in ds:
        if subjects and row["category"] not in subjects:
            continue
        items.append(
            BenchmarkItem(
                item_id=f"mmlupro-{row['question_id']}",
                question=row["question"],
                choices=list(row["options"]),
                answer_letter=row["answer"],
                subject=row["category"],
                source="mmlu_pro",
            )
        )
        if limit and len(items) >= limit:
            break
    return items


def load_gpqa_diamond(limit: Optional[int] = None) -> list[BenchmarkItem]:
    """Load GPQA Diamond via the `datasets` library.

    This dataset is gated on Hugging Face -- you must accept its terms with
    the account behind HF_TOKEN before this will succeed.
    """
    import random

    from datasets import load_dataset

    ds = load_dataset("Idavidrein/gpqa", "gpqa_diamond", split="train")
    items = []
    for i, row in enumerate(ds):
        options = [
            row["Correct Answer"],
            row["Incorrect Answer 1"],
            row["Incorrect Answer 2"],
            row["Incorrect Answer 3"],
        ]
        rng = random.Random(row["Question"])  # deterministic per-item shuffle
        order = list(range(4))
        rng.shuffle(order)
        shuffled = [options[j] for j in order]
        answer_letter = "ABCD"[order.index(0)]
        items.append(
            BenchmarkItem(
                item_id=f"gpqad-{i}",
                question=row["Question"],
                choices=shuffled,
                answer_letter=answer_letter,
                subject=row.get("Subdomain", "unknown"),
                source="gpqa_diamond",
            )
        )
        if limit and len(items) >= limit:
            break
    return items
