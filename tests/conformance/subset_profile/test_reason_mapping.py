"""The reason mapping and the finding renderer agree with agentic-mbse's records (Item 2a § A).

Pure: reads the packaged rule records through agentic-mbse's public API. That every
(reason, code) pair has a case where the generator emitted the code needs P2's cases, so it
lands there.
"""

from __future__ import annotations

import ast
from uuid import NAMESPACE_URL, uuid5

import pytest
from agentic_mbse.sysml.fact_refs import ElementRef, SafeLocation
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    SUBSET_REASON_CODES,
    Outcome,
    Qualification,
    ShapeRecord,
    SubsetFinding,
    rule_contexts,
)

from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.extraction.source_evidence import ReadinessCode
from sysml_codegen.subset_profile_adapter import (
    NO_REFUSAL,
    REASON_MAPPING,
    ReasonMapping,
    render_finding,
)
from tests.conftest import REPO_ROOT

SHAPES = [(rule.rule_id, shape) for rule in PACKAGED_RULES.rules for shape in rule.shapes]
#: Shapes whose records carry an `expected_code` but decide no context yet. Their mapping is
#: the expected code; when a case decides them, this set shrinks.
UNDECIDED_REFUSING_SHAPES = {
    ("part-multiplicity", "negative_bound"),
    ("part-multiplicity", "nonunique"),
}


def _id(item: tuple[str, ShapeRecord]) -> str:
    return f"{item[0]}/{item[1].shape_id}"


def test_mapping_keys_equal_subset_reason_codes():
    assert set(REASON_MAPPING) == set(SUBSET_REASON_CODES)


def test_each_reason_names_one_shape():
    reasons = [shape.reason for _, shape in SHAPES]
    assert sorted(reasons) == sorted(SUBSET_REASON_CODES)


def test_mapped_codes_are_generator_codes():
    generator_codes = {c.value for c in ElaborationCode} | {c.value for c in ReadinessCode}
    for reason, mapping in REASON_MAPPING.items():
        assert mapping.codes() <= generator_codes, reason


@pytest.mark.parametrize("item", SHAPES, ids=_id)
def test_no_refusal_exactly_when_the_record_names_no_refusal_code(item):
    rule_id, shape = item
    if shape.contexts_with(Outcome.REFUSED):
        assert shape.expected_code is not None
    assert (REASON_MAPPING[shape.reason] is NO_REFUSAL) == (shape.expected_code is None)


def test_the_undecided_refusing_shapes_are_the_named_two():
    undecided = {
        (rule_id, shape.shape_id)
        for rule_id, shape in SHAPES
        if shape.expected_code is not None and not shape.contexts_with(Outcome.REFUSED)
    }
    assert undecided == UNDECIDED_REFUSING_SHAPES


@pytest.mark.parametrize("item", [i for i in SHAPES if i[1].expected_code], ids=_id)
def test_record_expected_code_is_among_its_reason_codes(item):
    _, shape = item
    assert shape.expected_code in REASON_MAPPING[shape.reason].codes()


def _finding(rule_id: str, shape: ShapeRecord, context, outcome: Outcome) -> SubsetFinding:
    admission = shape.admissions.get(context)
    return SubsetFinding(
        rule_id=rule_id,
        shape_id=shape.shape_id,
        context_id=context,
        outcome=outcome,
        reason=shape.reason,
        detail_reasons=(),
        subject=ElementRef(uuid5(NAMESPACE_URL, "subset/subject"), "fx::Site::x", "AttributeUsage"),
        location=SafeLocation("root-0/model.sysml", 7, "fx::Site::x"),
        occurrence_count=None,
        via_roots=(),
        evidence=() if admission is None else admission.evidence,
        qualification=Qualification.NONE if admission is None else admission.qualification,
    )


def _decided_or_unconfirmed(rule_id: str, shape: ShapeRecord):
    """The shape's first refused context, else its first decided one, else an unconfirmed one."""
    refused = shape.contexts_with(Outcome.REFUSED)
    if refused:
        return refused[0], Outcome.REFUSED
    if shape.admissions:
        context, admission = next(iter(shape.admissions.items()))
        return context, admission.outcome
    return sorted(rule_contexts(rule_id))[0], Outcome.UNCONFIRMED


@pytest.mark.parametrize("item", SHAPES, ids=_id)
def test_render_finding_for_every_reason(item):
    rule_id, shape = item
    context, outcome = _decided_or_unconfirmed(rule_id, shape)
    rendered = render_finding(_finding(rule_id, shape, context, outcome), PACKAGED_RULES)
    assert rendered.subset_reason == shape.reason
    assert rendered.remedy == PACKAGED_RULES.rule(rule_id).remedy
    assert (rendered.subject, rendered.source_file, rendered.source_line) == (
        "fx::Site::x",
        "root-0/model.sysml",
        7,
    )
    if outcome is Outcome.REFUSED:
        mapping = REASON_MAPPING[shape.reason]
        assert isinstance(mapping, ReasonMapping)
        assert rendered.code == mapping.code_for(context)
        assert rendered.code == shape.expected_code
    else:
        assert rendered.code is None


def test_an_admitted_finding_of_a_refusing_reason_carries_no_code():
    rule = PACKAGED_RULES.rule("binding-source")
    shape = next(s for s in rule.shapes if s.shape_id == "expression_source")
    context = shape.contexts_with(Outcome.ADMITTED)[0]
    rendered = render_finding(
        _finding(rule.rule_id, shape, context, Outcome.ADMITTED), PACKAGED_RULES
    )
    assert rendered.code is None


def test_a_refused_finding_of_a_no_refusal_reason_is_refused_by_the_renderer():
    rule = PACKAGED_RULES.rule("string-value-omission")
    [shape] = rule.shapes
    [context] = list(shape.admissions)
    finding = _finding(rule.rule_id, shape, context, Outcome.REFUSED)
    with pytest.raises(ValueError, match="maps to NO_REFUSAL"):
        render_finding(finding, PACKAGED_RULES)


def _imported_modules(tree: ast.Module) -> set[str]:
    """Every module an import statement names, ``from a import b`` counting as ``a`` and ``a.b``."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules |= {node.module} | {f"{node.module}.{alias.name}" for alias in node.names}
    return modules


def test_nothing_in_src_imports_the_adapter():
    """The adapter is off the generate route in 2a: no module under src/ imports it."""
    importers = [
        str(path.relative_to(REPO_ROOT))
        for path in sorted((REPO_ROOT / "src" / "sysml_codegen").rglob("*.py"))
        if "sysml_codegen.subset_profile_adapter"
        in _imported_modules(ast.parse(path.read_text(encoding="utf-8")))
    ]
    assert importers == []
