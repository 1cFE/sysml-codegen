"""Phase 5: success-criteria fixtures locked, exercised through the wired
`build_pipeline_context` path (`lower_constraints_enabled=True`).

The shared default path (`lower_constraints_enabled=False`) is proven inert
by the corpus byte-identity gate (plan.md Phase 5 Validation) — nothing here
duplicates that; every test in this file passes the flag explicitly.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.graph_builder import (
    _validate_channel_references,
    collect_uncovered_params,
)
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
def test_roots_before_pruning_retains_producer_s4_reproduction():
    """S4 reproduction: with pruning enabled and a minimal exit selection, the
    control run (flag off) prunes `cost_calc`; the lowered run (flag on)
    retains it only via the resolved constraint input channel joined as a
    backtracking root — not because every output feeds the exit."""
    target = "toy_plant__demo_plant__area_calc.area"

    control = build_pipeline_context(
        [FIXTURES_DIR / "wi014_toy"], targets=[target], include_all=False
    )
    control_names = {m.name for m in control.computation_graph.modules}
    assert "toy_plant__demo_plant__cost_calc" not in control_names
    assert control.concrete_constraints == []

    lowered = build_pipeline_context(
        [FIXTURES_DIR / "wi014_toy"],
        targets=[target],
        include_all=False,
        lower_constraints_enabled=True,
    )
    lowered_names = {m.name for m in lowered.computation_graph.modules}
    assert "toy_plant__demo_plant__cost_calc" in lowered_names
    assert "constraint_report_aggregator" in lowered_names
    assert len(lowered.concrete_constraints) == 1
    assert lowered.concrete_constraints[0].eligible is True


@requires_license
def test_strict_resolution_no_fallback_v11_and_channel_refs_pass():
    """Strict resolution: V11 coverage and channel-reference validation pass
    on the extended graph produced by the wired path — re-run independently
    here (not just relying on `extend_graph_with_constraints` having raised
    internally during the build)."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    _validate_channel_references(ctx.computation_graph.modules)  # no raise
    uncovered = collect_uncovered_params(ctx.computation_graph)
    assert uncovered == []

    # Every module_output-resolved input is a real fallback-free binding: none
    # of the minted/bound channels are in fallback_entry_points (INV-2 proxy —
    # a fallback QN reaching the graph would mean synthesis leaked through).
    assert ctx.computation_graph.fallback_entry_points == set()


@requires_license
def test_deterministic_identity_across_repeated_live_loads():
    """Deterministic identity (spec S3): constraint_ids and catalog ordering
    are byte-identical across two independent fresh live loads."""
    a = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    b = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    ids_a = [c.constraint_id for c in a.concrete_constraints]
    ids_b = [c.constraint_id for c in b.concrete_constraints]
    assert ids_a == ids_b
    assert ids_a == sorted(ids_a)  # catalog ordering is by constraint_id (INV-4)


@requires_license
def test_multi_instance_end_to_end_through_wired_path():
    """Multi-instance (design Appendix B, B1-settled): three concrete
    constraints, three distinct constraint_ids, three distinct evaluation
    channels, wired all the way through the real pipeline (not just
    lower_constraints in isolation, covered in test_constraint_lowering.py)."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    assert len(ctx.concrete_constraints) == 3
    constraint_modules = [
        m for m in ctx.computation_graph.modules if m.module_kind == "constraint"
    ]
    assert len(constraint_modules) == 3
    assert len({m.outputs[0].channel_name for m in constraint_modules}) == 3


@requires_license
def test_inline_end_to_end_through_wired_path():
    """Inline (design Appendix B): an inline-form assertion lowers through the
    real pipeline, selecting the usage predicate, no formals/actuals."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_inline"], lower_constraints_enabled=True
    )
    assert len(ctx.concrete_constraints) == 1
    cc = ctx.concrete_constraints[0]
    assert cc.source_form == "inline"
    assert cc.eligible is True
    constraint_modules = [
        m for m in ctx.computation_graph.modules if m.module_kind == "constraint"
    ]
    assert len(constraint_modules) == 1


@requires_license
def test_inheritance_cross_check_instance_index_probe_oracle_unchanged():
    """instance_index_probe's inherited [3] assert must not move the Item-4
    9-instance oracle count when Item 5's lowering runs against it (must-not-
    move per design Appendix B).

    `instance_index_probe` is deliberately calc-free (Item 4's own fixture:
    "every instance must come from part structure"), so `build_pipeline_context`
    itself is not usable here (Step 2 requires >=1 calc def) — exercise
    `lower_constraints` + `build_part_instance_index` directly, the same
    production inputs the wired pipeline path would supply.
    """
    from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts

    from sysml_codegen.analysis.constraint_lowering import lower_constraints
    from sysml_codegen.analysis.part_instance_index import build_part_instance_index
    from sysml_codegen.core.output_registry import OutputRegistry
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([FIXTURES_DIR / "instance_index_probe"])
    extractor.load_models()
    index = build_part_instance_index(extractor.model)
    occurrences = index.occurrences_of("InstanceIndexProbe__ConstrainedLeaf")
    assert len(occurrences) == 9  # Item-4 oracle count, unchanged

    facts = extract_constraint_facts(extractor.model)
    concrete = lower_constraints(
        facts,
        occ_index=index,
        registry=OutputRegistry(),
        design_attrs={},
        calc_usages=[],
    )
    # The inherited `nonnegative` assert expands once per ConstrainedLeaf
    # occurrence it's inherited into -- distinct eligible/unassessed entries,
    # never silently dropped (INV-1); the 9-instance oracle above is untouched
    # by lowering having also run.
    assert len(concrete) > 0
    assert len(index.occurrences_of("InstanceIndexProbe__ConstrainedLeaf")) == 9


@requires_license
def test_wired_path_halts_on_profile_blocked_assert():
    """Audit cure (note 3): the preflight halt fires end-to-end through the
    wired pipeline, not only via direct lower_constraints calls."""
    with pytest.raises(CodeGenerationError) as exc_info:
        build_pipeline_context(
            [FIXTURES_DIR / "constraint_blocked_profile"],
            lower_constraints_enabled=True,
        )
    message = str(exc_info.value)
    assert "not executable" in message
    assert "exact" in message
    # Reason-grade, not just "blocked" (block_real_equality family)
    assert "equal" in message.lower()


@requires_license
def test_blocked_profile_fixture_generates_when_flag_off():
    """With the transitional default (flag off), the same model still builds a
    pipeline context — the halt is scoped to the lowering-enabled path until
    Item 8 flips the default."""
    ctx = build_pipeline_context([FIXTURES_DIR / "constraint_blocked_profile"])
    assert ctx.concrete_constraints == []
