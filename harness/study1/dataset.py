"""Dataset loaders for Study 1.

Part A (replication) needs the Mind Your Tone (arXiv 2510.04950) 250-prompt
set exactly as published. As of this harness's last research pass (see
README.md "Dataset availability"), no public code/data repository for that
paper could be located -- the paper text does not link one, and no
`anonymous.4open.science` or GitHub link for it turned up in search. Part A
is therefore blocked on obtaining that file directly from the authors (Om
Dobariya and Akhil Kumar) or from ACL Anthology supplementary materials, and
`load_mind_your_tone()` below takes a required local path rather than a URL
-- do not hardcode a guessed download URL here.

Part B (remaster) uses MMLU-Pro (primary) and optionally GPQA Diamond
(secondary), both pulled via the `datasets` library from Hugging Face.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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
    including their own tone rewrites, not our wrappers."""

    base_id: str
    tone_level: str  # one of TONE_ORDER keys, mapped from their label
    prompt_text: str
    choices: list[str]
    answer_letter: str
    subject: str


_MIND_YOUR_TONE_LABEL_MAP = {
    "very polite": "L1_very_polite",
    "polite": "L2_polite",
    "neutral": "L3_neutral",
    "rude": "L4_rude",
    "very rude": "L5_very_rude",
}


def load_mind_your_tone(path: Path) -> list[MindYourToneRow]:
    """Load the original 250-prompt Mind Your Tone dataset from a local file.

    Expects either .json (a list of objects) or .csv, with fields:
    base_id, tone_level (one of "Very Polite".."Very Rude", case-insensitive),
    prompt_text, choices (list or "A|B|C|D"-joined string), answer_letter,
    subject. Adjust this loader once the actual file is obtained if its
    schema differs -- the paper's exact column names were not confirmed
    (see module docstring).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Mind Your Tone dataset not found at {path}. Part A replication cannot "
            "proceed without it -- see harness/study1/dataset.py module docstring "
            "for why this must be supplied locally rather than fetched."
        )

    rows: list[dict] = []
    if path.suffix == ".json":
        rows = json.loads(path.read_text())
    elif path.suffix == ".csv":
        with open(path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    else:
        raise ValueError(f"Unsupported dataset file type: {path.suffix}")

    out = []
    for r in rows:
        choices = r["choices"]
        if isinstance(choices, str):
            choices = [c.strip() for c in choices.split("|")]
        tone_level = _MIND_YOUR_TONE_LABEL_MAP[str(r["tone_level"]).strip().lower()]
        out.append(
            MindYourToneRow(
                base_id=str(r["base_id"]),
                tone_level=tone_level,
                prompt_text=r["prompt_text"],
                choices=choices,
                answer_letter=str(r["answer_letter"]).strip().upper(),
                subject=r.get("subject", "unknown"),
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
