"""Reject identical full-file content across distinct numbered reference documents.

The failed Item 7 candidate replaced architecture documents with generic text, and the
tell was that several distinct numbered documents ended up carrying the *same* body. A
residue scan cannot see that: every file still exists, every file is non-empty, and every
file mentions the words a keyword scan looks for. What it cannot survive is being asked
whether two documents are the same document.

The check is deliberately narrow. It compares **exact full-file bytes** between numbered
reference documents and reports every group of two or more that match. It makes no
judgement about similarity, prose quality, or staleness — a document can be as stale as
you like and still be its own document. Anything fuzzier would need a threshold, and a
threshold is a knob someone eventually turns down.

``ALLOWLIST`` exists because the recovery plan asks for one, and it is empty on purpose. A
pair may only be added with a written reason: two numbered reference documents having
byte-identical content is the incident's signature, so an entry here is a claim that the
duplication is intended, not a way to quiet the check.

Usage::

    python scripts/check_doc_distinctness.py
"""

from __future__ import annotations

import hashlib
import sys
from collections import defaultdict
from pathlib import Path

__all__ = ["ALLOWLIST", "REFERENCE_DIR", "find_identical_documents", "numbered_reference_docs"]

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = REPO_ROOT / "docs" / "architecture" / "reference"

#: Pairs of reference-document filenames whose identical content is deliberate. Empty, and
#: it should stay empty — see the module docstring before adding one.
ALLOWLIST: frozenset[tuple[str, str]] = frozenset()


def numbered_reference_docs(reference_dir: Path) -> list[Path]:
    """Every ``NN-*.md`` in ``reference_dir``, sorted by name.

    The numbering is what makes a document distinct by construction: each number is one
    subject. An unnumbered file in this directory (a README, say) is not making that claim
    and is not compared.
    """
    return sorted(
        path
        for path in reference_dir.glob("*.md")
        if path.stem[:2].isdigit() and path.stem[2:3] == "-"
    )


def find_identical_documents(reference_dir: Path) -> list[tuple[str, ...]]:
    """Groups of numbered reference documents with byte-identical content.

    Returns one sorted tuple of filenames per group of two or more, sorted between groups.
    A group whose every pair is allowlisted is omitted. Empty means every numbered
    document is its own document.
    """
    by_digest: dict[str, list[str]] = defaultdict(list)
    for path in numbered_reference_docs(reference_dir):
        by_digest[hashlib.sha256(path.read_bytes()).hexdigest()].append(path.name)

    groups = []
    for names in by_digest.values():
        if len(names) < 2:
            continue
        group = tuple(sorted(names))
        if _every_pair_allowlisted(group):
            continue
        groups.append(group)
    return sorted(groups)


def _every_pair_allowlisted(group: tuple[str, ...]) -> bool:
    return all(
        tuple(sorted((first, second))) in ALLOWLIST
        for index, first in enumerate(group)
        for second in group[index + 1 :]
    )


def main() -> int:
    groups = find_identical_documents(REFERENCE_DIR)
    if not groups:
        total = len(numbered_reference_docs(REFERENCE_DIR))
        print(f"{total} numbered reference documents checked, 0 identical-content groups")
        return 0
    print("Identical full-file content across distinct numbered reference documents:")
    for group in groups:
        print(f"  {', '.join(group)}")
    print(
        "\nEach numbered document is one subject. Identical content means one of them is not "
        "describing its own subject, which is the failed candidate's signature."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
