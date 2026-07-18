"""Phase 5: success-criteria fixtures locked, exercised through the wired
`build_pipeline_context` path (`lower_constraints_enabled=True`).

Lowering defaults to True since Item 8 Phase 4; every test in this file that
needs a genuine "lowering did not run" control passes `False` explicitly
(there is no longer an implicit off-by-default path to rely on).
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
        [FIXTURES_DIR / "wi014_toy"],
        targets=[target],
        include_all=False,
        lower_constraints_enabled=False,
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
    constraint_modules = [m for m in ctx.computation_graph.modules if m.module_kind == "constraint"]
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
    constraint_modules = [m for m in ctx.computation_graph.modules if m.module_kind == "constraint"]
    assert len(constraint_modules) == 1


def test_inline_offline_fixture_reaches_module_rendering():
    """The committed snapshot must cross the leaf/input reconciliation guard offline."""
    from sysml_codegen.cli import _get_template_env
    from sysml_codegen.generation.modules import (
        compile_shared_predicates,
        render_constraint_module,
    )
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    snapshot = FIXTURES_DIR / "constraint_inline" / "extraction_snapshot.json"
    ctx = build_pipeline_context_from_snapshot(snapshot)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None
    [module] = [item for item in ctx.computation_graph.modules if item.module_kind == "constraint"]
    assert [item.param_name for item in module.inputs] == ["value"]

    compiled = compile_shared_predicates(catalog)
    source = render_constraint_module(
        module, catalog, compiled, _get_template_env(), package_name="constraint_inline_exec"
    )
    assert "def run(self, value: float)" in source


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
    from sysml_codegen.analysis.parameter_groups import extract_design_attributes
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
        # Inline leaves use the same strict production ladder as definition actuals. Supply the
        # extracted modeled defaults that pipeline_builder passes in production; an empty mapping
        # would correctly make strict resolution fail rather than prove inherited scoping.
        design_attrs=extract_design_attributes(extractor.model),
        calc_usages=[],
    )
    # The inherited `nonnegative` assert expands once per ConstrainedLeaf
    # occurrence it's inherited into -- distinct eligible/unassessed entries,
    # never silently dropped (INV-1); the 9-instance oracle above is untouched
    # by lowering having also run.
    assert len(concrete) == 9
    assert {item.owner_instance_path for item in concrete} == {
        "InstanceIndexProbe__root__bank__member[0]",
        "InstanceIndexProbe__root__bank__member[1]",
        "InstanceIndexProbe__root__bank__member[2]",
        "InstanceIndexProbe__root__container_a__leaf",
        "InstanceIndexProbe__root__container_b__leaf",
        "InstanceIndexProbe__root__direct_a",
        "InstanceIndexProbe__root__direct_b",
        "InstanceIndexProbe__root__plain_subtype",
        "InstanceIndexProbe__root__specialized__leaf",
    }
    assert all(
        [(input_.formal_name, input_.design_attribute_qn) for input_ in constraint.inputs]
        == [("reading", "InstanceIndexProbe__ConstrainedLeaf__reading")]
        for constraint in concrete
    )
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
    assert "block_real_equality_requires_tolerance" in message
    assert "two-inequality" in message


@requires_license
def test_blocked_profile_fixture_generates_when_lowering_explicitly_disabled():
    """Explicitly opting out of lowering (the grandfather mechanism, D3) still
    builds a pipeline context inertly — the halt is scoped to the
    lowering-enabled path, which is now the default (Item 8 Phase 4)."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_blocked_profile"], lower_constraints_enabled=False
    )
    assert ctx.concrete_constraints == []
