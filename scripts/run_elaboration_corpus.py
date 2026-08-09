#!/usr/bin/env python3
"""Run legacy and exact-ID construction independently over all 37 snapshots.

The command prints one JSON document.  It does not update snapshots, ledgers,
or generated baselines.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any

from sysml_codegen.elaboration.diff import (
    compare_computation_graphs,
    public_graph_signature,
)
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.resolution.models import ComputationGraph

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _graph_outcome(graph: ComputationGraph) -> dict[str, object]:
    signature = public_graph_signature(graph)
    return {
        "status": "graph",
        "fingerprint": hashlib.sha256(_canonical(signature)).hexdigest(),
        "modules": len(graph.modules),
        "entry_points": sum(len(group.parameters) for group in graph.entry_point_groups),
        "aliases": len(graph.output_aliases),
        "constraints": (
            len(graph.constraint_catalog.concrete_entries)
            if graph.constraint_catalog is not None
            else 0
        ),
    }


def _error_outcome(error: Exception) -> dict[str, object]:
    codes = []
    for attribute in ("diagnostics", "findings"):
        for item in getattr(error, attribute, ()):
            code = getattr(item, "code", None)
            codes.append(getattr(code, "value", str(code)))
    return {
        "status": "error",
        "error_type": type(error).__name__,
        "codes": sorted(codes),
        "message": str(error),
    }


def _run_route(builder: Any, fixture: Path) -> tuple[dict[str, object], ComputationGraph | None]:
    try:
        built = builder([fixture])
        graph = built if isinstance(built, ComputationGraph) else built.computation_graph
        return _graph_outcome(graph), graph
    except Exception as error:  # noqa: BLE001 - route outcome is the corpus datum
        return _error_outcome(error), None


def discover_fixture_names() -> list[str]:
    return sorted(path.parent.name for path in FIXTURES.glob("*/extraction_snapshot.json"))


def _display_outcome(outcome: dict[str, object]) -> str:
    if outcome["status"] == "graph":
        return "graph {modules}/{entry_points}/{constraints}/{aliases}".format(**outcome)
    codes = Counter(str(code) for code in outcome.get("codes", []))
    if codes:
        rendered = " + ".join(
            f"{count}× {code}" if count != 1 else code for code, count in sorted(codes.items())
        )
        return f"error: {rendered}"
    return f"error: {outcome['error_type']}"


def result_outcomes(result: dict[str, object]) -> dict[str, tuple[str, str, str]]:
    section_codes = {
        "modules": "M",
        "entry_points": "E",
        "execution_order": "O",
        "aliases": "A",
        "constraint_catalog": "C",
    }
    outcomes = {}
    for row in result["rows"]:
        legacy = _display_outcome(row["legacy"])
        exact = _display_outcome(row["exact"])
        if row["legacy"]["status"] != "graph" or row["exact"]["status"] != "graph":
            differences = "—"
        else:
            differences = (
                "/".join(section_codes[section] for section in row["difference_sections"]) or "none"
            )
        outcomes[row["fixture"]] = (legacy, exact, differences)
    return outcomes


def read_ledger_outcomes(path: Path) -> dict[str, tuple[str, str, str]]:
    outcomes = {}
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().replace("`", "") for cell in line.strip("|").split("|")]
        if not cells or not cells[0].isdigit() or len(cells) < 5:
            continue
        outcomes[cells[1]] = (cells[2], cells[3], cells[4])
    return outcomes


def run(names: list[str]) -> dict[str, object]:
    rows = []
    for name in names:
        fixture = FIXTURES / name
        legacy_outcome, legacy_graph = _run_route(build_pipeline_context, fixture)
        exact_outcome, exact_graph = _run_route(build_elaborated_pipeline, fixture)
        differences = (
            [
                difference.section
                for difference in compare_computation_graphs(legacy_graph, exact_graph)
            ]
            if legacy_graph is not None and exact_graph is not None
            else []
        )
        rows.append(
            {
                "fixture": name,
                "legacy": legacy_outcome,
                "exact": exact_outcome,
                "difference_sections": differences,
            }
        )
    return {"fixture_count": len(rows), "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixtures", nargs="*", help="optional fixture names")
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    names = args.fixtures or discover_fixture_names()
    result = run(names)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if len(names) == 37 or bool(args.fixtures) else 2


if __name__ == "__main__":
    raise SystemExit(main())
