#!/usr/bin/env python3
"""Prove unit-bearing features always carry an exact parser document origin."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse

import syside
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from probe_support import sha256_file, validate_lock, write_canonical_json

from sysml_codegen.extraction.feature_metadata import _source_file, extract_feature_unit
from sysml_codegen.extraction.source_manifest import admit_sources


def _root_relative_referent(referent: str) -> str:
    if type(referent) is not str:
        raise TypeError("SourceFile.referent must be a string")
    path = PurePosixPath(referent)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"SourceFile.referent is not root-relative: {referent!r}")
    return path.as_posix()


def _url_path(element: Any) -> Path:
    url = getattr(getattr(element, "document", None), "url", None)
    if url is None:
        raise RuntimeError("feature lacks a parser document URL")
    parsed = urlparse(str(url))
    return Path(unquote(parsed.path if parsed.scheme == "file" else str(url))).resolve()


def _load(paths: list[Path]) -> Any:
    model, diagnostics = SysideAdapter.load_model(paths)
    if diagnostics.contains_errors():
        raise RuntimeError(f"parser errors: {list(diagnostics.errors)!r}")
    return model


def _witnesses(model: Any, expected: dict[Path, str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for feature in SysideAdapter.elements_of_type(model, "AttributeUsage", include_subtypes=True):
        document_path = _url_path(feature)
        referent = expected.get(document_path)
        if referent is None:
            continue
        exact = _source_file(feature)
        unit = extract_feature_unit(feature)
        if unit is not None:
            if exact is None or exact.resolve() != document_path:
                raise RuntimeError("source lookup did not preserve the parser document")
            result.append(
                {
                    "feature": str(feature.qualified_name),
                    "document": referent,
                    "unit": unit,
                }
            )
    return sorted(result, key=lambda row: (row["document"], row["feature"]))


def run_probe(repository: Path) -> dict[str, object]:
    root = repository / "tests/fixtures/feature_metadata_multifile"
    original_files = sorted(root.glob("*.sysml"))
    original_map = {path.resolve(): str(path.relative_to(repository)) for path in original_files}
    live = _witnesses(_load([root]), original_map)
    with admit_sources([root]) as admission:
        staged_files = [item.staged_path for item in admission.files]
        staged_map = {
            item.staged_path.resolve(): _root_relative_referent(item.referent)
            for item in admission.files
        }
        admitted = _witnesses(_load(staged_files), staged_map)
    live_shape = [(Path(row["document"]).name, row["feature"], row["unit"]) for row in live]
    admitted_shape = [(Path(row["document"]).name, row["feature"], row["unit"]) for row in admitted]
    counts = {
        str(path.relative_to(repository)): sum(
            row["document"] == str(path.relative_to(repository)) for row in live
        )
        for path in original_files
    }
    passed = (
        len(original_files) >= 2
        and min(counts.values(), default=0) >= 1
        and live_shape == admitted_shape
    )
    return {
        "schema_version": "stop-parser-b10/v1",
        "verdict": "DELETE_UNREACHABLE" if passed else "DOCUMENT_ORIGIN_NOT_TOTAL",
        "document_count": len(original_files),
        "unit_features_per_file": counts,
        "live": live,
        "admitted": admitted,
        "syside_version": syside.__version__,
        "source_hashes": {
            str(path.relative_to(repository)): sha256_file(path) for path in original_files
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--probe-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()
    validate_lock(
        repository, lock_path=args.lock.resolve(), expected_probe_commit=args.probe_commit
    )
    result = run_probe(repository)
    write_canonical_json(args.output, result)
    return 0 if result["verdict"] == "DELETE_UNREACHABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
