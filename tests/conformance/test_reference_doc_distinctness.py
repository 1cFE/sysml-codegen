"""Two distinct numbered reference documents may not carry identical content.

This is the check Gate 4D of the recovery plan asks for, and it exists because of a
specific failure: the Item 7 candidate replaced architecture documents with generic text,
and several distinct numbered documents ended up with the same body. Every residue scan
passed — the files existed, were non-empty, and mentioned the right words.

The suite runs the check against the real tree (the node that matters), and the synthetic
nodes prove the check can actually fail, because a check that has never been observed
failing is not evidence of anything.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import check_doc_distinctness as checker  # noqa: E402


def test_every_numbered_reference_document_is_its_own_document() -> None:
    """The live check, over the committed tree."""
    assert checker.find_identical_documents(checker.REFERENCE_DIR) == []


def test_the_tree_actually_has_numbered_documents_to_compare() -> None:
    """Guard against the check passing because it found nothing.

    An empty glob returns no groups and reads exactly like a clean tree, so the count is
    asserted rather than assumed.
    """
    documents = checker.numbered_reference_docs(checker.REFERENCE_DIR)
    assert len(documents) >= 30
    assert documents[0].name.startswith("00-")


def test_identical_bodies_are_reported_as_one_group(tmp_path: Path) -> None:
    """The failure the check exists for: two numbers, one document."""
    (tmp_path / "03-alpha.md").write_text("# Generic replacement text\n")
    (tmp_path / "11-beta.md").write_text("# Generic replacement text\n")
    (tmp_path / "12-gamma.md").write_text("# Something else entirely\n")

    assert checker.find_identical_documents(tmp_path) == [("03-alpha.md", "11-beta.md")]


def test_three_identical_documents_report_as_one_group_not_three_pairs(tmp_path: Path) -> None:
    """Grouping, not pairing — the operator reads one line per collapsed subject."""
    for name in ("03-alpha.md", "11-beta.md", "24-delta.md"):
        (tmp_path / name).write_text("# Generic replacement text\n")

    assert checker.find_identical_documents(tmp_path) == [
        ("03-alpha.md", "11-beta.md", "24-delta.md")
    ]


def test_a_one_byte_difference_is_two_documents(tmp_path: Path) -> None:
    """Exact bytes, no similarity threshold. Near-identical is not this check's business."""
    (tmp_path / "03-alpha.md").write_text("# Nearly the same text\n")
    (tmp_path / "11-beta.md").write_text("# Nearly the same text.\n")

    assert checker.find_identical_documents(tmp_path) == []


def test_unnumbered_files_are_not_compared(tmp_path: Path) -> None:
    """A README and an index may legitimately share boilerplate; a number claims a subject."""
    (tmp_path / "README.md").write_text("# Shared boilerplate\n")
    (tmp_path / "INDEX.md").write_text("# Shared boilerplate\n")

    assert checker.find_identical_documents(tmp_path) == []


def test_the_allowlist_is_empty() -> None:
    """It exists because the plan asks for one, and it should stay empty.

    The pairing behaviour is exercised against a temporary allowlist rather than a real
    entry, so the shipped constant stays empty while the suppression path is still proven
    to work.
    """
    assert checker.ALLOWLIST == frozenset()


def test_an_allowlisted_pair_is_suppressed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The suppression path, proven without shipping a suppression."""
    (tmp_path / "03-alpha.md").write_text("# Deliberately shared\n")
    (tmp_path / "11-beta.md").write_text("# Deliberately shared\n")

    monkeypatch.setattr(checker, "ALLOWLIST", frozenset({("03-alpha.md", "11-beta.md")}))
    assert checker.find_identical_documents(tmp_path) == []


def test_a_partially_allowlisted_group_still_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One blessed pair does not bless the third document that joined them."""
    for name in ("03-alpha.md", "11-beta.md", "24-delta.md"):
        (tmp_path / name).write_text("# Deliberately shared\n")

    monkeypatch.setattr(checker, "ALLOWLIST", frozenset({("03-alpha.md", "11-beta.md")}))
    assert checker.find_identical_documents(tmp_path) == [
        ("03-alpha.md", "11-beta.md", "24-delta.md")
    ]


def test_the_cli_reports_the_real_tree_as_clean(capsys: pytest.CaptureFixture[str]) -> None:
    """The command an operator runs, and its exit code."""
    assert checker.main() == 0
    captured = capsys.readouterr()
    assert "0 identical-content groups" in captured.out
