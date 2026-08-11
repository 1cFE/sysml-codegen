#!/usr/bin/env python3
"""Measure Fusion Tea and execute its generated packages with the pinned real TEAx."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENTIC_ROOT = ROOT.parent / "agentic-mbse"
TEAX_ROOT = ROOT.parent / "teax"
CODEGEN_INTERPRETER = ROOT / ".venv/bin/python"
FUSION_TEA = ROOT / "tests/fixtures/fusion_tea"
EXPECTED_LCOE = 270.1211779380445
LCOE_CHANNEL = "hif_plant_pkg__hif_plant__lcoe_calc__lcoe"
AVAILABILITY_KEY = "hif_plant_pkg__hif_plant__availability"
THERMAL_EFFICIENCY_KEY = "hif_plant_pkg__hif_plant__thermal_efficiency"
AVAILABILITY_OUTPUTS = {
    "hif_plant_pkg__hif_plant__lcoe_calc__lcoe",
    "hif_plant_pkg__hif_plant__meier_coe_calc__coe_cents_kwh",
}
THERMAL_EFFICIENCY_OUTPUTS = {
    "hif_plant_pkg__hif_plant__lcoe_calc__lcoe",
    "hif_plant_pkg__hif_plant__recirc_calc__f_recirc",
}
PROJECTOR_MARKER = "instance-projector/v1"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_json_exclusive(path: Path, value: object) -> None:
    payload = json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        allow_nan=False,
    ).encode() + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _read_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def _helper_environment() -> dict[str, str]:
    environment = os.environ.copy()
    paths = [str(ROOT / "src"), str(AGENTIC_ROOT / "src")]
    if environment.get("PYTHONPATH"):
        paths.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(paths)
    return environment


def _run_codegen_helper(action: str, candidate_dir: Path, *args: str) -> None:
    subprocess.run(
        [
            str(CODEGEN_INTERPRETER),
            str(Path(__file__).resolve()),
            action,
            str(candidate_dir),
            *args,
        ],
        cwd=ROOT,
        env=_helper_environment(),
        check=True,
    )


def _projected_digest(graph: Any) -> str:
    payload = graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    return _sha256(
        json.dumps(
            {"projector_semantics": PROJECTOR_MARKER, "computation_graph": payload},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    )


def _graph_counts(graph: Any) -> dict[str, int]:
    return {
        "occurrences": len(graph.occurrences),
        "attributes": len(graph.attrs),
        "calculations": len(graph.calcs),
        "constraints": len(graph.constraints),
        "nodes": len(graph.attrs) + len(graph.calcs) + len(graph.constraints),
        "edges": sum(node.alias_target is not None for node in graph.attrs.values())
        + sum(len(node.inputs) for node in graph.calcs.values())
        + sum(len(node.inputs) for node in graph.constraints.values()),
    }


def _codegen_measure(candidate_dir: Path) -> None:
    import resource

    from sysml_codegen.cli import GenerationConfig, run_codegen
    from sysml_codegen.elaboration import project
    from sysml_codegen.orchestration.pipeline_builder import _load_and_elaborate
    from sysml_codegen.snapshot import capture_snapshot, load_snapshot
    from sysml_codegen.snapshot.source_manifest import admit_sources

    output = candidate_dir / "scale-codegen.json"
    scale_root = candidate_dir / "scale"
    labels = ("warmup", "measured-1", "measured-2", "measured-3")
    records: list[dict[str, object]] = []
    for label in labels:
        run_root = scale_root / label
        run_root.mkdir(parents=True)

        start = time.perf_counter_ns()
        with admit_sources([FUSION_TEA]) as admission:
            live_graph = _load_and_elaborate(admission)
        load_seconds = (time.perf_counter_ns() - start) / 1_000_000_000

        start = time.perf_counter_ns()
        projected = project(live_graph)
        projection_seconds = (time.perf_counter_ns() - start) / 1_000_000_000

        snapshot = run_root / "fusion-tea-v6.json"
        start = time.perf_counter_ns()
        capture_snapshot([FUSION_TEA], snapshot)
        capture_seconds = (time.perf_counter_ns() - start) / 1_000_000_000
        snapshot.chmod(0o444)

        in_place = load_snapshot(snapshot)
        relocated = run_root / "relocated" / "fusion-tea-v6.json"
        relocated.parent.mkdir()
        shutil.copyfile(snapshot, relocated)
        relocated.chmod(0o444)
        moved_graph = load_snapshot(relocated)

        package_name = f"item7_scale_{label.replace('-', '_')}"
        package = run_root / package_name
        start = time.perf_counter_ns()
        generated = run_codegen(
            GenerationConfig(
                output_path=package,
                models_path=FUSION_TEA,
                package_name=package_name,
                overwrite=True,
            )
        )
        generation_seconds = (time.perf_counter_ns() - start) / 1_000_000_000
        if not generated:
            raise RuntimeError(f"Fusion Tea generation failed for {label}")

        fingerprint = _read_json(snapshot)["instance_graph"]["fingerprint"]
        record = {
            "label": label,
            "load_elaborate_seconds": load_seconds,
            "projection_seconds": projection_seconds,
            "capture_seconds": capture_seconds,
            "generation_seal_seconds": generation_seconds,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "envelope_bytes": snapshot.stat().st_size,
            "graph_counts": _graph_counts(live_graph),
            "fingerprints": {
                "live_capture": fingerprint,
                "in_place": _read_json(snapshot)["instance_graph"]["fingerprint"],
                "relocated": _read_json(relocated)["instance_graph"]["fingerprint"],
            },
            "projected_digests": {
                "live": _projected_digest(projected),
                "in_place": _projected_digest(project(in_place)),
                "relocated": _projected_digest(project(moved_graph)),
            },
            "snapshot": str(snapshot.relative_to(candidate_dir)),
            "package": str(package.relative_to(candidate_dir)),
            "package_name": package_name,
        }
        record["codegen_budgets_met"] = (
            load_seconds <= 10.0
            and projection_seconds <= 2.0
            and capture_seconds <= 5.0
            and generation_seconds <= 30.0
            and record["peak_rss_kib"] <= 512 * 1024
            and record["envelope_bytes"] <= 25 * 1024 * 1024
            and len(set(record["fingerprints"].values())) == 1
            and len(set(record["projected_digests"].values())) == 1
        )
        records.append(record)

    measured = records[1:]
    stable = len(
        {
            json.dumps(
                {
                    "graph_counts": item["graph_counts"],
                    "fingerprints": item["fingerprints"],
                    "projected_digests": item["projected_digests"],
                    "envelope_bytes": item["envelope_bytes"],
                },
                sort_keys=True,
            )
            for item in measured
        }
    ) == 1
    _write_json_exclusive(
        output,
        {
            "warmup_runs": 1,
            "records": records,
            "stable_counts_and_digests": stable,
            "all_codegen_budgets_met": stable
            and all(bool(item["codegen_budgets_met"]) for item in records),
        },
    )


def _prepare_real_teax(candidate_dir: Path) -> None:
    from sysml_codegen.cli import GenerationConfig, run_codegen
    from sysml_codegen.contracts.verify import verify_package

    batch = _read_json(candidate_dir / "accepted-batch.json")
    fusion_row = next(row for row in batch["rows"] if row["id"] == "B37-15")
    snapshot = candidate_dir / fusion_row["artifact"]
    root = candidate_dir / "real-teax"
    routes = {
        "live": {
            "package_name": "item7_teax_live",
            "models_path": FUSION_TEA,
            "from_snapshot": None,
        },
        "relocated": {
            "package_name": "item7_teax_relocated",
            "models_path": None,
            "from_snapshot": snapshot,
        },
    }
    result: dict[str, object] = {"routes": {}}
    for route, configuration in routes.items():
        package_name = str(configuration["package_name"])
        package = root / route / package_name
        start = time.perf_counter_ns()
        generated = run_codegen(
            GenerationConfig(
                output_path=package,
                models_path=configuration["models_path"],
                from_snapshot=configuration["from_snapshot"],
                package_name=package_name,
                overwrite=True,
            )
        )
        duration = (time.perf_counter_ns() - start) / 1_000_000_000
        if not generated:
            raise RuntimeError(f"{route} Fusion Tea generation failed")
        verification = verify_package(package, package_name)
        result["routes"][route] = {
            "package": str(package.relative_to(candidate_dir)),
            "package_name": package_name,
            "generation_seal_seconds": duration,
            "trusted_verifier_ok": verification.ok,
            "trusted_diagnostics": [
                {
                    "kind": item.kind,
                    "path": item.path,
                    "message": item.message,
                }
                for item in verification.diagnostics
            ],
        }
    _write_json_exclusive(candidate_dir / "real-teax-preparation.json", result)


def _seal_package(candidate_dir: Path, package: Path, package_name: str) -> None:
    import argparse as argparse_module

    from sysml_codegen.cli import cmd_seal

    if not package.resolve().is_relative_to(candidate_dir.resolve()):
        raise RuntimeError("refusing to seal a package outside the candidate directory")
    result = cmd_seal(
        argparse_module.Namespace(
            package_dir=package,
            package_name=package_name,
            verbose=False,
        )
    )
    if result != 0:
        raise RuntimeError(f"failed to seal {package}")


def _assert_real_teax_environment() -> dict[str, str]:
    import simkit

    prefix = Path(sys.prefix).resolve()
    if prefix != (TEAX_ROOT / ".venv").resolve():
        raise RuntimeError(f"execution is not using the pinned TEAx environment: {prefix}")
    simkit_path = Path(simkit.__file__).resolve()
    if not simkit_path.is_relative_to(TEAX_ROOT.resolve()):
        raise RuntimeError(f"simkit did not load from the pinned TEAx checkout: {simkit_path}")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=TEAX_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=TEAX_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != "fa0e06a99b070346e68a3b3c29cfec546f3ac728" or status:
        raise RuntimeError("the pinned TEAx checkout changed before execution")
    return {"head": head, "simkit_path": str(simkit_path), "python_prefix": str(prefix)}


def _diagnostics(result: Any) -> list[dict[str, object]]:
    return [
        {"kind": item.kind, "path": item.path, "message": item.message}
        for item in result.diagnostics
    ]


def _verify_both(package: Path, package_name: str) -> dict[str, object]:
    from sysml_codegen.contracts.verify import verify_package

    trusted = verify_package(package, package_name)
    emitted_namespace = runpy.run_path(str(package / "contracts/verify.py"))
    emitted = emitted_namespace["verify_package"](package, package_name)
    seal = _read_json(package / "contracts/package_contract.json")
    return {
        "trusted_ok": trusted.ok,
        "emitted_ok": emitted.ok,
        "trusted_diagnostics": _diagnostics(trusted),
        "emitted_diagnostics": _diagnostics(emitted),
        "diagnostics_equal": _diagnostics(trusted) == _diagnostics(emitted),
        "covered_hashes_sha256": _sha256(
            json.dumps(seal["artifact_hashes"], sort_keys=True, separators=(",", ":")).encode()
        ),
    }


def _purge_package(package_name: str) -> None:
    for module_name in list(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            del sys.modules[module_name]
    importlib.invalidate_caches()


def _json_value(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _root_value(value: Any) -> float:
    if hasattr(value, "root"):
        return float(value.root)
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(mode="json")
        if isinstance(dumped, dict) and "root" in dumped:
            return float(dumped["root"])
    return float(value)


def _execute_package(
    package: Path,
    package_name: str,
    output_dir: Path,
) -> dict[str, object]:
    from simkit.core.pipeline import execute_pipeline

    _purge_package(package_name)
    parent = str(package.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    generated = importlib.import_module(package_name)
    factory = getattr(generated, f"create_{package_name}_registry")
    backing = factory.__globals__.get("create_registry")
    public_registry = getattr(backing, "__module__", "") == "simkit.core.registry_builder"
    registry = factory()
    start = time.perf_counter_ns()
    result = execute_pipeline(
        package / "pipelines/pipeline.yaml",
        output_dir,
        registry=registry,
        custom_schema_types=generated.CUSTOM_SCHEMA_TYPES,
    )
    duration = (time.perf_counter_ns() - start) / 1_000_000_000
    outputs = {key: _json_value(value) for key, value in result.outputs.items()}
    return {
        "duration_seconds": duration,
        "outputs": outputs,
        "lcoe": _root_value(result.outputs[LCOE_CHANNEL]),
        "public_registry": public_registry,
        "registry_type": f"{type(registry).__module__}.{type(registry).__name__}",
    }


def _mutated_package(
    candidate_dir: Path,
    route: str,
    source: Path,
    package_name: str,
    field: str,
    value: float,
) -> Path:
    destination = candidate_dir / "real-teax-mutations" / route / field / package_name
    shutil.copytree(source, destination)
    input_path = destination / "inputs/hif_plant_params.json"
    inputs = _read_json(input_path)
    inputs[field] = value
    input_path.write_text(json.dumps(inputs, sort_keys=True, indent=2) + "\n")
    _run_codegen_helper("seal-package", candidate_dir, str(destination), package_name)
    return destination


def _changed_outputs(baseline: dict[str, object], changed: dict[str, object]) -> set[str]:
    keys = set(baseline) | set(changed)
    return {key for key in keys if baseline.get(key) != changed.get(key)}


def run_real_teax_acceptance(candidate_dir: Path) -> dict[str, object]:
    """Generate, verify, and execute live/relocated packages plus C25/C2 mutations."""
    output = candidate_dir / "real-teax.json"
    if output.exists():
        return _read_json(output)
    evidence: dict[str, object] = {
        "status": "running",
        "packages": [],
        "environment": _assert_real_teax_environment(),
    }
    try:
        preparation_path = candidate_dir / "real-teax-preparation.json"
        if not preparation_path.exists():
            _run_codegen_helper("prepare-real-teax", candidate_dir)
        preparation = _read_json(preparation_path)
        route_results: dict[str, object] = {}
        for route in ("live", "relocated"):
            prepared = preparation["routes"][route]
            package = candidate_dir / prepared["package"]
            package_name = prepared["package_name"]
            verification = _verify_both(package, package_name)
            baseline = _execute_package(
                package,
                package_name,
                candidate_dir / "real-teax-outputs" / route / "baseline",
            )
            mutations: dict[str, object] = {}
            for field, value in (
                (AVAILABILITY_KEY, 0.91),
                (THERMAL_EFFICIENCY_KEY, 0.44),
            ):
                mutated = _mutated_package(
                    candidate_dir,
                    route,
                    package,
                    package_name,
                    field,
                    value,
                )
                mutation_verification = _verify_both(mutated, package_name)
                execution = _execute_package(
                    mutated,
                    package_name,
                    candidate_dir / "real-teax-outputs" / route / field,
                )
                mutations[field] = {
                    "package": str(mutated.relative_to(candidate_dir)),
                    "verification": mutation_verification,
                    "execution": execution,
                    "changed_outputs": sorted(
                        _changed_outputs(baseline["outputs"], execution["outputs"])
                    ),
                }
            route_results[route] = {
                "package": prepared["package"],
                "package_name": package_name,
                "generation_seal_seconds": prepared["generation_seal_seconds"],
                "verification": verification,
                "baseline": baseline,
                "mutations": mutations,
            }

        live = route_results["live"]
        relocated = route_results["relocated"]
        availability_sets = {
            tuple(route_results[route]["mutations"][AVAILABILITY_KEY]["changed_outputs"])
            for route in route_results
        }
        thermal_sets = {
            tuple(route_results[route]["mutations"][THERMAL_EFFICIENCY_KEY]["changed_outputs"])
            for route in route_results
        }
        evidence.update(
            {
                "status": "passed",
                "packages": ["live", "relocated"],
                "routes": route_results,
                "trusted_verifier_agreement": all(
                    route_results[route]["verification"]["trusted_ok"]
                    and route_results[route]["verification"]["emitted_ok"]
                    and route_results[route]["verification"]["diagnostics_equal"]
                    for route in route_results
                ),
                "public_registry": all(
                    route_results[route]["baseline"]["public_registry"]
                    for route in route_results
                ),
                "lcoe_matches": all(
                    math.isclose(
                        route_results[route]["baseline"]["lcoe"],
                        EXPECTED_LCOE,
                        rel_tol=1e-6,
                    )
                    for route in route_results
                ),
                "baseline_routes_equal": live["baseline"]["outputs"]
                == relocated["baseline"]["outputs"],
                "c25_every_and_only": availability_sets == {tuple(sorted(AVAILABILITY_OUTPUTS))},
                "c2_every_and_only": thermal_sets
                == {tuple(sorted(THERMAL_EFFICIENCY_OUTPUTS))},
            }
        )
    except BaseException as error:
        evidence.update(
            {
                "status": "failed",
                "error": f"{type(error).__name__}: {error}",
            }
        )
        _write_json_exclusive(output, evidence)
        raise
    _write_json_exclusive(output, evidence)
    return evidence


def measure_fusion_tea_acceptance(candidate_dir: Path) -> dict[str, object]:
    """Collect one warm-up plus three measured runs and real-TEAx durations."""
    output = candidate_dir / "scale.json"
    if output.exists():
        return _read_json(output)
    evidence: dict[str, object] = {
        "status": "running",
        "environment": _assert_real_teax_environment(),
    }
    try:
        codegen_path = candidate_dir / "scale-codegen.json"
        if not codegen_path.exists():
            _run_codegen_helper("measure-codegen", candidate_dir)
        codegen = _read_json(codegen_path)
        executions: list[dict[str, object]] = []
        for record in codegen["records"]:
            package = candidate_dir / record["package"]
            package_name = record["package_name"]
            verification = _verify_both(package, package_name)
            execution = _execute_package(
                package,
                package_name,
                candidate_dir / "scale-teax-outputs" / record["label"],
            )
            executions.append(
                {
                    "label": record["label"],
                    "duration_seconds": execution["duration_seconds"],
                    "lcoe": execution["lcoe"],
                    "public_registry": execution["public_registry"],
                    "verification": verification,
                    "budget_met": execution["duration_seconds"] <= 30.0,
                }
            )
        evidence.update(
            {
                "status": "passed",
                "warmup_runs": 1,
                "warmup": codegen["records"][0],
                "measurements": codegen["records"][1:],
                "teax_executions": executions,
                "stable_counts_and_digests": codegen["stable_counts_and_digests"],
                "all_budgets_met": codegen["all_codegen_budgets_met"]
                and all(item["budget_met"] for item in executions),
            }
        )
    except BaseException as error:
        evidence.update(
            {
                "status": "failed",
                "error": f"{type(error).__name__}: {error}",
            }
        )
        _write_json_exclusive(output, evidence)
        raise
    _write_json_exclusive(output, evidence)
    return evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("measure-codegen", "prepare-real-teax"):
        command = subparsers.add_parser(action)
        command.add_argument("candidate_dir", type=Path)
    seal = subparsers.add_parser("seal-package")
    seal.add_argument("candidate_dir", type=Path)
    seal.add_argument("package", type=Path)
    seal.add_argument("package_name")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.action == "measure-codegen":
        _codegen_measure(args.candidate_dir)
    elif args.action == "prepare-real-teax":
        _prepare_real_teax(args.candidate_dir)
    elif args.action == "seal-package":
        _seal_package(args.candidate_dir, args.package, args.package_name)
    else:
        raise AssertionError(args.action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
