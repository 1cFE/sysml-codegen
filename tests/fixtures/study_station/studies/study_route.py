"""The station study's execution route: the stock teax study lifecycle and nothing else.

Written for study-layer-to-codegen, as the neutral fixture's route. It loads the committed
package through teax's own seal-checking loader, runs a prepared list of points through teax's
``StudyRunner`` into a fresh store, and reads the cases back through ``StudyQuery``, which is
the surface ``verify`` samples. There is no adapter and no glue. A key the package does not
declare fails at teax's ``CandidateBridge`` before anything runs.

Two entry points:

- :func:`execute_baseline` runs the manifest's pinned baseline point. It deposits the two
  documents ``preflight gates`` reads, ``package_identity.json`` and ``baseline_result.json``.
- :func:`run_grid` runs :data:`GRID`, basin area by installed capacity, which carries both
  verdicts of the pump-fit constraint, for ``verify`` to sample.

Each writes its store as ``<out>/_work/<study id>.db``. The baseline result records the
store by its file name, which the integration seam resolves under ``<out>/_work/``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from sysml_codegen.study import common, identity

PACKAGE_NAME = "station_study"
BASELINE_STUDY = "station-baseline-v1"
GRID_STUDY = "station-grid-v1"
BASIN_AREA = "PumpStation__station__basin_area"
INSTALLED_CAPACITY = "PumpStation__station__installed_capacity"

#: Basin area by installed capacity. No point sits on the pump-fit boundary, and both
#: verdicts occur.
GRID = tuple(
    {BASIN_AREA: area, INSTALLED_CAPACITY: capacity}
    for area in (4.0, 8.0, 12.0, 16.0)
    for capacity in (0.20, 0.25, 0.30)
)


def run_points(
    study_id: str, proposals: Sequence[Mapping[str, float]], *, package_dir: Path, work: Path
) -> tuple[list[Any], Path]:
    """Run ``proposals`` into a new store ``work/<study_id>.db``; return its cases and path.

    Every case must complete under the package's own sealed fingerprint, or this raises.
    """
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.evaluation.package_load import ProvisionalPackageLoader
    from simkit.study.bridge import CandidateBridge
    from simkit.study.definition import StudyDefinition
    from simkit.study.identity import digest_of
    from simkit.study.policy import ObjectivePolicy
    from simkit.study.query import StudyQuery
    from simkit.study.runner import StudyRunner
    from simkit.study.store import StudyStore
    from simkit.study.strategy import PreparedListStrategy

    # The loader links this directory into place by name, so a relative one would dangle.
    package_dir = package_dir.resolve()
    db = work / f"{study_id}.db"
    if db.exists():
        raise FileExistsError(f"the store {db} already exists; each run writes a new one")
    work.mkdir(parents=True, exist_ok=True)
    evaluator = PreparedEvaluator(
        ProvisionalPackageLoader(
            package_dir=package_dir,
            package_name=PACKAGE_NAME,
            link_root=work / "link" / study_id,
        ),
        package_dir / "pipelines" / "pipeline.yaml",
        expects_constraint_report=True,
    )
    bridge = CandidateBridge(evaluator.entry_models)
    for proposal in proposals:
        bridge.build(proposal)
    contract = json.loads((package_dir / "contracts" / "model_contract.json").read_text())
    points = [dict(proposal) for proposal in proposals]
    definition = StudyDefinition(
        study_id=study_id,
        entry_models=evaluator.entry_models,
        strategy=PreparedListStrategy(points),
        validate_proposal=lambda proposal: proposal,
        policy=ObjectivePolicy((), {}),
        executable_fingerprint=evaluator.fingerprint,
        model_contract_fingerprint=contract["semantic_fingerprint"],
        input_schema_version="v1",
        evidence_schema_version=evaluator.EVIDENCE_SCHEMA_VERSION,
        study_definition_fingerprint=digest_of(points),
    )
    store = StudyStore.create_or_open(db, definition.compatibility())
    try:
        store.acquire_lease()
        StudyRunner(store, definition, evaluator).run()
        store.release_lease()
    finally:
        store.close()

    reopened = StudyStore.create_or_open(db, definition.compatibility())
    try:
        cases = StudyQuery(reopened, package_dir).cases()
    finally:
        reopened.close()
    incomplete = [case.candidate_id for case in cases if case.state != "completed"]
    if incomplete or len(cases) != len(points):
        raise RuntimeError(
            f"{study_id}: {len(cases)} of {len(points)} points came back, and these did not "
            f"complete: {incomplete}"
        )
    foreign = [case.candidate_id for case in cases
               if case.executable_fingerprint != evaluator.fingerprint]
    if foreign:
        raise RuntimeError(f"{study_id}: cases ran under another fingerprint: {foreign}")
    return cases, db


def execute_baseline(out: Path, *, package_dir: Path, manifest_path: Path) -> dict[str, Path]:
    """Run the manifest's pinned baseline point and deposit the two documents preflight reads."""
    out, package_dir = Path(out), Path(package_dir)
    point = json.loads(Path(manifest_path).read_text())["baseline"]["point"]
    (case,), store = run_points(
        BASELINE_STUDY, [point], package_dir=package_dir, work=out / "_work"
    )
    identity_path = common.write_document(
        identity.build_sealed(package_name=PACKAGE_NAME, package_root=package_dir),
        out / "package_identity.json",
    )
    baseline_path = common.write_document(
        baseline_result(case, store, package_dir), out / "baseline_result.json"
    )
    return {"identity": identity_path, "baseline_result": baseline_path}


def run_grid(out: Path, *, package_dir: Path) -> Path:
    """Run :data:`GRID` into ``<out>/_work/station-grid-v1.db`` and return the store's path."""
    _cases, store = run_points(
        GRID_STUDY, GRID, package_dir=Path(package_dir), work=Path(out) / "_work"
    )
    return store


def baseline_result(case: Any, store: Path, package_dir: Path) -> dict[str, Any]:
    """The ``study-baseline-result/v1`` document for one executed baseline case."""
    contract = json.loads((package_dir / "contracts" / "model_contract.json").read_text())
    catalog = {
        entry["constraint_id"]: entry
        for entry in contract["constraint_catalog"]["concrete_entries"]
    }
    return {
        "schema_version": "study-baseline-result/v1",
        "executed_under": {
            "identity_digest": case.executable_fingerprint,
            "store_id": store.name,
            "case_id": case.candidate_id,
        },
        "point": dict(case.inputs),
        "channels": dict(sorted(case.outputs.items())),
        "verdicts": [
            {
                "constraint_id": constraint_id,
                "definition_qualified_name": catalog[constraint_id]["definition_qualified_name"],
                "source_local_identity": catalog[constraint_id]["source_local_identity"],
                "status": status,
            }
            for constraint_id, status in sorted(case.verdicts.items())
        ],
    }
