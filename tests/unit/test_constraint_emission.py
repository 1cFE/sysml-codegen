"""Unit tests for the two integration seams S4 never ran (Item 7 / Phase 3).

(1) Compile-once meets class-per-assertion: under a two-instance-of-one-definition fixture,
    the shared predicate compiles exactly once and both instances' modules import it (INV-1).
(2) Leaf-name / input-name reconciliation (B5): a predicate leaf without a matching module
    input fails generation loudly, naming the `constraint_id`.

Also covers the same-IR generation guard (INV-2, both arms) at the catalog level.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest
from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog, assert_same_ir
from sysml_codegen.generation.modules import (
    compile_shared_predicates,
    constraint_predicate_function_name,
    render_constraint_module,
)
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConstraintFormalIdentity,
    InputSource,
    ModuleInput,
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


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _predicate_ir(op: str = ">") -> str:
    ir = OperatorNode(operator=op, operands=[_ref("a"), _ref("b")], operand_type=None)
    return serialize_expression(ir)


def _empty_facts() -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])


def _concrete(
    constraint_id: str,
    owner_instance_path: str,
    *,
    usage_qualified_name: str = "Pkg::Cell::nonneg",
    predicate_source_key: str | None = None,
    predicate_ir: str | None = None,
    is_negated: bool = False,
) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name=usage_qualified_name,
        source_local_identity="nonneg",
        source_form="inline",
        owner_kind="part_def",
        owner_qualified_name="Pkg::Cell",
        owner_instance_path=owner_instance_path,
        membership_kind="assert",
        predicate_source_key=predicate_source_key or usage_qualified_name,
        is_negated=is_negated,
        expected_value=not is_negated,
        predicate_ir=predicate_ir if predicate_ir is not None else _predicate_ir(),
        inputs=[],
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
    )


def _module_for(constraint_id: str, module_type: str, param_names: list[str]) -> PipelineModule:
    return PipelineModule(
        name=constraint_id.lower(),
        module_type=module_type,
        inputs=[
            ModuleInput(
                param_name=name,
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel=f"up__{name}"),
                formal_identity=ConstraintFormalIdentity(raw_name=name),
            )
            for name in param_names
        ],
        outputs=[
            ModuleOutput(
                field_name="evaluation",
                python_type="ConstraintEvaluation",
                channel_name=f"{constraint_id}__evaluation",
            )
        ],
        execution_order=0,
        module_kind=ModuleKind.CONSTRAINT,
    )


# ---------------------------------------------------------------------------
# (1) Compile-once meets class-per-assertion (INV-1)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CL-02")
def test_two_instances_of_one_definition_share_one_compiled_predicate():
    concrete = [
        _concrete("C1", "Pkg__Cell_1"),
        _concrete("C2", "Pkg__Cell_2"),
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    assert len(catalog.concrete_entries) == 2

    compiled = compile_shared_predicates(catalog)
    assert len(compiled) == 1  # one definition -> one compiled function (D3/INV-1)

    fn_name_1, src_1, args_1 = next(iter(compiled.values()))
    module_1 = _module_for("C1", "pkg.Cell1ConstraintModule", args_1)
    module_2 = _module_for("C2", "pkg.Cell2ConstraintModule", args_1)
    code_1 = render_constraint_module(module_1, catalog, compiled, _template_env(), "pkg")
    code_2 = render_constraint_module(module_2, catalog, compiled, _template_env(), "pkg")

    # Both classes import the SAME shared function; neither inlines/duplicates it.
    assert f"_finalize_assertion, {fn_name_1}" in code_1
    assert f"_finalize_assertion, {fn_name_1}" in code_2
    assert "def _cmp" not in code_1  # the Kleene runtime is not duplicated per class


def test_three_instances_still_compile_once(monkeypatch=None):
    concrete = [_concrete(f"C{i}", f"Pkg__Cell_{i}") for i in range(3)]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    compiled = compile_shared_predicates(catalog)
    assert len(compiled) == 1


def test_opposite_polarity_usages_share_one_neutral_source_body() -> None:
    source_key = "definition:Pkg::ReusableConstraint"
    concrete = [
        _concrete(
            "positive",
            "Pkg__positive",
            usage_qualified_name="Pkg::positive",
            predicate_source_key=source_key,
        ),
        _concrete(
            "negative",
            "Pkg__negative",
            usage_qualified_name="Pkg::negative",
            predicate_source_key=source_key,
            is_negated=True,
        ),
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    assert {entry.predicate_source_key for entry in catalog.concrete_entries} == {source_key}
    assert {(entry.is_negated, entry.expected_value) for entry in catalog.concrete_entries} == {
        (False, True),
        (True, False),
    }
    compiled = compile_shared_predicates(catalog)
    assert list(compiled) == [source_key]
    _name, source, _args = compiled[source_key]
    assert "_PredicateBodyResult" in source
    body_source = source.split("def constraint_pred_", maxsplit=1)[1]
    assert 'status = "satisfied"' not in body_source


COLLISION_CASES = [
    (("Pkg::Foo", "Pkg::foo"), "constraint_pred_pkg__foo"),
    (("Pkg::foo__bar", "Pkg::foo_bar"), "constraint_pred_pkg__foo_bar"),
    (("Pkg::'Foo-Bar'", "Pkg::Foo_Bar"), "constraint_pred_pkg__foo_bar"),
]


@pytest.mark.parametrize(("raw_keys", "expected_name"), COLLISION_CASES)
def test_constraint_predicate_function_name_matches_emission(raw_keys, expected_name):
    assert [constraint_predicate_function_name(key) for key in raw_keys] == [
        expected_name,
        expected_name,
    ]


@pytest.mark.parametrize(("raw_keys", "expected_name"), COLLISION_CASES)
@pytest.mark.parametrize("reverse", [False, True])
def test_distinct_definition_keys_with_same_function_name_are_rejected_deterministically(
    raw_keys, expected_name, reverse
):
    ordered_keys = tuple(reversed(raw_keys)) if reverse else raw_keys
    concrete = [
        _concrete("C1", "Pkg__Cell_1", usage_qualified_name=ordered_keys[0]),
        _concrete(
            "C2",
            "Pkg__Cell_2",
            usage_qualified_name=ordered_keys[1],
            predicate_ir=_predicate_ir("<"),
        ),
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    sorted_keys = sorted(raw_keys)
    expected = (
        "Predicate function-name collision: raw definition keys "
        f"{sorted_keys!r} all normalize to {expected_name!r}. "
        "Rename one; generation cannot emit them safely."
    )
    with pytest.raises(CodeGenerationError) as error:
        compile_shared_predicates(catalog)
    assert str(error.value) == expected


def test_collision_rejected_before_predicate_compilation(monkeypatch):
    import sysml_codegen.generation.predicate_compiler as predicate_compiler

    calls = []
    monkeypatch.setattr(
        predicate_compiler,
        "compile_predicate",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    catalog = assemble_constraint_catalog(
        [
            _concrete("C1", "Pkg__Cell_1", usage_qualified_name="Pkg::Foo"),
            _concrete("C2", "Pkg__Cell_2", usage_qualified_name="Pkg::foo"),
        ],
        _empty_facts(),
    )
    with pytest.raises(CodeGenerationError, match="constraint_pred_pkg__foo"):
        compile_shared_predicates(catalog)
    assert calls == []


def test_collision_free_definition_keys_retain_existing_names():
    catalog = assemble_constraint_catalog(
        [
            _concrete("C1", "Pkg__Cell_1", usage_qualified_name="Pkg::Foo"),
            _concrete("C2", "Pkg__Cell_2", usage_qualified_name="Pkg::Bar"),
        ],
        _empty_facts(),
    )
    compiled = compile_shared_predicates(catalog)
    assert {key: value[0] for key, value in compiled.items()} == {
        "Pkg::Foo": "constraint_pred_pkg__foo",
        "Pkg::Bar": "constraint_pred_pkg__bar",
    }


# ---------------------------------------------------------------------------
# (2) Leaf-name / input-name reconciliation (B5)
# ---------------------------------------------------------------------------


def test_leaf_without_matching_input_fails_generation_naming_id():
    concrete = [_concrete("C1", "Pkg__Cell_1")]  # predicate leaves: a, b
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    compiled = compile_shared_predicates(catalog)

    # Module only wires "a" — "b" has no matching input (B5 violation).
    bad_module = _module_for("C1", "pkg.Cell1ConstraintModule", ["a"])
    with pytest.raises(CodeGenerationError, match="C1"):
        render_constraint_module(bad_module, catalog, compiled, _template_env(), "pkg")


def test_positive_fixture_leaf_and_input_coincide():
    """The B5 positive companion: when they coincide, generation succeeds."""
    concrete = [_concrete("C1", "Pkg__Cell_1")]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    compiled = compile_shared_predicates(catalog)
    good_module = _module_for("C1", "pkg.Cell1ConstraintModule", ["a", "b"])
    code = render_constraint_module(good_module, catalog, compiled, _template_env(), "pkg")
    assert "class Cell1ConstraintModule" in code


# ---------------------------------------------------------------------------
# Same-IR generation guard (INV-2)
# ---------------------------------------------------------------------------


def test_same_ir_mutation_across_shared_definition_fails_naming_id():
    concrete = [
        _concrete("C1", "Pkg__Cell_1"),
        _concrete("C2", "Pkg__Cell_2", predicate_ir=_predicate_ir("<")),  # diverges (arm b)
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    with pytest.raises(CodeGenerationError, match="C2"):
        assert_same_ir(catalog.concrete_entries)


def test_round_trip_instability_fails_arm_a():
    bad_ir = _predicate_ir() + " "  # trailing whitespace: parses, but re-serializes without it
    concrete = [_concrete("C1", "Pkg__Cell_1", predicate_ir=bad_ir)]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    with pytest.raises(CodeGenerationError, match="C1"):
        assert_same_ir(catalog.concrete_entries)


def test_same_ir_clean_entries_pass():
    concrete = [_concrete("C1", "Pkg__Cell_1"), _concrete("C2", "Pkg__Cell_2")]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    assert_same_ir(catalog.concrete_entries)  # no raise


def test_mutated_catalog_polarity_fails_before_compilation():
    catalog = assemble_constraint_catalog([_concrete("C1", "Pkg__Cell_1")], _empty_facts())
    with pytest.raises(ValueError):
        catalog.concrete_entries[0].is_negated = None
    compile_shared_predicates(catalog)


def test_catalog_filter_revalidates_model_copy_before_fingerprinting():
    invalid = _concrete("C1", "Pkg__Cell_1").model_copy(update={"eligible": False})
    with pytest.raises(ValueError, match="unassessed.*executable payload"):
        assemble_constraint_catalog([invalid], _empty_facts())


# ---------------------------------------------------------------------------
# D11: catalog assembled even with zero eligible entries
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-CL-03")
def test_catalog_assembled_with_zero_eligible_entries():
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
    catalog = assemble_constraint_catalog([unassessed], _empty_facts())
    assert catalog.concrete_entries == []
    assert [record.constraint_id for record in catalog.excluded_records] == ["U1"]
    assert catalog.excluded_records[0].exclusion.kind == "unassessed_form"
    assert catalog.fingerprint  # still deterministic/non-empty


def test_catalog_projects_excluded_records_in_id_order():
    def excluded(constraint_id: str, kind: str, reasons: list[str]) -> ConcreteConstraint:
        return ConcreteConstraint(
            constraint_id=constraint_id,
            usage_qualified_name=f"Pkg::{constraint_id}",
            source_local_identity=constraint_id,
            source_form="inline",
            owner_kind="part_def",
            owner_qualified_name="Pkg::Cell",
            owner_instance_path="Pkg__cell",
            membership_kind="assert",
            predicate_source_key=f"inline:Pkg::{constraint_id}",
            is_negated=False,
            expected_value=None,
            predicate_ir=None,
            inputs=[],
            evaluation_channel=None,
            eligible=False,
            exclusion={
                "kind": kind,
                "reasons": reasons,
                "location": "model.sysml:12:4",
            },
        )

    catalog = assemble_constraint_catalog(
        [
            excluded("B", "non_numerical", ["warn_b", "warn_a"]),
            excluded("A", "unsupported_owner", []),
        ],
        _empty_facts(),
    )

    assert [record.constraint_id for record in catalog.excluded_records] == ["A", "B"]
    projected = catalog.excluded_records[1]
    assert projected.exclusion.kind == "non_numerical"
    assert projected.exclusion.reasons == ["warn_b", "warn_a"]
    assert projected.exclusion.location == "model.sysml:12:4"
