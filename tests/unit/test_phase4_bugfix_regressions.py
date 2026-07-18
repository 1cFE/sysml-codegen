"""CI regression pins for the three Phase-4 execution-lane bug fixes (audit Finding 1).

Each of these bugs was invisible to every offline/generation-level test that existed before
the execution lane caught it: a bracket character reaching a Python identifier is only a
`SyntaxError` at *import* time, and a hardcoded-`None` design-attribute default only fails at
*pydantic JSON-load* time. None of that needs `simkit` or a live syside license — `ast.parse`
and a direct call into the graph-extension/catalog machinery both run offline, in CI, and both
go RED if the corresponding fix is reverted.
"""

from __future__ import annotations

import ast
from pathlib import Path

import jinja2

from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.generation.modules import (
    compile_shared_predicates,
    render_constraint_module,
    render_report_aggregator,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"


def _template_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _empty_facts():
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    return ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])


def _bracket_ref_ir() -> str:
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import (
        FeatureReferenceNode,
        OperatorNode,
        serialize_expression,
    )

    def ref(name: str) -> FeatureReferenceNode:
        return FeatureReferenceNode(
            reference=FeatureReferenceFact(
                source_name=name, target=None, target_types=[], chain_segments=[]
            ),
            operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
        )

    ir = OperatorNode(operator=">=", operands=[ref("p"), ref("zero")], operand_type=None)
    return serialize_expression(ir)


def _bracketed_concrete(index: int) -> ConcreteConstraint:
    """A concrete constraint whose `owner_instance_path` carries an `[i]` occurrence
    bracket — the exact shape `constraint_multi_instance` produces live (three Cell
    occurrences), reproduced here without needing syside."""
    # Mirrors mint_constraint_id's real shape ({owner_instance_path}__{source_local}__{sha})
    # exactly, brackets included — a hand-picked bracket-free constraint_id would decouple
    # this fixture from the actual bug (b) shape and let a reverted fix pass silently.
    constraint_id = f"pkg__the_design__c__cell[{index}]__nonneg__deadbeefcafef00d"
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name="pkg::Cell::nonneg",
        source_local_identity="nonneg",
        source_form="inline",
        owner_kind="part_def",
        owner_qualified_name="pkg::Cell",
        owner_instance_path=f"pkg__the_design__c__cell[{index}]",
        membership_kind="assert",
        is_negated=False,
        expected_value=True,
        predicate_ir=_bracket_ref_ir(),
        inputs=[
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel=f"pkg__the_design__c__cell[{index}]__power_calc__p",
            ),
            ConcreteConstraintInput(
                formal_name="zero",
                resolution=ConstraintInputResolution.MODELED_DEFAULT,
                default_ir=None,
            ),
        ],
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
    )


def _producer_module(index: int) -> PipelineModule:
    return PipelineModule(
        name=f"cell{index}_power_calc",
        module_type="pkg.PowerCalcModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="p",
                python_type="float",
                channel_name=f"pkg__the_design__c__cell[{index}]__power_calc__p",
            )
        ],
        execution_order=index,
        module_kind=ModuleKind.CALCULATION,
        calc_def_name="PowerCalc",
        calc_def_qualified_name="pkg::PowerCalc",
    )


def _occurrence_indexed_extended_graph():
    modules = [_producer_module(i) for i in range(3)]
    graph = ComputationGraph(
        modules=modules,
        entry_point_groups=[],
        execution_order=[m.name for m in modules],
    )
    concrete = [_bracketed_concrete(i) for i in range(3)]
    deriver = ParameterGroupDeriver({}, calc_usages=[], calc_defs=[])
    extended = extend_graph_with_constraints(graph, concrete, deriver)
    extended.constraint_catalog = assemble_constraint_catalog(concrete, _empty_facts())
    return extended, concrete


def test_occurrence_indexed_constraint_modules_have_valid_class_names_and_parse():
    """Regression pin for bug (a): bracket-unsafe class names.

    Reverting the `_constraint_module_type` bracket fix reproduces
    `Cell[0]NonnegConstraintModule` — a `SyntaxError` at import time. This test catches it
    offline: every occurrence's rendered `module_type` final segment must be a plain Python
    identifier, and its rendered module source must `ast.parse` cleanly.
    """
    extended, _concrete = _occurrence_indexed_extended_graph()
    constraint_modules = [m for m in extended.modules if m.module_kind is ModuleKind.CONSTRAINT]
    assert len(constraint_modules) == 3

    compiled = compile_shared_predicates(extended.constraint_catalog)
    template_env = _template_env()
    seen_class_names = set()
    for module in constraint_modules:
        class_name = module.module_type.split(".")[-1]
        assert class_name.isidentifier(), f"invalid class name: {class_name!r}"
        seen_class_names.add(class_name)

        code = render_constraint_module(
            module, extended.constraint_catalog, compiled, template_env, "pkg"
        )
        ast.parse(code)  # a bracket regression is a SyntaxError here
        assert f"class {class_name}" in code

    # Three distinct occurrences must not collapse onto one class name (a naive
    # bracket-strip-to-nothing regression would do exactly that).
    assert len(seen_class_names) == 3


def test_occurrence_indexed_aggregator_fields_are_valid_identifiers_and_parse():
    """Regression pin for bug (b): unsanitized aggregator field names.

    Reverting the `sanitize_name(c.constraint_id)` fix reproduces a Pydantic field
    declaration like `pkg__cell[0]__nonneg__...: ConstraintEvaluation` — a `SyntaxError`.
    """
    extended, _concrete = _occurrence_indexed_extended_graph()
    aggregator = next(m for m in extended.modules if m.module_kind is ModuleKind.REPORT_AGGREGATOR)

    assert len(aggregator.inputs) == 3
    for inp in aggregator.inputs:
        assert inp.param_name.isidentifier(), f"invalid aggregator field: {inp.param_name!r}"
        assert "[" not in inp.param_name and "]" not in inp.param_name

    code = render_report_aggregator(aggregator, extended.constraint_catalog, _template_env(), "pkg")
    ast.parse(code)  # a bracket regression is a SyntaxError here
    for inp in aggregator.inputs:
        assert f"{inp.param_name}: ConstraintEvaluation" in code


def test_constraint_only_design_attribute_gets_real_default_not_none():
    """Regression pin for bug (c): hardcoded-`None` design-attribute default.

    Reverting `design_attribute_default_value` wiring reproduces a minted entry point with
    `default_value=None` for a design attribute referenced *only* by an assert (never by a
    calc) — the exact shape that made `wi014_toy`'s `plant_budget` fail JSON validation at
    simkit load. This test goes RED on revert without needing simkit or a live model.
    """
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import (
        FeatureReferenceNode,
        OperatorNode,
        serialize_expression,
    )

    def ref(name: str) -> FeatureReferenceNode:
        return FeatureReferenceNode(
            reference=FeatureReferenceFact(
                source_name=name, target=None, target_types=[], chain_segments=[]
            ),
            operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
        )

    predicate_ir = serialize_expression(
        OperatorNode(operator="<=", operands=[ref("cost"), ref("budget")], operand_type=None)
    )
    concrete = ConcreteConstraint(
        constraint_id="pkg__demo__affordable__deadbeefcafef00d",
        usage_qualified_name="pkg::Demo::affordable",
        source_local_identity="affordable",
        source_form="inline",
        owner_kind="part_def",
        owner_qualified_name="pkg::Demo",
        owner_instance_path="pkg__demo",
        membership_kind="assert",
        is_negated=False,
        expected_value=True,
        predicate_ir=predicate_ir,
        inputs=[
            ConcreteConstraintInput(
                formal_name="cost",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel="pkg__demo__cost_calc__cost",
            ),
            ConcreteConstraintInput(
                formal_name="budget",
                resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                design_attribute_qn="pkg__Demo__budget",
            ),
        ],
        evaluation_channel="pkg__demo__affordable__deadbeefcafef00d__evaluation",
        eligible=True,
    )
    producer = PipelineModule(
        name="cost_calc",
        module_type="pkg.CostCalcModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="cost", python_type="float", channel_name="pkg__demo__cost_calc__cost"
            )
        ],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
        calc_def_name="CostCalc",
        calc_def_qualified_name="pkg::CostCalc",
    )
    graph = ComputationGraph(
        modules=[producer], entry_point_groups=[], execution_order=["cost_calc"]
    )
    design_attrs = {
        Path("demo.sysml"): [
            DesignAttributeData(
                name="budget",
                sysml_type="Real",
                default_value="5000.0",  # the constraint-only attribute's REAL default
                unit=None,
                source_file=Path("demo.sysml"),
                source_line=1,
                parent_part="pkg::Demo",
                qualified_name="pkg__Demo__budget",
            )
        ]
    }
    deriver = ParameterGroupDeriver(design_attrs, calc_usages=[], calc_defs=[])
    extended = extend_graph_with_constraints(graph, [concrete], deriver)

    budget_entries = [
        p
        for g in extended.entry_point_groups
        for p in g.parameters
        if p.qualified_name == "pkg__Demo__budget"
    ]
    assert len(budget_entries) == 1
    assert budget_entries[0].default_value == 5000.0  # NOT None
