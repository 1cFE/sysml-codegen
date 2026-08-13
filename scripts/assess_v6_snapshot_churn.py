#!/usr/bin/env python3
"""Assess every tracked v6 snapshot without mutating the repository.

The tracked Git path set is the scope authority. A row is stale only when live
elaboration changes the exact encoded instance-graph payload or its port-unit
map. Projection, computation, generated entry-point, envelope, and source
manifest digests are review evidence and never change that decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from sysml_codegen.cli import _get_template_env
from sysml_codegen.elaboration import project
from sysml_codegen.extraction.source_manifest import admit_sources
from sysml_codegen.generation.entry_point import (
    generate_all_derived_jsons,
    generate_all_derived_schemas,
)
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_admitted_sources
from sysml_codegen.snapshot.envelope import (
    SnapshotCertifiabilityError,
    build_envelope,
    canonical_json,
    encode_envelope,
    load_instance_graph_snapshot,
)
from sysml_codegen.snapshot.instance_graph import decode_instance_graph, encode_instance_graph

ROOT = Path(__file__).resolve().parent.parent
TRACKED_PATHSPEC = "tests/fixtures/**/instance_graph_snapshot.json"


class InventorySetError(ValueError):
    """Assessment rows do not equal the Git-derived tracked snapshot set."""


def _run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def tracked_snapshot_paths(root: Path = ROOT) -> list[str]:
    """Return Git's exact tracked snapshot set using one literal pathspec argument."""
    result = subprocess.run(
        ["git", "ls-files", "-z", TRACKED_PATHSPEC],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return sorted(item.decode() for item in result.stdout.split(b"\0") if item)


def require_exact_row_set(tracked: list[str], row_paths: list[str]) -> None:
    """Refuse duplicate, missing, or extra assessment rows."""
    duplicates = sorted(path for path, count in Counter(row_paths).items() if count > 1)
    missing = sorted(set(tracked) - set(row_paths))
    extra = sorted(set(row_paths) - set(tracked))
    problems = []
    if duplicates:
        problems.append(f"duplicate rows: {duplicates}")
    if missing:
        problems.append(f"missing rows: {missing}")
    if extra:
        problems.append(f"extra rows: {extra}")
    if problems:
        raise InventorySetError("; ".join(problems))


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _projected_payload(computation_graph: Any) -> dict[str, object]:
    payload = computation_graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(computation_graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        computation_graph.constraint_catalog.model_dump(mode="json")
        if computation_graph.constraint_catalog is not None
        else None
    )
    return payload


def _generated_entry_point_evidence(computation_graph: Any) -> tuple[str, list[str]]:
    with tempfile.TemporaryDirectory(prefix="item8-entry-points-") as temporary:
        output = Path(temporary)
        template_env = _get_template_env()
        generate_all_derived_schemas(computation_graph.entry_point_groups, template_env, output)
        generate_all_derived_jsons(computation_graph.entry_point_groups, output)
        paths = sorted(
            path
            for path in output.rglob("*")
            if path.is_file() and path.parts[-2] in {"schemas", "inputs"}
        )
        relative_paths = [path.relative_to(output).as_posix() for path in paths]
        digest_input = [
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path.read_bytes()),
            }
            for path, relative in zip(paths, relative_paths, strict=True)
        ]
        return _sha256(canonical_json(digest_input)), relative_paths


def _diagnostics(error: Exception) -> list[dict[str, str]]:
    rows = []
    for diagnostic in getattr(error, "diagnostics", ()):
        code = getattr(diagnostic, "code", "")
        rows.append(
            {
                "code": getattr(code, "value", str(code)),
                "detail": str(getattr(diagnostic, "detail", diagnostic)),
            }
        )
    return rows


def _projection_evidence(graph: Any) -> dict[str, object]:
    try:
        computation_graph = project(graph)
    except Exception as error:  # noqa: BLE001 - the typed refusal is evidence
        diagnostics = _diagnostics(error)
        return {
            "status": "refused",
            "error_type": type(error).__name__,
            "message": str(error),
            "diagnostics": diagnostics,
            "codes": [row["code"] for row in diagnostics],
            "counts": None,
            "computation_digest": None,
            "generated_entry_point_digest": None,
            "generated_entry_point_paths": [],
            "generated_entry_point_inapplicable": "projection refused",
        }

    payload = _projected_payload(computation_graph)
    generated_digest, generated_paths = _generated_entry_point_evidence(computation_graph)
    catalog = computation_graph.constraint_catalog
    return {
        "status": "projectable",
        "error_type": None,
        "message": None,
        "diagnostics": [],
        "codes": [],
        "counts": {
            "modules": len(computation_graph.modules),
            "entry_points": sum(
                len(group.parameters) for group in computation_graph.entry_point_groups
            ),
            "entry_point_groups": len(computation_graph.entry_point_groups),
            "aliases": len(computation_graph.output_aliases),
            "constraints": len(catalog.concrete_entries) if catalog is not None else 0,
        },
        "computation_digest": _sha256(canonical_json(payload)),
        "generated_entry_point_digest": generated_digest,
        "generated_entry_point_paths": generated_paths,
        "generated_entry_point_inapplicable": None,
    }


def _unit_map(graph: Any) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for node_kind, nodes in (("calculation", graph.calcs), ("constraint", graph.constraints)):
        for node_id, node in sorted(nodes.items(), key=lambda item: str(item[0])):
            for port, metadata in node.input_metadata.items():
                rows.append(
                    {
                        "node_kind": node_kind,
                        "node_id": str(node_id),
                        "direction": "input",
                        "name": node.input_names[port],
                        "port": str(port),
                        "qualified_name": metadata.qualified_name,
                        "unit": metadata.unit,
                    }
                )
            if node_kind == "calculation":
                for declaration, metadata in node.output_metadata.items():
                    rows.append(
                        {
                            "node_kind": node_kind,
                            "node_id": str(node_id),
                            "direction": "output",
                            "name": node.output_names[declaration],
                            "port": str(node.outputs[declaration]),
                            "qualified_name": metadata.qualified_name,
                            "unit": metadata.unit,
                        }
                    )
    return sorted(rows, key=lambda row: (str(row["node_id"]), str(row["port"])))


def _graph_arm(
    graph: Any,
    *,
    instance_document: dict[str, object],
    envelope_payload: bytes | None,
    envelope_document: dict[str, object] | None,
    source_manifest_fingerprint: str,
) -> dict[str, object]:
    return {
        "envelope_sha256": _sha256(envelope_payload) if envelope_payload is not None else None,
        "outer_digest": (
            envelope_document["integrity"]["digest"]  # type: ignore[index]
            if envelope_document is not None
            else None
        ),
        "instance_graph_schema": instance_document["schema_version"],
        "instance_graph_fingerprint": instance_document["fingerprint"],
        "instance_graph_payload_digest": _sha256(canonical_json(instance_document)),
        "source_manifest_fingerprint": source_manifest_fingerprint,
        "unit_map": _unit_map(graph),
        "projection": _projection_evidence(graph),
    }


def _committed_arm(snapshot_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    payload = snapshot_path.read_bytes()
    document = json.loads(payload)
    try:
        graph = load_instance_graph_snapshot(snapshot_path)
        certification_refusal = None
    except SnapshotCertifiabilityError as error:
        # The envelope boundary may correctly refuse a graph that the Item 8
        # assessment still has to classify. Integrity and compatibility reached
        # certifiability before this typed exception; decode the same inner bytes
        # only to publish the refusal and compare them with final live behavior.
        graph = decode_instance_graph(canonical_json(document["instance_graph"]))
        certification_refusal = {
            "error_type": type(error).__name__,
            "message": str(error),
            "diagnostics": _diagnostics(error),
        }
    instance_document = document["instance_graph"]
    arm = _graph_arm(
        graph,
        instance_document=instance_document,
        envelope_payload=payload,
        envelope_document=document,
        source_manifest_fingerprint=document["sources"]["fingerprint"],
    )
    arm["envelope_certification_refusal"] = certification_refusal
    return arm, instance_document


def _live_arm(fixture_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    with admit_sources([fixture_root]) as admission:
        graph = elaborate_admitted_sources(admission)
        instance_document = json.loads(encode_instance_graph(graph))
        sources = admission.envelope_sources()
        try:
            envelope_document = build_envelope(graph, admission)
            envelope_payload = encode_envelope(envelope_document)
            certification_refusal = None
        except SnapshotCertifiabilityError as error:
            envelope_document = None
            envelope_payload = None
            certification_refusal = {
                "error_type": type(error).__name__,
                "message": str(error),
                "diagnostics": _diagnostics(error),
            }
        arm = _graph_arm(
            graph,
            instance_document=instance_document,
            envelope_payload=envelope_payload,
            envelope_document=envelope_document,
            source_manifest_fingerprint=str(sources["fingerprint"]),
        )
        arm["envelope_certification_refusal"] = certification_refusal
        return arm, instance_document


def _assess_row(relative_path: str) -> dict[str, object]:
    snapshot_path = ROOT / relative_path
    fixture_root = snapshot_path.parent
    committed, committed_instance = _committed_arm(snapshot_path)
    live, live_instance = _live_arm(fixture_root)
    graph_payload_changed = canonical_json(committed_instance) != canonical_json(live_instance)
    unit_map_changed = committed["unit_map"] != live["unit_map"]
    return {
        "path": relative_path,
        "fixture_root": fixture_root.relative_to(ROOT).as_posix(),
        "committed": committed,
        "live": live,
        "movement": {
            "instance_graph_payload_changed": graph_payload_changed,
            "unit_map_changed": unit_map_changed,
            "envelope_sha_changed": committed["envelope_sha256"] != live["envelope_sha256"],
            "source_manifest_changed": committed["source_manifest_fingerprint"]
            != live["source_manifest_fingerprint"],
            "computation_digest_changed": committed["projection"]["computation_digest"]  # type: ignore[index]
            != live["projection"]["computation_digest"],  # type: ignore[index]
            "generated_entry_point_digest_changed": committed["projection"][  # type: ignore[index]
                "generated_entry_point_digest"
            ]
            != live["projection"]["generated_entry_point_digest"],  # type: ignore[index]
            "projected_counts_changed": committed["projection"]["counts"]  # type: ignore[index]
            != live["projection"]["counts"],  # type: ignore[index]
        },
        "stale": graph_payload_changed or unit_map_changed,
        "stale_reason": [
            reason
            for changed, reason in (
                (graph_payload_changed, "instance_graph_payload_changed"),
                (unit_map_changed, "unit_map_changed"),
            )
            if changed
        ],
    }


def build_inventory() -> dict[str, object]:
    tracked = tracked_snapshot_paths()
    rows = [_assess_row(path) for path in tracked]
    row_paths = [str(row["path"]) for row in rows]
    require_exact_row_set(tracked, row_paths)
    return {
        "schema": "unit-lane-v6-snapshot-inventory/v1",
        "baseline_commit": _run_git("rev-parse", "HEAD").strip(),
        "git_status": _run_git("status", "--short", "--branch").splitlines(),
        "tracked_pathspec": TRACKED_PATHSPEC,
        "tracked_paths": tracked,
        "tracked_count": len(tracked),
        "row_count": len(rows),
        "missing_paths": [],
        "extra_paths": [],
        "duplicate_paths": [],
        "stale_paths": [str(row["path"]) for row in rows if row["stale"]],
        "stale_trigger": "exact instance-graph payload or relevant PortMetadata.unit movement",
        "non_trigger_evidence": [
            "envelope bytes/digest",
            "source-manifest fingerprint",
            "projected counts/refusal",
            "computation digest",
            "generated entry-point digest",
        ],
        "captured_at_field": "inapplicable: v6 rejects captured_at and is deterministic",
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()

    inventory = build_inventory()
    if args.baseline is not None:
        baseline = json.loads(args.baseline.read_text())
        pre_paths = set(baseline["tracked_paths"])
        final_paths = set(inventory["tracked_paths"])
        inventory["path_additions"] = sorted(final_paths - pre_paths)
        inventory["path_removals"] = sorted(pre_paths - final_paths)
    else:
        inventory["path_additions"] = []
        inventory["path_removals"] = []

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print(
        f"{inventory['tracked_count']} tracked, {inventory['row_count']} assessed, "
        f"{len(inventory['stale_paths'])} stale, 0 missing, 0 extra, 0 duplicate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
