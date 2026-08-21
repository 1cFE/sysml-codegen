#!/usr/bin/env python3
"""Measure resolved-reference leaf totality across the closed real corpus."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import syside
from agentic_mbse.sysml.reference_use import (
    ExactReferenceUse,
    inspect_reference_uses,
    resolved_target_fact,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from probe_support import load_json, load_model, sha256_file, validate_lock, write_canonical_json


def _nodes(expression: Any) -> list[Any]:
    """Materialize every operand; iterator failure is a probe failure, never partial evidence."""
    if expression is None:
        return []
    result = [expression]
    operands = tuple(getattr(expression, "operands", ()) or ())
    for operand in operands:
        result.extend(_nodes(operand))
    return result


def run_probe(repository: Path, agentic_commit: str) -> dict[str, object]:
    manifest = load_json(repository / "verification/fixture-manifest.json")
    rows: list[dict[str, object]] = []
    feature_references = 0
    feature_chains = 0
    missing_leaves = 0
    for record in manifest["roots"]:
        root = repository / record["root"]
        model = load_model(root)
        root_refs = 0
        root_chains = 0
        root_missing = 0
        for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True):
            expression = getattr(feature, "feature_value_expression", None)
            for node in _nodes(expression):
                if SysideAdapter.is_instance(node, "FeatureChainExpression"):
                    uses = inspect_reference_uses(node)
                    if any(isinstance(use, ExactReferenceUse) for use in uses):
                        root_chains += 1
                        if any(
                            isinstance(use, ExactReferenceUse) and use.path.leaf is None
                            for use in uses
                        ):
                            root_missing += 1
                elif SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
                    if resolved_target_fact(getattr(node, "referent", None)) is not None:
                        root_refs += 1
        feature_references += root_refs
        feature_chains += root_chains
        missing_leaves += root_missing
        rows.append(
            {
                "root": record["root"],
                "source_hashes": record["sources"],
                "feature_references": root_refs,
                "feature_chains": root_chains,
                "missing_leaves": root_missing,
            }
        )
    total = feature_references + feature_chains
    verdict = (
        "REAL_CORPUS_TOTAL"
        if total > 0 and feature_references > 0 and feature_chains > 0 and missing_leaves == 0
        else "REAL_CORPUS_NOT_TOTAL"
    )
    return {
        "schema_version": "stop-parser-b8a/v1",
        "verdict": verdict,
        "root_count": len(rows),
        "total_resolved_facts": total,
        "feature_reference_facts": feature_references,
        "feature_chain_facts": feature_chains,
        "missing_leaf_count": missing_leaves,
        "syside_version": syside.__version__,
        "agentic_commit": agentic_commit,
        "manifest_sha256": sha256_file(repository / "verification/fixture-manifest.json"),
        "roots": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--probe-commit", required=True)
    parser.add_argument("--agentic-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()
    validate_lock(
        repository, lock_path=args.lock.resolve(), expected_probe_commit=args.probe_commit
    )
    result = run_probe(repository, args.agentic_commit)
    write_canonical_json(args.output, result)
    return 0 if result["verdict"] == "REAL_CORPUS_TOTAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
