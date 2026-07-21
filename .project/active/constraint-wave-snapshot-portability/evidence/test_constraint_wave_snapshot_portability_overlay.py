"""Frozen Item 4 R-6/R-11 historical overlay.

Every desired-behavior node is independently runnable against an archived source tree selected
through ``EXPECTED_CODEGEN_REPO``. Compatibility controls pin behavior that was already correct.
"""

from __future__ import annotations

import copy
import json
import logging
import os
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
    parse,
)
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

from sysml_codegen.analysis import constraint_lowering
from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.snapshot import SnapshotFormatError
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from sysml_codegen.snapshot.serializer import serialize_extraction_snapshot

EXPECTED_REPO = Path(os.environ.get("EXPECTED_CODEGEN_REPO", Path.cwd())).resolve()
LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"


def _identity(name: str | None, qualified_name: str | None) -> IdentityFact:
    return IdentityFact(kind="AssertConstraintUsage", name=name, qualified_name=qualified_name)


def _non_numerical(file: Path, *, name: str | None, line: int = 10) -> ConstraintUsageFact:
    identity = _identity(name, f"Pkg__{name}" if name else None)
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
        location=LocationFact(str(file), line, 2),
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


def _facts(root: Path, *, named: bool = True) -> ConstraintFacts:
    root.mkdir(parents=True, exist_ok=True)
    model = root / "model.sysml"
    model.write_text("")
    return ConstraintFacts(
        definitions=[],
        usages=[_non_numerical(model, name="status" if named else None)],
        contexts=[],
        diagnostics=[],
    )


def _serialize(facts: ConstraintFacts, root: Path) -> dict:
    return serialize_extraction_snapshot(
        model_name="historical",
        calc_defs=[],
        calc_usages=[],
        design_attributes={},
        hierarchy_data=None,
        aggregation_expressions=[],
        computed_attributes=[],
        channel_aliases=[],
        constraint_facts=facts,
        part_occurrences={},
        constraint_lowering_mode="applied",
        model_paths=[root],
    )


def _lower(facts: ConstraintFacts, root: Path, *, mode: str = "live"):
    return lower_constraints(
        facts,
        occ_index=None,
        registry=None,
        design_attrs={},
        calc_usages=[],
        source_location_mode=mode,
        source_roots=[root] if mode == "live" else [],
    )


def _valid_snapshot() -> dict:
    return json.loads(
        (EXPECTED_REPO / "tests/fixtures/chain_spike_model/extraction_snapshot.json").read_text()
    )


def _write_snapshot(tmp_path: Path, raw: object) -> Path:
    path = tmp_path / "extraction_snapshot.json"
    path.write_text(json.dumps(raw))
    return path


def test_r6_named_capture_is_canonical_reviewed(tmp_path):
    root = tmp_path / "models"
    facts = _facts(root)
    raw_before = facts.usages[0].location.file
    snapshot = _serialize(facts, root)
    assert snapshot["constraint_facts"]["usages"][0]["location"]["file"] == "root-0/model.sysml"
    assert facts.usages[0].location.file == raw_before


def test_r6_named_warning_and_record_are_canonical_reviewed(tmp_path, caplog):
    root = tmp_path / "models"
    facts = _facts(root)
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        [record] = _lower(facts, root)
    [warning] = [entry.getMessage() for entry in caplog.records if entry.name == LOWERING_LOGGER]
    assert "root-0/model.sysml:10:2" in warning
    assert record.exclusion.location == "root-0/model.sysml:10:2"


def test_r6_non_numerical_route_projects_once_reviewed(tmp_path, monkeypatch):
    root = tmp_path / "models"
    facts = _facts(root, named=False)
    calls: list[str] = []
    real = constraint_lowering.map_live_source_referent

    def counted(raw_file, roots):
        calls.append(raw_file)
        return real(raw_file, roots)

    monkeypatch.setattr(constraint_lowering, "map_live_source_referent", counted)
    _lower(facts, root)
    assert calls == [str(root / "model.sysml")]


def test_r6_named_id_and_fingerprint_are_root_independent_reviewed(tmp_path):
    roots = [tmp_path / "a", tmp_path / "b"]
    records = [_lower(_facts(root), root)[0] for root in roots]
    assert records[0].constraint_id == records[1].constraint_id
    assert records[0].constraint_id == "Pkg_status__status__9532d77db3859f40"
    assert records[0].model_dump_json() == records[1].model_dump_json()


@pytest.mark.parametrize(
    "mutate,pointer",
    [
        (lambda _raw: [], "/"),
        (lambda raw: {**raw, "constraint_facts": []}, "/constraint_facts"),
        (lambda raw: {**raw, "part_occurrences": []}, "/part_occurrences"),
        (
            lambda raw: {**raw, "constraint_facts": {**raw["constraint_facts"], "usages": 42}},
            "/constraint_facts/usages",
        ),
        (
            lambda raw: {**raw, "constraint_facts": {**raw["constraint_facts"], "usages": [[]]}},
            "/constraint_facts/usages/0",
        ),
        (
            lambda raw: {**raw, "part_occurrences": {"Pkg::Host": [{"part_def_qn": "Pkg::Host"}]}},
            "/part_occurrences/Pkg::Host/0/steps",
        ),
        (
            lambda raw: {**raw, "part_occurrences": {"Pkg::Host": [{"part_def_qn": "Pkg::Host", "steps": {}}]}},
            "/part_occurrences/Pkg::Host/0/steps",
        ),
        (lambda raw: {**raw, "constraint_lowering_mode": []}, "/constraint_lowering_mode"),
    ],
)
def test_r11_malformed_shape_is_contextual_domain_error_reviewed(tmp_path, mutate, pointer):
    malformed = mutate(_valid_snapshot())
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_snapshot(tmp_path, malformed))
    message = str(caught.value)
    assert pointer in message
    assert "Expected" in message
    assert "Recapture the snapshot." in message


def test_compat_anonymous_route_parity_control(tmp_path):
    root = tmp_path / "models"
    facts = _facts(root, named=False)
    snapshot = _serialize(facts, root)
    replay_facts = parse(json.dumps(snapshot["constraint_facts"]))
    assert _lower(facts, root)[0].model_dump_json() == _lower(replay_facts, root, mode="snapshot")[0].model_dump_json()


def test_compat_valid_empties_nullable_optional_and_legacy_degrade_control(tmp_path, caplog):
    raw = _valid_snapshot()
    raw["constraint_facts"] = {
        "schema_version": "constraint-facts/v1",
        "definitions": [],
        "usages": [],
        "contexts": [],
        "diagnostics": [],
    }
    raw["part_occurrences"] = {"Pkg::Host": []}
    raw.pop("compilation_results", None)
    loaded = load_extraction_snapshot(_write_snapshot(tmp_path, raw))
    assert loaded["constraint_facts"].usages == []
    assert loaded["part_occurrences"] == {"Pkg::Host": []}
    assert loaded["compilation_results"] == {}
    assert "no compilation_results section" in caplog.text


def test_compat_unknown_extra_v1_accepted_and_v2_rejected_control(tmp_path):
    raw = _valid_snapshot()
    raw["constraint_facts"]["extra"] = {"schema_version": "expression-ir/v1"}
    load_extraction_snapshot(_write_snapshot(tmp_path, raw))
    bad = copy.deepcopy(raw)
    bad["constraint_facts"]["extra"]["schema_version"] = "expression-ir/v2"
    with pytest.raises(SnapshotFormatError, match="expression-ir/v2"):
        load_extraction_snapshot(_write_snapshot(tmp_path, bad))
