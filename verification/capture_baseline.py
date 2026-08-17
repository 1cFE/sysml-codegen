#!/usr/bin/env python3
"""Create and verify the closed fixture inventory and immutable before-state ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import tempfile
from pathlib import Path
from typing import Any

import syside

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import project
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from sysml_codegen.snapshot.instance_graph import encode_instance_graph

ROOT = Path(__file__).resolve().parent.parent
BATCH_PATH = Path("tests/fixtures/v6_recapture_batch/batch.json")
ADDED_ROOTS = (
    "feature_metadata_multifile",
    "feature_typing_integrity",
    "indexed_expression_source",
    "multiplicity_writer_authority",
    "occurrence_calc_domain_derivation",
    "occurrence_domain_derivation",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_rows(root: Path) -> list[dict[str, str]]:
    files = sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix in {".sysml", ".kerml"}
    )
    if not files:
        raise ValueError(f"fixture root has no source: {root.relative_to(ROOT)}")
    return [{"path": str(path.relative_to(ROOT)), "sha256": _sha(path)} for path in files]


def build_manifest() -> dict[str, object]:
    batch = json.loads((ROOT / BATCH_PATH).read_text())
    roots: list[dict[str, object]] = []
    for name in batch["fixtures"]:
        record = batch["records"][name]
        roots.append(
            {
                "kind": "canonical",
                "name": name,
                "root": f"tests/fixtures/{name}",
                "outcome": record["status"],
                "sources": _source_rows(ROOT / "tests/fixtures" / name),
            }
        )
    for name in ADDED_ROOTS:
        roots.append(
            {
                "kind": "added",
                "name": name,
                "root": f"tests/fixtures/{name}",
                "outcome": "measure",
                "sources": _source_rows(ROOT / "tests/fixtures" / name),
            }
        )
    return {
        "schema_version": "stop-parser-fixture-inventory/v1",
        "canonical_batch": {"path": str(BATCH_PATH), "sha256": _sha(ROOT / BATCH_PATH)},
        "counts": {
            "canonical_roots": 37,
            "canonical_graph_records": len(batch["captured"]),
            "canonical_refusal_records": len(batch["refused"]),
            "added_roots": len(ADDED_ROOTS),
            "added_source_files": sum(
                len(row["sources"]) for row in roots if row["kind"] == "added"
            ),
            "total_roots": len(roots),
        },
        "roots": roots,
    }


def validate_manifest(manifest: dict[str, Any]) -> None:
    expected = build_manifest()
    if manifest != expected:
        raise ValueError("fixture manifest differs from the closed on-disk inventory")
    roots = manifest["roots"]
    if len({row["root"] for row in roots}) != len(roots):
        raise ValueError("fixture manifest contains duplicate roots")
    listed: set[str] = set()
    for row in roots:
        root_path = Path(row["root"])
        if root_path.is_absolute() or ".." in root_path.parts:
            raise ValueError(f"non-portable root: {root_path}")
        actual = {
            str(path.relative_to(ROOT))
            for path in (ROOT / root_path).rglob("*")
            if path.is_file() and path.suffix in {".sysml", ".kerml"}
        }
        recorded = {source["path"] for source in row["sources"]}
        if actual != recorded:
            raise ValueError(f"unlisted or missing source under {root_path}")
        for source in row["sources"]:
            path = Path(source["path"])
            if path.is_absolute() or ".." in path.parts or source["path"] in listed:
                raise ValueError(f"duplicate or non-portable source: {path}")
            listed.add(source["path"])
            if _sha(ROOT / path) != source["sha256"]:
                raise ValueError(f"source hash mismatch: {path}")


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): _sha(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _json_value(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "root"):
        return _json_value(value.root)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"execution result contains unsupported {type(value).__name__}")


def _execute(package: Path, package_name: str, work: Path) -> dict[str, object]:
    from simkit.core.pipeline import execute_pipeline
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    try:
        module, fingerprint = ProvisionalPackageLoader(
            package_dir=package,
            package_name=package_name,
            link_root=work / "link",
        ).load()
        registry = getattr(module, f"create_{package_name}_registry")()
        result = execute_pipeline(
            package / "pipelines/pipeline.yaml",
            work / "run",
            registry=registry,
            custom_schema_types=getattr(module, "CUSTOM_SCHEMA_TYPES", []),
        )
        output = _json_value(result.outputs)
        return {
            "status": "executed",
            "package_fingerprint": fingerprint,
            "output_count": len(output),
            "output_sha256": hashlib.sha256(_canonical(output)).hexdigest(),
        }
    except Exception as error:
        return {
            "status": "refused",
            "error_type": type(error).__name__,
            "message": str(error).replace(str(work), "<execution-root>"),
        }


def _generated(snapshot: Path, live_root: Path, name: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"stop-parser-{name}-") as temporary:
        work = Path(temporary)
        live = work / "live"
        replay = work / "snapshot"
        package = f"baseline_{name}"
        live_succeeded = run_codegen(
            GenerationConfig(
                models_path=live_root, output_path=live, package_name=package, overwrite=True
            )
        )
        replay_succeeded = run_codegen(
            GenerationConfig(
                from_snapshot=snapshot, output_path=replay, package_name=package, overwrite=True
            )
        )
        if live_succeeded != replay_succeeded:
            raise RuntimeError(f"live/snapshot generation outcomes differ for {name}")
        if not live_succeeded:
            return {
                "status": "refused",
                "public_result": False,
                "live_snapshot_parity": True,
                "relative_file_hashes": {},
            }
        live_tree = _tree_hashes(live)
        replay_tree = _tree_hashes(replay)
        if live_tree != replay_tree:
            raise RuntimeError(f"live/snapshot package bytes differ for {name}")
        return {
            "status": "generated",
            "public_result": True,
            "live_snapshot_parity": True,
            "relative_file_hashes": live_tree,
            "execution": _execute(live, package, work / "execution"),
        }


def _refusal(error: Exception) -> dict[str, object]:
    codes: list[str] = []
    diagnostics: list[dict[str, str]] = []
    for attribute in ("diagnostics", "findings"):
        for item in getattr(error, attribute, ()):
            code = getattr(item, "code", None)
            rendered_code = str(getattr(code, "value", code))
            codes.append(rendered_code)
            reference = getattr(item, "reference", None)
            if reference is None:
                reference = getattr(item, "consumer_display", None)
            location = getattr(item, "location", None)
            diagnostics.append(
                {
                    "code": rendered_code,
                    "reference": str(reference or ""),
                    "location": str(location or ""),
                }
            )
    return {
        "status": "refused",
        "error_type": type(error).__name__,
        "codes": sorted(codes),
        "diagnostics": sorted(
            diagnostics,
            key=lambda item: (item["code"], item["reference"], item["location"]),
        ),
        "message": str(error),
    }


def _identity_rows(graph: Any) -> dict[str, list[str]]:
    return {
        "occurrences": sorted(
            item.occurrence_id.to_wire() for item in graph.occurrences.values()
        ),
        "attributes": sorted(item.node_id.to_wire() for item in graph.attrs.values()),
        "calculations": sorted(item.node_id.to_wire() for item in graph.calcs.values()),
        "constraints": sorted(item.node_id.to_wire() for item in graph.constraints.values()),
    }


def capture(
    manifest: dict[str, Any],
    codegen_commit: str,
    agentic_commit: str,
    teax_root: Path,
) -> dict[str, object]:
    import simkit

    if not Path(simkit.__file__).resolve().is_relative_to(teax_root.resolve()):
        raise RuntimeError("simkit did not import from the explicit frozen TEAx root")
    batch = json.loads((ROOT / BATCH_PATH).read_text())
    records: list[dict[str, object]] = []
    for inventory in manifest["roots"]:
        name = inventory["name"]
        root = ROOT / inventory["root"]
        if inventory["kind"] == "canonical":
            old = batch["records"][name]
            if old["status"] == "refused":
                try:
                    elaborate_model_paths([root])
                except Exception as error:
                    outcome = _refusal(error)
                else:
                    raise RuntimeError(f"canonical refusal unexpectedly elaborated: {name}")
                for field in ("status", "error_type", "codes", "message"):
                    if outcome[field] != old[field]:
                        raise RuntimeError(f"canonical refusal moved for {name}: {field}")
            else:
                snapshot = ROOT / old["snapshot"]
                graph = load_instance_graph_snapshot(snapshot)
                encoded = encode_instance_graph(graph)
                projected = project(graph).model_dump(mode="json")
                outcome = {
                    "status": "graph",
                    "snapshot": old["snapshot"],
                    "snapshot_sha256": _sha(snapshot),
                    "instance_graph_sha256": hashlib.sha256(encoded).hexdigest(),
                    "instance_graph": json.loads(encoded),
                    "projected_graph_sha256": hashlib.sha256(_canonical(projected)).hexdigest(),
                    "semantic_identity_rows": _identity_rows(graph),
                    "identity_counts": {
                        "occurrences": len(graph.occurrences),
                        "attributes": len(graph.attrs),
                        "calculations": len(graph.calcs),
                        "constraints": len(graph.constraints),
                    },
                    "generated_package": _generated(snapshot, root, name),
                }
        else:
            try:
                graph = elaborate_model_paths([root])
                encoded = encode_instance_graph(graph)
                try:
                    with tempfile.TemporaryDirectory(
                        prefix=f"stop-parser-added-{name}-"
                    ) as temporary:
                        snapshot = capture_instance_graph_snapshot(
                            [root], Path(temporary) / "snapshot.json"
                        )
                        snapshot_sha256 = _sha(snapshot)
                        generated_package = _generated(snapshot, root, name)
                except Exception as generation_error:
                    snapshot_sha256 = None
                    generated_package = _refusal(generation_error)
                outcome = {
                    "status": "graph",
                    "instance_graph_sha256": hashlib.sha256(encoded).hexdigest(),
                    "instance_graph": json.loads(encoded),
                    "semantic_identity_rows": _identity_rows(graph),
                    "snapshot_sha256": snapshot_sha256,
                    "identity_counts": {
                        "occurrences": len(graph.occurrences),
                        "attributes": len(graph.attrs),
                        "calculations": len(graph.calcs),
                        "constraints": len(graph.constraints),
                    },
                    "generated_package": generated_package,
                }
            except Exception as error:
                outcome = _refusal(error)
        records.append(
            {"root": inventory["root"], "source_hashes": inventory["sources"], "outcome": outcome}
        )
    return {
        "schema_version": "stop-parser-before-state/v1",
        "source_identity": {
            "codegen_commit": codegen_commit,
            "agentic_commit": agentic_commit,
            "teax_commit": "744745f895677f3344b9884627369a6a47ed987f",
            "costingfe_commit": "02543850089be175ea7c28b92a8b2a4184e1637e",
        },
        "versions": {"python": platform.python_version(), "syside": syside.__version__},
        "manifest_sha256": _sha(ROOT / "verification/fixture-manifest.json"),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-fixture-manifest", action="store_true")
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "verification/pre-change-baseline.json"
    )
    parser.add_argument("--codegen-commit")
    parser.add_argument("--agentic-commit")
    parser.add_argument("--teax-root", type=Path)
    args = parser.parse_args()
    manifest_path = ROOT / "verification/fixture-manifest.json"
    if args.write_fixture_manifest:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(_canonical(build_manifest()) + b"\n")
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest)
    if args.capture:
        if not args.codegen_commit or not args.agentic_commit or args.teax_root is None:
            parser.error(
                "--capture requires --codegen-commit, --agentic-commit, and --teax-root"
            )
        args.output.write_bytes(
            _canonical(
                capture(manifest, args.codegen_commit, args.agentic_commit, args.teax_root)
            )
            + b"\n"
        )
    if args.check:
        baseline = json.loads(args.output.read_text())
        if baseline.get("schema_version") != "stop-parser-before-state/v1":
            raise ValueError("baseline schema is not the frozen before-state schema")
        if baseline["manifest_sha256"] != _sha(manifest_path) or len(
            baseline["records"]
        ) != 43:
            raise ValueError("baseline does not match the closed inventory")
        outcome_counts = {"graph": 0, "refused": 0}
        for inventory, record in zip(manifest["roots"], baseline["records"], strict=True):
            if (
                record["root"] != inventory["root"]
                or record["source_hashes"] != inventory["sources"]
            ):
                raise ValueError(f"baseline source identity moved: {inventory['root']}")
            outcome = record["outcome"]
            status = outcome.get("status")
            if status not in outcome_counts:
                raise ValueError(f"unnamed baseline outcome: {inventory['root']}")
            outcome_counts[status] += 1
            if status == "refused":
                if not outcome.get("error_type") or not outcome.get("message"):
                    raise ValueError(f"unnamed baseline refusal: {inventory['root']}")
                continue
            graph_bytes = _canonical(outcome["instance_graph"])
            if hashlib.sha256(graph_bytes).hexdigest() != outcome["instance_graph_sha256"]:
                raise ValueError(f"graph bytes moved: {inventory['root']}")
            rows = outcome["semantic_identity_rows"]
            for kind in ("occurrences", "attributes", "calculations", "constraints"):
                if len(rows[kind]) != outcome["identity_counts"][kind]:
                    raise ValueError(f"identity rows are incomplete: {inventory['root']} {kind}")
            generated = outcome.get("generated_package")
            if generated is None or not generated.get("status"):
                raise ValueError(f"generation outcome is absent: {inventory['root']}")
            if generated["status"] == "generated":
                if not generated["live_snapshot_parity"] or not generated["relative_file_hashes"]:
                    raise ValueError(f"generated parity is incomplete: {inventory['root']}")
                execution = generated.get("execution")
                if execution is None or execution.get("status") not in {"executed", "refused"}:
                    raise ValueError(f"execution outcome is absent: {inventory['root']}")
                if execution["status"] == "executed" and (
                    execution.get("output_count", 0) <= 0
                    or len(execution.get("output_sha256", "")) != 64
                ):
                    raise ValueError(f"execution hash is incomplete: {inventory['root']}")
        if outcome_counts["graph"] + outcome_counts["refused"] != 43:
            raise ValueError("baseline outcome count changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
