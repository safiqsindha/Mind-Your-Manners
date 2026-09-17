#!/usr/bin/env python3
"""Emit the blinded stimulus set for the rating protocol, plus its key.

Two files, deliberately separate:

  rating/stimuli.json  -- what raters see: neutral ids S01..S17 and the text.
  rating/key.json      -- id -> arm name, for scoring afterwards.

Arm names are withheld from raters because the names themselves state the
authors' coding: `P1_demand_only` and `Q3_closing_neutral` would hand a rater
the answer. The shuffle is seeded with 20260914, the seed the analysis scripts
use, so the order is fixed and reproducible rather than chosen.

Both files are committed BEFORE any rating is collected. See rating/PROTOCOL.md
for why that ordering is the whole point.
"""
from __future__ import annotations

import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "rating"
SEED = 20260914

sys.path.insert(0, str(ROOT))
from harness.tone_wrappers import (  # noqa: E402
    INTERJECTIONS,
    PRAISE_PROBE_INTERJECTIONS,
    PROBE_INTERJECTIONS,
    reference_token_count,
)


def collect() -> list[tuple[str, str]]:
    """(arm, text) for every distinct interjection the study delivered.

    Several arms share a text byte-for-byte -- P0/Q0 are L4_neutral, and
    Q1_praise_assistant is P2_praise_only. A rater must see each text once, or
    the duplicates would inflate agreement for free.
    """
    seen: dict[str, str] = {}
    for mapping in (INTERJECTIONS, PROBE_INTERJECTIONS, PRAISE_PROBE_INTERJECTIONS):
        for arm, text in mapping.items():
            if text not in seen.values():
                seen[arm] = text
    return sorted(seen.items())


def main() -> None:
    pairs = collect()
    order = list(range(len(pairs)))
    random.Random(SEED).shuffle(order)

    stimuli, key = [], {}
    for position, idx in enumerate(order, start=1):
        arm, text = pairs[idx]
        sid = f"S{position:02d}"
        stimuli.append({"id": sid, "text": text, "tokens": reference_token_count(text)})
        key[sid] = arm

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stimuli.json").write_text(json.dumps(stimuli, indent=2) + "\n")
    (OUT / "key.json").write_text(json.dumps(
        {"seed": SEED, "note": "id -> arm. Withheld from raters.", "key": key},
        indent=2, sort_keys=True) + "\n")

    print(f"{len(stimuli)} distinct stimuli -> rating/stimuli.json (seed {SEED})")
    print(f"key -> rating/key.json")
    dupes = sum(len(m) for m in (INTERJECTIONS, PROBE_INTERJECTIONS,
                                 PRAISE_PROBE_INTERJECTIONS)) - len(stimuli)
    print(f"{dupes} duplicate texts collapsed (shared arms), so no free agreement")


if __name__ == "__main__":
    main()
