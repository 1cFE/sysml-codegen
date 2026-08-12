"""Live extraction-evidence conformance (SOURCE-IDENTITY Item 4, Phase 1).

Proves the plan's first proof point: a deep calculation chain, a constraint
leaf, an aggregation term, and a redefinition each retain the exact
SysIDE-resolved target as immutable evidence, captured before chain
flattening, virtual-binding rewrite, or snapshot AST removal — and
``_rewrite_virtual_bindings`` cannot mutate that evidence.

Every expected qualified name below is the SysIDE oracle's answer (probed
live 2026-08-07), not a value derived from the implementation. Routes map to
the ratified contract's Appendix C cells; see
``tests/fixtures/source_identity_mixed_consumers/PROVENANCE.md``.

All tests require a live SysIDE license.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.source_evidence import (
    ReadinessCode,
    SourceForm,
    screen_source_readiness,
)
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

PKG = "source_identity_mixed_consumers"


@pytest.fixture(scope="module")
def extracted_cache():
    """Load each fixture model once and extract usages + hierarchy."""
    cache: dict[str, dict[str, Any]] = {}

    def get(fixture_name: str) -> dict[str, Any]:
        if fixture_name not in cache:
            extractor = SysMLDataExtractor([FIXTURES_DIR / fixture_name])
            assert extractor.load_models(), f"fixture {fixture_name} failed to load"
            model = extractor.model
            usages, report = extract_calculation_usages(model)
            cache[fixture_name] = {
                "model": model,
                "usages": usages,
                "report": report,
            }
        return cache[fixture_name]

    return get


@pytest.fixture(scope="module")
def mixed(extracted_cache):
    return extracted_cache(PKG)


def _binding(usages, qn_suffix: str, param: str):
    matches = [u for u in usages if u.qualified_name.endswith(qn_suffix)]
    assert matches, f"no calc usage matching *{qn_suffix}"
    (usage,) = matches
    for binding in usage.bindings:
        if binding.param_name == param:
            return binding
    raise AssertionError(f"no binding {param!r} on {usage.qualified_name}")


def _evidence(usages, qn_suffix: str, param: str):
    binding = _binding(usages, qn_suffix, param)
    evidence = binding.reference_evidence
    assert evidence is not None, f"binding {qn_suffix}|{param} carries no evidence"
    return evidence


def _feature_reference_facts(node: Any) -> list[FeatureReferenceFact]:
    """Collect every FeatureReferenceFact inside an expression IR tree."""
    found: list[FeatureReferenceFact] = []
    if isinstance(node, FeatureReferenceFact):
        found.append(node)
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        for field in dataclasses.fields(node):
            found.extend(_feature_reference_facts(getattr(node, field.name)))
    elif isinstance(node, (list, tuple)):
        for item in node:
            found.extend(_feature_reference_facts(item))
    return found


# ---------------------------------------------------------------------------
# Target fidelity per authored form (I1: the exact SysIDE-resolved target)
# ---------------------------------------------------------------------------


def test_chain_target_is_the_redefining_feature(mixed) -> None:
    """C11: a chain to an overridden child attribute resolves to the redefining
    ReferenceUsage at the occurrence, which redefines the definition attribute."""
    evidence = _evidence(mixed["usages"], "__station__chain_calc", "value_in")
    assert evidence.source_form is SourceForm.FEATURE_CHAIN
    assert evidence.referent is not None
    assert evidence.referent.qualified_name == f"{PKG}::Station::rig::gain_setting"
    assert evidence.referent.element_kind == "ReferenceUsage"
    assert evidence.referent.redefined_qualified_names == (
        f"{PKG}::Rig::gain_setting",
    )
    assert not evidence.referent.owner_is_definition  # owned by the rig usage
    assert evidence.chain_root is not None
    assert evidence.chain_root.qualified_name == f"{PKG}::Station::rig"
    assert not evidence.is_self_binding


def test_deep_chain_retains_exact_leaf_target(mixed) -> None:
    """C24: a three-segment chain to a computed output keeps the exact resolved
    leaf (the calc-def output attribute) and every resolved step, while the
    legacy dispatch still emits only the flattened dotted path."""
    binding = _binding(
        mixed["usages"], "__computed_station__computed_calc", "value_in"
    )
    assert binding.binding_type == BindingType.CHAIN
    assert binding.source_path == "source_identity_computed.producer_calc.result"

    evidence = binding.reference_evidence
    assert evidence is not None
    assert evidence.source_form is SourceForm.FEATURE_CHAIN
    assert evidence.referent is not None
    assert (
        evidence.referent.qualified_name
        == f"{PKG}::'Source Identity Producer'::result"
    )
    assert evidence.referent.owner_is_definition
    assert evidence.chain_root is not None
    assert (
        evidence.chain_root.qualified_name
        == f"{PKG}::'Computed Station'::source_identity_computed"
    )
    assert evidence.resolved_segment_qns == (
        f"{PKG}::'Computed Station'::source_identity_computed",
        f"{PKG}::'Computed Unit'::producer_calc",
        f"{PKG}::'Source Identity Producer'::result",
    )


def test_def_and_usage_context_referent_classes(mixed) -> None:
    """C25: the def-authored leg resolves to the def-level attribute; the
    usage-authored leg resolves to the occurrence-level redefining feature."""
    def_leg = _evidence(mixed["usages"], "__avail_plant__def_authored_calc", "value_in")
    assert def_leg.source_form is SourceForm.BARE_REFERENCE
    assert def_leg.referent is not None
    assert def_leg.referent.qualified_name == f"{PKG}::'Avail Plant'::availability"
    assert def_leg.referent.owner_is_definition

    usage_leg = _evidence(
        mixed["usages"], "__avail_plant__usage_authored_calc", "value_in"
    )
    assert usage_leg.source_form is SourceForm.BARE_REFERENCE
    assert usage_leg.referent is not None
    assert (
        usage_leg.referent.qualified_name
        == f"{PKG}::'Avail Design Ctx'::avail_plant::availability"
    )
    assert not usage_leg.referent.owner_is_definition
    assert usage_leg.referent.redefined_qualified_names == (
        f"{PKG}::'Avail Plant'::availability",
    )


def test_written_form_separates_qualified_from_bare(mixed) -> None:
    """C12 vs C13: the authored form comes from the written text, never the
    resolved QN — resolution makes both forms identical."""
    qualified = _evidence(mixed["usages"], "__qual_plant__qual_calc", "value_in")
    assert qualified.source_form is SourceForm.QUALIFIED_REFERENCE
    assert qualified.written_qualifier == "'Qual Plant'"
    assert qualified.referent is not None
    assert qualified.referent.qualified_name == f"{PKG}::'Qual Plant'::level"
    assert qualified.referent.owner_is_definition  # def-level referent: bridge required

    bare = _evidence(mixed["usages"], "__bare_rig__bare_calc", "value_in")
    assert bare.source_form is SourceForm.BARE_REFERENCE
    assert bare.written_qualifier is None
    assert bare.referent is not None
    assert (
        bare.referent.qualified_name
        == f"{PKG}::'Bare Station'::bare_rig::intensity"
    )
    assert not bare.referent.owner_is_definition


def test_cross_owner_consumers_share_one_exact_referent(mixed) -> None:
    """C15: the child-part calculation and the parent-owned constraint resolve
    to the same exact parent attribute — no consumer-local substitute."""
    # Owned by the part usage `child` inside part def 'Parent Unit' — not a
    # template, so it keeps the definition-scoped QN.
    child = _evidence(mixed["usages"], "__child__child_calc", "value_in")
    assert child.referent is not None
    assert child.referent.qualified_name == f"{PKG}::'Parent Unit'::shared_rate"
    assert child.referent.owner_is_definition
    assert not child.is_self_binding

    from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts

    facts = extract_constraint_facts(mixed["model"])
    guards = [
        usage
        for usage in facts.usages
        if usage.identity.qualified_name
        and usage.identity.qualified_name.endswith("'Parent Unit'::parent_guard")
    ]
    assert guards, "parent_guard constraint not extracted"
    (guard,) = guards
    leaf_targets = {
        fact.target.qualified_name
        for actual in guard.actuals
        for fact in _feature_reference_facts(actual.value)
        if fact.target is not None
    }
    assert leaf_targets == {f"{PKG}::'Parent Unit'::shared_rate"}


def test_bound_formal_identity_is_exact(mixed) -> None:
    """Both sides of a binding are captured: the formal's own QN and the
    calc-def formal it redefines (provenance for the identity seam)."""
    evidence = _evidence(mixed["usages"], "__stamp_plant__stamp_calc", "value_in")
    assert (
        evidence.bound_formal_qn == f"{PKG}::'Stamp Plant'::stamp_calc::value_in"
    )
    assert evidence.bound_formal_redefines == (
        f"{PKG}::'Reading Consumer'::value_in",
    )


# ---------------------------------------------------------------------------
# Aggregation terms (exact target evidence before names are rendered)
# ---------------------------------------------------------------------------


def test_aggregation_terms_retain_exact_targets(mixed) -> None:
    hierarchy = extract_hierarchy_data(mixed["model"])
    by_attr = {agg.attribute_name: agg for agg in hierarchy.aggregation_expressions}

    station = by_attr["station_total"]
    (chain_term,) = station.singleton_terms
    assert chain_term.source_path == "rig.gain_setting"
    assert chain_term.resolved_target is not None
    assert (
        chain_term.resolved_target.qualified_name
        == f"{PKG}::Station::rig::gain_setting"
    )

    bank = by_attr["bank_total"]
    (sum_term,) = bank.sum_terms
    assert sum_term.part_usage_name == "cell"
    assert sum_term.resolved_target is not None
    assert sum_term.resolved_target.qualified_name == f"{PKG}::'Bank Cell'::cell_cost"

    qual = by_attr["qual_total"]
    (qual_term,) = qual.local_terms
    assert qual_term.resolved_target is not None
    assert qual_term.resolved_target.qualified_name == f"{PKG}::'Qual Plant'::level"
    assert qual_term.resolved_target.owner_is_definition

    parent = by_attr["parent_total"]
    (parent_term,) = parent.local_terms
    assert parent_term.resolved_target is not None
    assert (
        parent_term.resolved_target.qualified_name
        == f"{PKG}::'Parent Unit'::shared_rate"
    )


# ---------------------------------------------------------------------------
# Modeled value sites (D2: exact value-bearing element identity)
# ---------------------------------------------------------------------------


def test_occurrence_override_value_sites_carry_exact_identity(mixed) -> None:
    hierarchy = extract_hierarchy_data(mixed["model"])

    rig_overrides = [
        override
        for override in hierarchy.design_overrides
        if override.member_qualified_name == f"{PKG}::Station::rig::gain_setting"
    ]
    assert rig_overrides, "rig gain_setting override not captured with member QN"
    (rig_override,) = rig_overrides
    assert rig_override.literal_value == 42.0
    assert rig_override.redefined_target_qns == (f"{PKG}::Rig::gain_setting",)

    deep_overrides = [
        override
        for override in hierarchy.design_overrides
        if override.is_deep_path
        and override.redefined_target_qns
        == (f"{PKG}::'Deep Panel'::deep_rig", f"{PKG}::Rig::gain_setting")
    ]
    assert deep_overrides, "deep-path override lost its exact chained target QNs"
    (deep_override,) = deep_overrides
    assert deep_override.literal_value == 43.0
    assert deep_override.member_qualified_name is None  # anonymous chained member


# ``test_definition_default_value_site_carries_raw_qn`` stood here. It read
# ``analysis/parameter_groups.extract_design_attributes`` and asserted the raw, unsanitized
# QN was recorded on each design attribute. Both the function and the
# ``raw_qualified_name`` field retired with the v5 family (retirement step 2), and no
# ``raw_qualified_name`` remains anywhere in ``src/`` — the exact route keeps unsanitized
# identity in the node's ``DeclarationId`` instead, which the elaboration tests pin. There
# is nothing left here to make the old statement about.


def test_authored_literal_is_a_distinct_evidence_class(mixed) -> None:
    evidence = _evidence(mixed["usages"], "__stamp_plant__lit_calc", "value_in")
    assert evidence.source_form is SourceForm.AUTHORED_LITERAL
    assert evidence.referent is None
    assert not evidence.is_reference_derived


# ---------------------------------------------------------------------------
# Post-rewrite immutability (I4: VBR cannot mutate or replace evidence)
# ---------------------------------------------------------------------------


# Both post-rewrite immutability nodes retired with the v5 family (retirement step 2).
# What they asserted was that ``pipeline_builder._rewrite_virtual_bindings`` — the legacy
# virtual-binding rewrite — could literal-stamp a binding without mutating or replacing its
# frozen ``reference_evidence``. That rewrite is the mutator; with it deleted there is no
# code path that can mutate the evidence, so the property has no counter-example left to
# guard against. The evidence classes themselves (bare reference, authored literal, deep
# chain) are pinned by the nodes above, which read them straight off extraction.


# ---------------------------------------------------------------------------
# Readiness dispositions (D8, Phase-1 subset; emit-only in Phase 1)
# ---------------------------------------------------------------------------


def test_indexed_source_is_evidence_not_flattened(extracted_cache) -> None:
    """SRC-02/02a: the #(i) form is retained as INDEXED_SOURCE evidence. The
    legacy dispatch still emits the flattened leaf (the pinned 02a defect);
    the evidence is what makes the readiness disposition possible."""
    indexed = extracted_cache("source_identity_indexed_source")
    binding = _binding(indexed["usages"], "__design_ctx__c1", "r_in")
    assert binding.source_path == "plant_r"  # legacy flatten, unchanged until cutover

    evidence = binding.reference_evidence
    assert evidence is not None
    assert evidence.source_form is SourceForm.INDEXED_SOURCE
    assert evidence.referent is None  # no source feature identity exists
    assert evidence.chain_root is not None
    assert (
        evidence.chain_root.qualified_name
        == "source_identity_indexed_source::'Design Ctx'::plants"
    )

    findings = screen_source_readiness(indexed["usages"])
    indexed_findings = [
        finding
        for finding in findings
        if finding.code is ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED
    ]
    assert len(indexed_findings) == 2  # c1 and c2
    assert all("valid" in finding.detail for finding in indexed_findings)


def test_self_binding_detected_despite_same_named_outer(extracted_cache) -> None:
    """SRC-01: the trap's binding resolves to its own formal; the same-named
    outer attribute never suppresses the disposition (exact semantic
    comparison, not a name heuristic)."""
    trap = extracted_cache("self_named_binding_trap")
    self_bound = [
        binding.reference_evidence
        for usage in trap["usages"]
        for binding in usage.bindings
        if binding.reference_evidence is not None
        and binding.reference_evidence.is_self_binding
    ]
    assert self_bound, "trap self-binding not detected"

    findings = screen_source_readiness(trap["usages"])
    assert any(f.code is ReadinessCode.SI_SELF_BINDING for f in findings)


def test_shadowed_reference_is_not_a_self_binding(extracted_cache) -> None:
    """Control: a bare reference that resolves to an outer feature (through a
    same-named shadow) is not a self-binding and produces no finding."""
    shadowed = extracted_cache("shadowed_reference")
    evidences = [
        binding.reference_evidence
        for usage in shadowed["usages"]
        for binding in usage.bindings
        if binding.reference_evidence is not None
    ]
    assert evidences, "shadowed_reference produced no evidence"
    assert not any(evidence.is_self_binding for evidence in evidences)
    findings = screen_source_readiness(shadowed["usages"])
    assert not any(f.code is ReadinessCode.SI_SELF_BINDING for f in findings)


def test_expression_source_disposition(extracted_cache) -> None:
    probe = extracted_cache("expression_binding_probe")
    expression_evidence = [
        binding.reference_evidence
        for usage in probe["usages"]
        for binding in usage.bindings
        if binding.reference_evidence is not None
        and binding.reference_evidence.source_form is SourceForm.EXPRESSION_SOURCE
    ]
    assert expression_evidence, "expression source not classified"
    findings = screen_source_readiness(probe["usages"])
    assert any(
        f.code is ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED for f in findings
    )
