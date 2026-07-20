"""Association and preparation: the Item 1 lifecycle boundary.

License-free. Facts are hand-built and the profile result is injected at the
production profile-evaluation boundary (``constraint_lowering.evaluate_profile``),
never through a test-only production parameter.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.executable_profile import ProfileResult, evaluate_profile
from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

import sysml_codegen.analysis.constraint_lowering as constraint_lowering
from sysml_codegen.analysis.constraint_lowering import (
    associate_usage_decisions,
    lower_constraints,
    prepare_constraint_usages,
)
from sysml_codegen.analysis.part_instance_index import (
    FrozenOccurrenceIndexCorruptionError,
    InstanceOccurrence,
    PathStep,
    RecursiveContainmentError,
)
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.supplied_values import enrich_graph_design_attributes

LOWERING_LOGGER = "sysml_codegen.analysis.constraint_lowering"


# --------------------------------------------------------------------------
# Fact builders
# --------------------------------------------------------------------------


def _real(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _admitted_predicate() -> OperatorNode:
    return OperatorNode(operator="<=", operands=[_real(1.0), _real(2.0)], operand_type=None)


def _non_numerical_predicate() -> OperatorNode:
    boolean = LiteralNode(
        literal=LiteralFact(kind="LiteralBoolean", value=True, result_type="boolean"),
        operand_type=OperandTypeFact(category="boolean", enumeration=None, unit=None),
    )
    return OperatorNode(operator="==", operands=[boolean, boolean], operand_type=None)


def _usage(
    *,
    owner_kind: str,
    owner_qn: str,
    location: LocationFact | None,
    predicate: OperatorNode | None,
    name: str | None = None,
    qualified_name: str | None = None,
    source_form: str = "inline",
) -> ConstraintUsageFact:
    identity = IdentityFact(
        kind="AssertConstraintUsage", name=name, qualified_name=qualified_name
    )
    return ConstraintUsageFact(
        identity=identity,
        location=location,
        source=ConstraintSource(
            form=source_form,
            effective_predicate_source=identity if source_form == "inline" else None,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=identity,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind=owner_kind, qualified_name=owner_qn),
        ),
        scope=IdentityFact(kind="AssertConstraintUsage", name=None, qualified_name=None),
        membership_kind=None,
        is_negated=False if predicate is not None else None,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts(usages: list[ConstraintUsageFact]) -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=list(usages), contexts=[], diagnostics=[])


def anonymous_sibling_batch() -> ConstraintFacts:
    """Two anonymous package asserts distinguishable only by location."""
    return _facts(
        [
            _usage(
                owner_kind="package",
                owner_qn="Design",
                location=LocationFact(file="root-0/design.sysml", line=10, column=2),
                predicate=_admitted_predicate(),
            ),
            _usage(
                owner_kind="package",
                owner_qn="Design",
                location=LocationFact(file="root-0/design.sysml", line=20, column=2),
                predicate=_admitted_predicate(),
            ),
        ]
    )


# --------------------------------------------------------------------------
# Spies
# --------------------------------------------------------------------------


class _SpyIndex:
    """Records every owner query. Answers one occurrence per requested owner."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]:
        self.calls.append(part_def_qn)
        return [InstanceOccurrence(part_def_qn, (PathStep(part_def_qn, "member", None),))]


class _RaisingIndex:
    """Answers the first owner and fails for every later one."""

    def __init__(self, *, ok_owner: str, error: Exception) -> None:
        self.calls: list[str] = []
        self._ok_owner = ok_owner
        self._error = error

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]:
        self.calls.append(part_def_qn)
        if part_def_qn == self._ok_owner:
            return [InstanceOccurrence(part_def_qn, (PathStep(part_def_qn, "member", None),))]
        raise self._error


@pytest.fixture
def spy_index() -> _SpyIndex:
    return _SpyIndex()


def _inject_decisions(monkeypatch: pytest.MonkeyPatch, decisions: list) -> None:
    """Replace the production profile evaluation with a fixed decision list."""
    monkeypatch.setattr(
        constraint_lowering, "evaluate_profile", lambda _facts: ProfileResult(decisions=decisions)
    )


# --------------------------------------------------------------------------
# Association
# --------------------------------------------------------------------------


def _independent_mutations(decisions: list) -> list[tuple[str, list]]:
    """Deletion, duplication, reorder, identity edit, and location edit clones."""
    base = deepcopy(decisions)
    identity_edit = deepcopy(decisions)
    identity_edit[1] = replace(
        identity_edit[1], identity=replace(identity_edit[1].identity, name="renamed")
    )
    location_edit = deepcopy(decisions)
    location_edit[1] = replace(
        location_edit[1], location=replace(location_edit[1].location, line=999)
    )
    return [
        ("deletion", base[:1]),
        ("duplication", [deepcopy(base[0]), deepcopy(base[0])]),
        ("reorder", [base[1], base[0]]),
        ("identity", identity_edit),
        ("location", location_edit),
    ]


def test_association_rejects_independent_decision_mutations_before_preflight(
    monkeypatch: pytest.MonkeyPatch, spy_index: _SpyIndex, caplog: pytest.LogCaptureFixture
) -> None:
    facts = anonymous_sibling_batch()
    truth = evaluate_profile(facts).decisions
    assert [decision.identity.qualified_name for decision in truth] == [None, None]

    for label, mutated in _independent_mutations(truth):
        _inject_decisions(monkeypatch, mutated)
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
            with pytest.raises(CodeGenerationError, match="association mismatch"):
                prepare_constraint_usages(facts, occ_index=spy_index, calc_usages=[])
        assert spy_index.calls == [], label
        assert caplog.records == [], label


def test_profile_version_guard_precedes_association_and_queries(
    monkeypatch: pytest.MonkeyPatch, spy_index: _SpyIndex
) -> None:
    facts = anonymous_sibling_batch()
    monkeypatch.setattr(constraint_lowering, "PROFILE_SEMANTIC_VERSION", "executable-profile/v5")

    def _must_not_run(_facts):  # pragma: no cover - the guard must fire first
        raise AssertionError("profile evaluated after a semantic-version skew")

    monkeypatch.setattr(constraint_lowering, "evaluate_profile", _must_not_run)
    with pytest.raises(RuntimeError, match="executable-profile semantics changed"):
        prepare_constraint_usages(facts, occ_index=spy_index, calc_usages=[])
    assert spy_index.calls == []


def test_associate_returns_verified_pairs_in_source_order() -> None:
    facts = anonymous_sibling_batch()
    pairs = associate_usage_decisions(facts)
    assert [usage for usage, _decision in pairs] == facts.usages
    assert [decision.location.line for _usage, decision in pairs] == [10, 20]


# --------------------------------------------------------------------------
# Owner filtering and expansion
# --------------------------------------------------------------------------


def test_excluded_unsupported_zero_query_and_package_branch(spy_index: _SpyIndex) -> None:
    facts = _facts(
        [
            _usage(
                owner_kind="requirement_def",
                owner_qn="Design::ReqDef",
                location=LocationFact(file="root-0/design.sysml", line=5, column=2),
                predicate=_admitted_predicate(),
                name="unsupported",
                qualified_name="Design__unsupported",
            ),
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Excluded",
                location=LocationFact(file="root-0/design.sysml", line=15, column=2),
                predicate=_non_numerical_predicate(),
                name="excluded",
                qualified_name="Design__excluded",
            ),
            _usage(
                owner_kind="package",
                owner_qn="Design",
                location=LocationFact(file="root-0/design.sysml", line=25, column=2),
                predicate=_admitted_predicate(),
                name="admitted",
                qualified_name="Design__admitted",
            ),
        ]
    )
    batch = prepare_constraint_usages(
        facts,
        occ_index=spy_index,
        calc_usages=[],
        source_location_mode="snapshot",
    )

    unsupported, excluded, admitted = batch.items
    assert (unsupported.owner_kind, unsupported.owner_instances) == ("requirement_def", ())
    assert unsupported.projected_exclusion is not None
    assert (excluded.owner_kind, excluded.owner_instances) == ("part_def", ())
    assert excluded.projected_exclusion is not None
    assert admitted.owner_kind == "package"
    assert admitted.owner_instances == (("Design_admitted", ""),)
    assert admitted.projected_exclusion is None

    # A part_def owner that is excluded is never expanded, so nothing queries it.
    assert spy_index.calls == []
    assert batch.occurrence_transcript == ()


def test_admitted_part_owner_query_is_staged_once_per_owner(spy_index: _SpyIndex) -> None:
    facts = _facts(
        [
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Admitted",
                location=None,
                predicate=_admitted_predicate(),
                name=f"check_{index}",
                qualified_name=f"Design__check_{index}",
            )
            for index in range(2)
        ]
    )
    batch = prepare_constraint_usages(facts, occ_index=spy_index, calc_usages=[])
    assert spy_index.calls == ["Design__Admitted"]
    assert [owner for owner, _occ in batch.occurrence_transcript] == ["Design__Admitted"]
    assert all(item.owner_instances for item in batch.items)


def test_missing_required_frozen_owner_wraps_corruption_with_recapture_guidance(
    spy_index: _SpyIndex,
) -> None:
    facts = _facts(
        [
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Missing",
                location=None,
                predicate=_admitted_predicate(),
                name="check",
                qualified_name="Design__check",
            )
        ]
    )
    index = _RaisingIndex(
        ok_owner="<none>",
        error=FrozenOccurrenceIndexCorruptionError("owner 'Design__Missing' was queried"),
    )
    with pytest.raises(CodeGenerationError, match="Recapture|recapture") as caught:
        prepare_constraint_usages(facts, occ_index=index, calc_usages=[])
    assert isinstance(caught.value.__cause__, FrozenOccurrenceIndexCorruptionError)
    assert "Design__Missing" in str(caught.value)


def test_later_owner_failure_discards_staged_transcript() -> None:
    facts = _facts(
        [
            _usage(
                owner_kind="part_def",
                owner_qn="Design::First",
                location=None,
                predicate=_admitted_predicate(),
                name="first",
                qualified_name="Design__first",
            ),
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Second",
                location=None,
                predicate=_admitted_predicate(),
                name="second",
                qualified_name="Design__second",
            ),
        ]
    )
    index = _RaisingIndex(
        ok_owner="Design__First",
        error=FrozenOccurrenceIndexCorruptionError("absent"),
    )
    with pytest.raises(CodeGenerationError):
        prepare_constraint_usages(facts, occ_index=index, calc_usages=[])
    # The first owner was answered, but no batch — and so no transcript — was returned.
    assert index.calls == ["Design__First", "Design__Second"]


# --------------------------------------------------------------------------
# Lowering ownership
# --------------------------------------------------------------------------


def test_lowering_accepts_only_prepared_disposition_and_instances() -> None:
    import inspect

    parameters = inspect.signature(lower_constraints).parameters
    assert list(parameters) == ["facts", "prepared", "registry", "design_attrs"]

    source = inspect.getsource(lower_constraints)
    for forbidden in ("evaluate_profile", "occurrences_of", "map_live_source_referent"):
        assert forbidden not in source


def test_lowering_uses_the_batch_owner_instances_not_the_index(spy_index: _SpyIndex) -> None:
    facts = _facts(
        [
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Admitted",
                location=None,
                predicate=_admitted_predicate(),
                name="check",
                qualified_name="Design__check",
            )
        ]
    )
    batch = prepare_constraint_usages(facts, occ_index=spy_index, calc_usages=[])
    spy_index.calls.clear()
    [record] = lower_constraints(
        facts, prepared=batch, registry=None, design_attrs={}
    )
    assert record.eligible is True
    assert record.owner_instance_path == "Design__Admitted__member"
    assert spy_index.calls == []


def test_warning_then_block_preflight_completes_before_any_owner_query(
    spy_index: _SpyIndex, caplog: pytest.LogCaptureFixture
) -> None:
    """R-8 preservation control: the warning/BLOCK order and bytes are unchanged,
    and neither step reaches an owner query."""
    warned = _usage(
        owner_kind="part_def",
        owner_qn="Design::Admitted",
        location=LocationFact(file="root-0/design.sysml", line=10, column=2),
        predicate=_non_numerical_predicate(),
        name="warned",
        qualified_name="Design__warned",
    )
    blocked = _usage(
        owner_kind="package",
        owner_qn="Design",
        location=LocationFact(file="root-0/design.sysml", line=20, column=2),
        predicate=OperatorNode(
            operator="==", operands=[_real(1.0), _real(2.0)], operand_type=None
        ),
        name="blocked",
        qualified_name="Design__blocked",
    )
    with caplog.at_level(logging.WARNING, logger=LOWERING_LOGGER):
        with pytest.raises(CodeGenerationError, match="not executable"):
            prepare_constraint_usages(
                _facts([warned, blocked]),
                occ_index=spy_index,
                calc_usages=[],
                source_location_mode="snapshot",
            )
    messages = [record.getMessage() for record in caplog.records if record.name == LOWERING_LOGGER]
    assert len(messages) == 1
    assert "Design__warned" in messages[0]
    assert spy_index.calls == []


def test_prepared_predicate_source_key_carries_the_route_referent(tmp_path: Path) -> None:
    """Lowering never re-derives a referent: the key is decided during preparation."""
    model = tmp_path / "root-0" / "design.sysml"
    model.parent.mkdir()
    model.write_text("")
    facts = _facts(
        [
            _usage(
                owner_kind="package",
                owner_qn="Design",
                location=LocationFact(file=str(model), line=10, column=2),
                predicate=_admitted_predicate(),
            )
        ]
    )
    batch = prepare_constraint_usages(
        facts,
        occ_index=None,
        calc_usages=[],
        source_location_mode="live",
        source_roots=[tmp_path],
    )
    [item] = batch.items
    assert item.predicate_source_key == "inline:AssertConstraintUsage:design.sysml:10:2"


# --------------------------------------------------------------------------
# Cycle atomicity at the preparation boundary
# --------------------------------------------------------------------------


def test_later_owner_cycle_discards_staged_transcript() -> None:
    """A finite first owner followed by a recursive second owner publishes nothing:
    the public failure is a contextual CodeGenerationError over the structured cause."""
    facts = _facts(
        [
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Finite",
                location=None,
                predicate=_admitted_predicate(),
                name="first",
                qualified_name="Design__first",
            ),
            _usage(
                owner_kind="part_def",
                owner_qn="Design::Cyclic",
                location=None,
                predicate=_admitted_predicate(),
                name="second",
                qualified_name="Design__second",
            ),
        ]
    )
    cycle = RecursiveContainmentError(
        requested_owner_qn="Design__Cyclic",
        edge_owner_qn="Design__Cyclic",
        edge_feature_name="recursive",
        edge_type_qn="Design__Cyclic",
        cycle_path=("Design__Cyclic", "Design__Cyclic"),
    )
    index = _RaisingIndex(ok_owner="Design__Finite", error=cycle)

    lowered: list[object] = []
    enriched: list[object] = []
    with pytest.raises(CodeGenerationError, match="recursively contained") as caught:
        batch = prepare_constraint_usages(facts, occ_index=index, calc_usages=[])
        lowered.append(lower_constraints(facts, prepared=batch, registry=None, design_attrs={}))
        enriched.append(
            enrich_graph_design_attributes(
                {},
                calc_usages=[],
                prepared=batch,
                redefinitions=[],
                design_overrides=[],
                usage_type_map={},
            )
        )

    cause = caught.value.__cause__
    assert isinstance(cause, RecursiveContainmentError)
    assert cause.requested_owner_qn == "Design__Cyclic"
    assert cause.edge_owner_qn == "Design__Cyclic"
    assert cause.edge_feature_name == "recursive"
    assert cause.edge_type_qn == "Design__Cyclic"
    assert cause.cycle_path == ("Design__Cyclic", "Design__Cyclic")
    # The first owner was answered, but no batch escaped, so nothing downstream ran.
    assert index.calls == ["Design__Finite", "Design__Cyclic"]
    assert lowered == []
    assert enriched == []
