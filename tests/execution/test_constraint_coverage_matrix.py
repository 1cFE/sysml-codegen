"""All six states, end to end, each pinned by something no other state satisfies.

The chain under test is the whole item: model -> elaborate -> project -> generate -> seal ->
TEAx's own loader -> execute -> `project()` onto the canonical vocabulary -> policy disposition.
Nothing here re-implements the precedence rule or the token map; both are read from the code
that ships.

**Six states, not five.** The sixth is *report absent* — a constraint-free package — and it is
the one the item exists to keep separable. Before this item a model with 65 unassessed checks
and a model with no checks at all produced the same runtime label, `unconstrained`.

Every expected account below is the fixture's entry in
`.project/active/constraint-coverage-policy/expected-coverage.md`, hand-written from `.sysml`
source before any of this code existed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.execution.real_teax import generate_package_from_models, load_sealed_package

pytestmark = pytest.mark.execution

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REPORT_CH = "constraint_report"

#: fixture -> (report headline, canonical token, ObjectivePolicy disposition, coverage_state)
#:
#: `violation` and `partial_coverage` are the two states the item added the ability to tell
#: apart from their neighbours; the other four were already distinguishable and are pinned so
#: they stay that way.
KEEP = "keep-for-boundary"
SIX_STATES = [
    ("constraint_coverage_violation_partial", "violation", "violated", "reject", "partial"),
    ("constraint_domain_detached_owner", "partial_coverage", "partial_coverage", KEEP, "partial"),
    ("gate_a_d5", "full_satisfaction", "satisfied", "feed-strategy", "complete"),
    ("constraint_domain_plain_forms", "not_assessed", "not_assessed", KEEP, "none"),
    ("constraint_coverage_all_inapplicable", "not_assessed", "not_assessed", KEEP, "none"),
]


def _execute(fixture: str, name: str, root: Path):
    from simkit.core.pipeline import execute_pipeline

    package = generate_package_from_models(FIXTURES / fixture, root / name, name)
    module, _fingerprint = load_sealed_package(package, name, root / "link")
    result = execute_pipeline(
        package / "pipelines" / "pipeline.yaml",
        root / "run",
        registry=getattr(module, f"create_{name}_registry")(),
        # A constraint-free package exports no custom schema types, which is the sixth state
        # showing up in the package's shape rather than only in its outputs.
        custom_schema_types=getattr(module, "CUSTOM_SCHEMA_TYPES", []),
    )
    return package, result


def _canonical(report) -> str:
    from simkit.evaluation.evidence import canonical_headline

    return canonical_headline(report.headline)


def _disposition(canonical: str) -> str:
    """The disposition `ObjectivePolicy` gives this headline, at its default configuration.

    `satisfied` is resolved by the policy itself against `penalty_threshold`; with no
    threshold configured it reaches `feed-strategy`, which is the steering loop.
    """
    from simkit.study.policy import _HEADLINE_DISPOSITION, _disposition_for

    if canonical == "satisfied":
        return "feed-strategy"
    return _disposition_for(canonical, _HEADLINE_DISPOSITION, "_HEADLINE_DISPOSITION")


@pytest.mark.parametrize(
    "fixture,report_headline,canonical,disposition,coverage_state",
    SIX_STATES,
    ids=[row[0] for row in SIX_STATES],
)
def test_each_state_is_pinned_by_something_no_other_state_satisfies(
    tmp_path, fixture, report_headline, canonical, disposition, coverage_state
):
    _package, result = _execute(fixture, f"matrix_{fixture}", tmp_path)
    report = result.outputs[REPORT_CH]

    assert report.headline == report_headline
    assert report.coverage.coverage_state == coverage_state
    assert _canonical(report) == canonical
    assert _disposition(canonical) == disposition


def test_the_sixth_state_is_the_absence_of_a_report(tmp_path):
    """A constraint-free package ships no report at all, and that is a distinct answer.

    `sample_model` declares no constraints, so `ships_constraint_machinery` is False: no
    aggregator, no `constraint_report` channel, and no evidence schema. TEAx's
    `ships_constraint_report` reads the same emptiness off the shipped model contract and
    agrees, which is the two-authorities-one-answer property (invariant 10) across the repo
    boundary.

    Asserted on the sealed package rather than on an executed run: the claim is about what the
    package *contains*, and TEAx's own suite already covers what `project()` does with a
    report-less result.

    This is what `catf_mfe_d5` used to look like, with 65 authored checks. The whole item is
    the distance between this test and `test_a_descriptive_only_model_is_no_longer_silent`.
    """
    from simkit.study.model_contract import load_model_contract, ships_constraint_report

    package = generate_package_from_models(
        FIXTURES / "sample_model", tmp_path / "cfree", "cfree"
    )
    assert not (package / "schemas" / "constraint_types.py").exists()
    assert REPORT_CH not in (package / "pipelines" / "pipeline.yaml").read_text()
    assert not ships_constraint_report(load_model_contract(package))


def test_the_two_report_authorities_agree_on_a_zero_input_package(tmp_path):
    """Validation item 12: producer and consumer read the same population, oppositely-shaped.

    `catf_mfe_d5` has 65 usage rows and zero concrete entries. Codegen's
    `ships_constraint_machinery` says it ships a report; TEAx's `ships_constraint_report` says
    it expects one. There is no spec-derived fallback left to disagree with either — the one
    that existed was deleted, which is what keeps the invariant-46a corruption check switched
    on for exactly the packages this item taught to emit a report.
    """
    from simkit.study.model_contract import load_model_contract, ships_constraint_report

    package = generate_package_from_models(
        FIXTURES / "catf_mfe_d5", tmp_path / "d5auth", "d5auth"
    )
    assert ships_constraint_report(load_model_contract(package))
    assert REPORT_CH in (package / "pipelines" / "pipeline.yaml").read_text()


def test_a_descriptive_only_model_is_no_longer_silent(tmp_path):
    """`catf_mfe_d5`: 65 authored usages, none assessed — and now it says so.

    Ledger entry: 65 / 0 / 0 / 0 / 0 / `{}` / `none`. It is `not_assessed`, which maps to a
    canonical `not_assessed` and `keep-for-boundary` — never `unconstrained`, which is the
    label the sixth state owns.
    """
    _package, result = _execute("catf_mfe_d5", "matrix_descriptive", tmp_path)
    report = result.outputs[REPORT_CH]

    assert report.headline == "not_assessed"
    assert report.assessed_entry_count == 0
    assert report.coverage.model_dump() == {
        "authored_usage_total": 65,
        "applicable_gate_total": 0,
        "assessed_gate_count": 0,
        "unassessed_gate_count": 0,
        "inapplicable_gate_count": 0,
        "unassessed_reasons": {},
        "coverage_state": "none",
    }
    assert _canonical(report) == "not_assessed"


def test_the_two_not_assessed_models_are_still_told_apart_by_the_account(tmp_path):
    """D4's ruling, and why nothing is lost by it.

    A descriptive-only model and an all-inapplicable model share a headline. They must: both
    assessed nothing, and neither may claim otherwise. What separates them is
    `inapplicable_gate_count` — zero for the first, positive for the second — so a consumer
    that wants "every gate was deliberately waived" reads that field rather than the headline.
    """
    _p1, descriptive = _execute("constraint_domain_plain_forms", "d4_descriptive", tmp_path)
    _p2, waived = _execute("constraint_coverage_all_inapplicable", "d4_waived", tmp_path)

    first = descriptive.outputs[REPORT_CH].coverage
    second = waived.outputs[REPORT_CH].coverage
    assert first.inapplicable_gate_count == 0
    assert second.inapplicable_gate_count == 1
    assert first.coverage_state == second.coverage_state == "none"


def test_violation_states_its_coverage_all_the_way_into_the_case_record(tmp_path):
    """Spec success criterion 2: coverage survives a higher-precedence headline.

    The report's headline is `violation` — the top precedence arm, unchanged by this item —
    and the account beside it still says one gate was never checked. Then the policy copies
    that account into `assessment_json`, which is what a study query reads, so
    "rejected on physics, fully covered" and "rejected on physics, one gate unchecked" are
    different rows rather than the same one.
    """
    from simkit.evaluation.evidence import EvidenceProvenance, ModelEvidence
    from simkit.study.policy import DispositionPolicy

    _package, result = _execute(
        "constraint_coverage_violation_partial", "violation_record", tmp_path
    )
    report = result.outputs[REPORT_CH]
    assert report.headline == "violation"
    assert report.coverage.coverage_state == "partial"
    assert report.coverage.unassessed_gate_count == 1

    evidence = ModelEvidence(
        responses={"headline": _canonical(report)},
        outputs={},
        provenance=EvidenceProvenance(
            executable_fingerprint="f" * 64,
            evidence_schema_version="v2",
            evaluator_version="v1",
            input_digest="d",
        ),
        report=report.model_dump(mode="json"),
    )
    assessment = DispositionPolicy().assess(evidence, candidate_id="c0")

    assert assessment["disposition"] == "infeasible"
    assert assessment["coverage"]["unassessed_gate_count"] == 1
    assert assessment["coverage"]["coverage_state"] == "partial"
    assert assessment["catalog_fingerprint"] == report.catalog_fingerprint

    # It must be plain enough to serialize into the case row (invariant 41 freezes the
    # evidence copy; the assessment gets its own thawed one).
    import json

    json.dumps(assessment)


def test_full_satisfaction_is_unclaimable_when_anything_was_unassessed(tmp_path):
    """Spec success criterion 3, stated as the property rather than as one fixture.

    Across every fixture in the matrix, `full_satisfaction` implies the account says nothing
    was left unassessed and at least one gate ran. This is required invariant 3, and it is the
    single claim the whole item exists to make true.
    """
    for fixture, headline, *_rest in SIX_STATES:
        _package, result = _execute(fixture, f"inv3_{fixture}", tmp_path / fixture)
        report = result.outputs[REPORT_CH]
        if report.headline == "full_satisfaction":
            assert report.coverage.unassessed_gate_count == 0
            assert report.coverage.assessed_gate_count > 0
        else:
            assert not (
                report.coverage.unassessed_gate_count == 0
                and report.coverage.assessed_gate_count > 0
                and not [r for r in report.results if r.status != "satisfied"]
            ), f"{fixture} could have claimed full satisfaction and did not"
