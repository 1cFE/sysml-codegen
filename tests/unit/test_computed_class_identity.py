"""Copies of one computed definition feature share one class per distinct shape.

A formula or rollup module's type comes from the definition that owns it, so every copy
(``sub[0].capital_cost``, ``sub[1].capital_cost``) shares it and the registry registers it
once. Projection settles the one case where copies cannot share: when they render
different classes, each distinct shape takes the module type of its first copy's
occurrence path (design D3, D5, D8 in ``.project/active/repeated-rollup-collision``).

The shape comparison (``class_signature``) and the formula refusal are license-free; the
graph-level checks elaborate the ``tests/fixtures/repeated_rollup`` models and are licensed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.models import AutoImplContext, AutoImplOutput
from sysml_codegen.elaboration.project import _shape_split_module_types
from sysml_codegen.resolution.models import (
    ComputationGraph,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
    class_signature,
)
from tests.conftest import FIXTURES_DIR, requires_license

REPEATED = FIXTURES_DIR / "repeated_rollup"


def _rollup(
    name: str,
    leaf_keys: list[str],
    *,
    module_type: str = "p.sub.capital_costModule",
    kind: ModuleKind = ModuleKind.AGGREGATION,
    expression: str = "sum",
    python_type: str = "float",
    execution_order: int = 0,
) -> PipelineModule:
    return PipelineModule(
        name=name,
        module_type=module_type,
        inputs=[
            ModuleInput(
                param_name=f"capital_cost_{i}",
                python_type=python_type,
                source=InputSource(
                    source_type="entry_point", param_group="m_params", qualified_name=key
                ),
            )
            for i, key in enumerate(leaf_keys)
        ],
        outputs=[
            ModuleOutput(
                field_name="root", python_type="float", channel_name=f"{name}__capital_cost"
            )
        ],
        execution_order=execution_order,
        compiled_expression=expression,
        module_kind=kind,
        auto_impl_context=AutoImplContext(
            execution_steps=[],
            output_expressions=[AutoImplOutput(name="capital_cost", expression=expression)],
            output_count=1,
            single_output_expression=expression,
        ),
        calc_def_name="capital_cost",
        calc_def_qualified_name="P::Sub",
    )


def _leaves(prefix: str, count: int) -> list[str]:
    return [f"{prefix}__leaf[{i}]__capital_cost" for i in range(count)]


# --- class_signature -------------------------------------------------------------------


def test_copies_differing_only_in_occurrence_fields_share_a_signature():
    first = _rollup("p__top__sub[0]__capital_cost", _leaves("P__top__sub[0]", 3))
    second = _rollup(
        "p__top__sub[1]__capital_cost",
        _leaves("P__top__sub[1]", 3),
        module_type="p.top.sub_1.capital_costModule",
        execution_order=7,
    )
    assert class_signature(first) == class_signature(second)


@pytest.mark.parametrize(
    "change",
    [
        {"expression": "max"},
        {"kind": ModuleKind.FORMULA},
        {"python_type": "int"},
    ],
    ids=["compiled_expression", "module_kind", "input_python_type"],
)
def test_a_difference_the_class_body_renders_splits_the_signature(change):
    base = _rollup("p__top__a__capital_cost", _leaves("P__top__a", 3))
    other = _rollup("p__top__b__capital_cost", _leaves("P__top__b", 3), **change)
    assert class_signature(base) != class_signature(other)


def test_a_different_auto_impl_context_splits_the_signature():
    base = _rollup("p__top__a__capital_cost", _leaves("P__top__a", 3))
    assert base.auto_impl_context is not None
    other = base.model_copy(
        update={
            "name": "p__top__b__capital_cost",
            "auto_impl_context": base.auto_impl_context.model_copy(
                update={"single_output_expression": "capital_cost_0"}
            ),
        }
    )
    assert class_signature(base) != class_signature(other)


def test_a_different_input_count_splits_the_signature():
    three = _rollup("p__top__a__capital_cost", _leaves("P__top__a", 3))
    two = _rollup("p__top__b__capital_cost", _leaves("P__top__b", 2))
    assert class_signature(three) != class_signature(two)


# --- settlement ------------------------------------------------------------------------


def test_same_shape_copies_keep_the_definition_type():
    modules = {
        "s0": _rollup("p__top__sub[0]__capital_cost", _leaves("P__top__sub[0]", 3)),
        "s1": _rollup("p__top__sub[1]__capital_cost", _leaves("P__top__sub[1]", 3)),
    }
    assert _shape_split_module_types(modules) == {}


def test_differing_rollup_copies_take_one_type_per_shape_from_its_first_copy():
    modules = {
        "b1": _rollup("p__top__row[1]__b__capital_cost", _leaves("P__top__row[1]__b", 2)),
        "a0": _rollup("p__top__row[0]__a__capital_cost", _leaves("P__top__row[0]__a", 3)),
        "b0": _rollup("p__top__row[0]__b__capital_cost", _leaves("P__top__row[0]__b", 2)),
        "a1": _rollup("p__top__row[1]__a__capital_cost", _leaves("P__top__row[1]__a", 3)),
    }
    retyped = _shape_split_module_types(modules)
    assert {key: module.module_type for key, module in retyped.items()} == {
        "a0": "p.top.row_0.a.capital_costModule",
        "a1": "p.top.row_0.a.capital_costModule",
        "b0": "p.top.row_0.b.capital_costModule",
        "b1": "p.top.row_0.b.capital_costModule",
    }


def test_a_differing_group_that_includes_a_formula_is_an_internal_defect():
    """D8: a formula class's file is the definition's path for every copy, so a per-shape
    type cannot be given its own file. No model reaches this; it fails loudly if one does."""
    modules = {
        "a": _rollup("p__top__a__capital_cost", _leaves("P__top__a", 3), kind=ModuleKind.FORMULA),
        "b": _rollup("p__top__b__capital_cost", _leaves("P__top__b", 2), kind=ModuleKind.FORMULA),
    }
    with pytest.raises(AssertionError, match="include a formula"):
        _shape_split_module_types(modules)


# --- graph level (licensed) ------------------------------------------------------------


def _project(name: str, targets: tuple[str, ...] | None = None) -> ComputationGraph:
    from sysml_codegen.elaboration import project
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

    return project(elaborate_model_paths([Path(REPEATED / name)]), targets)


def _types(graph: ComputationGraph) -> dict[str, str]:
    return {
        module.name: module.module_type
        for module in graph.modules
        if module.module_kind in (ModuleKind.FORMULA, ModuleKind.AGGREGATION)
    }


@requires_license
def test_identical_copies_share_the_definition_type():
    types = _types(_project("two"))
    assert types["p__top__sub[0]__capital_cost"] == "p.sub.capital_costModule"
    assert types["p__top__sub[1]__capital_cost"] == "p.sub.capital_costModule"


@requires_license
def test_copies_of_different_arity_split_by_shape():
    types = _types(_project("arity"))
    assert types["p__top__a__capital_cost"] == "p.top.a.capital_costModule"
    assert types["p__top__b__capital_cost"] == "p.top.b.capital_costModule"


@requires_license
def test_identical_rows_of_differing_copies_share_one_type_per_shape():
    types = _types(_project("nestdiv"))
    assert {name: types[name] for name in types if "__row[" in name and "__a__" in name} == {
        "p__top__row[0]__a__capital_cost": "p.top.row_0.a.capital_costModule",
        "p__top__row[1]__a__capital_cost": "p.top.row_0.a.capital_costModule",
    }
    assert {name: types[name] for name in types if "__b__" in name} == {
        "p__top__row[0]__b__capital_cost": "p.top.row_0.b.capital_costModule",
        "p__top__row[1]__b__capital_cost": "p.top.row_0.b.capital_costModule",
    }


@requires_license
def test_same_shape_copies_share_inside_a_differing_group():
    types = _types(_project("trio"))
    assert types["p__top__s[0]__capital_cost"] == "p.top.s_0.capital_costModule"
    assert types["p__top__s[1]__capital_cost"] == "p.top.s_0.capital_costModule"
    assert types["p__top__b__capital_cost"] == "p.top.b.capital_costModule"


@requires_license
def test_a_selection_gets_the_same_type_as_the_full_build():
    selected = _types(_project("arity", ("P__top__b__capital_cost__capital_cost",)))
    assert selected == {"p__top__b__capital_cost": "p.top.b.capital_costModule"}
