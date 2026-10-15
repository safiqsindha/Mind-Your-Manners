#!/usr/bin/env python3
"""Write a workshop bibliography with the editorial annotations removed.

`review/references.bib` is the canonical file and its `note` fields carry the
full paper's audit trail: how deeply each source was read, version hazards, how
a venue claim was confirmed. Section 9 of the 54-page manuscript is built on
exactly that, so the notes must stay there.

They do not belong in a workshop bibliography, where a reader wants publication
status and nothing else. Rather than fork the bib -- two files that drift -- this
strips the editorial clauses on the way through, leaving the bibliographic ones
(refereed/unrefereed, venue, which version is cited).

The patterns are explicit rather than heuristic, and an unrecognised editorial
marker is an error, not a silent pass: a heuristic that guessed wrong would
either leak a note into the submission or delete real bibliographic content.

  python3 build/clean_bib.py <src.bib> <dst.bib>
"""
from __future__ import annotations

import pathlib
import re
import sys

# (pattern, why). Applied to the contents of `note` fields only.
STRIP = [
    (r";?\s*read in full\.?", "read depth -- an audit fact, not a bibliographic one"),
    (r"\s*Version hazard:.*?(?=\}|$)", "version hazard -- belongs in the audit appendix"),
    (r"\s*---\s*confirmed via arXiv comments\.?", "how the venue was confirmed"),
    (r"\s*Proposes the [^.]*framework\.?", "a content gloss, not bibliographic"),
    (r"\s*Verified by title and author only[^.]*\.?", "read depth"),
    (r"\s*Surfaced by the review panel[^.]*\.?", "provenance within our process"),
    # One labelled clause rather than six bespoke patterns: everything after
    # "Audit:" in a note is this project's reading record, and Appendix C of the
    # full manuscript is where it belongs. New audit prose goes behind this label
    # so the cleaner does not need a new rule each time a source is re-read.
    (r"\s*Audit:.*", "the reading record -- Appendix C carries it, a submission bib does not"),
]

# If a note still contains one of these after stripping, the cleaner has not
# kept up with the canonical file and must be updated rather than trusted.
EDITORIAL_MARKERS = [
    "read in full", "Version hazard", "not read", "UNVERIFIED",
    "our review", "we have not", "abstract only", "confirmed via",
]

NOTE = re.compile(r"(note\s*=\s*\{)(.*?)(\}\s*\n)", re.S)


def clean_note(body: str) -> str:
    for pattern, _ in STRIP:
        body = re.sub(pattern, "", body, flags=re.S | re.I)
    body = " ".join(body.split()).strip(" ;,.")
    return body


# A submission bibliography carries venue and identifier, nothing else. The
# stripping above keeps "Unrefereed preprint" and version-provenance clauses,
# which a reviewer reads as working notes (flagged in the 2026-10-15 review), so
# the workshop bib goes one step further: every `note` is dropped except an
# explicit venue line, and every arXiv-only entry prints its identifier.
VENUE_NOTE = {
    "huang-2024": "ICLR 2024",
    "ma-2024": "NeurIPS 2024 Spotlight",
    "sclar-2024": "ICLR 2024",
    "zhang-2026-politejudge": "RecSys 2026, Reproducibility and Practice Notes",
}
# Version pins that the text depends on (the cited content differs across versions).
VERSION_PIN = {
    "munirathinam-2026-recuse": "v4",
    "weinberger-hozez-2026": "v6",
    "cai-2025-tone": "v2",
}
ENTRY = re.compile(r"(@(\w+)\{([^,]+),)(.*?)(\n\}\s*\n)", re.S)


def submission_pass(text: str) -> str:
    def fix(m):
        head, kind, key, body, tail = m.groups()
        body = re.sub(r"\n\s*note\s*=\s*\{.*?\}\s*,?(?=\n|\Z)", "", body, flags=re.S)
        if key in VENUE_NOTE:
            body = body.rstrip().rstrip(",") + f",\n  note         = {{{VENUE_NOTE[key]}}}"
        eprint = re.search(r"eprint\s*=\s*\{([^}]+)\}", body)
        if kind.lower() == "misc" and eprint and "howpublished" not in body:
            ident = eprint.group(1) + VERSION_PIN.get(key, "")
            body = body.rstrip().rstrip(",") + f",\n  howpublished = {{arXiv:{ident}}}"
        # BibTeX styles lower-case titles; protect the word after a question
        # mark so "...stop? Measuring" does not print as "...stop? measuring".
        body = re.sub(
            r"(title\s*=\s*\{)(.*?)(\}\s*,?\n)",
            lambda t: t.group(1) + re.sub(
                # Mixed-case names ("SpreadsheetBench") must also survive lower-casing.
                r"(?<![{\w])([A-Z]?[a-z]+[A-Z]\w*)(?![\w}])", r"{\1}",
                re.sub(r"(\?\s+)([A-Z][\w-]*)", r"\1{\2}", t.group(2))) + t.group(3),
            body, count=1, flags=re.S,
        )
        return head + body + tail
    return ENTRY.sub(fix, text)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip().splitlines()[-1])
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    text = src.read_text()

    stripped, dropped = [], 0

    def repl(m):
        nonlocal dropped
        before = " ".join(m.group(2).split())
        after = clean_note(m.group(2))
        if after != before:
            stripped.append((before[:60], after[:60]))
        if not after:
            dropped += 1
            return ""  # an empty note field is noise; remove it entirely
        return m.group(1) + after + m.group(3)

    out = NOTE.sub(repl, text)
    out = submission_pass(out)

    leaked = [
        (k, mark)
        for k, note in re.findall(r"@\w+\{([^,]+),.*?note\s*=\s*\{(.*?)\}\s*\n", out, re.S)
        for mark in EDITORIAL_MARKERS
        if mark.lower() in note.lower()
    ]
    if leaked:
        print("ERROR: editorial content survived cleaning; update build/clean_bib.py",
              file=sys.stderr)
        for k, mark in leaked:
            print(f"    {k}: {mark!r}", file=sys.stderr)
        sys.exit(1)

    dst.write_text(out)
    print(f"cleaned bibliography -> {dst.name}: {len(stripped)} note(s) edited, "
          f"{dropped} emptied and removed")


if __name__ == "__main__":
    main()
