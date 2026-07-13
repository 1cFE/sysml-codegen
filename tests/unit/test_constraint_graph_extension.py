"""Phase 4 (P3 EXTEND): extend_graph_with_constraints — offline, no syside needed.

Pure data transformation over ComputationGraph + ConcreteConstraint +
ParameterGroupDeriver, so every case is testable without a live model.
"""

from pathlib import Path

import pytest

from sysml_codegen.analysis.constraint_lowering import (
    AGGREGATOR_MODULE_NAME,
    extend_graph_with_constraints,
)
from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)


def _empty_graph() -> ComputationGraph:
    return ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])


def _graph_with_producer(channel: str) -> ComputationGraph:
    """A graph with one producer module whose output is `channel`."""
    module = PipelineModule(
        name="producer",
        module_type="pkg.ProducerModule",
        inputs=[],
        outputs=[ModuleOutput(field_name="p", python_type="float", channel_name=channel)],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )
    return ComputationGraph(
        modules=[module], entry_point_groups=[], execution_order=["producer"]
    )


def _deriver(attrs: list[DesignAttributeData] | None = None) -> ParameterGroupDeriver:
    design_attrs = {Path("design.sysml"): attrs or []}
    return ParameterGroupDeriver(design_attrs, calc_usages=[], calc_defs=[])


def _cc(
    constraint_id: str,
    inputs: list[ConcreteConstraintInput],
    eligible: bool = True,
) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name="Design__c__nonneg",
        source_local_identity="nonneg",
        source_form="definition_typed",
        owner_kind="part_def",
        owner_qualified_name="Design__Cell",
        owner_instance_path="Design__c",
        membership_kind=None,
        is_negated=False,
        expected_value=True,
        predicate_ir='{"kind":"literal"}' if eligible else None,
        inputs=inputs if eligible else [],
        evaluation_channel=f"{constraint_id}__evaluation" if eligible else None,
        eligible=eligible,
    )


def test_module_output_input_wires_producer_channel_no_mint():
    channel = "Design__c__power_calc__p"
    graph = _graph_with_producer(channel)
    cc = _cc(
        "id1",
        [
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel=channel,
            )
        ],
    )
    extended = extend_graph_with_constraints(graph, [cc], _deriver())
    constraint_module = next(m for m in extended.modules if m.module_kind == ModuleKind.CONSTRAINT)
    assert constraint_module.inputs[0].source.source_type == "module_output"
    assert constraint_module.inputs[0].source.producer_channel == channel
    assert extended.entry_point_groups == []  # nothing minted


def test_design_attribute_input_mints_deduped_entry_point():
    attr = DesignAttributeData(
        name="threshold",
        sysml_type="Real",
        default_value="10.0",
        unit=None,
        source_file=Path("design.sysml"),
        source_line=1,
        parent_part="Design",
        qualified_name="Design__threshold",
    )
    graph = _empty_graph()
    cc = _cc(
        "id1",
        [
            ConcreteConstraintInput(
                formal_name="threshold",
                resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                design_attribute_qn="Design__threshold",
            )
        ],
    )
    extended = extend_graph_with_constraints(graph, [cc], _deriver([attr]))
    all_params = [p for g in extended.entry_point_groups for p in g.parameters]
    assert len(all_params) == 1
    assert all_params[0].qualified_name == "Design__threshold"
    assert all_params[0].entry_type == "design_attribute"


def test_design_attribute_already_an_entry_point_is_reused_not_reminted():
    """F4-safe: a QN already present as an entry point is reused, never a
    second mint (INV-5)."""
    attr = DesignAttributeData(
        name="threshold",
        sysml_type="Real",
        default_value="10.0",
        unit=None,
        source_file=Path("design.sysml"),
        source_line=1,
        parent_part="Design",
        qualified_name="Design__threshold",
    )
    graph = _empty_graph()
    two_constraints = [
        _cc(
            "id1",
            [
                ConcreteConstraintInput(
                    formal_name="threshold",
                    resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                    design_attribute_qn="Design__threshold",
                )
            ],
        ),
        _cc(
            "id2",
            [
                ConcreteConstraintInput(
                    formal_name="threshold",
                    resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
                    design_attribute_qn="Design__threshold",
                )
            ],
        ),
    ]
    extended = extend_graph_with_constraints(graph, two_constraints, _deriver([attr]))
    all_params = [p for g in extended.entry_point_groups for p in g.parameters]
    assert len(all_params) == 1  # deduped, not two


def test_modeled_default_mints_library_default_scoped_to_constraint():
    graph = _empty_graph()
    cc = _cc(
        "id1",
        [
            ConcreteConstraintInput(
                formal_name="margin",
                resolution=ConstraintInputResolution.MODELED_DEFAULT,
                default_ir=(
                    '{"kind":"literal","literal":{"kind":"LiteralRational",'
                    '"value":2.5,"result_type":null},"operand_type":'
                    '{"category":"real","enumeration":null,"unit":null},'
                    '"schema_version":"expression-ir/v1"}'
                ),
            )
        ],
    )
    extended = extend_graph_with_constraints(graph, [cc], _deriver())
    all_params = [p for g in extended.entry_point_groups for p in g.parameters]
    assert len(all_params) == 1
    assert all_params[0].qualified_name == "id1__margin"
    assert all_params[0].entry_type == "library_default"
    assert all_params[0].default_value == 2.5


def test_unassessed_record_contributes_no_constraint_node_no_mint():
    """No CONSTRAINT node and no minted entry point for an unassessed record — but the
    aggregator DOES still appear (D11): the constraint pathway is active (this function
    ran at all), so a zero-eligible model still gets the `not_assessed` report surface."""
    graph = _empty_graph()
    cc = _cc("id1", [], eligible=False)
    extended = extend_graph_with_constraints(graph, [cc], _deriver())
    assert extended.entry_point_groups == []
    assert not any(m.module_kind == ModuleKind.CONSTRAINT for m in extended.modules)
    assert [m.name for m in extended.modules] == [AGGREGATOR_MODULE_NAME]
    aggregator = extended.modules[0]
    assert aggregator.inputs == []  # zero-eligible -> zero-required-field aggregator input


def test_aggregator_appears_whenever_lowering_ran_d11():
    """D11: the aggregator emits whenever `extend_graph_with_constraints` runs at all,
    with real inputs when eligible constraints exist and zero inputs when they don't —
    never absent."""
    graph = _graph_with_producer("Design__c__power_calc__p")
    cc = _cc(
        "id1",
        [
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel="Design__c__power_calc__p",
            )
        ],
    )
    extended = extend_graph_with_constraints(graph, [cc], _deriver())
    assert any(m.name == AGGREGATOR_MODULE_NAME for m in extended.modules)
    assert any(m.module_kind == ModuleKind.REPORT_AGGREGATOR for m in extended.modules)

    # All-unassessed: the aggregator still appears (D11), with zero required inputs.
    extended_empty = extend_graph_with_constraints(
        _empty_graph(), [_cc("id2", [], eligible=False)], _deriver()
    )
    agg_modules = [m for m in extended_empty.modules if m.name == AGGREGATOR_MODULE_NAME]
    assert len(agg_modules) == 1
    assert agg_modules[0].inputs == []


def test_v11_violation_raises_on_uncovered_module_output():
    """A module_output input pointing at a channel no module produces fails
    _validate_channel_references -- must raise, not silently pass through."""
    graph = _empty_graph()  # no producer module at all
    cc = _cc(
        "id1",
        [
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel="Design__c__power_calc__p",
            )
        ],
    )
    with pytest.raises(ValueError, match="power_calc"):
        extend_graph_with_constraints(graph, [cc], _deriver())


def test_evaluation_channels_distinct_and_multiple_constraint_modules_present():
    graph = _empty_graph()
    ccs = [_cc(f"id{i}", []) for i in range(3)]
    # each _cc has empty inputs -- fine, no coverage requirement without inputs
    extended = extend_graph_with_constraints(graph, ccs, _deriver())
    constraint_modules = [m for m in extended.modules if m.module_kind == ModuleKind.CONSTRAINT]
    assert len(constraint_modules) == 3
    channels = {m.outputs[0].channel_name for m in constraint_modules}
    assert len(channels) == 3
