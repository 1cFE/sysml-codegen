"""Item 8 Phase 2: snapshot v3 rejection matrix + round-trip (MF1/MF2, INV-8).

``load_extraction_snapshot`` gates all three new v3 sections
(``constraint_facts``, ``part_occurrences``, ``constraint_lowering_mode``) with
the full rejection matrix from design.md#architecture "Load / rejection" —
every corruption cell raises ``SnapshotFormatError`` with a re-capture
instruction, never a raw ``KeyError``, and an unrecognized
``constraint_lowering_mode`` is corruption, never a silent skip (MF2).

Fixtures are hand-mutated from a committed v3 snapshot plus a locally-built,
license-free ``ConstraintFacts`` carrying one real predicate (substituted in
place of the fixture's own facts section), so the embedded expression-ir
version check (cell g) has something to scan. The v2-rejection test hand-bumps
a v3 snapshot back down to v2, rather than relying on any committed snapshot
still being v2 (Phase 5 re-captured the whole corpus at v3 — INV-6 forbids
v2/v3 coexistence).
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any

import pytest
from agentic_mbse.sysml import constraint_facts as constraint_facts_module
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

from sysml_codegen import _upstream_pins
from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION, SnapshotFormatError
from sysml_codegen.snapshot import loader as snapshot_loader
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from tests.conftest import snapshot_fixture


def _real_literal(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="Real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _facts_with_predicate() -> ConstraintFacts:
    """One package-owned admitted assert — real embedded expression-ir nodes."""
    predicate = OperatorNode(
        operator="<=", operands=[_real_literal(1.0), _real_literal(2.0)], operand_type=None
    )
    usage = ConstraintUsageFact(
        identity=IdentityFact(kind="AssertConstraintUsage", name="ok", qualified_name="Design__ok"),
        location=None,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=IdentityFact(
                kind="AssertConstraintUsage", name=None, qualified_name="Design__ok"
            ),
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=IdentityFact(
                kind="AssertConstraintUsage", name=None, qualified_name="Design__ok"
            ),
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Design"),
        ),
        scope=IdentityFact(kind="AssertConstraintUsage", name=None, qualified_name="Design__ok"),
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )
    return ConstraintFacts(
        definitions=[],
        usages=[usage],
        contexts=[],
        diagnostics=[],
    )


def _v3_snapshot_dict() -> dict[str, Any]:
    """A committed current-version snapshot with its constraint section replaced by a
    locally-built, predicate-bearing facts object (so cell (g)'s embedded
    expression-ir scan has a real node to corrupt)."""
    raw = json.loads(snapshot_fixture("chain_spike_model").read_text())
    raw["snapshot_format_version"] = SNAPSHOT_FORMAT_VERSION
    raw["constraint_facts"] = json.loads(constraint_facts_module.serialize(_facts_with_predicate()))
    raw["part_occurrences"] = {}
    raw["constraint_lowering_mode"] = "applied"
    return raw


def _rewrite_first_ir_version(obj: Any, new_version: str) -> bool:
    """Find and overwrite the first embedded expression-ir ``schema_version``."""
    if isinstance(obj, dict):
        version = obj.get("schema_version")
        if isinstance(version, str) and version.startswith("expression-ir/"):
            obj["schema_version"] = new_version
            return True
        return any(_rewrite_first_ir_version(v, new_version) for v in obj.values())
    if isinstance(obj, list):
        return any(_rewrite_first_ir_version(v, new_version) for v in obj)
    return False


def _write_tmp(d: dict, tmp_path) -> Any:
    path = tmp_path / "extraction_snapshot.json"
    path.write_text(json.dumps(d))
    return path


def drop_key(key: str):
    def _mutate(d: dict) -> dict:
        d = copy.deepcopy(d)
        del d[key]
        return d

    return _mutate


def strip_facts_schema_version(d: dict) -> dict:
    d = copy.deepcopy(d)
    del d["constraint_facts"]["schema_version"]
    return d


def set_facts_version(version: str):
    def _mutate(d: dict) -> dict:
        d = copy.deepcopy(d)
        d["constraint_facts"]["schema_version"] = version
        return d

    return _mutate


def set_embedded_ir_version(version: str):
    def _mutate(d: dict) -> dict:
        d = copy.deepcopy(d)
        assert _rewrite_first_ir_version(d["constraint_facts"], version), (
            "fixture must embed at least one expression-ir node"
        )
        return d

    return _mutate


def set_mode(mode: str):
    def _mutate(d: dict) -> dict:
        d = copy.deepcopy(d)
        d["constraint_lowering_mode"] = mode
        return d

    return _mutate


@pytest.mark.parametrize(
    "mutate,match",
    [
        (drop_key("constraint_facts"), "constraint_facts"),  # (b) MF1
        (drop_key("part_occurrences"), "part_occurrences"),  # (c) MF1
        (drop_key("constraint_lowering_mode"), "constraint_lowering_mode"),  # (d) MF1
        (strip_facts_schema_version, "schema_version"),  # (e) torn facts dict
        (set_facts_version("constraint-facts/v2"), "constraint-facts"),  # (f) data pin
        (set_embedded_ir_version("expression-ir/v2"), "expression-ir"),  # (g) NH5 data pin
        (set_mode("off"), "constraint_lowering_mode"),  # (h) MF2 unknown enum
        (set_mode(""), "constraint_lowering_mode"),  # (h) empty
    ],
)
def test_v3_corruption_raises_with_recapture_message(tmp_path, mutate, match):
    bad = mutate(_v3_snapshot_dict())
    with pytest.raises(SnapshotFormatError, match=match) as exc_info:
        load_extraction_snapshot(_write_tmp(bad, tmp_path))
    assert "recapture" in str(exc_info.value).lower()


def test_v2_snapshot_rejected_by_version_gate(tmp_path):
    # Each envelope bump re-captures the whole corpus (INV-6: no coexistence), so a
    # stale-version fixture is hand-built here rather than read off a committed
    # snapshot. Keyed off the constant so the next bump needs no edit in this file.
    v2 = json.loads(snapshot_fixture("chain_spike_model").read_text())
    assert v2["snapshot_format_version"] == SNAPSHOT_FORMAT_VERSION
    v2["snapshot_format_version"] = SNAPSHOT_FORMAT_VERSION - 2
    with pytest.raises(SnapshotFormatError, match="format version"):
        load_extraction_snapshot(_write_tmp(v2, tmp_path))


def test_facts_and_occurrences_roundtrip_byte_identical(tmp_path):
    good = _v3_snapshot_dict()
    loaded = load_extraction_snapshot(_write_tmp(good, tmp_path))
    reserialized = json.loads(constraint_facts_module.serialize(loaded["constraint_facts"]))
    assert reserialized == good["constraint_facts"]  # INV-2, byte-identical
    assert loaded["part_occurrences"] == {}
    assert loaded["constraint_lowering_mode"] == "applied"


def _identity(name: str | None = "item") -> dict[str, Any]:
    return {"kind": "Thing", "name": name, "qualified_name": "Pkg::item" if name else None}


def _literal_ir() -> dict[str, Any]:
    return {
        "schema_version": "expression-ir/v1",
        "kind": "literal",
        "literal": {"kind": "LiteralString", "value": None, "result_type": None},
    }


def _rich_v3_snapshot_dict() -> dict[str, Any]:
    raw = _v3_snapshot_dict()
    literal = _literal_ir()
    operand_type = {
        "category": "quantity",
        "enumeration": None,
        "unit": {"unit": None, "dimension": None},
    }
    feature = {
        "schema_version": "expression-ir/v1",
        "kind": "feature_ref",
        "reference": {
            "source_name": None,
            "target": None,
            "target_types": [],
            "chain_segments": [],
        },
    }
    operator = {
        "schema_version": "expression-ir/v1",
        "kind": "operator",
        "operator": "and",
        "operands": [literal],
        "operand_type": None,
    }
    unit = {
        "schema_version": "expression-ir/v1",
        "kind": "unit",
        "value": literal,
        "unit_text": None,
    }
    invocation = {
        "schema_version": "expression-ir/v1",
        "kind": "invocation",
        "function_qn": None,
        "arguments": [literal],
        "operand_type": operand_type,
    }
    unsupported = {
        "schema_version": "expression-ir/v1",
        "kind": "unsupported",
        "node_kind": "Mystery",
        "diagnostic": "unsupported",
        "source_text": None,
    }
    raw["constraint_facts"] = {
        "schema_version": _upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION,
        "definitions": [
            {
                "identity": _identity("definition"),
                "formals": [
                    {
                        "name": None,
                        "qualified_name": None,
                        "types": [],
                        "has_default": True,
                        "default": feature,
                    }
                ],
                "predicate": operator,
            }
        ],
        "usages": [
            {
                "identity": _identity("usage"),
                "location": {"file": "root-0/model.sysml", "line": 1, "column": 2},
                "source": {
                    "form": "inline",
                    "effective_predicate_source": None,
                    "constraint_definition": None,
                    "referenced_feature_target": None,
                    "asserted_constraint": None,
                },
                "owner": {
                    "owner": None,
                    "owning_definition": {"kind": "package", "qualified_name": "Pkg"},
                },
                "scope": _identity("scope"),
                "membership_kind": None,
                "is_negated": None,
                "actuals": [
                    {
                        "name": None,
                        "direction": None,
                        "formal_targets": [],
                        "value": unit,
                    }
                ],
                "omitted_default_formals": [],
                "predicate": invocation,
                "inherited_into": [],
            }
        ],
        "contexts": [
            {
                "identity": _identity("context"),
                "general_types": [],
                "types": [],
                "inherited_constraints": [],
                "redefinitions": [{"feature": None, "redefines": None, "value": unsupported}],
            }
        ],
        "diagnostics": [
            {
                "kind": "non_finite_literal",
                "message": "message",
                "severity": "blocking",
                "operand_source": None,
                "location": None,
            }
        ],
        "ordinary_extra": {
            "schema_version": "expression-ir/v1",
            "kind": "literal",
            "literal": {"kind": "LiteralString", "value": "extra", "result_type": None},
        },
    }
    raw["part_occurrences"] = {
        "Pkg~/Host": [
            {
                "part_def_qn": "Pkg::Host",
                "steps": [
                    {
                        "owning_def_qn": "Pkg::Host",
                        "feature_name": "host",
                        "occurrence_index": None,
                    }
                ],
            }
        ]
    }
    return raw


def _at(root: dict[str, Any], path: tuple[str | int, ...]) -> Any:
    current: Any = root
    for token in path:
        current = current[token]
    return current


def _replace_path(root: dict[str, Any], path: tuple[str | int, ...], value: Any) -> None:
    _at(root, path[:-1])[path[-1]] = value


def _delete_path(root: dict[str, Any], path: tuple[str | int, ...]) -> None:
    del _at(root, path[:-1])[path[-1]]


def _pointer(path: tuple[str | int, ...]) -> str:
    return "/" + "/".join(str(token).replace("~", "~0").replace("/", "~1") for token in path)


@dataclass(frozen=True)
class ShapeCase:
    id: str
    path: tuple[str | int, ...]
    replacement: Any


REQUIRED_SHAPE_CASES = [
    (("constraint_facts",), []),
    (("constraint_facts", "definitions"), {}),
    (("constraint_facts", "definitions", 0), []),
    (("constraint_facts", "definitions", 0, "identity"), None),
    (("constraint_facts", "definitions", 0, "formals"), {}),
    (("constraint_facts", "definitions", 0, "formals", 0), []),
    (("constraint_facts", "definitions", 0, "formals", 0, "types"), {}),
    (("constraint_facts", "definitions", 0, "formals", 0, "has_default"), 1),
    (("constraint_facts", "usages"), {}),
    (("constraint_facts", "usages", 0), []),
    (("constraint_facts", "usages", 0, "location", "line"), True),
    (("constraint_facts", "usages", 0, "source"), []),
    (("constraint_facts", "usages", 0, "owner"), []),
    (("constraint_facts", "usages", 0, "actuals"), {}),
    (("constraint_facts", "usages", 0, "actuals", 0), []),
    (("constraint_facts", "usages", 0, "omitted_default_formals"), {}),
    (("constraint_facts", "contexts"), {}),
    (("constraint_facts", "contexts", 0, "redefinitions"), {}),
    (("constraint_facts", "diagnostics"), {}),
    (("part_occurrences",), []),
    (("part_occurrences", "Pkg~/Host"), {}),
    (("part_occurrences", "Pkg~/Host", 0), []),
    (("part_occurrences", "Pkg~/Host", 0, "steps"), {}),
    (("part_occurrences", "Pkg~/Host", 0, "steps", 0), []),
    (("part_occurrences", "Pkg~/Host", 0, "steps", 0, "occurrence_index"), True),
    (("constraint_lowering_mode",), []),
]


@pytest.mark.parametrize("path,replacement", REQUIRED_SHAPE_CASES)
def test_v3_shape_matrix_rejects_wrong_containers_and_leaf_types(tmp_path, path, replacement):
    malformed = _rich_v3_snapshot_dict()
    _replace_path(malformed, path, replacement)
    pointer = "/" + "/".join(str(token).replace("~", "~0").replace("/", "~1") for token in path)
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(malformed, tmp_path))
    message = str(caught.value)
    assert pointer in message
    assert "Expected" in message
    assert "Recapture the snapshot." in message


REQUIRED_FIELD_PATHS = [
    ("constraint_facts", "definitions", 0, "predicate"),
    ("constraint_facts", "definitions", 0, "formals", 0, "name"),
    ("constraint_facts", "definitions", 0, "formals", 0, "default"),
    ("constraint_facts", "usages", 0, "location"),
    ("constraint_facts", "usages", 0, "membership_kind"),
    ("constraint_facts", "usages", 0, "is_negated"),
    ("constraint_facts", "usages", 0, "predicate"),
    ("constraint_facts", "usages", 0, "actuals", 0, "direction"),
    ("constraint_facts", "contexts", 0, "redefinitions", 0, "feature"),
    ("constraint_facts", "diagnostics", 0, "operand_source"),
    ("constraint_facts", "diagnostics", 0, "location"),
    ("part_occurrences", "Pkg~/Host", 0, "steps", 0, "occurrence_index"),
]


@pytest.mark.parametrize("path", REQUIRED_FIELD_PATHS)
def test_required_nullable_fields_accept_null_but_reject_absence(tmp_path, path):
    valid = _rich_v3_snapshot_dict()
    _replace_path(valid, path, None)
    load_extraction_snapshot(_write_tmp(valid, tmp_path))

    malformed = _rich_v3_snapshot_dict()
    _delete_path(malformed, path)
    pointer = "/" + "/".join(str(token).replace("~", "~0").replace("/", "~1") for token in path)
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(malformed, tmp_path))
    assert pointer in str(caught.value)
    assert "missing required field" in str(caught.value)


@pytest.mark.parametrize("kind", ["literal", "feature_ref", "unit"])
def test_optional_operand_type_absence_remains_valid(tmp_path, kind):
    raw = _rich_v3_snapshot_dict()
    candidates = []

    def collect(value):
        if isinstance(value, dict):
            if value.get("kind") == kind and value.get("schema_version") == "expression-ir/v1":
                candidates.append(value)
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(raw["constraint_facts"])
    assert candidates
    candidates[0].pop("operand_type", None)
    load_extraction_snapshot(_write_tmp(raw, tmp_path))


CF = ("constraint_facts",)
DEFINITION = CF + ("definitions", 0)
FORMAL = DEFINITION + ("formals", 0)
USAGE = CF + ("usages", 0)
SOURCE = USAGE + ("source",)
OWNER = USAGE + ("owner",)
OWNING_DEFINITION = OWNER + ("owning_definition",)
ACTUAL = USAGE + ("actuals", 0)
CONTEXT = CF + ("contexts", 0)
REDEFINITION = CONTEXT + ("redefinitions", 0)
DIAGNOSTIC = CF + ("diagnostics", 0)
IDENTITY = USAGE + ("identity",)
LOCATION = USAGE + ("location",)
OPERATOR = DEFINITION + ("predicate",)
LITERAL = OPERATOR + ("operands", 0)
LITERAL_FACT = LITERAL + ("literal",)
FEATURE_REF = FORMAL + ("default",)
REFERENCE = FEATURE_REF + ("reference",)
UNIT = ACTUAL + ("value",)
INVOCATION = USAGE + ("predicate",)
UNSUPPORTED = REDEFINITION + ("value",)
OPERAND_TYPE = INVOCATION + ("operand_type",)
UNIT_FACT = OPERAND_TYPE + ("unit",)
OCCURRENCE = ("part_occurrences", "Pkg~/Host", 0)
STEP = OCCURRENCE + ("steps", 0)


MISSING_FIELD_PATHS = [
    CF + ("schema_version",),
    CF + ("definitions",),
    CF + ("usages",),
    CF + ("contexts",),
    CF + ("diagnostics",),
    DEFINITION + ("identity",),
    DEFINITION + ("formals",),
    DEFINITION + ("predicate",),
    IDENTITY + ("kind",),
    IDENTITY + ("name",),
    IDENTITY + ("qualified_name",),
    LOCATION + ("file",),
    LOCATION + ("line",),
    LOCATION + ("column",),
    SOURCE + ("form",),
    SOURCE + ("effective_predicate_source",),
    SOURCE + ("constraint_definition",),
    SOURCE + ("referenced_feature_target",),
    SOURCE + ("asserted_constraint",),
    OWNER + ("owner",),
    OWNER + ("owning_definition",),
    OWNING_DEFINITION + ("kind",),
    OWNING_DEFINITION + ("qualified_name",),
    USAGE + ("identity",),
    USAGE + ("location",),
    USAGE + ("source",),
    USAGE + ("owner",),
    USAGE + ("scope",),
    USAGE + ("membership_kind",),
    USAGE + ("is_negated",),
    USAGE + ("actuals",),
    USAGE + ("omitted_default_formals",),
    USAGE + ("predicate",),
    USAGE + ("inherited_into",),
    FORMAL + ("name",),
    FORMAL + ("qualified_name",),
    FORMAL + ("types",),
    FORMAL + ("has_default",),
    FORMAL + ("default",),
    ACTUAL + ("name",),
    ACTUAL + ("direction",),
    ACTUAL + ("formal_targets",),
    ACTUAL + ("value",),
    CONTEXT + ("identity",),
    CONTEXT + ("general_types",),
    CONTEXT + ("types",),
    CONTEXT + ("inherited_constraints",),
    CONTEXT + ("redefinitions",),
    REDEFINITION + ("feature",),
    REDEFINITION + ("redefines",),
    REDEFINITION + ("value",),
    DIAGNOSTIC + ("kind",),
    DIAGNOSTIC + ("message",),
    DIAGNOSTIC + ("operand_source",),
    DIAGNOSTIC + ("location",),
    LITERAL + ("schema_version",),
    LITERAL + ("kind",),
    LITERAL + ("literal",),
    LITERAL_FACT + ("kind",),
    LITERAL_FACT + ("value",),
    LITERAL_FACT + ("result_type",),
    FEATURE_REF + ("schema_version",),
    FEATURE_REF + ("kind",),
    FEATURE_REF + ("reference",),
    REFERENCE + ("source_name",),
    REFERENCE + ("target",),
    REFERENCE + ("target_types",),
    REFERENCE + ("chain_segments",),
    OPERATOR + ("schema_version",),
    OPERATOR + ("kind",),
    OPERATOR + ("operator",),
    OPERATOR + ("operands",),
    OPERATOR + ("operand_type",),
    UNIT + ("schema_version",),
    UNIT + ("kind",),
    UNIT + ("value",),
    UNIT + ("unit_text",),
    INVOCATION + ("schema_version",),
    INVOCATION + ("kind",),
    INVOCATION + ("function_qn",),
    INVOCATION + ("arguments",),
    INVOCATION + ("operand_type",),
    UNSUPPORTED + ("schema_version",),
    UNSUPPORTED + ("kind",),
    UNSUPPORTED + ("node_kind",),
    UNSUPPORTED + ("diagnostic",),
    UNSUPPORTED + ("source_text",),
    OPERAND_TYPE + ("category",),
    OPERAND_TYPE + ("enumeration",),
    OPERAND_TYPE + ("unit",),
    UNIT_FACT + ("unit",),
    UNIT_FACT + ("dimension",),
    OCCURRENCE + ("part_def_qn",),
    OCCURRENCE + ("steps",),
    STEP + ("owning_def_qn",),
    STEP + ("feature_name",),
    STEP + ("occurrence_index",),
    ("constraint_lowering_mode",),
]


@pytest.mark.parametrize("path", MISSING_FIELD_PATHS, ids=lambda path: _pointer(path))
def test_every_required_and_nullable_policy_field_rejects_absence(tmp_path, path):
    malformed = _rich_v3_snapshot_dict()
    _delete_path(malformed, path)
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(malformed, tmp_path))
    message = str(caught.value)
    assert _pointer(path) in message
    assert "missing required field" in message
    assert "Recapture the snapshot." in message


WRONG_TYPE_CASES = [
    ShapeCase("facts-schema-type", CF + ("schema_version",), []),
    ShapeCase("definitions-list", CF + ("definitions",), {}),
    ShapeCase("definition-item", CF + ("definitions", 0), []),
    ShapeCase("definition-identity", DEFINITION + ("identity",), []),
    ShapeCase("definition-formals", DEFINITION + ("formals",), {}),
    ShapeCase("formal-item", FORMAL, []),
    ShapeCase("formal-name", FORMAL + ("name",), 1),
    ShapeCase("formal-qualified-name", FORMAL + ("qualified_name",), 1),
    ShapeCase("formal-types", FORMAL + ("types",), {}),
    ShapeCase("formal-types-member", FORMAL + ("types", 0), 1),
    ShapeCase("formal-has-default", FORMAL + ("has_default",), 1),
    ShapeCase("formal-default", FORMAL + ("default",), []),
    ShapeCase("usages-list", CF + ("usages",), {}),
    ShapeCase("usage-item", CF + ("usages", 0), []),
    ShapeCase("identity-container", IDENTITY, []),
    ShapeCase("identity-kind", IDENTITY + ("kind",), 1),
    ShapeCase("identity-name", IDENTITY + ("name",), 1),
    ShapeCase("identity-qualified-name", IDENTITY + ("qualified_name",), 1),
    ShapeCase("location-container", LOCATION, []),
    ShapeCase("location-file", LOCATION + ("file",), 1),
    ShapeCase("location-line", LOCATION + ("line",), "1"),
    ShapeCase("location-column", LOCATION + ("column",), True),
    ShapeCase("source-container", SOURCE, []),
    ShapeCase("source-form", SOURCE + ("form",), 1),
    ShapeCase("source-effective", SOURCE + ("effective_predicate_source",), []),
    ShapeCase("source-definition", SOURCE + ("constraint_definition",), []),
    ShapeCase("source-feature", SOURCE + ("referenced_feature_target",), []),
    ShapeCase("source-asserted", SOURCE + ("asserted_constraint",), []),
    ShapeCase("owner-container", OWNER, []),
    ShapeCase("owner-identity", OWNER + ("owner",), []),
    ShapeCase("owning-definition", OWNER + ("owning_definition",), []),
    ShapeCase("owning-kind", OWNING_DEFINITION + ("kind",), 1),
    ShapeCase("owning-qn", OWNING_DEFINITION + ("qualified_name",), 1),
    ShapeCase("scope-container", USAGE + ("scope",), []),
    ShapeCase("membership-kind", USAGE + ("membership_kind",), 1),
    ShapeCase("is-negated", USAGE + ("is_negated",), "false"),
    ShapeCase("actuals-list", USAGE + ("actuals",), {}),
    ShapeCase("actual-item", ACTUAL, []),
    ShapeCase("actual-name", ACTUAL + ("name",), 1),
    ShapeCase("actual-direction", ACTUAL + ("direction",), 1),
    ShapeCase("formal-targets", ACTUAL + ("formal_targets",), {}),
    ShapeCase("formal-target-member", ACTUAL + ("formal_targets", 0), 1),
    ShapeCase("actual-value", ACTUAL + ("value",), []),
    ShapeCase("omitted-defaults", USAGE + ("omitted_default_formals",), {}),
    ShapeCase("omitted-default-member", USAGE + ("omitted_default_formals", 0), 1),
    ShapeCase("usage-predicate", USAGE + ("predicate",), []),
    ShapeCase("inherited-into", USAGE + ("inherited_into",), {}),
    ShapeCase("inherited-into-member", USAGE + ("inherited_into", 0), 1),
    ShapeCase("contexts-list", CF + ("contexts",), {}),
    ShapeCase("context-item", CF + ("contexts", 0), []),
    ShapeCase("context-identity", CONTEXT + ("identity",), []),
    ShapeCase("general-types", CONTEXT + ("general_types",), {}),
    ShapeCase("general-type-member", CONTEXT + ("general_types", 0), 1),
    ShapeCase("context-types", CONTEXT + ("types",), {}),
    ShapeCase("context-type-member", CONTEXT + ("types", 0), 1),
    ShapeCase("inherited-constraints", CONTEXT + ("inherited_constraints",), {}),
    ShapeCase("inherited-constraint-member", CONTEXT + ("inherited_constraints", 0), 1),
    ShapeCase("redefinitions-list", CONTEXT + ("redefinitions",), {}),
    ShapeCase("redefinition-item", REDEFINITION, []),
    ShapeCase("redefinition-feature", REDEFINITION + ("feature",), 1),
    ShapeCase("redefinition-redefines", REDEFINITION + ("redefines",), 1),
    ShapeCase("redefinition-value", REDEFINITION + ("value",), []),
    ShapeCase("diagnostics-list", CF + ("diagnostics",), {}),
    ShapeCase("diagnostic-item", CF + ("diagnostics", 0), []),
    ShapeCase("diagnostic-kind", DIAGNOSTIC + ("kind",), 1),
    ShapeCase("diagnostic-message", DIAGNOSTIC + ("message",), 1),
    ShapeCase("diagnostic-operand-source", DIAGNOSTIC + ("operand_source",), 1),
    ShapeCase("diagnostic-location", DIAGNOSTIC + ("location",), []),
    ShapeCase("literal-schema", LITERAL + ("schema_version",), 1),
    ShapeCase("literal-kind", LITERAL + ("kind",), 1),
    ShapeCase("literal-container", LITERAL + ("literal",), []),
    ShapeCase("literal-fact-kind", LITERAL_FACT + ("kind",), 1),
    ShapeCase("literal-result-type", LITERAL_FACT + ("result_type",), 1),
    ShapeCase("literal-operand-type", LITERAL + ("operand_type",), []),
    ShapeCase("feature-schema", FEATURE_REF + ("schema_version",), 1),
    ShapeCase("feature-kind", FEATURE_REF + ("kind",), 1),
    ShapeCase("reference-container", FEATURE_REF + ("reference",), []),
    ShapeCase("source-name", REFERENCE + ("source_name",), 1),
    ShapeCase("target-identity", REFERENCE + ("target",), []),
    ShapeCase("target-types", REFERENCE + ("target_types",), {}),
    ShapeCase("target-type-member", REFERENCE + ("target_types", 0), 1),
    ShapeCase("chain-segments", REFERENCE + ("chain_segments",), {}),
    ShapeCase("chain-segment-member", REFERENCE + ("chain_segments", 0), 1),
    ShapeCase("feature-operand-type", FEATURE_REF + ("operand_type",), []),
    ShapeCase("operator-schema", OPERATOR + ("schema_version",), 1),
    ShapeCase("operator-kind", OPERATOR + ("kind",), 1),
    ShapeCase("operator-unknown-kind", OPERATOR + ("kind",), "mystery"),
    ShapeCase("operator-name", OPERATOR + ("operator",), 1),
    ShapeCase("operator-operands", OPERATOR + ("operands",), {}),
    ShapeCase("operator-operand-item", OPERATOR + ("operands", 0), 1),
    ShapeCase("operator-operand-type", OPERATOR + ("operand_type",), []),
    ShapeCase("unit-schema", UNIT + ("schema_version",), 1),
    ShapeCase("unit-kind", UNIT + ("kind",), 1),
    ShapeCase("unit-value", UNIT + ("value",), 1),
    ShapeCase("unit-text", UNIT + ("unit_text",), 1),
    ShapeCase("unit-operand-type", UNIT + ("operand_type",), []),
    ShapeCase("invocation-schema", INVOCATION + ("schema_version",), 1),
    ShapeCase("invocation-kind", INVOCATION + ("kind",), 1),
    ShapeCase("function-qn", INVOCATION + ("function_qn",), {}),
    ShapeCase("function-qn-member", INVOCATION + ("function_qn", 0), 1),
    ShapeCase("arguments", INVOCATION + ("arguments",), {}),
    ShapeCase("argument-item", INVOCATION + ("arguments", 0), 1),
    ShapeCase("invocation-operand-type", INVOCATION + ("operand_type",), []),
    ShapeCase("unsupported-schema", UNSUPPORTED + ("schema_version",), 1),
    ShapeCase("unsupported-kind", UNSUPPORTED + ("kind",), 1),
    ShapeCase("unsupported-node-kind", UNSUPPORTED + ("node_kind",), 1),
    ShapeCase("unsupported-diagnostic", UNSUPPORTED + ("diagnostic",), 1),
    ShapeCase("unsupported-source", UNSUPPORTED + ("source_text",), 1),
    ShapeCase("operand-category", OPERAND_TYPE + ("category",), 1),
    ShapeCase("operand-enumeration", OPERAND_TYPE + ("enumeration",), 1),
    ShapeCase("operand-unit", OPERAND_TYPE + ("unit",), []),
    ShapeCase("unit-name", UNIT_FACT + ("unit",), 1),
    ShapeCase("unit-dimension", UNIT_FACT + ("dimension",), 1),
    ShapeCase("occurrences-root", ("part_occurrences",), []),
    ShapeCase("occurrence-owner-list", ("part_occurrences", "Pkg~/Host"), {}),
    ShapeCase("occurrence-item", OCCURRENCE, []),
    ShapeCase("part-def-qn", OCCURRENCE + ("part_def_qn",), 1),
    ShapeCase("steps-list", OCCURRENCE + ("steps",), {}),
    ShapeCase("step-item", STEP, []),
    ShapeCase("step-owner", STEP + ("owning_def_qn",), 1),
    ShapeCase("step-feature", STEP + ("feature_name",), 1),
    ShapeCase("step-index", STEP + ("occurrence_index",), True),
    ShapeCase("mode-type", ("constraint_lowering_mode",), []),
]


@pytest.mark.parametrize("case", WRONG_TYPE_CASES, ids=lambda case: case.id)
def test_every_field_policy_row_rejects_wrong_non_null_type(tmp_path, case):
    malformed = _rich_v3_snapshot_dict()
    path = case.path
    if path[-1] == 0:
        container = _at(malformed, path[:-1])
        if container is None:
            _replace_path(malformed, path[:-1], ["valid"])
            container = _at(malformed, path[:-1])
        if not container:
            container.append("valid")
    if path[-1] == "operand_type" and path in {
        LITERAL + ("operand_type",),
        FEATURE_REF + ("operand_type",),
        UNIT + ("operand_type",),
    }:
        _at(malformed, path[:-1])[path[-1]] = None
    _replace_path(malformed, path, case.replacement)
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(malformed, tmp_path))
    message = str(caught.value)
    assert _pointer(path) in message
    assert "Expected" in message
    assert "Recapture the snapshot." in message


NULLABLE_PATHS = [
    IDENTITY + ("kind",),
    IDENTITY + ("name",),
    IDENTITY + ("qualified_name",),
    USAGE + ("location",),
    USAGE + ("membership_kind",),
    USAGE + ("is_negated",),
    USAGE + ("predicate",),
    SOURCE + ("effective_predicate_source",),
    SOURCE + ("constraint_definition",),
    SOURCE + ("referenced_feature_target",),
    SOURCE + ("asserted_constraint",),
    OWNER + ("owner",),
    FORMAL + ("name",),
    FORMAL + ("qualified_name",),
    FORMAL + ("default",),
    ACTUAL + ("name",),
    ACTUAL + ("direction",),
    ACTUAL + ("value",),
    REDEFINITION + ("feature",),
    REDEFINITION + ("redefines",),
    REDEFINITION + ("value",),
    DIAGNOSTIC + ("operand_source",),
    DIAGNOSTIC + ("location",),
    LITERAL_FACT + ("result_type",),
    REFERENCE + ("source_name",),
    REFERENCE + ("target",),
    OPERATOR + ("operand_type",),
    UNIT + ("unit_text",),
    INVOCATION + ("function_qn",),
    INVOCATION + ("operand_type",),
    UNSUPPORTED + ("source_text",),
    OPERAND_TYPE + ("enumeration",),
    OPERAND_TYPE + ("unit",),
    UNIT_FACT + ("unit",),
    UNIT_FACT + ("dimension",),
    STEP + ("occurrence_index",),
]


@pytest.mark.parametrize("path", NULLABLE_PATHS, ids=lambda path: _pointer(path))
def test_every_nullable_field_accepts_explicit_null(tmp_path, path):
    valid = _rich_v3_snapshot_dict()
    _replace_path(valid, path, None)
    load_extraction_snapshot(_write_tmp(valid, tmp_path))


@pytest.mark.parametrize(
    "path",
    [
        CF + ("definitions",),
        CF + ("usages",),
        CF + ("contexts",),
        CF + ("diagnostics",),
        DEFINITION + ("formals",),
        USAGE + ("actuals",),
        USAGE + ("omitted_default_formals",),
        USAGE + ("inherited_into",),
        CONTEXT + ("general_types",),
        CONTEXT + ("types",),
        CONTEXT + ("inherited_constraints",),
        CONTEXT + ("redefinitions",),
        ("part_occurrences", "Pkg~/Host"),
        OCCURRENCE + ("steps",),
        OPERATOR + ("operands",),
        INVOCATION + ("arguments",),
    ],
    ids=lambda path: _pointer(path),
)
def test_every_list_policy_accepts_empty_list(tmp_path, path):
    valid = _rich_v3_snapshot_dict()
    _replace_path(valid, path, [])
    load_extraction_snapshot(_write_tmp(valid, tmp_path))


@pytest.mark.parametrize("literal_value", [None, True, 1, 1.5, "text", [], {}])
def test_literal_value_accepts_every_json_value(tmp_path, literal_value):
    valid = _rich_v3_snapshot_dict()
    _replace_path(valid, LITERAL_FACT + ("value",), literal_value)
    load_extraction_snapshot(_write_tmp(valid, tmp_path))


def test_compilation_results_remains_degradable_outside_v3_gate(tmp_path, caplog):
    valid = _rich_v3_snapshot_dict()
    valid.pop("compilation_results", None)
    loaded = load_extraction_snapshot(_write_tmp(valid, tmp_path))
    assert loaded["compilation_results"] == {}
    assert "compilation_results" in caplog.text


def test_json_syntax_and_non_mapping_root_are_contextual(tmp_path):
    path = tmp_path / "extraction_snapshot.json"
    path.write_text("{")
    with pytest.raises(SnapshotFormatError, match="valid JSON object") as syntax_error:
        load_extraction_snapshot(path)
    assert ": /:" in str(syntax_error.value)
    path.write_text("[]")
    with pytest.raises(SnapshotFormatError, match="Expected object") as root_error:
        load_extraction_snapshot(path)
    assert ": /:" in str(root_error.value)


def test_unknown_extra_version_scan_and_pointer_escaping_controls(tmp_path):
    valid = _rich_v3_snapshot_dict()
    load_extraction_snapshot(_write_tmp(valid, tmp_path))
    invalid = _rich_v3_snapshot_dict()
    invalid["constraint_facts"]["ordinary_extra"]["schema_version"] = "expression-ir/v2"
    with pytest.raises(SnapshotFormatError, match="expression-ir/v2"):
        load_extraction_snapshot(_write_tmp(invalid, tmp_path))

    escaped = _rich_v3_snapshot_dict()
    del escaped["part_occurrences"]["Pkg~/Host"][0]["steps"]
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(escaped, tmp_path))
    assert "/part_occurrences/Pkg~0~1Host/0/steps" in str(caught.value)


@pytest.mark.parametrize(
    "target,pointer",
    [
        ("facts", "/constraint_facts"),
        ("occurrences", "/part_occurrences"),
    ],
)
def test_residual_reconstructor_failures_are_contextual_and_chained(
    tmp_path, monkeypatch, target, pointer
):
    def fail_reconstruction(*_args, **_kwargs):
        raise ValueError("injected typed reconstruction failure")

    if target == "facts":
        monkeypatch.setattr(snapshot_loader.constraint_facts_module, "parse", fail_reconstruction)
    else:
        monkeypatch.setattr(snapshot_loader, "deserialize_part_occurrences", fail_reconstruction)
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(_write_tmp(_rich_v3_snapshot_dict(), tmp_path))
    assert pointer in str(caught.value)
    assert "reconstruction failed: injected typed reconstruction failure" in str(caught.value)
    assert "Recapture the snapshot." in str(caught.value)
    assert isinstance(caught.value.__cause__, ValueError)
