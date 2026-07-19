from __future__ import annotations

import json
import logging
from pathlib import Path

from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
    parse,
)
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.snapshot.serializer import serialize_extraction_snapshot

LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"


def _anonymous_non_numerical(file: Path, line: int) -> ConstraintUsageFact:
    identity = IdentityFact(kind="AssertConstraintUsage", name=None, qualified_name=None)
    predicate = OperatorNode(
        operator="==",
        operands=[
            LiteralNode(
                literal=LiteralFact(kind="LiteralBoolean", value=True, result_type="boolean"),
                operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
            ),
            LiteralNode(
                literal=LiteralFact(kind="LiteralBoolean", value=False, result_type="boolean"),
                operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    return ConstraintUsageFact(
        identity=identity,
        location=LocationFact(str(file), line, 2),
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=identity,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Pkg"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts_for(root: Path) -> ConstraintFacts:
    model = root / "model.sysml"
    model.write_text("")
    return ConstraintFacts(
        definitions=[],
        usages=[_anonymous_non_numerical(model, 10), _anonymous_non_numerical(model, 20)],
        contexts=[],
        diagnostics=[],
    )


def _serialize_facts(facts: ConstraintFacts, roots: list[Path]) -> ConstraintFacts:
    snapshot = serialize_extraction_snapshot(
        model_name="identity",
        calc_defs=[],
        calc_usages=[],
        design_attributes={},
        hierarchy_data=None,
        aggregation_expressions=[],
        computed_attributes=[],
        channel_aliases=[],
        constraint_facts=facts,
        part_occurrences={},
        constraint_lowering_mode="applied",
        model_paths=roots,
    )
    return parse(json.dumps(snapshot["constraint_facts"]))


def _lower(facts: ConstraintFacts, mode: str, roots: list[Path]):
    return lower_constraints(
        facts,
        occ_index=None,
        registry=None,
        design_attrs={},
        calc_usages=[],
        source_location_mode=mode,
        source_roots=roots,
    )


def _projection(records, facts: ConstraintFacts):
    catalog = assemble_constraint_catalog(records, facts)
    return {
        "records": [record.model_dump_json() for record in records],
        "locations": [record.exclusion.location for record in records],
        "fingerprint": catalog.fingerprint,
    }


def _lower_with_warnings(caplog, facts: ConstraintFacts, mode: str, roots: list[Path]):
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        records = _lower(facts, mode, roots)
    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.levelno == logging.WARNING and record.name == LOWERING_LOGGER
    ]
    return records, warnings


def test_live_snapshot_and_relocated_trees_are_byte_identical(tmp_path: Path, caplog):
    root_a = tmp_path / "checkout-a"
    root_b = tmp_path / "checkout-b"
    root_a.mkdir()
    root_b.mkdir()
    facts_a = _facts_for(root_a)
    facts_b = _facts_for(root_b)
    original_a = json.dumps(facts_a, default=lambda value: value.__dict__, sort_keys=True)

    live_a, live_a_warnings = _lower_with_warnings(caplog, facts_a, "live", [root_a])
    repeated_a, repeated_a_warnings = _lower_with_warnings(caplog, facts_a, "live", [root_a])
    live_b, live_b_warnings = _lower_with_warnings(caplog, facts_b, "live", [root_b])
    snapshot_facts = _serialize_facts(facts_a, [root_a])
    replay, replay_warnings = _lower_with_warnings(caplog, snapshot_facts, "snapshot", [])

    expected_warnings = [
        "Constraint <anonymous> at root-0/model.sysml:10:2 is not numerical and will not "
        "execute: warn_non_numerical_equality: equality is a valid non-numerical statement and "
        "is not executed",
        "Constraint <anonymous> at root-0/model.sysml:20:2 is not numerical and will not "
        "execute: warn_non_numerical_equality: equality is a valid non-numerical statement and "
        "is not executed",
    ]

    assert _projection(live_a, facts_a) == _projection(repeated_a, facts_a)
    assert _projection(live_a, facts_a) == _projection(live_b, facts_b)
    assert _projection(live_a, facts_a) == _projection(replay, snapshot_facts)
    assert live_a_warnings == expected_warnings
    assert repeated_a_warnings == expected_warnings
    assert live_b_warnings == expected_warnings
    assert replay_warnings == expected_warnings
    assert json.dumps(facts_a, default=lambda value: value.__dict__, sort_keys=True) == original_a
    assert [usage.location.file for usage in snapshot_facts.usages] == [
        "root-0/model.sysml",
        "root-0/model.sysml",
    ]


def test_two_ordered_roots_keep_same_relative_file_distinct(tmp_path: Path):
    roots = [tmp_path / "library", tmp_path / "design"]
    for root in roots:
        root.mkdir()
        (root / "model.sysml").write_text("")
    facts = ConstraintFacts(
        definitions=[],
        usages=[
            _anonymous_non_numerical(roots[0] / "model.sysml", 10),
            _anonymous_non_numerical(roots[1] / "model.sysml", 10),
        ],
        contexts=[],
        diagnostics=[],
    )
    records = _lower(facts, "live", roots)
    assert len({record.constraint_id for record in records}) == 2
    assert {record.exclusion.location for record in records} == {
        "root-0/model.sysml:10:2",
        "root-1/model.sysml:10:2",
    }


def test_capture_canonicalizes_only_anonymous_excluded_copy(tmp_path: Path):
    facts = _facts_for(tmp_path)
    named = _anonymous_non_numerical(tmp_path / "model.sysml", 30)
    named.identity.name = "named"
    named.identity.qualified_name = "Pkg__named"
    facts.usages.append(named)
    raw_named = named.location.file

    snapshot_facts = _serialize_facts(facts, [tmp_path])

    assert facts.usages[0].location.file == str(tmp_path / "model.sysml")
    assert snapshot_facts.usages[0].location.file == "root-0/model.sysml"
    assert snapshot_facts.usages[2].location.file == raw_named
