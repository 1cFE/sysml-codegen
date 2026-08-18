#!/usr/bin/env python3
"""Create and verify the closed fixture inventory and immutable before-state ledger."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import project
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from sysml_codegen.snapshot.instance_graph import encode_instance_graph
from verification.artifact_sources import codegen_history_root

ROOT = Path(__file__).resolve().parent.parent
BATCH_PATH = Path("tests/fixtures/v6_recapture_batch/batch.json")
P_SEED = "52a03cd2d0a9fdd340b60b16cea79a5b72234b08"
FOUR_A = "09fdae1986c81c2a5738e1401bdc78e0ea5fa607"
FROZEN_BATCH_SHA256 = "bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288"
FOUR_A_BATCH_SHA256 = "79a0ea9f712652a4665deb8304fbb7d4c4529d76d72dbb1097e712aafaddc1b4"
CURRENT_BATCH_SHA256 = "7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40"
MANIFEST_PATH = Path("verification/fixture-manifest.json")
TRANSITIONS_PATH = Path("verification/expected-transitions.md")
ADDED_ROOTS = (
    "feature_metadata_multifile",
    "feature_typing_integrity",
    "indexed_expression_source",
    "multiplicity_writer_authority",
    "occurrence_calc_domain_derivation",
    "occurrence_domain_derivation",
)


def _history_root() -> Path:
    """Resolve the declared history only for checks that consume historical bytes."""
    return codegen_history_root(ROOT)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _historical_source_rows(root: Path, commit: str) -> list[dict[str, str]]:
    """Read one fixture root's source inventory from the named historical tree."""
    relative_root = root.relative_to(ROOT)
    result = subprocess.run(
        [
            "git",
            "-C",
            str(_history_root()),
            "ls-tree",
            "-r",
            "--name-only",
            commit,
            "--",
            str(relative_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    paths = sorted(
        Path(line)
        for line in result.stdout.splitlines()
        if Path(line).suffix in {".sysml", ".kerml"}
    )
    if not paths:
        raise ValueError(f"fixture root has no source at {commit}: {relative_root}")
    return [
        {
            "path": str(path),
            "sha256": hashlib.sha256(_git_bytes(commit, path)).hexdigest(),
        }
        for path in paths
    ]


def _git_bytes(commit: str, path: Path) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(_history_root()), "show", f"{commit}:{path}"],
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as error:
        raise ValueError(f"cannot load {path} from named commit {commit}") from error


def _frozen_batch() -> dict[str, Any]:
    raw = _git_bytes(P_SEED, BATCH_PATH)
    if hashlib.sha256(raw).hexdigest() != FROZEN_BATCH_SHA256:
        raise ValueError("named P_seed does not contain the frozen batch-manifest bytes")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("frozen batch manifest is not a JSON object")
    return cast(dict[str, Any], value)


def build_manifest() -> dict[str, object]:
    """Reconstruct the Phase 1 source inventory from its named frozen P_seed.

    The live batch file is an output expectation and transitioned in 4A.  It is deliberately not
    an input here: probe identity is the frozen roots and SysML/KerML source bytes.
    """
    batch = _frozen_batch()
    roots: list[dict[str, object]] = []
    for name in batch["fixtures"]:
        record = batch["records"][name]
        roots.append(
            {
                "kind": "canonical",
                "name": name,
                "root": f"tests/fixtures/{name}",
                "outcome": record["status"],
                "sources": _historical_source_rows(
                    ROOT / "tests/fixtures" / name,
                    P_SEED,
                ),
            }
        )
    for name in ADDED_ROOTS:
        roots.append(
            {
                "kind": "added",
                "name": name,
                "root": f"tests/fixtures/{name}",
                "outcome": "measure",
                "sources": _historical_source_rows(
                    ROOT / "tests/fixtures" / name,
                    P_SEED,
                ),
            }
        )
    return {
        "schema_version": "stop-parser-fixture-inventory/v1",
        "canonical_batch": {"path": str(BATCH_PATH), "sha256": FROZEN_BATCH_SHA256},
        "counts": {
            "canonical_roots": 37,
            "canonical_graph_records": len(batch["captured"]),
            "canonical_refusal_records": len(batch["refused"]),
            "added_roots": len(ADDED_ROOTS),
            "added_source_files": sum(
                len(cast(list[object], row["sources"]))
                for row in roots
                if row["kind"] == "added"
            ),
            "total_roots": len(roots),
        },
        "roots": roots,
    }


def validate_manifest(manifest: dict[str, Any]) -> None:
    frozen_manifest = _git_bytes(P_SEED, MANIFEST_PATH)
    if hashlib.sha256(frozen_manifest).hexdigest() != _sha(ROOT / MANIFEST_PATH):
        raise ValueError("fixture manifest differs from its named P_seed bytes")
    expected = build_manifest()
    if manifest != expected:
        raise ValueError("fixture manifest differs from the frozen P_seed source inventory")
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
    validate_current_fixture_sources(manifest)


def _ledger_rows_for_path(path: str, transitions_path: Path) -> list[tuple[str, ...]]:
    matches: list[tuple[str, ...]] = []
    for line in transitions_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = tuple(cell.strip().strip("`") for cell in line.strip().strip("|").split("|"))
        if cells and cells[0] == path:
            matches.append(cells)
    return matches


def validate_current_fixture_sources(
    manifest: dict[str, Any],
    *,
    repository_root: Path = ROOT,
    transitions_path: Path = TRANSITIONS_PATH,
) -> dict[str, object]:
    """Pin every current fixture source or require one exact transition row.

    The manifest remains the immutable P_seed inventory. This independent leg compares the bytes
    kept tests read today with that inventory; an intentional difference must name the file and both
    hashes in the transition ledger. Reconstructing the manifest from P_seed cannot satisfy this
    check because current bytes are always read from ``repository_root``.
    """
    ledger_path = (
        transitions_path
        if transitions_path.is_absolute()
        else repository_root / transitions_path
    )
    checked = 0
    added_roots = 0
    added_sources = 0
    transitioned: list[str] = []
    for root in manifest["roots"]:
        if root["kind"] == "added":
            added_roots += 1
        for source in root["sources"]:
            checked += 1
            if root["kind"] == "added":
                added_sources += 1
            source_path = str(source["path"])
            frozen_hash = str(source["sha256"])
            current_hash = _sha(repository_root / source_path)
            if current_hash == frozen_hash:
                continue
            rows = _ledger_rows_for_path(source_path, ledger_path)
            if len(rows) != 1:
                raise ValueError(
                    f"unowned current fixture source transition: {source_path}; "
                    f"expected one ledger row, found {len(rows)}"
                )
            [row] = rows
            if frozen_hash not in row or current_hash not in row:
                raise ValueError(
                    f"fixture source transition row omits the frozen or current hash: {source_path}"
                )
            transitioned.append(source_path)
    return {
        "checked_source_files": checked,
        "added_roots": added_roots,
        "added_source_files": added_sources,
        "transitioned_sources": tuple(sorted(transitioned)),
    }


def validate_current_batch() -> dict[str, Any]:
    """Validate the transitioned output expectations independently of the probe lock."""
    path = ROOT / BATCH_PATH
    current_hash = _sha(path)
    if current_hash != CURRENT_BATCH_SHA256:
        raise ValueError(
            "current batch-manifest output expectation moved: "
            f"expected {CURRENT_BATCH_SHA256}, found {current_hash}"
        )
    batch = json.loads(path.read_text())
    fixtures = batch.get("fixtures")
    records = batch.get("records")
    captured = batch.get("captured")
    refused = batch.get("refused")
    if (
        not isinstance(fixtures, list)
        or len(fixtures) != 37
        or not isinstance(records, dict)
        or set(fixtures) != set(records)
        or not isinstance(captured, list)
        or not isinstance(refused, list)
        or set(captured) | set(refused) != set(fixtures)
        or set(captured) & set(refused)
    ):
        raise ValueError("current batch-manifest record inventory is not closed")
    for name in fixtures:
        record = records[name]
        if record.get("status") == "graph":
            snapshot = Path(str(record.get("snapshot", "")))
            if snapshot.is_absolute() or ".." in snapshot.parts or not (ROOT / snapshot).is_file():
                raise ValueError(f"current batch snapshot path is invalid: {name}")
            if _sha(ROOT / snapshot) != record.get("sha256"):
                raise ValueError(f"current batch snapshot hash moved: {name}")
        elif record.get("status") != "refused":
            raise ValueError(f"current batch outcome is unnamed: {name}")
    return {
        "path": str(BATCH_PATH),
        "frozen_p_seed": P_SEED,
        "frozen_sha256": FROZEN_BATCH_SHA256,
        "current_sha256": current_hash,
        "captured": len(captured),
        "refused": len(refused),
    }


def _snapshot_semantics(payload: bytes) -> dict[str, Any]:
    document = json.loads(payload)
    normalized = copy.deepcopy(document)
    authority = normalized.get("authority")
    integrity = normalized.get("integrity")
    if not isinstance(authority, dict) or not isinstance(integrity, dict):
        raise ValueError("transitioned snapshot omits authority or integrity")
    for field in ("agentic_mbse_version", "sysml_codegen_version"):
        if field not in authority:
            raise ValueError(f"transitioned snapshot omits authority.{field}")
        del authority[field]
    if "digest" not in integrity:
        raise ValueError("transitioned snapshot omits integrity.digest")
    del integrity["digest"]
    return cast(dict[str, Any], normalized)


def _json_leaf_differences(
    before: Any, after: Any, path: tuple[str, ...] = ()
) -> dict[str, tuple[Any, Any]]:
    if isinstance(before, dict) and isinstance(after, dict) and set(before) == set(after):
        result: dict[str, tuple[Any, Any]] = {}
        for key in sorted(before):
            result.update(_json_leaf_differences(before[key], after[key], (*path, key)))
        return result
    if before == after:
        return {}
    return {"::".join(path): (before, after)}


def validate_output_transitions() -> dict[str, Any]:
    """Prove every post-P_seed output byte is metadata-only or owned by a named A/B row."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(_history_root()),
            "diff",
            "--name-only",
            P_SEED,
            FOUR_A,
            "--",
            "tests/fixtures",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {Path(line) for line in result.stdout.splitlines() if line}
    snapshot_paths = {
        path for path in changed if path.name == "instance_graph_snapshot.json"
    }
    expected_non_snapshots = {
        BATCH_PATH,
        Path("tests/fixtures/golden/computed_attribute_golden.json"),
    }
    if len(snapshot_paths) != 23 or changed != snapshot_paths | expected_non_snapshots:
        raise ValueError(
            "4A fixture transition set is not 23 snapshots plus batch and golden outputs"
        )

    ledger = (ROOT / TRANSITIONS_PATH).read_text()
    for path in sorted(snapshot_paths):
        before = _git_bytes(P_SEED, path)
        after = _git_bytes(FOUR_A, path)
        before_hash = hashlib.sha256(before).hexdigest()
        after_hash = hashlib.sha256(after).hexdigest()
        if _snapshot_semantics(before) != _snapshot_semantics(after):
            raise ValueError(f"unowned 4A snapshot semantic difference: {path}")
        if str(path) not in ledger or before_hash not in ledger or after_hash not in ledger:
            raise ValueError(f"transition ledger omits exact 4A snapshot hashes: {path}")
        current = ROOT / path
        if path.parts[-2] == "deep_cross_scope_probe":
            if current.exists():
                raise ValueError("stale deep_cross_scope_probe snapshot remains after A2 refusal")
        elif not current.is_file() or current.read_bytes() != after:
            raise ValueError(f"maintained snapshot moved after its 4A recapture: {path}")

    golden_path = Path("tests/fixtures/golden/computed_attribute_golden.json")
    before_golden = json.loads(_git_bytes(P_SEED, golden_path))
    after_golden = json.loads(_git_bytes(FOUR_A, golden_path))
    differences = _json_leaf_differences(before_golden, after_golden)
    deep_classification = (
        "deep_cross_scope_probe::DeepCrossScopeProducer::'Monitoring Station'::"
        "station_output::classification"
    )
    expected_golden = {
        deep_classification: (
            "expose_chain_tentative",
            "unresolvable",
        ),
        "ife_plant::IfePlantSubsystems::radial_build::magnet_volume_total::classification": (
            "expose_chain_tentative",
            "unresolvable",
        ),
    }
    if differences != expected_golden:
        raise ValueError(f"unowned golden-output differences: {differences}")
    current_golden = (ROOT / golden_path).read_bytes()
    after_golden_bytes = _git_bytes(FOUR_A, golden_path)
    if current_golden != after_golden_bytes:
        raise ValueError("computed-attribute golden output moved after 4A")
    for digest in (
        hashlib.sha256(_git_bytes(P_SEED, golden_path)).hexdigest(),
        hashlib.sha256(after_golden_bytes).hexdigest(),
    ):
        if digest not in ledger:
            raise ValueError("transition ledger omits a computed-attribute golden hash")

    before_batch_raw = _git_bytes(FOUR_A, BATCH_PATH)
    if hashlib.sha256(before_batch_raw).hexdigest() != FOUR_A_BATCH_SHA256:
        raise ValueError("named 4A does not contain its recorded batch-manifest bytes")
    before_batch = json.loads(before_batch_raw)
    current_batch = json.loads((ROOT / BATCH_PATH).read_text())
    moved_records = sorted(
        name
        for name in before_batch["fixtures"]
        if before_batch["records"][name] != current_batch["records"][name]
    )
    if moved_records != ["deep_cross_scope_probe", "plant_value_shapes"]:
        raise ValueError(f"unowned current batch record transitions: {moved_records}")
    if before_batch["fixtures"] != current_batch["fixtures"]:
        raise ValueError("current batch fixture inventory moved")
    if set(before_batch) != set(current_batch):
        raise ValueError("current batch top-level schema moved")
    expected_captured = [
        name for name in before_batch["captured"] if name != "deep_cross_scope_probe"
    ]
    expected_refused = sorted([*before_batch["refused"], "deep_cross_scope_probe"])
    if (
        current_batch["captured"] != expected_captured
        or current_batch["refused"] != expected_refused
    ):
        raise ValueError("current batch captured/refused transition is not the exact A2 move")
    for digest in (FOUR_A_BATCH_SHA256, CURRENT_BATCH_SHA256):
        if digest not in ledger:
            raise ValueError("transition ledger omits a batch-manifest hash")

    return {
        "metadata_only_snapshots": len(snapshot_paths),
        "golden_rows": [
            "deep_cross_scope_probe::DeepCrossScopeProducer::'Monitoring Station'::station_output",
            "ife_plant::IfePlantSubsystems::radial_build::magnet_volume_total",
        ],
        "batch_record_transitions": moved_records,
        "maintained_current_snapshots": len(snapshot_paths) - 1,
    }


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
    import syside

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
        "batch_transition": validate_current_batch(),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-fixture-manifest", action="store_true")
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-current-batch", action="store_true")
    parser.add_argument("--check-output-transitions", action="store_true")
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
    current_batch = validate_current_batch()
    output_transitions = validate_output_transitions()
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
    if args.check_current_batch:
        print(json.dumps(current_batch, sort_keys=True))
    if args.check_output_transitions:
        print(json.dumps(output_transitions, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
