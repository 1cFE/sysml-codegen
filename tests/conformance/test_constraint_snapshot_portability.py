"""Item 4 exact relocation projection for named and anonymous exclusions."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Any

from agentic_mbse.sysml import constraint_facts as constraint_facts_module
from agentic_mbse.sysml.constraint_facts import (
    ConstraintSource,
    ConstraintUsageFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

from sysml_codegen.analysis.constraint_lowering import (
    associate_usage_decisions,
    is_excluded_usage,
)
from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from sysml_codegen.snapshot.capture import capture_snapshot
from sysml_codegen.snapshot.serializer import snapshot_to_json
from tests.conftest import FIXTURES_DIR, requires_license

LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"
PACKAGE_NAME = "snapshot_portability"
SNAPSHOT_MANIFEST_SHA256 = "bf2b3d49ad6710fa2032fa940932ec7e1a0b6ea846a6d9b7dbcd7e6f370a8266"


def _anonymous_non_numerical() -> ConstraintUsageFact:
    identity = IdentityFact(kind="AssertConstraintUsage", name=None, qualified_name=None)
    predicate = OperatorNode(
        operator="==",
        operands=[
            LiteralNode(
                literal=LiteralFact(kind="LiteralBoolean", value=True, result_type="boolean"),
                operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
            ),
            LiteralNode(
                literal=LiteralFact(kind="LiteralBoolean", value=False, result_type="boolean"),
                operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    return ConstraintUsageFact(
        identity=identity,
        location=LocationFact(file="root-0/model.sysml", line=18, column=9),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Pkg"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _eligible_numeric() -> ConstraintUsageFact:
    identity = IdentityFact(
        kind="AssertConstraintUsage",
        name="portable_positive",
        qualified_name="Pkg::portable_positive",
    )
    predicate = OperatorNode(
        operator=">",
        operands=[
            LiteralNode(
                literal=LiteralFact(kind="LiteralInteger", value=1, result_type="integer"),
                operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
            ),
            LiteralNode(
                literal=LiteralFact(kind="LiteralInteger", value=0, result_type="integer"),
                operand_type=OperandTypeFact(category="integer", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    return ConstraintUsageFact(
        identity=identity,
        location=LocationFact(file="root-0/model.sysml", line=22, column=9),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Pkg"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _collision_free_snapshot_bytes() -> bytes:
    raw = json.loads((FIXTURES_DIR / "catf_mfe_model/extraction_snapshot.json").read_text())
    facts = constraint_facts_module.parse(json.dumps(raw["constraint_facts"]))
    facts.usages.append(_anonymous_non_numerical())
    facts.usages.append(_eligible_numeric())
    raw["constraint_facts"] = json.loads(constraint_facts_module.serialize(facts))
    return snapshot_to_json(raw).encode("utf-8")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )


def _warnings(caplog) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING and record.name == LOWERING_LOGGER
    ]


def _manifest_from_context_and_output(
    snapshot: Path, context: Any, output: Path, warning_values: list[str]
) -> dict[str, Any]:
    raw = json.loads(snapshot.read_text())
    facts = constraint_facts_module.parse(json.dumps(raw["constraint_facts"]))
    selected = tuple(
        index
        for index, (usage, decision) in enumerate(associate_usage_decisions(facts))
        if is_excluded_usage(usage, decision)
    )
    assert any(facts.usages[index].identity.name for index in selected)
    assert any(facts.usages[index].identity.name is None for index in selected)
    assert any(index not in selected for index in range(len(facts.usages)))
    excluded_facts = [raw["constraint_facts"]["usages"][index] for index in selected]
    catalog = context.computation_graph.constraint_catalog
    assert catalog is not None
    catalog_dump = catalog.model_dump(mode="json")
    model_contract_path = output / "contracts/model_contract.json"
    package_contract_path = output / "contracts/package_contract.json"
    report_path = output / "modules/constraints/constraintreportaggregatormodule.py"
    model_contract = json.loads(model_contract_path.read_text())
    package_contract = json.loads(package_contract_path.read_text())
    return {
        "excluded_facts": _canonical_bytes(excluded_facts),
        "warnings": warning_values,
        "excluded_records": _canonical_bytes(catalog_dump["excluded_records"]),
        "catalog_fingerprint": catalog_dump["fingerprint"],
        "model_contract_bytes": model_contract_path.read_bytes(),
        "model_contract_excluded": _canonical_bytes(
            model_contract["constraint_catalog"]["excluded_records"]
        ),
        "model_contract_catalog_fingerprint": model_contract["constraint_catalog"]["fingerprint"],
        "semantic_fingerprint": model_contract["semantic_fingerprint"],
        "report_bytes": report_path.read_bytes(),
        "model_contract_artifact_hash": package_contract["artifact_hashes"][
            "contracts/model_contract.json"
        ],
        "report_artifact_hash": package_contract["artifact_hashes"][
            "modules/constraints/constraintreportaggregatormodule.py"
        ],
    }


def _collect_live_manifest(
    models_root: Path, snapshot: Path, output: Path, caplog
) -> dict[str, Any]:
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        context = build_pipeline_context([models_root], lower_constraints_enabled=True)
    warning_values = _warnings(caplog)
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            models_path=models_root,
            package_name=PACKAGE_NAME,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )
    return _manifest_from_context_and_output(snapshot, context, output, warning_values)


def _collect_replay_manifest(snapshot: Path, output: Path, caplog) -> dict[str, Any]:
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        context = build_pipeline_context_from_snapshot(snapshot)
    warning_values = _warnings(caplog)
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=snapshot,
            package_name=PACKAGE_NAME,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )
    return _manifest_from_context_and_output(snapshot, context, output, warning_values)


def _assert_manifest_equal_and_root_free(
    first: dict[str, Any], second: dict[str, Any], roots: list[Path]
) -> None:
    assert first == second
    payload = b"\n".join(
        value if isinstance(value, bytes) else _canonical_bytes(value) for value in first.values()
    )
    for root in roots:
        encoded = root.as_posix().encode()
        assert encoded not in payload


def _manifest_sha256(manifest: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    for key, value in sorted(manifest.items()):
        payload = value if isinstance(value, bytes) else _canonical_bytes(value)
        digest.update(len(key).to_bytes(4, "big"))
        digest.update(key.encode("utf-8"))
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _write_replay_pair(tmp_path: Path) -> tuple[Path, Path, list[Path]]:
    snapshot_bytes = _collision_free_snapshot_bytes()
    source_bytes = (FIXTURES_DIR / "catf_mfe_model/designs/catf_mfe/system.sysml").read_bytes()
    roots = [tmp_path / "replay-a/models", tmp_path / "replay-b/models"]
    snapshots: list[Path] = []
    for root in roots:
        root.mkdir(parents=True)
        (root / "model.sysml").write_bytes(source_bytes)
        snapshot = root / "extraction_snapshot.json"
        snapshot.write_bytes(snapshot_bytes)
        assert (
            hashlib.sha256(snapshot.read_bytes()).digest()
            == hashlib.sha256(snapshot_bytes).digest()
        )
        snapshots.append(snapshot)
    return snapshots[0], snapshots[1], roots


def _assert_live_controls(snapshot: Path) -> None:
    raw = json.loads(snapshot.read_text())
    facts = constraint_facts_module.parse(json.dumps(raw["constraint_facts"]))
    selected = tuple(
        index
        for index, (usage, decision) in enumerate(associate_usage_decisions(facts))
        if is_excluded_usage(usage, decision)
    )
    assert len(facts.usages) == 3
    assert {facts.usages[index].identity.name for index in selected} == {
        "status_annotation",
        None,
    }
    assert {
        facts.usages[index].location.file
        for index in selected
        if facts.usages[index].location is not None
    } == {"root-0/model.sysml"}
    [eligible] = [
        facts.usages[index] for index in range(len(facts.usages)) if index not in selected
    ]
    assert eligible.identity.name == "positive_value"


def test_snapshot_only_moved_replay_manifest(tmp_path, caplog):
    snapshot_a, snapshot_b, roots = _write_replay_pair(tmp_path)
    manifest_a = _collect_replay_manifest(snapshot_a, tmp_path / "out-a", caplog)
    manifest_b = _collect_replay_manifest(snapshot_b, tmp_path / "out-b", caplog)
    assert len(json.loads(manifest_a["excluded_facts"])) == 66
    assert len(manifest_a["warnings"]) == 1
    _assert_manifest_equal_and_root_free(manifest_a, manifest_b, roots)
    assert _manifest_sha256(manifest_a) == SNAPSHOT_MANIFEST_SHA256


def test_manifest_collectors_use_distinct_live_and_replay_routes(tmp_path, monkeypatch):
    calls: list[tuple[str, Any]] = []
    live_context = object()
    replay_context = object()
    snapshot = tmp_path / "extraction_snapshot.json"
    snapshot.write_text("{}")

    def fake_live_builder(paths, *, lower_constraints_enabled):
        calls.append(("live_context", (paths, lower_constraints_enabled)))
        return live_context

    def fake_replay_builder(path):
        calls.append(("replay_context", path))
        return replay_context

    def fake_codegen(config):
        calls.append(("generation", config))
        return True

    def fake_manifest(path, context, output, warnings):
        calls.append(("manifest", (path, context, output, warnings)))
        return {"route": context}

    monkeypatch.setattr(
        "tests.conformance.test_constraint_snapshot_portability.build_pipeline_context",
        fake_live_builder,
    )
    monkeypatch.setattr(
        "tests.conformance.test_constraint_snapshot_portability.build_pipeline_context_from_snapshot",
        fake_replay_builder,
    )
    monkeypatch.setattr(
        "tests.conformance.test_constraint_snapshot_portability.run_codegen", fake_codegen
    )
    monkeypatch.setattr(
        "tests.conformance.test_constraint_snapshot_portability._manifest_from_context_and_output",
        fake_manifest,
    )

    class EmptyLog:
        records: list[Any] = []

        def clear(self):
            self.records.clear()

        def at_level(self, *_args, **_kwargs):
            from contextlib import nullcontext

            return nullcontext()

    caplog = EmptyLog()
    models_root = tmp_path / "models"
    live = _collect_live_manifest(models_root, snapshot, tmp_path / "live", caplog)
    replay = _collect_replay_manifest(snapshot, tmp_path / "replay", caplog)

    assert live == {"route": live_context}
    assert replay == {"route": replay_context}
    live_config = next(value for name, value in calls if name == "generation")
    replay_config = [value for name, value in calls if name == "generation"][1]
    assert live_config.models_path == models_root
    assert live_config.from_snapshot is None
    assert replay_config.models_path is None
    assert replay_config.from_snapshot == snapshot
    assert [name for name, _value in calls] == [
        "live_context",
        "generation",
        "manifest",
        "replay_context",
        "generation",
        "manifest",
    ]


@requires_license
def test_live_capture_replay_relocation_manifest(tmp_path, caplog):
    model_text = (FIXTURES_DIR / "constraint_non_numerical/model.sysml").read_text()
    model_text = model_text.replace("attribute value", "attribute safe_value")
    model_text = model_text.replace("value > 0.0", "safe_value > 0.0")
    model_text = model_text.replace(
        "assert constraint positive_value",
        'assert constraint { status == "on" }\n\n        assert constraint positive_value',
    )
    roots = [tmp_path / "checkout-a/models", tmp_path / "checkout-b/models"]
    snapshots: list[Path] = []
    for root in roots:
        root.mkdir(parents=True)
        (root / "model.sysml").write_text(model_text)
        snapshots.append(capture_snapshot([root], root / "extraction_snapshot.json"))
    assert (roots[0] / "model.sysml").read_bytes() == (roots[1] / "model.sysml").read_bytes()
    for snapshot in snapshots:
        _assert_live_controls(snapshot)
    moved = tmp_path / "moved/models"
    moved.mkdir(parents=True)
    shutil.copy2(roots[0] / "model.sysml", moved / "model.sysml")
    shutil.copy2(snapshots[0], moved / "extraction_snapshot.json")
    assert (moved / "extraction_snapshot.json").read_bytes() == snapshots[0].read_bytes()
    live_a = _collect_live_manifest(roots[0], snapshots[0], tmp_path / "live-a", caplog)
    live_b = _collect_live_manifest(roots[1], snapshots[1], tmp_path / "live-b", caplog)
    replay_a = _collect_replay_manifest(snapshots[0], tmp_path / "replay-a", caplog)
    _assert_manifest_equal_and_root_free(live_a, live_b, roots + [moved])
    _assert_manifest_equal_and_root_free(live_a, replay_a, roots + [moved])

    moved_replay = _collect_replay_manifest(
        moved / "extraction_snapshot.json", tmp_path / "moved-out", caplog
    )
    _assert_manifest_equal_and_root_free(replay_a, moved_replay, roots + [moved])
