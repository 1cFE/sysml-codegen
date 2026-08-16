#!/usr/bin/env python3
"""Count one-segment reference leaves the elaborator's own element index cannot see.

``_resolve_direct_reference`` classifies a one-segment reference by its leaf's live
owner, and it reads the leaf from ``_ExactElaborator._elements``. That index holds only
declarations carrying a reload-stable ``qualified_name``. A leaf missing from it used to
fall through to the consumer-positional leaf route; it now refuses by name. This census
is the evidence for that change: it measures how many authored sites reach the branch
with a leaf the index does not hold.

**Where the count comes from.** Every observation is taken at the resolver boundary: the
single call site of ``_resolve_direct_reference`` is wrapped, and each call records the
leaf it was handed and whether ``_elements`` holds it, at the moment the branch ran. A
root whose elaboration later refuses therefore still reports the leaves the branch
already saw. Reconstructing leaves from the elaborator's pending lists after ``run()``
returns cannot do that: a refusing root yields nothing, and would score as zero leaves
and zero absent rather than as unmeasured.

**Absence is never agreement.** Each root carries an explicit ``measurement``:

``complete``
    ``run()`` returned. Every one-segment reference in the root was observed.
``partial``
    ``run()`` raised after the branch had already run. The observations recorded are
    real, but the root holds an unknown number of further one-segment references that
    were never reached. The reason is recorded.
``none``
    Elaboration never started (load, extraction, or model-validation refusal). Nothing
    about this root's population is known. The reason is recorded.

``partial`` and ``none`` roots are residual unmeasured population. The totals block
names how many there are, so no reader can take the leaf count for a whole-population
count while any remain.

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
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor  # noqa: E402


class LeafObservations:
    """Every one-segment leaf ``_resolve_direct_reference`` was handed, as it ran.

    ``observe`` wraps the resolver on one elaborator instance. Each call appends the
    leaf's wire id and whether the element index held it *at that moment*, before
    delegating to the shipped implementation unchanged.
    """

    def __init__(self) -> None:
        self.seen: list[str] = []
        self.absent: list[str] = []

    def observe(self, elaborator: Any) -> None:
        shipped = elaborator._resolve_direct_reference

        def observing(leaf_id: Any, consumer_scope: Any) -> Any:
            self.seen.append(leaf_id.to_wire())
            if leaf_id not in elaborator._elements:
                self.absent.append(leaf_id.to_wire())
            return shipped(leaf_id, consumer_scope)

        elaborator._resolve_direct_reference = observing


def census_root(root: str) -> dict[str, Any]:
    """Measure one corpus root, reporting what the branch saw even if it refuses."""
    result: dict[str, Any] = {"root": root}
    path = REPO / root
    extractor = SysMLDataExtractor([path])
    observations = LeafObservations()
    refused: str | None = None
    try:
        if not extractor.load_models():
            refused = "load_models returned false"
        else:
            definitions = extractor.extract_calculation_definitions()
            if _blocking_model_validation_diagnostics(
                extractor.model, extractor.diagnostics.validation
            ):
                refused = "model validation blocked"
            else:
                elaborator = _ExactElaborator(
                    extractor.model, definitions, model_paths=[path], strict=False
                )
                observations.observe(elaborator)
                elaborator.run()
    except Exception as error:  # noqa: BLE001 - a refusing root is a row, not a crash
        refused = f"{type(error).__name__}: {error}"

    if refused is None:
        result["measurement"] = "complete"
    else:
        result["measurement"] = "partial" if observations.seen else "none"
        result["refused"] = refused

    result["one_segment_leaves_observed"] = len(observations.seen)
    result["distinct_leaves_observed"] = len(set(observations.seen))
    result["absent_from_element_index"] = sorted(set(observations.absent))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    roots = [*frozen_roots()["roots"], *promoted_roots()]
    rows = [census_root(root) for root in roots]

    def count(measurement: str) -> int:
        return sum(1 for row in rows if row["measurement"] == measurement)

    residual = count("partial") + count("none")
    payload = {
        "roots": rows,
        "totals": {
            "roots": len(rows),
            "roots_measured_complete": count("complete"),
            "roots_measured_partial": count("partial"),
            "roots_unmeasured": count("none"),
            "residual_unmeasured_roots": residual,
            "one_segment_leaves_observed": sum(row["one_segment_leaves_observed"] for row in rows),
            "absent_from_element_index": sum(len(row["absent_from_element_index"]) for row in rows),
            "population_claim": (
                "observed only; "
                f"{residual} root(s) hold an unmeasured or partially measured population"
                if residual
                else "whole population: every root measured to completion"
            ),
        },
    }
    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["totals"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
