"""The reason mapping and the finding renderer agree with agentic-mbse's records (Item 2a § A).

Pure: reads the packaged rule records through agentic-mbse's public API, and, for the
witness test, the stored answers of every conformance case.
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
from tests.helpers.subset_profile import cases

SHAPES = [(rule.rule_id, shape) for rule in PACKAGED_RULES.rules for shape in rule.shapes]


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


def test_every_shape_with_a_refusal_code_is_refused_somewhere():
    """So the mapping's codes are observed refusals, never a code read from the generator."""
    undecided = [
        (rule_id, shape.shape_id)
        for rule_id, shape in SHAPES
        if shape.expected_code is not None and not shape.contexts_with(Outcome.REFUSED)
    ]
    assert undecided == []


REASON_OF = {(rule_id, shape.shape_id): shape.reason for rule_id, shape in SHAPES}
MAPPED_PAIRS = sorted(
    (reason, code)
    for reason, mapping in REASON_MAPPING.items()
    if isinstance(mapping, ReasonMapping)
    for code in mapping.codes()
)


@pytest.mark.parametrize("pair", MAPPED_PAIRS, ids="/".join)
def test_every_mapping_pair_has_a_witnessing_case(pair):
    """Some case refuses with the code where its screen answer refuses with the reason (O19)."""
    reason, code = pair
    witnesses = [
        answer.case_id
        for answer in cases.all_answers()
        if code in answer.generator.run.codes
        and any(
            f.outcome is Outcome.REFUSED and REASON_OF[(f.rule, f.shape)] == reason
            for f in cases.screen_of(answer).findings
        )
    ]
    assert witnesses, f"no case shows {reason} refused with {code}"


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


def _runtime_adapter_imports(tree: ast.Module) -> list[str]:
    """The enclosing function of each run-time import of the adapter (``<module>`` at top level).

    An import under ``if TYPE_CHECKING:`` is a type-checking import and is not counted.
    """
    found: list[str] = []

    def visit(node: ast.AST, function: str) -> None:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name):
            if node.test.id == "TYPE_CHECKING":
                for child in node.orelse:
                    visit(child, function)
                return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function = node.name
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            wrapper = ast.Module(body=[node], type_ignores=[])
            if "sysml_codegen.subset_profile_adapter" in _imported_modules(wrapper):
                found.append(function)
        for child in ast.iter_child_nodes(node):
            visit(child, function)

    visit(tree, "<module>")
    return found


def test_only_the_screen_imports_the_adapter_and_only_after_the_version_check():
    """Item 2b design D10: ``subset_screen._screen`` is the one run-time importer.

    ``_screen`` compares the installed ``SUBSET_PROFILE_VERSION`` with the pin before its
    import, and ``assess_screen`` calls it under its catch-all, so a skewed or failing
    import is reported as "not assessed", never raised.
    """
    importers = {
        str(path.relative_to(REPO_ROOT)): functions
        for path in sorted((REPO_ROOT / "src" / "sysml_codegen").rglob("*.py"))
        if (functions := _runtime_adapter_imports(ast.parse(path.read_text(encoding="utf-8"))))
    }
    assert importers == {"src/sysml_codegen/subset_screen.py": ["_screen"]}
    source = (REPO_ROOT / "src/sysml_codegen/subset_screen.py").read_text(encoding="utf-8")
    body = source[source.index("def _screen(") :]
    assert body.index("installed != SUBSET_PROFILE_VERSION") < body.index(
        "from sysml_codegen.subset_profile_adapter import"
    )
