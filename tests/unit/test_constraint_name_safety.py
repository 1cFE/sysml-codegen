from __future__ import annotations

from itertools import product

import pytest
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    IdentityFact,
    OperandTypeFact,
)
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.generation.constraint_name_safety import (
    PREDICATE_SCOPE_POLICY,
    WRAPPER_SCOPE_POLICY,
    ConstraintBinding,
    ScopePolicyMismatchError,
    format_name_safety_violation,
    graph_name_safety_violations,
    predicate_bindings,
    select_graph_name_safety_violation,
    select_name_safety_violation,
    validate_scope_bindings,
    verify_emitted_scope,
)
from sysml_codegen.generation.predicate_compiler import compile_predicate
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogSourceRecord,
    ConstraintFormalIdentity,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)


def _ref(name: str, qn: str | None = None) -> FeatureReferenceNode:
    target = IdentityFact(kind="Feature", name=name, qualified_name=qn) if qn else None
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=target, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def test_distinct_predicate_identities_cannot_share_one_binding():
    ir = OperatorNode(
        operator=">", operands=[_ref("x", "A::x"), _ref("x", "B::x")], operand_type=None
    )
    bindings = predicate_bindings(ir)
    violation = select_name_safety_violation(
        validate_scope_bindings(bindings, PREDICATE_SCOPE_POLICY)
    )
    assert violation is not None
    assert violation.kind == "binding_identity_collision"
    assert [identity.qualified_name for identity in violation.identities] == ["A::x", "B::x"]


@pytest.mark.parametrize(
    ("policy", "source", "model_names"),
    [
        (
            PREDICATE_SCOPE_POLICY,
            "def p(x, limit):\n    value = x\n    return value\n",
            {"x", "limit"},
        ),
        (
            WRAPPER_SCOPE_POLICY,
            "class M:\n"
            "    def run(self, x, limit):\n"
            "        body = x <= limit\n"
            "        verdict = x <= limit\n"
            "        return verdict\n",
            {"x", "limit"},
        ),
    ],
)
def test_production_scope_policies_match_semantic_bindings(policy, source, model_names):
    verify_emitted_scope(
        source,
        policy,
        model_names,
        function_name="p" if policy.scope == "predicate" else "run",
        class_name=None if policy.scope == "predicate" else "M",
    )


def test_scope_policy_fails_when_generated_local_changes():
    source = (
        "def p(x):\n    value = x\n    surprise = 1\n    return value\n"
    )
    with pytest.raises(ScopePolicyMismatchError, match="surprise"):
        verify_emitted_scope(source, PREDICATE_SCOPE_POLICY, {"x"}, function_name="p")


def test_wrapper_reserved_bindings_are_separate_policy():
    identity = ConstraintFormalIdentity(raw_name="self", qualified_name="Pkg::C::self")
    binding = ConstraintBinding(scope="wrapper", final_binding="self", identity=identity)
    violation = select_name_safety_violation(
        validate_scope_bindings([binding], WRAPPER_SCOPE_POLICY)
    )
    assert violation is not None
    assert violation.generated_binding == "self"


def test_identity_carrier_survives_copy_but_is_excluded_from_dumps():
    identity = ConstraintFormalIdentity(raw_name="limit", qualified_name="Pkg::C::limit")
    module_input = ModuleInput(
        param_name="limit",
        python_type="float",
        source=InputSource(source_type="module_output", producer_channel="up__limit"),
        formal_identity=identity,
    )
    assert module_input.model_copy(deep=True).formal_identity == identity
    assert "formal_identity" not in module_input.model_dump(mode="python")
    assert "formal_identity" not in module_input.model_dump(mode="json")


def _module(constraint_id: str, bindings: list[tuple[str, str]]) -> PipelineModule:
    return PipelineModule(
        name=constraint_id.lower(),
        module_type=f"constraints.{constraint_id}ConstraintModule",
        inputs=[
            ModuleInput(
                param_name=name,
                python_type="float",
                source=InputSource(
                    source_type="module_output", producer_channel=f"up__{name}__{index}"
                ),
                formal_identity=ConstraintFormalIdentity(raw_name=name, qualified_name=qn),
            )
            for index, (name, qn) in enumerate(bindings)
        ],
        outputs=[
            ModuleOutput(
                field_name="evaluation",
                python_type="ConstraintEvaluation",
                channel_name=f"{constraint_id.lower()}__evaluation",
            )
        ],
        execution_order=0,
        module_kind=ModuleKind.CONSTRAINT,
    )


def test_constraint_module_without_catalog_is_a_structured_join_violation():
    graph = ComputationGraph(
        modules=[_module("C1", [("x", "Pkg::C1::x")])],
        entry_point_groups=[],
        execution_order=["c1"],
        constraint_catalog=None,
    )
    violation = select_graph_name_safety_violation(graph)
    assert violation is not None
    assert violation.kind == "catalog_module_join"
    assert violation.final_binding == "c1"
    assert violation.identities == ()
    assert format_name_safety_violation(violation) == (
        "Constraint name-safety violation: scope='wrapper', kind='catalog_module_join', "
        "final_binding='c1'; identities=[]"
    )


def test_constraint_free_graph_without_catalog_remains_valid():
    graph = ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])
    assert graph_name_safety_violations(graph) == []


def _permuted_collision_graph(
    *, reverse_catalog: bool, reverse_formals: bool, reverse_leaves: bool, reverse_inputs: bool
) -> ComputationGraph:
    c1_leaf_specs = [("x", "A::x"), ("x", "B::x")]
    if reverse_leaves:
        c1_leaf_specs.reverse()
    c1_ir = OperatorNode(
        operator="<=",
        operands=[_ref(name, qn) for name, qn in c1_leaf_specs],
        operand_type=None,
    )
    c2_ir = OperatorNode(
        operator="<=",
        operands=[_ref("y", "C::y"), _ref("limit", "C::limit")],
        operand_type=None,
    )
    entries = [
        ConstraintCatalogEntry(
            constraint_id="C1",
            usage_qualified_name="Pkg::C1",
            source_local_identity="C1",
            source_form="inline",
            owner_qualified_name="Pkg",
            definition_qualified_name=None,
            owner_instance_path="Pkg",
            membership_kind="assert",
            predicate_source_key="inline:Pkg::C1",
            is_negated=False,
            expected_value=True,
            predicate_ir=serialize_expression(c1_ir),
            evaluation_channel="c1__evaluation",
        ),
        ConstraintCatalogEntry(
            constraint_id="C2",
            usage_qualified_name="Pkg::C2",
            source_local_identity="C2",
            source_form="inline",
            owner_qualified_name="Pkg",
            definition_qualified_name=None,
            owner_instance_path="Pkg",
            membership_kind="assert",
            predicate_source_key="inline:Pkg::C2",
            is_negated=False,
            expected_value=True,
            predicate_ir=serialize_expression(c2_ir),
            evaluation_channel="c2__evaluation",
        ),
    ]
    if reverse_catalog:
        entries.reverse()
    formal_names = ["x_a", "x_b"]
    if reverse_formals:
        formal_names.reverse()
    c1_inputs = [("x", "A::x"), ("x", "B::x")]
    if reverse_inputs:
        c1_inputs.reverse()
    return ComputationGraph(
        modules=[
            _module("C1", c1_inputs),
            _module("C2", [("y", "C::y"), ("limit", "C::limit")]),
        ],
        entry_point_groups=[],
        execution_order=["c1", "c2"],
        constraint_catalog=ConstraintCatalog(
            source_records=[
                ConstraintCatalogSourceRecord(
                    definition_qualified_name="Pkg::Def", formal_names=formal_names
                )
            ],
            concrete_entries=entries,
            fingerprint="permutation",
        ),
    )


@pytest.mark.parametrize(
    ("reverse_catalog", "reverse_formals", "reverse_leaves", "reverse_inputs"),
    product([False, True], repeat=4),
)
def test_graph_diagnostic_is_invariant_under_all_input_permutations(
    reverse_catalog, reverse_formals, reverse_leaves, reverse_inputs
):
    violation = select_graph_name_safety_violation(
        _permuted_collision_graph(
            reverse_catalog=reverse_catalog,
            reverse_formals=reverse_formals,
            reverse_leaves=reverse_leaves,
            reverse_inputs=reverse_inputs,
        )
    )
    assert violation is not None
    assert format_name_safety_violation(violation) == (
        "Constraint name-safety violation: constraint_id='C1', "
        "usage_qualified_name='Pkg::C1': scope='predicate', "
        "kind='binding_identity_collision', final_binding='x'; "
        "identities=[raw_name='x', qualified_name='A::x', "
        "raw_name='x', qualified_name='B::x']"
    )


def test_safe_predicate_argument_order_remains_first_occurrence_order():
    ir = OperatorNode(
        operator="<=",
        operands=[_ref("second"), _ref("first")],
        operand_type=None,
    )
    _source, arguments = compile_predicate(ir, "ordered_predicate")
    assert arguments == ["second", "first"]
