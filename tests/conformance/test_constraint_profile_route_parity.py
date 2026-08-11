"""Integrated live/codec continuity for profile-v4 source identity and polarity."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import parse, serialize
from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_profile
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode, serialize_expression
from agentic_mbse.sysml.syside_adapter import get_syside
from agentic_mbse.validation import level6_architecture

from sysml_codegen.analysis.constraint_lowering import (
    lower_constraints,
    prepare_constraint_usages,
)
from sysml_codegen.cli import GenerationConfig, _get_template_env
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan
from tests.conftest import requires_license
from tests.helpers.legacy_route import generate_via_legacy_route

_MODEL = """\
package RouteContinuity {
    private import ScalarValues::*;

    constraint def FixedLimit {
        1.0 <= 2.0
    }

    assert constraint inline_positive { 1.0 <= 2.0 }
    assert not constraint inline_negative { 1.0 <= 2.0 }
    assert constraint definition_positive : FixedLimit;
    assert not constraint definition_negative : FixedLimit;
}
"""


def _route_record(facts):
    profile = evaluate_profile(facts)
    concrete = lower_constraints(
        facts,
        prepared=prepare_constraint_usages(facts, occ_index=None, calc_usages=[]),
        registry=None,
        design_attrs={},
    )
    catalog = assemble_constraint_catalog(concrete, facts)
    graph = SimpleNamespace(constraint_catalog=catalog, modules=[])
    plan = build_constraint_generation_plan(graph, _get_template_env(), "route_pkg")
    return {
        "decisions": [
            (
                decision.identity.name,
                decision.eligibility.value,
                decision.is_negated,
                decision.expected_value,
                serialize_expression(decision.effective_predicate),
                tuple(diagnostic.reason for diagnostic in decision.diagnostics),
            )
            for decision in profile.decisions
        ],
        "concrete": [item.model_dump(mode="json") for item in concrete],
        "catalog": catalog.model_dump(mode="json"),
        "compiled": dict(plan.compiled_predicates),
        "predicates_code": plan.predicates_code,
    }


def _tree_manifest(root):
    if not root.exists():
        return None
    return [
        (path.relative_to(root).as_posix(), path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def _typed_literal(value, category: str) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(
            kind={"boolean": "LiteralBoolean", "string": "LiteralString"}[category],
            value=value,
            result_type={"boolean": "ScalarValues::Boolean", "string": "ScalarValues::String"}[
                category
            ],
        ),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


@requires_license
def test_positive_negated_inline_definition_live_codec_continuity(tmp_path) -> None:
    model_path = tmp_path / "route_continuity.sysml"
    model_path.write_text(_MODEL)
    model, diagnostics = get_syside().try_load_model([str(model_path)])
    assert not diagnostics.contains_errors()

    live = extract_constraint_facts(model)
    codec = parse(serialize(live))
    live_record = _route_record(live)
    codec_record = _route_record(codec)
    assert codec_record == live_record

    decisions = {row[0]: row for row in live_record["decisions"]}
    assert set(decisions) == {
        "inline_positive",
        "inline_negative",
        "definition_positive",
        "definition_negative",
    }
    assert all(row[1] == Eligibility.ADMIT.value for row in decisions.values())
    assert decisions["inline_positive"][2:4] == (False, True)
    assert decisions["inline_negative"][2:4] == (True, False)
    assert decisions["definition_positive"][2:4] == (False, True)
    assert decisions["definition_negative"][2:4] == (True, False)
    assert len({row[4] for row in decisions.values()}) == 1

    catalog_entries = live_record["catalog"]["concrete_entries"]
    definition_entries = [
        entry
        for entry in catalog_entries
        if entry["predicate_source_key"].startswith("definition:")
    ]
    assert len(definition_entries) == 2
    assert len({entry["predicate_source_key"] for entry in definition_entries}) == 1
    assert len({entry["predicate_ir"] for entry in definition_entries}) == 1
    assert len(live_record["compiled"]) == 3


@pytest.mark.parametrize("source_form", ["inline", "definition_typed"])
@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
@requires_license
def test_forged_source_identity_preserves_output_tree(
    tmp_path, monkeypatch: pytest.MonkeyPatch, caplog, source_form: str, initial_tree: str
) -> None:
    model_path = tmp_path / "route_continuity.sysml"
    model_path.write_text(_MODEL)
    model, diagnostics = get_syside().try_load_model([str(model_path)])
    assert not diagnostics.contains_errors()
    facts = extract_constraint_facts(model)
    usage = next(item for item in facts.usages if item.source.form == source_form)
    usage.source.effective_predicate_source = IdentityFact(
        kind=("AssertConstraintUsage" if source_form == "inline" else "ConstraintDefinition"),
        name="forged_source",
        qualified_name=(
            "RouteContinuity::forged_source"
            if source_form == "inline"
            else "RouteContinuity::OtherConstraint"
        ),
    )

    import sysml_codegen.cli as cli
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    def reject_during_context_build(*_args, **_kwargs):
        return lower_constraints(
            facts,
            prepared=prepare_constraint_usages(facts, occ_index=None, calc_usages=[]),
            registry=None,
            design_attrs={},
        )

    mutation_calls = {"clear": 0, "setup": 0}

    def forbidden_clear(*_args, **_kwargs):
        mutation_calls["clear"] += 1

    def forbidden_setup(*_args, **_kwargs):
        mutation_calls["setup"] += 1

    monkeypatch.setattr(pipeline_builder, "build_pipeline_context", reject_during_context_build)
    monkeypatch.setattr(cli, "_clear_output_directory", forbidden_clear)
    monkeypatch.setattr(cli, "_setup_output_directories", forbidden_setup)

    output = tmp_path / "output"
    if initial_tree == "populated":
        (output / "nested").mkdir(parents=True)
        (output / "marker.bin").write_bytes(b"unchanged\x00")
        (output / "nested" / "record.txt").write_text("preserve me\n")
    before = (output.exists(), _tree_manifest(output))

    config = GenerationConfig(output_path=output, models_path=model_path, overwrite=True)
    assert generate_via_legacy_route(config) is False
    assert mutation_calls == {"clear": 0, "setup": 0}
    assert (output.exists(), _tree_manifest(output)) == before
    assert "effective predicate source identity violation" in caplog.text


@requires_license
def test_compound_profile_diagnostics_reach_level6_and_preserve_output_tree(
    tmp_path, monkeypatch: pytest.MonkeyPatch, caplog
) -> None:
    model_path = tmp_path / "route_continuity.sysml"
    model_path.write_text(_MODEL)
    model, diagnostics = get_syside().try_load_model([str(model_path)])
    assert not diagnostics.contains_errors()
    facts = extract_constraint_facts(model)
    usage = next(item for item in facts.usages if item.identity.name == "inline_positive")
    usage.predicate = OperatorNode(
        operator="and",
        operands=[
            OperatorNode(
                operator="<",
                operands=[_typed_literal(True, "boolean"), _typed_literal(False, "boolean")],
                operand_type=None,
            ),
            OperatorNode(
                operator="<=",
                operands=[_typed_literal("a", "string"), _typed_literal("b", "string")],
                operand_type=None,
            ),
        ],
        operand_type=None,
    )
    facts.usages = [usage]
    facts.definitions = []

    decision = evaluate_profile(facts).decisions[0]
    assert [item.reason for item in decision.diagnostics] == [
        "block_ordering_category_pair",
        "block_ordering_category_pair",
    ]
    assert [item.construct for item in decision.diagnostics] == ["comparison", "comparison"]

    monkeypatch.setattr(level6_architecture, "extract_constraint_facts", lambda _model: facts)
    issues = level6_architecture.check_constraint_executability(object())
    assert [issue.suggestion for issue in issues] == [
        "ordering '<' requires Integer/Real operands or two Quantity operands; got "
        "boolean/boolean. Rewrite both operands as one admitted numerical pair.",
        "ordering '<=' requires Integer/Real operands or two Quantity operands; got "
        "string/string. Rewrite both operands as one admitted numerical pair.",
    ]

    import sysml_codegen.cli as cli
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    def reject_during_context_build(*_args, **_kwargs):
        return lower_constraints(
            facts,
            prepared=prepare_constraint_usages(facts, occ_index=None, calc_usages=[]),
            registry=None,
            design_attrs={},
        )

    mutation_calls = {"clear": 0, "setup": 0}
    monkeypatch.setattr(pipeline_builder, "build_pipeline_context", reject_during_context_build)
    monkeypatch.setattr(
        cli,
        "_clear_output_directory",
        lambda *_args, **_kwargs: mutation_calls.__setitem__("clear", mutation_calls["clear"] + 1),
    )
    monkeypatch.setattr(
        cli,
        "_setup_output_directories",
        lambda *_args, **_kwargs: mutation_calls.__setitem__("setup", mutation_calls["setup"] + 1),
    )
    output = tmp_path / "output"
    (output / "nested").mkdir(parents=True)
    (output / "marker.bin").write_bytes(b"unchanged\x00")
    (output / "nested" / "record.txt").write_text("preserve me\n")
    before = _tree_manifest(output)

    config = GenerationConfig(output_path=output, models_path=model_path, overwrite=True)
    assert generate_via_legacy_route(config) is False
    assert mutation_calls == {"clear": 0, "setup": 0}
    assert _tree_manifest(output) == before
    assert caplog.text.index("boolean/boolean") < caplog.text.index("string/string")
