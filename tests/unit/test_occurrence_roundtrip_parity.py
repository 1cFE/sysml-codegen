"""Phase 1 de-risk spike (Item 8, snapshot v3): occurrence round-trip +
``constraint_id`` parity on the smallest per-occurrence-expansion fixture.

Proves B1/B2 (design.md#key-bets) before any serializer/loader surgery: a
serialized occurrence table reloads byte-identical (frozen-dataclass equality)
and drives the real ``lower_constraints`` offline to byte-identical
``constraint_id``s. A divergence here means the frozen-table shape (D1) is
wrong — cheapest to learn on this fixture, before the full v3 format is built
around it.
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.analysis.part_instance_index import (
    FrozenOccurrenceIndex,
    FrozenOccurrenceIndexCorruptionError,
    deserialize_part_occurrences,
)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.snapshot.serializer import _serialize_value
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
def test_multi_instance_occurrence_roundtrip_and_constraint_id_parity():
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    live_ids = sorted(c.constraint_id for c in ctx.concrete_constraints)
    assert live_ids, "fixture must produce at least one concrete constraint"
    table = ctx.part_occurrences

    # --- round-trip the two identity-bearing inputs ---
    from agentic_mbse.sysml import constraint_facts as constraint_facts_module

    facts_json = json.loads(constraint_facts_module.serialize(ctx.constraint_facts))
    occ_json = _serialize_value(table, None)
    reloaded_facts = constraint_facts_module.parse(json.dumps(facts_json))
    reloaded_table = deserialize_part_occurrences(occ_json)
    assert reloaded_table == table  # INV-2 occurrence equality, byte-for-byte

    # --- offline leg: real lower_constraints through the frozen index ---
    frozen = FrozenOccurrenceIndex(reloaded_table)
    concrete = lower_constraints(
        reloaded_facts,
        occ_index=frozen,
        registry=ctx.output_registry,
        design_attrs=ctx.design_attributes,
        calc_usages=ctx.calc_usages,
    )
    assert sorted(c.constraint_id for c in concrete) == live_ids  # B2 parity


@requires_license
def test_frozen_occurrence_index_raises_on_missing_owner():
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    frozen = FrozenOccurrenceIndex(ctx.part_occurrences)
    with pytest.raises(FrozenOccurrenceIndexCorruptionError, match="nonexistent"):
        frozen.occurrences_of("nonexistent")
