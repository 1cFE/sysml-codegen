"""Origin-aware logical demand: one deterministic operation per normalized target.

License-free. Builds ``DemandOrigin`` records directly against the real
``_binding_target`` normalizer, so the tests exercise the production identity seam
rather than a parallel one.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.supplied_values import (
    DemandOrigin,
    LogicalDemand,
    _binding_target,
    _logical_demands,
    _origin_sort_key,
    enrich_graph_design_attributes,
    resolve_logical_demand,
    select_group_source,
)

MATERIALIZER_LOGGER = "sysml_codegen.resolution.supplied_values"

CALC_ROUTE = Path("calc_route.sysml")
CONSTRAINT_ROUTE = Path("constraint_route.sysml")

ABSOLUTE_PATH = "Lib::Plant::value"
ABSOLUTE_TARGET = "Lib__Plant__value"


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------


def _override(owner: str, attr: str, value: str | None, *, chain: bool = False) -> RedefinitionData:
    return RedefinitionData(
        owning_part_qn=owner,
        attribute_name=attr,
        redefinition_type=RedefinitionType.CHAIN if chain else RedefinitionType.LITERAL,
        literal_value=value,
        expression_text=None,
        expression_ast=None,
    )


def _origin(
    *,
    route: str,
    source_path: str,
    instance_scope: str,
    owning_part_def_qn: str | None = None,
    group: Path | None = CALC_ROUTE,
    label: str | None = None,
) -> DemandOrigin:
    target = _binding_target(source_path, instance_scope)
    assert target is not None, source_path
    return DemandOrigin(
        route=route,
        target=target,
        lookup_context=(instance_scope, owning_part_def_qn),
        group_provenance=group,
        diagnostic_context=label or f"{route} {instance_scope}.{source_path}",
    )


def _demand(*origins: DemandOrigin) -> LogicalDemand:
    return LogicalDemand(
        target=origins[0].target, origins=tuple(sorted(origins, key=_origin_sort_key))
    )


def _resolve(demand: LogicalDemand, **kwargs):
    return resolve_logical_demand(
        demand,
        redefinitions=kwargs.get("redefinitions", []),
        design_overrides=kwargs.get("design_overrides", []),
        usage_type_map=kwargs.get("usage_type_map", {}),
        exact_real_sources=kwargs.get("exact_real_sources", {}),
    )


def _resolve_and_group(demand: LogicalDemand, **kwargs):
    """Resolve, then select provenance — what the enrichment seam does for a target
    it is really going to synthesize."""
    resolved = _resolve(demand, **kwargs)
    return resolved, select_group_source(
        resolved, exact_real_sources=kwargs.get("exact_real_sources", {})
    )


# --------------------------------------------------------------------------
# Semantic outcome comparison across distinct lookup contexts
# --------------------------------------------------------------------------


def test_absolute_target_accepts_distinct_scopes_with_equal_outcomes():
    """Two calc scopes reference one absolute target. Their raw lookup contexts differ,
    which is valid; both resolve to 17.0, so the demand resolves once."""
    demand = _demand(
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__a"),
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__b"),
    )
    assert demand.target.qn == ABSOLUTE_TARGET

    resolved, group_source = _resolve_and_group(
        demand,
        redefinitions=[_override("Lib__Plant", "value", "17.0")],
        usage_type_map={
            ("Design__a", "Plant"): "Lib__Plant",
            ("Design__b", "Plant"): "Lib__Plant",
        },
    )
    assert resolved.value == 17.0
    assert resolved.nonliteral is False
    assert group_source == CALC_ROUTE
    assert len(resolved.outcomes) == 2


def test_absolute_target_rejects_different_semantic_outcomes():
    demand = _demand(
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__a"),
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__b"),
    )
    with pytest.raises(CodeGenerationError, match="distinct lookup contexts disagree") as caught:
        _resolve(
            demand,
            design_overrides=[
                _override("Design__a__Plant", "value", "17.0"),
                _override("Design__b__Plant", "value", "23.0"),
            ],
        )
    message = str(caught.value)
    assert ABSOLUTE_TARGET in message
    assert "17.0" in message and "23.0" in message


def test_literal_nonliteral_and_unresolved_disagreement_is_contextual():
    demand = _demand(
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__a"),
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__b"),
    )
    with pytest.raises(CodeGenerationError, match="distinct lookup contexts disagree") as caught:
        _resolve(
            demand,
            design_overrides=[
                _override("Design__a__Plant", "value", "17.0"),
                _override("Design__b__Plant", "value", None, chain=True),
            ],
        )
    assert "non-literal" in str(caught.value)


def test_distinct_lookup_context_is_evaluated_once():
    """Three origins, two distinct contexts -> two evaluations, not three."""
    demand = _demand(
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__a", label="one"),
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__a", label="two"),
        _origin(route="calc", source_path=ABSOLUTE_PATH, instance_scope="Design__b", label="three"),
    )
    resolved = _resolve(demand, redefinitions=[])
    assert len(demand.origins) == 3
    assert [outcome.lookup_context for outcome in resolved.outcomes] == [
        ("Design__a", None),
        ("Design__b", None),
    ]


# --------------------------------------------------------------------------
# Post-resolution provenance
# --------------------------------------------------------------------------


def test_calc_origin_group_precedes_constraint_origin_after_resolution():
    """B3: adding an assertion over an existing calc input must not regroup it."""
    demand = _demand(
        _origin(
            route="calc",
            source_path="source.value",
            instance_scope="DemandShared__plant",
            group=CALC_ROUTE,
        ),
        _origin(
            route="constraint",
            source_path="source.value",
            instance_scope="DemandShared__plant",
            group=CONSTRAINT_ROUTE,
        ),
    )
    resolved, group_source = _resolve_and_group(
        demand,
        design_overrides=[_override("DemandShared__plant__source", "value", "17.0")],
    )
    assert resolved.value == 17.0
    assert group_source == CALC_ROUTE


def test_constraint_only_provenance_ladder_and_missing_failure():
    constraint_only = _origin(
        route="constraint",
        source_path="source.value",
        instance_scope="DemandOnly__plant",
        group=CONSTRAINT_ROUTE,
    )
    overrides = [_override("DemandOnly__plant__source", "value", "4.0")]

    # Tier: exact captured design-attribute source for this target wins over the
    # portable constraint-usage source.
    _exact, exact_source = _resolve_and_group(
        _demand(constraint_only),
        design_overrides=overrides,
        exact_real_sources={"DemandOnly__plant__source__value": Path("captured.sysml")},
    )
    assert exact_source == Path("captured.sysml")

    # Tier: real source behind the winning record.
    _by_record, record_source = _resolve_and_group(
        _demand(constraint_only),
        design_overrides=overrides,
        exact_real_sources={"DemandOnly__plant__source__other": Path("owner.sysml")},
    )
    assert record_source == Path("owner.sysml")

    # Tier: portable constraint-usage source.
    _portable, portable_source = _resolve_and_group(
        _demand(constraint_only), design_overrides=overrides
    )
    assert portable_source == CONSTRAINT_ROUTE

    # Absence fails rather than inventing a sentinel.
    unusable = _origin(
        route="constraint",
        source_path="source.value",
        instance_scope="DemandOnly__plant",
        group=Path("unknown"),
    )
    with pytest.raises(CodeGenerationError, match="provenance is missing"):
        _resolve_and_group(_demand(unusable), design_overrides=overrides)


def test_conflicting_sources_at_the_selected_tier_fail():
    demand = _demand(
        _origin(
            route="calc",
            source_path="source.value",
            instance_scope="Design__a",
            group=Path("one.sysml"),
        ),
        _origin(
            route="calc",
            source_path="source.value",
            instance_scope="Design__a",
            group=Path("two.sysml"),
            label="second",
        ),
    )
    with pytest.raises(CodeGenerationError, match="provenance is ambiguous"):
        _resolve_and_group(
            demand, design_overrides=[_override("Design__a__source", "value", "1.0")]
        )


# --------------------------------------------------------------------------
# One logical operation per target, through the enrichment seam
# --------------------------------------------------------------------------


class _Binding:
    def __init__(self, source_path: str) -> None:
        self.source_path = source_path


class _CalcUsage:
    def __init__(self, qn: str, source_file: Path, *paths: str, owning: str | None = None) -> None:
        self.qualified_name = qn
        self.source_file = source_file
        self.bindings = [_Binding(path) for path in paths]
        self.owning_part_def_qn = owning


def test_unique_target_counts_warning_and_synthesis_order(caplog):
    """Two routes onto one target: one scan, one apply, one synthesized attribute."""
    usages = [
        _CalcUsage("DemandShared__plant__consume", CALC_ROUTE, "source.value"),
        _CalcUsage("DemandShared__plant__check", CALC_ROUTE, "source.value"),
    ]
    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=[_override("DemandShared__plant__source", "value", "17.0")],
            usage_type_map={},
        )
    synthesized = [attr for attrs in enriched.values() for attr in attrs]
    assert [attr.qualified_name for attr in synthesized] == [
        "DemandShared__plant__source__value"
    ]
    assert [attr.default_value for attr in synthesized] == ["17.0"]
    assert [record.getMessage() for record in caplog.records] == [
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    ]


def test_multiple_targets_scan_and_emit_in_ascending_target_order(caplog):
    usages = [_CalcUsage("D__plant__c", CALC_ROUTE, "beta.value", "alpha.value", "gamma.value")]
    overrides = [
        _override("D__plant__alpha", "value", "1.0"),
        _override("D__plant__beta", "value", "2.0"),
        _override("D__plant__gamma", "value", "3.0"),
    ]
    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=overrides,
            usage_type_map={},
        )
    synthesized = [attr for attrs in enriched.values() for attr in attrs]
    assert [attr.qualified_name for attr in synthesized] == [
        "D__plant__alpha__value",
        "D__plant__beta__value",
        "D__plant__gamma__value",
    ]
    assert [record.getMessage() for record in caplog.records] == [
        "supplied-value materializer scanned 3 referenced bindings: "
        "3 literal applied, 0 non-literal skipped."
    ]


def test_real_attribute_collision_counts_applied_once_and_keeps_real_value(caplog):
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    real = DesignAttributeData(
        name="value",
        sysml_type="Real",
        default_value="99.0",
        unit=None,
        source_file=CALC_ROUTE,
        source_line=3,
        parent_part="source",
        qualified_name="D__plant__source__value",
    )
    usages = [
        _CalcUsage("D__plant__one", CALC_ROUTE, "source.value"),
        _CalcUsage("D__plant__two", CALC_ROUTE, "source.value"),
    ]
    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {CALC_ROUTE: [real]},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=[_override("D__plant__source", "value", "17.0")],
            usage_type_map={},
        )
    assert [attr.default_value for attr in enriched[CALC_ROUTE]] == ["99.0"]
    messages = [record.getMessage() for record in caplog.records]
    assert sum("already covers" in message for message in messages) == 1
    assert messages[-1] == (
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    )


def test_enrichment_is_copy_on_write():
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    real = DesignAttributeData(
        name="kept",
        sysml_type="Real",
        default_value="1.0",
        unit=None,
        source_file=CALC_ROUTE,
        source_line=1,
        parent_part="plant",
        qualified_name="D__plant__kept",
    )
    incoming = {str(CALC_ROUTE): [real]}
    enriched = enrich_graph_design_attributes(
        incoming,
        calc_usages=[_CalcUsage("D__plant__c", CALC_ROUTE, "source.value")],
        prepared=None,
        redefinitions=[],
        design_overrides=[_override("D__plant__source", "value", "5.0")],
        usage_type_map={},
    )
    assert all(isinstance(key, Path) for key in enriched)
    assert len(enriched[CALC_ROUTE]) == 2
    # The caller's mapping and its lists are untouched.
    assert list(incoming) == [str(CALC_ROUTE)]
    assert [attr.qualified_name for attr in incoming[str(CALC_ROUTE)]] == ["D__plant__kept"]


def test_non_literal_only_target_is_skipped_loudly_and_counted_once(caplog):
    usages = [
        _CalcUsage("D__plant__one", CALC_ROUTE, "source.value"),
        _CalcUsage("D__plant__two", CALC_ROUTE, "source.value"),
    ]
    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=[_override("D__plant__source", "value", None, chain=True)],
            usage_type_map={},
        )
    assert enriched == {}
    assert [record.getMessage() for record in caplog.records] == [
        "supplied-value materializer scanned 1 referenced bindings: 0 literal "
        "applied, 1 non-literal skipped (deferred: ['source.value'])."
    ]


def test_logical_demands_merge_by_exact_target_qn_and_sort_ascending():
    usages = [
        _CalcUsage("D__plant__c", CALC_ROUTE, "zeta.value", "alpha.value"),
        _CalcUsage("D__plant__d", CALC_ROUTE, "alpha.value"),
    ]
    demands = _logical_demands(usages, None)
    assert [demand.target.qn for demand in demands] == [
        "D__plant__alpha__value",
        "D__plant__zeta__value",
    ]
    assert len(demands[0].origins) == 2
    assert len(demands[1].origins) == 1


def test_collision_covered_target_with_split_calc_sources_does_not_raise(caplog):
    """Regression: a target already covered by a real captured design attribute must
    never have its grouping provenance validated.

    Its calc origins sit in two different .sysml files, so provenance selection would
    fail "calc-origin provenance is ambiguous" — but the value is discarded by the
    REQ-SVM-03 collision guard, so there is no grouping decision to make. The real
    value wins, the target still counts as applied, and exactly one warning is emitted.
    """
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    other_route = Path("other_route.sysml")
    real = DesignAttributeData(
        name="value",
        sysml_type="Real",
        default_value="99.0",
        unit=None,
        source_file=CALC_ROUTE,
        source_line=3,
        parent_part="source",
        qualified_name="D__plant__source__value",
    )
    usages = [
        _CalcUsage("D__plant__one", CALC_ROUTE, "source.value"),
        _CalcUsage("D__plant__two", other_route, "source.value"),
    ]

    # The two calc origins genuinely disagree on provenance ...
    demands = _logical_demands(usages, None)
    assert len(demands) == 1
    assert {origin.group_provenance for origin in demands[0].origins} == {
        CALC_ROUTE,
        other_route,
    }
    with pytest.raises(CodeGenerationError, match="calc-origin provenance is ambiguous"):
        _resolve_and_group(
            demands[0],
            design_overrides=[_override("D__plant__source", "value", "17.0")],
        )

    # ... but under the collision guard that disagreement is never consulted.
    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {CALC_ROUTE: [real]},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=[_override("D__plant__source", "value", "17.0")],
            usage_type_map={},
        )

    assert [attr.default_value for attr in enriched[CALC_ROUTE]] == ["99.0"]
    assert other_route not in enriched
    messages = [record.getMessage() for record in caplog.records]
    assert sum("already covers" in message for message in messages) == 1
    assert messages[-1] == (
        "supplied-value materializer scanned 1 referenced bindings: "
        "1 literal applied, 0 non-literal skipped."
    )


def test_two_warnings_occur_in_order_within_one_batch(caplog):
    """OD-A10's warning-order observation: exactly two warnings, X then Y, one batch.

    This is the observation OD-A10 exists to make. It is pinned here at the enrichment
    seam rather than through a public SysML fixture — see the deviation recorded in
    evidence.md §6 for why the design's live 3/2/1 shape is not modelable as specified.

    Ordering is a real property of the seam, not an artifact of this test: every
    resolution is staged, then per-target collision warnings are emitted in ascending
    target order, and only then the single deferred summary. A future change that
    emitted the summary first, or interleaved it, fails here.
    """
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    real = DesignAttributeData(
        name="a_collision",
        sysml_type="Real",
        default_value="101.0",
        unit=None,
        source_file=CALC_ROUTE,
        source_line=4,
        parent_part="source",
        qualified_name="D__plant__source__a_collision",
    )
    usages = [
        _CalcUsage(
            "D__plant__consume",
            CALC_ROUTE,
            "source.a_collision",
            "source.b_nonliteral",
            "source.c_clean",
        )
    ]
    overrides = [
        _override("D__plant__source", "a_collision", "11.0"),
        _override("D__plant__source", "b_nonliteral", None, chain=True),
        _override("D__plant__source", "c_clean", "33.0"),
    ]

    with caplog.at_level(logging.INFO, logger=MATERIALIZER_LOGGER):
        enriched = enrich_graph_design_attributes(
            {CALC_ROUTE: [real]},
            calc_usages=usages,
            prepared=None,
            redefinitions=[],
            design_overrides=overrides,
            usage_type_map={},
        )

    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.levelno >= logging.WARNING and record.name == MATERIALIZER_LOGGER
    ]
    assert warnings == [
        "supplied-value materializer: a real design attribute already covers "
        "D__plant__source__a_collision (source.a_collision); keeping the real value, "
        "skipping synthesis (REQ-SVM-03).",
        "supplied-value materializer scanned 3 referenced bindings: 2 literal applied, "
        "1 non-literal skipped (deferred: ['source.b_nonliteral']).",
    ]

    # The collision keeps the real value; only the clean target synthesizes.
    synthesized = [
        attr.qualified_name
        for attrs in enriched.values()
        for attr in attrs
        if attr is not real
    ]
    assert synthesized == ["D__plant__source__c_clean"]
    assert [attr.default_value for attr in enriched[CALC_ROUTE] if attr is real] == ["101.0"]
