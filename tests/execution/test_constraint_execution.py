"""Real-simkit execution lane (Item 7 / D10) — the single teax-dependent lane.

Reproduces the S4 slice (SC-1) end-to-end through PRODUCTION generation (not S4's test-only
sidecar emitters) and covers the S4-unexercised cases. Runs by hand in the agentic-mbse venv
with `teax/packages/teax-simkit` on `sys.path` (`tests/execution/conftest.py` documents the
incantation) — excluded from the default `uv run pytest` via the `execution` marker
(`pyproject.toml`).

Teax-state precondition (plan.md's pinned decision, 2026-07-12): teax `main` HEAD carries
`write_json_primitive` (scalar persistence) — the orchestrator verified this live before
pinning "persist-and-assert in force"; re-verified here (see the run log entry) rather than
assumed.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from sysml_codegen.cli import (
    GenerationConfig,
    _check_duplicate_output_paths,
    _generate_backlog,
    _generate_entry_points,
    _generate_modules,
    _generate_pipeline,
    _generate_primitives,
    _generate_registry,
    _generate_schemas,
    _generate_stencils,
    _generate_tests,
    _get_template_env,
    _reconcile_params_coverage,
    _setup_output_directories,
)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

BUDGET_QN = "toy_plant__Toy_Plant__plant_budget"
AREA_CH = "toy_plant__demo_plant__area_calc__area"
COST_CH = "toy_plant__demo_plant__cost_calc__cost"
REPORT_CH = "constraint_report"


class _Ctx:
    def __init__(self, ctx) -> None:
        self.computation_graph = ctx.computation_graph


def _generate_full_package(ctx, output_path: Path, package_name: str) -> None:
    """Mirror `cli.run_codegen`'s step sequence, given an already-built ctx (so the caller
    controls `lower_constraints_enabled`, which `run_codegen` itself does not expose)."""
    config = GenerationConfig(output_path=output_path, package_name=package_name)
    _check_duplicate_output_paths(ctx.computation_graph.modules)
    _reconcile_params_coverage(ctx.computation_graph)
    _setup_output_directories(config)
    _generate_primitives(config)
    template_env = _get_template_env()
    fake_ctx = _Ctx(ctx)
    _generate_schemas(fake_ctx, config, template_env)
    from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan

    plan = build_constraint_generation_plan(fake_ctx, template_env, config.package_name)
    _generate_modules(fake_ctx, config, template_env, plan)
    _generate_stencils(fake_ctx, config, template_env)
    _generate_pipeline(fake_ctx, config, template_env)
    _generate_registry(fake_ctx, config, template_env)
    _generate_entry_points(fake_ctx, config, template_env)
    _generate_backlog(fake_ctx, config)
    _generate_tests(fake_ctx, config, template_env)


def _override_budget(pkg_dir: Path, budget: float) -> None:
    for jf in (pkg_dir / "inputs").glob("*.json"):
        data = json.loads(jf.read_text())
        if BUDGET_QN in data:
            data[BUDGET_QN] = budget
            jf.write_text(json.dumps(data, indent=2) + "\n")
            return
    raise RuntimeError(f"{BUDGET_QN} not found in any inputs JSON")


def _run(pkg_parent: Path, pkg_name: str, out_dir: Path):
    import importlib
    import sys

    from simkit.core.pipeline import execute_pipeline

    parent = str(pkg_parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    pkg = importlib.import_module(pkg_name)
    registry = getattr(pkg, f"create_{pkg_name}_registry")()
    yaml_path = pkg_parent / pkg_name / "pipelines" / "pipeline.yaml"
    return execute_pipeline(
        yaml_path, out_dir, registry=registry, custom_schema_types=list(pkg.CUSTOM_SCHEMA_TYPES)
    )


@pytest.mark.execution
def test_s4_slice_both_truth_values(tmp_path):
    """SC-1: both truth values, identical ordinary outputs, verdicts/margins correct, the
    violated run completes as evidence (INV-3), report persisted (teax-state pin)."""
    ctx = build_pipeline_context([FIXTURES_DIR / "wi014_toy"], lower_constraints_enabled=True)
    catalog = ctx.computation_graph.constraint_catalog
    assert catalog is not None and len(catalog.concrete_entries) == 1
    # constraint_id mints a sha-suffixed channel (Item 5) — read it from the real graph
    # rather than hardcoding the S4 probe's unsuffixed guess.
    eval_channel = catalog.concrete_entries[0].evaluation_channel

    pkg_name = "wi014_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    res_true = _run(tmp_path, pkg_name, tmp_path / "run_true")
    outs_true = dict(res_true.outputs)
    assert outs_true[AREA_CH].root == 12.0
    assert outs_true[COST_CH].root == 3000.0
    ev_true = outs_true[eval_channel]
    rep_true = outs_true[REPORT_CH]
    assert ev_true.status == "satisfied" and ev_true.actual_value is True
    assert ev_true.margin == 2000.0
    assert rep_true.headline == "all_satisfied" and rep_true.assessed_count == 1

    _override_budget(staged, 2500.0)
    res_false = _run(tmp_path, pkg_name, tmp_path / "run_false")  # must NOT raise (INV-3)
    outs_false = dict(res_false.outputs)
    ev_false = outs_false[eval_channel]
    rep_false = outs_false[REPORT_CH]
    assert ev_false.status == "violated" and ev_false.actual_value is False
    assert ev_false.margin == -500.0
    assert rep_false.headline == "violation"
    assert outs_false[AREA_CH].root == outs_true[AREA_CH].root
    assert outs_false[COST_CH].root == outs_true[COST_CH].root

    # Report persisted beside the ordinary outputs (teax-state pin: persist-and-assert).
    manifest = res_false.manifest
    by_channel = {a.channel: a for a in manifest.artifacts}
    assert by_channel.get(REPORT_CH) is not None and by_channel[REPORT_CH].produced
    written_files = list((tmp_path / "run_false").glob("*/constraint_report.json"))
    assert written_files
    written = json.loads(written_files[0].read_text())
    assert written["headline"] == "violation"
    assert written["results"][0]["status"] == "violated"


@pytest.mark.execution
def test_zero_assertion_aggregator_not_assessed(tmp_path):
    """D11 under real simkit: a zero-eligible-but-active constraint pathway still emits an
    aggregator, and running it with no evaluations wired produces `not_assessed`. Built
    in-process (no live SysIDE model needed for the D7 unassessed shape — already proven
    live in `test_constraint_lowering.py::test_requirement_def_owner_cataloged_unassessed`;
    this test's job is to prove the *generated* aggregator behaves under real simkit, not to
    re-prove lowering)."""
    from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
    from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConcreteConstraint,
        EntryPoint,
        EntryPointType,
        ParameterGroup,
    )

    # simkit requires exactly one EntryPoint module in a pipeline; a single unused
    # design-attribute param satisfies that structurally without affecting the aggregator
    # behavior under test.
    dummy_group = ParameterGroup(
        name="unused_params",
        class_name="UnusedParams",
        source_file=Path("unused.sysml"),
        parameters=[
            EntryPoint(
                qualified_name="Pkg__unused",
                simple_name="unused",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=0.0,
                param_group="unused_params",
            )
        ],
    )

    unassessed = ConcreteConstraint(
        constraint_id="U1",
        usage_qualified_name="Pkg::Req::r1",
        source_local_identity="r1",
        source_form="satisfy",
        owner_kind="requirement_def",
        owner_qualified_name="Pkg::Req",
        owner_instance_path="Pkg__Req__r1",
        membership_kind=None,
        predicate_source_key="excluded:satisfy:Pkg::Req::r1",
        is_negated=None,
        expected_value=None,
        predicate_ir=None,
        inputs=[],
        evaluation_channel=None,
        eligible=False,
        exclusion={
            "kind": "unassessed_form",
            "reasons": [],
            "location": "<no location>",
        },
    )
    empty_graph = ComputationGraph(modules=[], entry_point_groups=[dummy_group], execution_order=[])
    deriver = ParameterGroupDeriver({}, calc_usages=[], calc_defs=[])
    extended = extend_graph_with_constraints(empty_graph, [unassessed], deriver)
    assert len(extended.modules) == 1  # aggregator only, D11

    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog

    empty_facts = ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])
    extended.constraint_catalog = assemble_constraint_catalog([unassessed], empty_facts)

    class _EmptyCtx:
        computation_graph = extended

    pkg_name = "zero_assert_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(_EmptyCtx(), staged, pkg_name)

    res = _run(tmp_path, pkg_name, tmp_path / "run_zero")
    rep = dict(res.outputs)["constraint_report"]
    assert rep.headline == "not_assessed"
    assert rep.assessed_count == 0
    assert rep.results == []


@pytest.mark.execution
def test_multi_instance_expansion_n_modules_one_predicate(tmp_path):
    """N modules -> N aggregator fields, one shared predicate (compile-once at execution)."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    pkg_name = "cmi_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    predicates_src = (staged / "modules" / "constraints" / "predicates.py").read_text()
    assert predicates_src.count("def constraint_pred_") == 1

    res = _run(tmp_path, pkg_name, tmp_path / "run_cmi")
    outs = dict(res.outputs)
    rep = outs["constraint_report"]
    assert rep.assessed_count == 3
    assert rep.headline == "all_satisfied"  # cell_rating=10.0 -> p=20.0 >= 0.0 for all three


@pytest.mark.execution
def test_committed_inline_snapshot_rejects_reserved_value(tmp_path):
    """The historical inline fixture now closes R-3 at generation, before execution."""
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    snapshot = FIXTURES_DIR / "constraint_inline" / "extraction_snapshot.json"
    ctx = build_pipeline_context_from_snapshot(snapshot)
    pkg_name = "constraint_inline_exec"
    staged = tmp_path / pkg_name
    with pytest.raises(CodeGenerationError) as error:
        _generate_full_package(ctx, staged, pkg_name)
    assert error.value.name_safety_violation.final_binding == "value"


# ---------------------------------------------------------------------------
# Audit cures (Phase 6): SC-2 (indeterminate, negated), SC-3 (modeled-default
# override), and Break-the-YAML. Built in-process (no live SysIDE needed — the
# same pattern `test_zero_assertion_aggregator_not_assessed` already proved) so
# each test controls its own operator/polarity/resolution shape directly.
# ---------------------------------------------------------------------------


def _ref(name: str):
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode

    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _literal_ir(value: float) -> str:
    from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import LiteralNode, serialize_expression

    node = LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    return serialize_expression(node)


def _cmp_ir(op: str, left: str, right: str) -> str:
    from agentic_mbse.sysml.expression_ir import OperatorNode, serialize_expression

    return serialize_expression(
        OperatorNode(operator=op, operands=[_ref(left), _ref(right)], operand_type=None)
    )


def _division_comparison_ir() -> str:
    from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode, serialize_expression

    division = OperatorNode(operator="/", operands=[_ref("a"), _ref("b")], operand_type=None)
    zero = LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=0.0, result_type="real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    return serialize_expression(
        OperatorNode(operator=">", operands=[division, zero], operand_type=None)
    )


def _single_constraint_graph(
    *,
    constraint_id: str,
    predicate_ir: str,
    negated: bool,
    inputs,  # list[ConcreteConstraintInput]
    design_attrs,  # dict[str, str] qn -> default_value (str form)
):
    """Build one eligible constraint + its aggregator through the real
    `extend_graph_with_constraints`/`assemble_constraint_catalog` machinery (not hand-wired
    PipelineModules) — every entry-point mint, default, and catalog field comes from
    production code, only the source facts are synthetic."""
    from pathlib import Path as _Path

    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
    from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConcreteConstraint,
        ConstraintFormalIdentity,
    )

    provenance_inputs = [
        item
        if item.formal_identity is not None
        else item.model_copy(
            update={"formal_identity": ConstraintFormalIdentity(raw_name=item.formal_name)}
        )
        for item in inputs
    ]

    concrete = ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name=f"pkg::Demo::{constraint_id}",
        source_local_identity=constraint_id,
        source_form="inline",
        owner_kind="part_def",
        owner_qualified_name="pkg::Demo",
        owner_instance_path="pkg__demo",
        membership_kind="assert",
        predicate_source_key=f"inline:pkg::Demo::{constraint_id}",
        is_negated=negated,
        expected_value=not negated,
        predicate_ir=predicate_ir,
        inputs=provenance_inputs,
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
    )
    empty_graph = ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])
    design_attr_data = [
        DesignAttributeData(
            name=qn.split("__")[-1],
            sysml_type="Real",
            default_value=default,
            unit=None,
            source_file=_Path("demo.sysml"),
            source_line=1,
            parent_part="pkg::Demo",
            qualified_name=qn,
        )
        for qn, default in design_attrs.items()
    ]
    deriver = ParameterGroupDeriver(
        {_Path("demo.sysml"): design_attr_data}, calc_usages=[], calc_defs=[]
    )
    extended = extend_graph_with_constraints(empty_graph, [concrete], deriver)
    empty_facts = ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])
    extended.constraint_catalog = assemble_constraint_catalog([concrete], empty_facts)

    class _SyntheticCtx:
        computation_graph = extended

    return _SyntheticCtx()


def _opposite_polarity_constraint_graph(*, predicate_ir: str, left: float, right: float):
    """Build two reversed-order wrappers sharing one definition-owned predicate body."""
    from pathlib import Path as _Path

    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
    from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConcreteConstraint,
        ConcreteConstraintInput,
        ConstraintFormalIdentity,
        ConstraintInputResolution,
    )

    inputs = [
        ConcreteConstraintInput(
            formal_name=name,
            formal_identity=ConstraintFormalIdentity(raw_name=name),
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn=f"pkg__Demo__{name}",
        )
        for name in ("a", "b")
    ]
    concrete = [
        ConcreteConstraint(
            constraint_id=constraint_id,
            usage_qualified_name=f"pkg::Demo::{constraint_id}",
            source_local_identity=constraint_id,
            source_form="definition_typed",
            owner_kind="part_def",
            owner_qualified_name="pkg::Demo",
            owner_instance_path="pkg__demo",
            membership_kind="assert",
            predicate_source_key="definition:pkg::SharedConstraint",
            is_negated=negated,
            expected_value=not negated,
            predicate_ir=predicate_ir,
            inputs=inputs,
            evaluation_channel=f"{constraint_id}__evaluation",
            eligible=True,
        )
        for constraint_id, negated in (("negative", True), ("positive", False))
    ]
    design_attrs = [
        DesignAttributeData(
            name=name,
            sysml_type="Real",
            default_value=str(value),
            unit=None,
            source_file=_Path("demo.sysml"),
            source_line=1,
            parent_part="pkg::Demo",
            qualified_name=f"pkg__Demo__{name}",
        )
        for name, value in (("a", left), ("b", right))
    ]
    deriver = ParameterGroupDeriver(
        {_Path("demo.sysml"): design_attrs}, calc_usages=[], calc_defs=[]
    )
    graph = extend_graph_with_constraints(
        ComputationGraph(modules=[], entry_point_groups=[], execution_order=[]), concrete, deriver
    )
    empty_facts = ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])
    graph.constraint_catalog = assemble_constraint_catalog(concrete, empty_facts)

    class _SyntheticCtx:
        computation_graph = graph

    return _SyntheticCtx()


def _set_json_value(pkg_dir: Path, qn: str, value: float) -> None:
    found = False
    for jf in (pkg_dir / "inputs").glob("*.json"):
        data = json.loads(jf.read_text())
        if qn in data:
            data[qn] = value
            jf.write_text(json.dumps(data, indent=2) + "\n")
            found = True
            break
    if not found:
        raise RuntimeError(f"{qn} not found in any inputs JSON")


@pytest.mark.execution
def test_indeterminate_point_at_execution(tmp_path):
    """SC-2: a non-finite operand at execution reads as `indeterminate`, never a confident
    verdict — the exact failure the Kleene work exists to prevent."""
    from sysml_codegen.resolution.models import ConcreteConstraintInput, ConstraintInputResolution

    inputs = [
        ConcreteConstraintInput(
            formal_name="a",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__a",
        ),
        ConcreteConstraintInput(
            formal_name="b",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__b",
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id="indet_check",
        predicate_ir=_cmp_ir(">", "a", "b"),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__a": "5.0", "pkg__Demo__b": "3.0"},
    )
    pkg_name = "indet_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    res_finite = _run(tmp_path, pkg_name, tmp_path / "run_finite")
    ev_finite = dict(res_finite.outputs)["indet_check__evaluation"]
    assert ev_finite.status == "satisfied" and ev_finite.actual_value is True

    _set_json_value(staged, "pkg__Demo__a", float("inf"))
    res_indet = _run(tmp_path, pkg_name, tmp_path / "run_indet")
    ev_indet = dict(res_indet.outputs)["indet_check__evaluation"]
    assert ev_indet.status == "indeterminate"
    assert ev_indet.actual_value is None
    assert ev_indet.margin is None


@pytest.mark.execution
def test_generated_constraint_wrapper_propagates_arithmetic_exception(tmp_path, monkeypatch):
    """The generated wrapper preserves the native raise before constructing evidence."""
    from sysml_codegen.resolution.models import (
        ConcreteConstraintInput,
        ConstraintInputResolution,
        ModuleKind,
    )

    inputs = [
        ConcreteConstraintInput(
            formal_name="a",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__a",
        ),
        ConcreteConstraintInput(
            formal_name="b",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__b",
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id="raising_check",
        predicate_ir=_division_comparison_ir(),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__a": "1.0", "pkg__Demo__b": "0.0"},
    )
    pkg_name = "raising_constraint_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    constraint_module = next(
        module
        for module in ctx.computation_graph.modules
        if module.module_kind == ModuleKind.CONSTRAINT
    )
    class_name = constraint_module.module_type.split(".")[-1]
    wrapper_file = next(
        path
        for path in (staged / "modules").rglob("*.py")
        if path.name != "predicates.py" and f"class {class_name}" in path.read_text()
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    dotted_module = ".".join((pkg_name, *wrapper_file.relative_to(staged).with_suffix("").parts))
    generated_wrapper = importlib.import_module(dotted_module)

    def evidence_must_not_be_constructed(**_kwargs):
        raise AssertionError("ConstraintEvaluation was constructed after arithmetic failed")

    monkeypatch.setattr(generated_wrapper, "ConstraintEvaluation", evidence_must_not_be_constructed)
    wrapper = getattr(generated_wrapper, class_name)()
    with pytest.raises(ZeroDivisionError) as error:
        wrapper.run(a=1.0, b=0.0)
    assert str(error.value) == "float division by zero"


@pytest.mark.execution
def test_negated_inline_assertion_at_execution(tmp_path):
    """SC-2: a negated, inline-form assertion's verdict and margin sign are correct under
    real execution — S4 never exercised negation at execution, only the compiler-unit level
    did (Phase 1)."""
    from sysml_codegen.resolution.models import ConcreteConstraintInput, ConstraintInputResolution

    inputs = [
        ConcreteConstraintInput(
            formal_name="a",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__a",
        ),
        ConcreteConstraintInput(
            formal_name="b",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__b",
        ),
    ]
    # a=3, b=5 -> raw predicate (a > b) is False; negated -> expected False -> satisfied.
    ctx = _single_constraint_graph(
        constraint_id="negated_check",
        predicate_ir=_cmp_ir(">", "a", "b"),
        negated=True,
        inputs=inputs,
        design_attrs={"pkg__Demo__a": "3.0", "pkg__Demo__b": "5.0"},
    )
    pkg_name = "negated_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    res = _run(tmp_path, pkg_name, tmp_path / "run_negated")
    ev = dict(res.outputs)["negated_check__evaluation"]
    assert ev.status == "satisfied"
    assert ev.actual_value is False  # the raw (un-negated) predicate value
    assert ev.margin == 2.0  # sign-flipped: raw (a-b)=-2.0, negated -> +2.0


@pytest.mark.execution
@pytest.mark.parametrize(
    (
        "operator",
        "left",
        "right",
        "raw_value",
        "positive_status",
        "positive_margin",
        "negative_status",
        "negative_margin",
    ),
    [
        (">", 3.0, 1.0, True, "satisfied", 2.0, "violated", -2.0),
        (">", 1.0, 3.0, False, "violated", -2.0, "satisfied", 2.0),
        (">", 2.0, 2.0, False, "violated", 0.0, "satisfied", 0.0),
        (">=", 2.0, 2.0, True, "satisfied", 0.0, "violated", 0.0),
        (">", float("inf"), 3.0, None, "indeterminate", None, "indeterminate", None),
    ],
    ids=["true", "false", "strict-boundary", "inclusive-boundary", "non-finite"],
)
def test_shared_definition_opposite_polarity_exact_once_execution(
    tmp_path,
    operator,
    left,
    right,
    raw_value,
    positive_status,
    positive_margin,
    negative_status,
    negative_margin,
):
    generated_left = 5.0 if raw_value is None else left
    ctx = _opposite_polarity_constraint_graph(
        predicate_ir=_cmp_ir(operator, "a", "b"), left=generated_left, right=right
    )
    operator_name = {">": "gt", ">=": "ge"}[operator]
    pkg_name = f"paired_{operator_name}_{str(raw_value).lower()}"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)
    if raw_value is None:
        _set_json_value(staged, "pkg__Demo__a", left)

    predicates_source = (staged / "modules" / "constraints" / "predicates.py").read_text()
    assert predicates_source.count("def constraint_pred_") == 1
    result = dict(_run(tmp_path, pkg_name, tmp_path / "run").outputs)
    positive = result["positive__evaluation"]
    negative = result["negative__evaluation"]
    assert positive.actual_value is raw_value
    assert negative.actual_value is raw_value
    assert (positive.status, positive.margin) == (positive_status, positive_margin)
    assert (negative.status, negative.margin) == (negative_status, negative_margin)


@pytest.mark.execution
def test_name_safety_collision_free_exact_evidence(tmp_path):
    from sysml_codegen.resolution.models import ConcreteConstraintInput, ConstraintInputResolution

    inputs = [
        ConcreteConstraintInput(
            formal_name="x",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__x",
        ),
        ConcreteConstraintInput(
            formal_name="limit",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__limit",
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id="name_safety_control",
        predicate_ir=_cmp_ir("<=", "x", "limit"),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__x": "2.0", "pkg__Demo__limit": "3.0"},
    )
    pkg_name = "name_safety_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    satisfied = dict(_run(tmp_path, pkg_name, tmp_path / "run_satisfied").outputs)[
        "name_safety_control__evaluation"
    ]
    assert (
        satisfied.actual_value,
        satisfied.status,
        satisfied.margin,
        satisfied.observed,
    ) == (True, "satisfied", 1.0, {"x": 2.0, "limit": 3.0})

    _set_json_value(staged, "pkg__Demo__x", 4.0)
    violated = dict(_run(tmp_path, pkg_name, tmp_path / "run_violated").outputs)[
        "name_safety_control__evaluation"
    ]
    assert (
        violated.actual_value,
        violated.status,
        violated.margin,
        violated.observed,
    ) == (False, "violated", -1.0, {"x": 4.0, "limit": 3.0})


@pytest.mark.execution
def test_modeled_default_override_flips_verdict(tmp_path):
    """SC-3: the defaulted formal is an overridable entry parameter. Not overriding uses the
    modeled default (satisfied); overriding flips the verdict (violated) — proving the
    default is entry-point-sourced, never baked into the compiled predicate (INV-6)."""
    from sysml_codegen.resolution.models import ConcreteConstraintInput, ConstraintInputResolution

    constraint_id = "default_override_check"
    inputs = [
        ConcreteConstraintInput(
            formal_name="measurement",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__measurement",
        ),
        ConcreteConstraintInput(
            formal_name="threshold",
            resolution=ConstraintInputResolution.MODELED_DEFAULT,
            default_ir=_literal_ir(3.0),
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id=constraint_id,
        predicate_ir=_cmp_ir(">", "measurement", "threshold"),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__measurement": "5.0"},
    )
    pkg_name = "default_override_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # Not overriding: value(5.0) > default threshold(3.0) -> satisfied.
    res_default = _run(tmp_path, pkg_name, tmp_path / "run_default")
    ev_default = dict(res_default.outputs)[f"{constraint_id}__evaluation"]
    assert ev_default.status == "satisfied" and ev_default.actual_value is True

    # The defaulted formal is exposed as a real, overridable entry parameter.
    threshold_qn = f"{constraint_id}__threshold"
    _set_json_value(staged, threshold_qn, 10.0)
    res_override = _run(tmp_path, pkg_name, tmp_path / "run_override")
    ev_override = dict(res_override.outputs)[f"{constraint_id}__evaluation"]
    assert ev_override.status == "violated" and ev_override.actual_value is False


@pytest.mark.execution
def test_break_the_yaml_surfaces_execution_failure(tmp_path):
    """S4 carry-forward (2): rewiring an upstream evaluation in the generated pipeline YAML
    surfaces as an execution failure THROUGH THE EXECUTOR (a schema/wiring failure), never a
    silent gap (INV-4 end-to-end)."""
    from sysml_codegen.resolution.models import ConcreteConstraintInput, ConstraintInputResolution

    inputs = [
        ConcreteConstraintInput(
            formal_name="a",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__a",
        ),
        ConcreteConstraintInput(
            formal_name="b",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
            design_attribute_qn="pkg__Demo__b",
        ),
    ]
    ctx = _single_constraint_graph(
        constraint_id="break_yaml_check",
        predicate_ir=_cmp_ir(">", "a", "b"),
        negated=False,
        inputs=inputs,
        design_attrs={"pkg__Demo__a": "5.0", "pkg__Demo__b": "3.0"},
    )
    pkg_name = "break_yaml_exec"
    staged = tmp_path / pkg_name
    _generate_full_package(ctx, staged, pkg_name)

    # Sanity: the untouched package executes cleanly first.
    _run(tmp_path, pkg_name, tmp_path / "run_before")

    # Rewire ONLY the aggregator's input reference to the constraint's evaluation channel —
    # not the constraint module's own output declaration — so the break is a pure wiring
    # gap (the producer still exists; the aggregator just no longer points at it).
    yaml_path = staged / "pipelines" / "pipeline.yaml"
    text = yaml_path.read_text()
    real_channel = "break_yaml_check__evaluation"
    target_line = next(
        line
        for line in text.splitlines()
        if "ConstraintEvaluation" in line and real_channel in line
    )
    broken_line = target_line.replace(real_channel, "nonexistent_evaluation_channel")
    assert broken_line != target_line
    text = text.replace(target_line, broken_line, 1)
    yaml_path.write_text(text)

    with pytest.raises(Exception):  # noqa: B017 — simkit's own wiring/schema failure class
        _run(tmp_path, pkg_name, tmp_path / "run_broken")
