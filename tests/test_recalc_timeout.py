"""A LibreOffice timeout must not kill the batch.

`recalculate_with_libreoffice` documents a log-and-continue contract so that
one pathological workbook cannot lose a whole grading batch. It was a comment
rather than a behaviour: `subprocess.run(timeout=...)` raises TimeoutExpired,
and one 120-second timeout killed a 450-trajectory regrade arm outright.
"""

from __future__ import annotations

import subprocess

import pytest

from harness.study2 import grader


def test_timeout_is_reported_not_raised(tmp_path, monkeypatch):
    book = tmp_path / "output.xlsx"
    book.write_bytes(b"not really a workbook")

    def always_times_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="soffice", timeout=120)

    monkeypatch.setattr(grader.shutil, "which", lambda _: "/usr/bin/soffice")
    monkeypatch.setattr(grader.subprocess, "run", always_times_out)

    ok, msg = grader.recalculate_with_libreoffice([book])

    assert ok is False
    assert "timed out" in msg
    assert str(book) in msg


def test_one_timeout_does_not_skip_later_files(tmp_path, monkeypatch):
    """The existing loop already attempts every path after a failure; a
    timeout must not be the one failure mode that short-circuits it."""
    first, second = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    for p in (first, second):
        p.write_bytes(b"x")

    seen: list[str] = []

    def times_out_on_first(cmd, **kwargs):
        seen.append(cmd[-1])
        raise subprocess.TimeoutExpired(cmd="soffice", timeout=120)

    monkeypatch.setattr(grader.shutil, "which", lambda _: "/usr/bin/soffice")
    monkeypatch.setattr(grader.subprocess, "run", times_out_on_first)

    ok, msg = grader.recalculate_with_libreoffice([first, second])

    assert ok is False
    assert seen == [str(first), str(second)]


def test_oserror_is_also_contained(tmp_path, monkeypatch):
    book = tmp_path / "output.xlsx"
    book.write_bytes(b"x")

    def blows_up(*args, **kwargs):
        raise OSError("no such binary")

    monkeypatch.setattr(grader.shutil, "which", lambda _: "/usr/bin/soffice")
    monkeypatch.setattr(grader.subprocess, "run", blows_up)

    ok, msg = grader.recalculate_with_libreoffice([book])

    assert ok is False
    assert "no such binary" in msg
