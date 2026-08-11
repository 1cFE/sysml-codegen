"""Learning tests: where semantic source identity survives or is lost (SOURCE-IDENTITY Item 2).

These tests PIN CURRENT BEHAVIOR, including the two known fan-out defects, so the
Item 4/5 repair shows up as deliberate red — they are the kept probes required by
the epic (`.project/backlog/epic_semantic_source_identity.md`, Item 2 success
criteria). Each test names which behavior is the defect pin and which is the
evidence a repair can rely on. Findings doc:
`.project/research/20260805-054752_source-identity-route-evidence.md`.

The two fan-out paths (both forensic reports, 2026-08-03):

* **Path A — silent literal stamp.** An occurrence ``:>>`` override is stamped
  into every self-named consumer binding by leaf-name coincidence
  (``pipeline_builder.py`` ``_rewrite_virtual_bindings``): ``binding_type=LITERAL``,
  ``source_path=None``. The backtracker's LITERAL arm then mints one entry point
  per consumer and never calls the resolver. **The stamp is persisted**: snapshot
  capture serializes post-VBR bindings (``snapshot/capture.py`` runs the full
  ``build_pipeline_context``), and the snapshot rebuild never re-runs VBR — the
  offline route depends on the baked-in stamp.

* **Path B — warned lenient miss.** A def-default self-named binding stays a
  REFERENCE whose ``source_path`` is the calc's own formal; every key form
  misses (the attribute index holds the *definition* QN, the demand is
  *occurrence*-relative; nothing bridges them) and the LENIENT terminal mints
  one entry point per consumer.

All tests are license-free: they read committed extraction snapshots only.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.resolution.models import EntryPointType
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import FIXTURES_DIR, requires_license, snapshot_fixture


@pytest.fixture(scope="module")
def ctx_cache():
    """Build each fixture's full pipeline context once per module."""
    cache: dict[str, object] = {}

    def get(name: str):
        if name not in cache:
            cache[name] = build_pipeline_context_from_snapshot(snapshot_fixture(name))
        return cache[name]

    return get


def _entry_points(ctx) -> dict[str, object]:
    return {
        ep.qualified_name: ep
        for gr in ctx.computation_graph.entry_point_groups
        for ep in gr.parameters
    }


def _binding(ctx, usage_qn: str, param: str):
    for cu in ctx.calc_usages:
        if cu.qualified_name == usage_qn:
            for b in cu.bindings:
                if b.param_name == param:
                    return b
    raise AssertionError(f"no binding {usage_qn}|{param}")


# ---------------------------------------------------------------------------
# Path A — silent literal stamp (customer/demo shape, fusion_tea fixture)
# ---------------------------------------------------------------------------


def test_path_a_one_modeled_gain_is_three_public_fields(ctx_cache) -> None:
    """DEFECT PIN: the one modeled ``gain`` (plant ``:>> gain = 80.0``) is exposed
    as THREE public fields — the converged design-attribute field the constraint
    reaches, plus one consumer-local copy per stamped calc binding. Item 5's
    cutover must flip this to exactly one field."""
    eps = _entry_points(ctx_cache("fusion_tea"))
    assert "hif_plant_pkg__hif_plant__gain" in eps  # constraint route converges
    assert "hif_plant_pkg__hif_plant__lcoe_calc__gain_in" in eps  # Path A copy
    assert "hif_plant_pkg__hif_plant__recirc_calc__gain_in" in eps  # Path A copy
    # All three carry the same captured value — the defect is invisible at the
    # design point and only manifests when one copy is mutated.
    assert (
        eps["hif_plant_pkg__hif_plant__gain"].default_value
        == eps["hif_plant_pkg__hif_plant__lcoe_calc__gain_in"].default_value
        == eps["hif_plant_pkg__hif_plant__recirc_calc__gain_in"].default_value
        == 80.0
    )
    # The stamped copies are classified as if the modeler wrote literals here.
    for copy in (
        "hif_plant_pkg__hif_plant__lcoe_calc__gain_in",
        "hif_plant_pkg__hif_plant__recirc_calc__gain_in",
    ):
        assert eps[copy].entry_type is EntryPointType.USAGE_LITERAL, copy


def test_path_a_stamp_is_persisted_into_the_snapshot() -> None:
    """The committed fusion_tea snapshot already contains the stamped bindings
    (capture serializes post-VBR state): ``binding_type=LITERAL`` with
    ``source_path=None``. The offline route never sees pre-stamp evidence — any
    repair that reconstructs identity at load time must work from what survives
    below, or force a recapture."""
    snap = load_extraction_snapshot(snapshot_fixture("fusion_tea"))
    (lcoe,) = [
        cu for cu in snap["calc_usages"]
        if cu.qualified_name == "hif_plant_pkg__hif_plant__lcoe_calc"
    ]
    (gain,) = [b for b in lcoe.bindings if b.param_name == "gain_in"]
    assert gain.binding_type == BindingType.LITERAL
    assert gain.source_path is None
    assert gain.literal_value == 80.0


def test_path_a_written_evidence_survives_the_stamp() -> None:
    """EVIDENCE PIN: the stamp clears the resolved route but NOT the written-form
    fields — ``source_attribute_name``/``written_reference`` still name the
    referent, even when the formal is renamed (``rep_rate`` bound to
    ``pulse_rate_ref``). This is what makes reference-derived literals
    reconstructible at all from existing snapshots."""
    snap = load_extraction_snapshot(snapshot_fixture("fusion_tea"))
    by_qn = {cu.qualified_name: cu for cu in snap["calc_usages"]}

    for usage_qn in (
        "hif_plant_pkg__hif_plant__lcoe_calc",
        "hif_plant_pkg__hif_plant__recirc_calc",
    ):
        (gain,) = [b for b in by_qn[usage_qn].bindings if b.param_name == "gain_in"]
        assert gain.binding_type == BindingType.LITERAL
        assert gain.written_reference == "gain", usage_qn

    # Renamed referent: the written evidence names the ATTRIBUTE, not the formal.
    meier = by_qn["hif_plant_pkg__hif_plant__driver__meier_cost"]
    (rep_rate,) = [b for b in meier.bindings if b.param_name == "rep_rate"]
    assert rep_rate.binding_type == BindingType.LITERAL
    assert rep_rate.written_reference == "pulse_rate_ref"


def test_reference_derived_literal_distinguishable_from_authored_literal() -> None:
    """EVIDENCE PIN (Item 2 criterion): genuinely authored usage literals are
    distinguishable from stamped reference-derived ones on existing snapshot
    fields — an authored literal has no written referent
    (``written_reference is None``); a stamped one names its referent. A repair
    must preserve authored literals as distinct sources while converging
    reference-derived ones."""
    snap = load_extraction_snapshot(snapshot_fixture("fusion_tea"))
    by_qn = {cu.qualified_name: cu for cu in snap["calc_usages"]}

    # Authored in the model as literals — legitimately independent sources.
    (num_units,) = [
        b
        for b in by_qn["hif_plant_pkg__hif_plant__meier_reactor_cost_calc"].bindings
        if b.param_name == "num_units"
    ]
    assert num_units.binding_type == BindingType.LITERAL
    assert num_units.written_reference is None

    # Stamped from the shared plant attribute — reference-derived.
    (gain,) = [
        b
        for b in by_qn["hif_plant_pkg__hif_plant__lcoe_calc"].bindings
        if b.param_name == "gain_in"
    ]
    assert gain.binding_type == BindingType.LITERAL
    assert gain.written_reference is not None


@requires_license
def test_reference_derived_discriminator_on_immutable_evidence() -> None:
    """Item 4 evidence: the authored-vs-reference-derived discriminator now
    rests on immutable extraction evidence, not on surviving written-name
    fields. Live extraction of the vendored fusion_tea models: the stamped
    ``gain`` keeps its bare-reference evidence through the VBR literal stamp
    (and is the exact self-binding the contract classifies SRC-01), while the
    authored ``num_units`` literal is AUTHORED_LITERAL with no referent. The
    snapshot-based pins above stay in force for the offline route."""
    from sysml_codegen.extraction.source_evidence import SourceForm
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
    from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
    from sysml_codegen.orchestration.pipeline_builder import _rewrite_virtual_bindings

    extractor = SysMLDataExtractor([FIXTURES_DIR / "fusion_tea"])
    assert extractor.load_models()
    usages, _report = extract_calculation_usages(extractor.model)
    hierarchy = extract_hierarchy_data(extractor.model)

    by_qn = {u.qualified_name: u for u in usages if not u.is_template}
    lcoe = by_qn["hif_plant_pkg__hif_plant__lcoe_calc"]
    (gain,) = [b for b in lcoe.bindings if b.param_name == "gain_in"]
    before = gain.reference_evidence
    assert before is not None
    assert before.source_form is SourceForm.BARE_REFERENCE
    # Not a self-binding any more: Slice 3D migrated `in gain = gain` to the
    # D-5 `in gain_in = gain` form, so the RHS resolves to the plant attribute
    # rather than the calc's own formal. SRC-01's specimen moved to
    # `self_named_binding_trap`; the Path-A stamp below is unaffected, because
    # the legacy route stamps any bare reference it cannot resolve.
    assert not before.is_self_binding

    _rewrite_virtual_bindings(usages, hierarchy)

    assert gain.binding_type == BindingType.LITERAL  # Path-A stamp fired
    assert gain.reference_evidence is before  # evidence never replaced
    assert gain.reference_evidence.is_reference_derived

    meier = by_qn["hif_plant_pkg__hif_plant__meier_reactor_cost_calc"]
    (num_units,) = [b for b in meier.bindings if b.param_name == "num_units"]
    assert num_units.reference_evidence is not None
    assert num_units.reference_evidence.source_form is SourceForm.AUTHORED_LITERAL
    assert num_units.reference_evidence.referent is None
    assert not num_units.reference_evidence.is_reference_derived


# ---------------------------------------------------------------------------
# Path B — warned lenient miss (def-default shape, ife_plant fixture)
# ---------------------------------------------------------------------------


def test_path_b_lenient_miss_mints_per_consumer(ctx_cache) -> None:
    """DEFECT PIN: two calcs on one occurrence (``hif_plant.driver``) self-name
    the same def-default attribute ``bank_energy``; the resolver misses every key
    form and the lenient terminal mints one entry point per consumer. The
    def-declared source is never a public field."""
    eps = _entry_points(ctx_cache("ife_plant"))
    assert "IfePlantDesign__hif_plant__driver__base_power_calc__bank_energy" in eps
    assert "IfePlantDesign__hif_plant__driver__hif_cost_calc__bank_energy" in eps
    # The modeled source (def-declared, def QN) never becomes a runtime source.
    assert not any("Hif_Driver__bank_energy" in qn for qn in eps)


def test_path_b_identity_evidence_present_but_unbridged(ctx_cache) -> None:
    """EVIDENCE PIN: Path B destroys nothing — the binding still carries the
    resolved self-ref ``source_path`` and the written leaf. What is missing is a
    bridge: the attribute index holds the definition QN
    (``IfePlantLib::Ife Power Plant::gain``) while demand is occurrence-relative
    (``IfePlantDesign__baseline_plant``  + ``gain``). This is the same
    occurrence->definition gap filed under [NESTED-OCCURRENCE-OVERRIDE]."""
    ctx = ctx_cache("ife_plant")
    b = _binding(ctx, "IfePlantDesign__baseline_plant__lcoe_calc", "gain")
    assert b.binding_type == BindingType.REFERENCE
    assert b.source_path == "IfePlantLib::'Ife Power Plant'::lcoe_calc::gain"
    assert b.written_reference == "gain"
    # The definition-side source with the modeled default exists in the capture.
    attr_qns = {
        a.qualified_name
        for attrs in ctx.design_attributes.values()
        for a in attrs
    }
    assert "IfePlantLib__Ife_Power_Plant__gain" in attr_qns


def test_path_b_value_backfill_masks_identity_loss(ctx_cache) -> None:
    """DEFECT PIN: the per-consumer entry point is classified USAGE_LITERAL (no
    literal exists in the model) yet carries the def default ``500.0`` — the
    value is quietly repaired by a separate resolution authority (the parameter
    group deriver backfill, ``graph_builder.py`` ``_derived_groups_to_params``)
    while the identity stays per-consumer. Value agreement at capture is why the
    defect is invisible at any single-point run."""
    eps = _entry_points(ctx_cache("ife_plant"))
    ep = eps["IfePlantDesign__baseline_plant__lcoe_calc__gain"]
    assert ep.entry_type is EntryPointType.USAGE_LITERAL
    assert ep.default_value == 500.0  # == IfePlantLib::'Ife Power Plant'::gain default


# ---------------------------------------------------------------------------
# Controls — routes where identity currently survives
# ---------------------------------------------------------------------------


def test_shared_producer_control_converges(ctx_cache) -> None:
    """CONTROL: the SR-A02 shape (attribute declared directly on a concrete
    PartUsage, unbracketed, calc + constraint consumers) converges on the one
    occurrence field via row 16. Proves the convergence machinery a repair
    should route more shapes into already exists."""
    eps = _entry_points(ctx_cache("shared_producer"))
    assert "SharedProducer__the_rig__gain" in eps
    assert eps["SharedProducer__the_rig__gain"].entry_type is EntryPointType.DESIGN_ATTRIBUTE
    assert "SharedProducer__the_rig__scaler__gain" not in eps


def test_dotted_cross_part_control_converges(ctx_cache) -> None:
    """CONTROL: the dotted cross-part shape (``driver.efficiency`` renamed into
    two consumers) collapses to one source-QN entry point via the supplied-value
    materializer — identity survives when the reference route is retained."""
    eps = _entry_points(ctx_cache("fusion_tea"))
    assert "hif_plant_pkg__hif_plant__driver__efficiency" in eps
    assert "hif_plant_pkg__hif_plant__lcoe_calc__driver_efficiency" not in eps
    assert "hif_plant_pkg__hif_plant__recirc_calc__eta" not in eps


# ---------------------------------------------------------------------------
# Cross-owner cell — where owner-local reconstruction is insufficient
# ---------------------------------------------------------------------------


def test_cross_owner_stamp_defeats_owner_local_reconstruction(ctx_cache) -> None:
    """DEFECT + EVIDENCE PIN: ``pack_count`` lives on ``battery_system`` but is
    consumed by ``battery_bos.cost_model``. The stamp mints a consumer-local copy
    (alongside the converged aggregation/constraint field), and the surviving
    written evidence (consumer owner + leaf) reconstructs a QN that names NO
    design attribute — owner-local reconstruction cannot recover a cross-owner
    source. This is the cell that forces either scope-search heuristics or an
    extraction-owned semantic source ID."""
    ctx = ctx_cache("solar_battery_model")
    eps = _entry_points(ctx)
    converged = "SolarBatteryDesign__solar_battery_plant__battery_system__pack_count"
    stamped = (
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_bos"
        "__cost_model__pack_count"
    )
    assert converged in eps
    assert stamped in eps  # one modeled attribute, two public fields

    b = _binding(
        ctx,
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_bos__cost_model",
        "pack_count",
    )
    assert b.binding_type == BindingType.LITERAL  # stamped
    assert b.written_reference == "pack_count"  # evidence survives ...
    # ... but consumer-owner + leaf reconstructs a QN that names nothing — not a
    # captured design attribute and not a public field:
    attr_qns = {
        a.qualified_name for attrs in ctx.design_attributes.values() for a in attrs
    }
    owner = "SolarBatteryDesign__solar_battery_plant__battery_system__battery_bos"
    assert f"{owner}__pack_count" not in attr_qns
    assert f"{owner}__pack_count" not in eps
    # The true source is one scope up. Note it is not in the raw captured
    # attribute map either — the converged field exists only because the
    # supplied-value materializer synthesizes the occurrence attribute from the
    # aggregation/constraint demand (classified DESIGN_ATTRIBUTE from the
    # enriched index). Owner-local evidence cannot rebuild that link.
    assert converged not in attr_qns
    assert eps[converged].entry_type is EntryPointType.DESIGN_ATTRIBUTE


def test_unbound_formals_are_a_distinct_per_usage_class(ctx_cache) -> None:
    """CLASSIFICATION PIN: the 8x ``fab_factor`` population is NOT one of the two
    fan-out paths — each is an unbound formal minted per-usage as
    LIBRARY_DEFAULT (ADR-001). The model never binds them to one source, so
    per-usage identity is the currently-documented reading; Item 3 dispositions
    whether that reading stands."""
    eps = _entry_points(ctx_cache("solar_battery_model"))
    fab = [qn for qn in eps if qn.endswith("__fab_factor")]
    assert len(fab) == 8
    assert all(eps[qn].entry_type is EntryPointType.LIBRARY_DEFAULT for qn in fab)
