"""Item 14 Phase 2 (W2): the manifest -> catalog no-silent-drop mapping test (D1, INV-A).

The kept proof the migration invariant rests on: every constraint usage the
retiring drop-manifest (`extractor.collect_constraint_manifest()`) would have
reported has a carrier in the catalog era — either an eligible concrete entry
(`graph.constraint_catalog.concrete_entries`, grouped by `usage_qualified_name`)
or an explicit catalog `excluded_records` projection of the validated exclusion payload.
This test must be green BEFORE Phase 3 deletes the manifest era — the proof
precedes the retirement it authorizes.

Re-anchors REQ-EXT-09 from "manifest reports a drop" onto "the catalog carries
what the manifest reports."
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_profile

from sysml_codegen.extraction.constraint_report import ConstraintKind
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

# Full-pipeline fixtures with at least one constraint usage (`ife_plant` has
# zero and is excluded; `item4_require` has no calc defs and cannot build a
# full graph — its manifest-classification behavior is covered directly in
# test_extractor.py, re-anchored in Phase 3, not here).
CONSTRAINT_BEARING_FIXTURES = [
    "catf_mfe_model",
    "fusion_tea",
    "plant_values",
    "wi014_toy",
    "constraint_inline",
    "constraint_multi_instance",
    "constraint_non_numerical",
]

# Requirement-side kinds the manifest sweeps but the profile/lowering never
# admits as an executable assertion — a named, justified carrier-free category
# (design-review B1 hidden bet), not a catch-all. None of CONSTRAINT_BEARING_
# FIXTURES currently carries one (item4_require does, but has no calc defs to
# build a full graph); if one is ever added here, it must land as an unassessed
# record via the requirement_def owner-kind branch (`lower_constraints`
# docstring, D7) like item4_require's `within_budget` does today.
_JUSTIFIED_CARRIER_FREE_KINDS = frozenset({ConstraintKind.REQUIREMENT, ConstraintKind.SATISFY})


def _usage_identity(entry) -> str:
    """The manifest entry's join key against `ConcreteConstraint.usage_qualified_name`
    (`owner_qualified_name::constraint_name`, matching `usage.identity.qualified_name`
    exactly for a named usage — verified against every fixture in
    CONSTRAINT_BEARING_FIXTURES).

    No fixture in the corpus carries an anonymous constraint usage today (verified:
    zero `constraint_name == "<anonymous>"` entries across every fixture, catf_mfe's
    65 plain constraints included) — `usage_qualified_name` collapses every anonymous
    usage to the literal string ``"<anonymous>"`` with no line-based tiebreak
    surviving onto `ConcreteConstraint`, so the join cannot disambiguate multiple
    anonymous usages under one owner. Raising here (rather than silently joining
    wrong) is the loud signal if that ever changes (design.md `implementation-notes`,
    "Mapping-test join key" — the anonymous case explicitly flagged for verification
    before locking).
    """
    if entry.constraint_name == "<anonymous>":
        raise NotImplementedError(
            "an anonymous constraint usage entered the corpus — the join key must "
            "be widened with a source-location tiebreak before this test can cover "
            f"it (owner={entry.owner_qualified_name}, line={entry.source_line})"
        )
    return f"{entry.owner_qualified_name}::{entry.constraint_name}"


def _is_justified_carrier_free(entry) -> bool:
    return entry.constraint_kind in _JUSTIFIED_CARRIER_FREE_KINDS


@requires_license
@pytest.mark.req("REQ-EXT-09")
@pytest.mark.req("REQ-CL-04")
@pytest.mark.parametrize("fixture", CONSTRAINT_BEARING_FIXTURES)
def test_every_manifest_usage_has_a_catalog_carrier(fixture):
    ctx = build_pipeline_context([FIXTURES_DIR / fixture])
    manifest = ctx.extractor.collect_constraint_manifest()
    assert manifest, f"{fixture}: expected at least one swept constraint usage"

    eligible_by_usage: dict[str, list] = {}
    if ctx.computation_graph.constraint_catalog is not None:
        for entry in ctx.computation_graph.constraint_catalog.concrete_entries:
            eligible_by_usage.setdefault(entry.usage_qualified_name, []).append(entry)
    unassessed_usages = {c.usage_qualified_name for c in ctx.concrete_constraints if not c.eligible}

    for entry in manifest:
        usage_qn = _usage_identity(entry)
        carried = usage_qn in eligible_by_usage or usage_qn in unassessed_usages
        assert carried or _is_justified_carrier_free(entry), (
            f"{fixture}: silent drop — {usage_qn} has no catalog carrier (eligible "
            "or unassessed) and is not a justified carrier-free requirement/satisfy "
            "usage"
        )


@requires_license
@pytest.mark.req("REQ-EXT-09")
def test_catf_mfe_65_plain_constraints_land_unassessed_not_block(caplog):
    """R1 (profile disposition of non-asserted plain constraints, confirmed
    empirically): catf_mfe's 65 plain `constraint {}` usages (no `assert`) all land
    `eligible=False` unassessed — none is admitted (the profile does not treat a
    non-asserted inline constraint as an executable assertion) and none BLOCKs
    (the fixture already halts today if any classified BLOCK, which it does not)."""
    ctx = build_pipeline_context([FIXTURES_DIR / "catf_mfe_model"])
    assert len(ctx.concrete_constraints) == 65
    assert all(not c.eligible for c in ctx.concrete_constraints)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None
    assert catalog.concrete_entries == []
    assert len(catalog.excluded_records) == 65
    assert all(record.exclusion.kind == "unassessed_form" for record in catalog.excluded_records)

    profile = evaluate_profile(ctx.constraint_facts)
    dispositions = {d.eligibility for d in profile.decisions}
    assert Eligibility.BLOCK not in dispositions, (
        "a BLOCK disposition among catf_mfe's 65 plain constraints would mean the "
        "fixture already halts today — a real finding to surface (R1), not silently "
        "absorbed into the unassessed count"
    )


@requires_license
@pytest.mark.req("REQ-EXT-09")
@pytest.mark.parametrize(
    "fixture", ["fusion_tea", "plant_values", "wi014_toy", "constraint_inline"]
)
def test_catalog_source_records_cover_every_constraint_definition(fixture):
    """D1b (inverted, safe direction): `source_records` is built from every
    `ConstraintDefinition` in the model (`assemble_constraint_catalog`), not filtered
    to only those with a concrete entry — so an unused definition stays visible as
    authoring inventory (concept line 102: "never appears as unassessed") rather than
    silently absent. `ConstraintCatalogEntry` carries no definition-QN field to join
    against per-entry (it is per-usage, not per-definition, Core Concept); this
    asserts the inventory-completeness property the catalog assembly guarantees by
    construction, not a per-entry join."""
    ctx = build_pipeline_context([FIXTURES_DIR / fixture])
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None
    src_defs = {r.definition_qualified_name for r in catalog.source_records}
    fact_defs = {
        d.identity.qualified_name or "<anonymous>" for d in ctx.constraint_facts.definitions
    }
    assert src_defs == fact_defs, f"{fixture}: source_records must cover every definition"
