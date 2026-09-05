"""Generated scalar fields survive real evaluation and reopened study evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.execution.real_teax import (
    generate_package_from_models,
    generate_package_from_snapshot,
    package_loader,
)

pytestmark = pytest.mark.execution

MODELS = Path(__file__).resolve().parents[1] / "fixtures" / "numeric_evidence"
SOURCE = "NumericEvidence__plant__source"
TWICE = "NumericEvidence__plant__split__twice"
SHIFTED = "NumericEvidence__plant__split__shifted"
TOTAL = "NumericEvidence__plant__combine__total"
EXPECTED = {
    3.0: {TWICE: 6.0, SHIFTED: 10.0, TOTAL: 16.0},
    5.0: {TWICE: 10.0, SHIFTED: 12.0, TOTAL: 22.0},
}


@pytest.mark.parametrize("route", ["live", "snapshot"])
def test_generated_mixed_outputs_survive_evaluation_and_reopened_study(tmp_path, route):
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge
    from simkit.study.definition import StudyDefinition
    from simkit.study.identity import digest_of
    from simkit.study.policy import ObjectivePolicy
    from simkit.study.query import StudyQuery
    from simkit.study.runner import StudyRunner
    from simkit.study.store import StudyStore
    from simkit.study.strategy import PreparedListStrategy

    name = f"numeric_evidence_{route}"
    package = tmp_path / name
    if route == "live":
        generate_package_from_models(MODELS, package, name)
    else:
        snapshot = capture_instance_graph_snapshot([MODELS], tmp_path / "snapshot.json")
        generate_package_from_snapshot(snapshot, package, name)
    evaluator = PreparedEvaluator(
        package_loader(package, name, tmp_path / "link"),
        package / "pipelines" / "pipeline.yaml",
        expects_constraint_report=False,
    )
    bridge = CandidateBridge(evaluator.entry_models)
    proposals = [{SOURCE: 3.0}, {SOURCE: 5.0}]
    for proposal in proposals:
        evidence = evaluator.evaluate(bridge.build(proposal))
        # Literal membership and values catch equal-but-incomplete projections.
        assert evidence.outputs == EXPECTED[proposal[SOURCE]]
        assert evidence.provenance.evidence_schema_version == "v3"

    contract = json.loads((package / "contracts" / "model_contract.json").read_text())
    definition = StudyDefinition(
        study_id=name,
        entry_models=evaluator.entry_models,
        strategy=PreparedListStrategy(proposals),
        validate_proposal=lambda proposal: proposal,
        policy=ObjectivePolicy((), {}),
        executable_fingerprint=evaluator.fingerprint,
        model_contract_fingerprint=contract["semantic_fingerprint"],
        input_schema_version="v1",
        evidence_schema_version=evaluator.EVIDENCE_SCHEMA_VERSION,
        study_definition_fingerprint=digest_of(proposals),
    )
    db = tmp_path / "study.db"
    store = StudyStore.create_or_open(db, definition.compatibility())
    try:
        store.acquire_lease()
        StudyRunner(store, definition, evaluator).run()
        store.release_lease()
    finally:
        store.close()

    reopened = StudyStore.create_or_open(db, definition.compatibility())
    try:
        cases = StudyQuery(reopened, package).cases()
        assert len(cases) == 2
        assert {case.inputs[SOURCE] for case in cases} == set(EXPECTED)
        for case in cases:
            assert case.state == "completed"
            assert case.outputs == EXPECTED[case.inputs[SOURCE]]
            assert case.executable_fingerprint == evaluator.fingerprint
            assert case.evidence_digest
    finally:
        reopened.close()
