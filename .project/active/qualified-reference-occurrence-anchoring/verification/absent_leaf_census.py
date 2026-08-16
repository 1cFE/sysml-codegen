#!/usr/bin/env python3
"""Count one-segment reference leaves the elaborator's own element index cannot see.

``_resolve_direct_reference`` classifies a one-segment reference by its leaf's live
owner, and it reads the leaf from ``_ExactElaborator._elements``. That index holds only
declarations carrying a reload-stable ``qualified_name``. A leaf missing from it used to
fall through to the consumer-positional leaf route; it now refuses by name. This census
is the evidence for that change: it measures how many authored sites reach the branch
with a leaf the index does not hold.

It measures the whole population of the refusal, which is wider than
``corpus_compare.py``'s ledger population. The ledger rows only sites whose leaf has a
live ``PartUsage`` owner; the refusal fires before an owner can be classified at all, so
owner kind cannot be part of the question here.

Usage::

    set -a; source ../agentic-mbse/.env; set +a
    uv run python .project/active/qualified-reference-occurrence-anchoring/\
verification/absent_leaf_census.py --output <path>

Output is canonical JSON: sorted keys, repository-relative paths, no timestamps.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from corpus_compare import REPO, frozen_roots, promoted_roots  # noqa: E402

from sysml_codegen.elaboration.elaborate import (  # noqa: E402
    _blocking_model_validation_diagnostics,
    _ExactElaborator,
    _UnsupportedExpressionError,
)
from sysml_codegen.elaboration.identity import DeclarationId  # noqa: E402
from sysml_codegen.extraction.extractor import SysMLDataExtractor  # noqa: E402


def one_segment_leaves(elaborator: Any) -> list[DeclarationId]:
    """Every one-segment reference leaf the shipped resolver was asked to resolve.

    The three lanes that produce a semantic reference fact are walked with the same
    calls the resolver makes, so a leaf counted here is a leaf the branch saw.
    """
    leaves: list[DeclarationId] = []
    for pending in elaborator._pending_bindings:
        fact = pending.evidence.semantic_reference
        if fact is not None and fact.leaf is not None and len(fact.segment_element_ids) == 1:
            leaves.append(DeclarationId(fact.leaf.element_id))
    for pending in (*elaborator._pending_aliases, *elaborator._pending_expressions):
        try:
            facts = elaborator._expression_references(pending.expression, plural=False)
        except _UnsupportedExpressionError:
            continue
        for fact, _plural in facts:
            if fact.leaf is not None and len(fact.segment_element_ids) == 1:
                leaves.append(DeclarationId(fact.leaf.element_id))
    return leaves


def census_root(root: str) -> dict[str, Any]:
    result: dict[str, Any] = {"root": root}
    path = REPO / root
    extractor = SysMLDataExtractor([path])
    try:
        if not extractor.load_models():
            result["refused"] = "load_models returned false"
            return result
        definitions = extractor.extract_calculation_definitions()
        if _blocking_model_validation_diagnostics(
            extractor.model, extractor.diagnostics.validation
        ):
            result["refused"] = "model validation blocked"
            return result
        elaborator = _ExactElaborator(
            extractor.model, definitions, model_paths=[path], strict=False
        )
        elaborator.run()
    except Exception as error:  # noqa: BLE001 - a refusing root is a row, not a crash
        result["refused"] = f"{type(error).__name__}: {error}"
        return result

    leaves = one_segment_leaves(elaborator)
    absent = sorted(leaf.to_wire() for leaf in leaves if leaf not in elaborator._elements)
    result["one_segment_leaves"] = len(leaves)
    result["absent_from_element_index"] = absent
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    roots = [*frozen_roots()["roots"], *promoted_roots()]
    rows = [census_root(root) for root in roots]
    payload = {
        "roots": rows,
        "totals": {
            "roots": len(rows),
            "roots_refused": sum(1 for row in rows if "refused" in row),
            "one_segment_leaves": sum(row.get("one_segment_leaves", 0) for row in rows),
            "absent_from_element_index": sum(
                len(row.get("absent_from_element_index", ())) for row in rows
            ),
        },
    }
    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["totals"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
