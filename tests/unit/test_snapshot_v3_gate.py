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

from sysml_codegen.snapshot import SnapshotFormatError
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
    """A committed v3 snapshot with its constraint section replaced by a
    locally-built, predicate-bearing facts object (so cell (g)'s embedded
    expression-ir scan has a real node to corrupt)."""
    raw = json.loads(snapshot_fixture("chain_spike_model").read_text())
    raw["snapshot_format_version"] = 3
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
    # Phase 5 re-captured the corpus at v3 (INV-6: no v2/v3 coexistence), so a
    # v2 fixture is hand-built here rather than read off a committed snapshot.
    v2 = json.loads(snapshot_fixture("chain_spike_model").read_text())
    assert v2["snapshot_format_version"] == 3
    v2["snapshot_format_version"] = 2
    with pytest.raises(SnapshotFormatError, match="format version"):
        load_extraction_snapshot(_write_tmp(v2, tmp_path))


def test_facts_and_occurrences_roundtrip_byte_identical(tmp_path):
    good = _v3_snapshot_dict()
    loaded = load_extraction_snapshot(_write_tmp(good, tmp_path))
    reserialized = json.loads(constraint_facts_module.serialize(loaded["constraint_facts"]))
    assert reserialized == good["constraint_facts"]  # INV-2, byte-identical
    assert loaded["part_occurrences"] == {}
    assert loaded["constraint_lowering_mode"] == "applied"
