"""One public bridge preserves agentic semantic-evidence failures."""

from __future__ import annotations

import ast
import importlib
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from agentic_mbse import SemanticEvidenceCode, SemanticEvidenceError

from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.orchestration import elaborated_pipeline
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

RAW_SOURCE = str(Path("/stage/model.sysml").resolve())
REFERENT = "root-0/model.sysml"


class _EvidenceFailingExtractor:
    def __init__(self, _model_paths: list[Path] | None = None) -> None:
        self.model = object()
        self.diagnostics = SimpleNamespace(validation=())

    def load_models(self) -> bool:
        return True

    def extract_calculation_definitions(self) -> list[Any]:
        parser_cause = RuntimeError("installed parser metatype failure")
        semantic_error = SemanticEvidenceError(
            SemanticEvidenceCode.METATYPE_CHECK_FAILED,
            "is_instance",
            "the installed parser rejected the metatype query",
            location=(RAW_SOURCE, 7),
            reference="plant::source",
            cause=parser_cause,
        )
        raise semantic_error from parser_cause


class _BoundaryExtractor:
    def __init__(self, _model_paths: list[Path] | None = None) -> None:
        self.model = object()
        self.diagnostics = SimpleNamespace(validation=())

    def load_models(self) -> bool:
        return True

    def extract_calculation_definitions(self) -> list[Any]:
        return []


class MockOperatorExpression:
    qualified_name = "Probe::broken_operands"
    document = SimpleNamespace(url=f"file:{RAW_SOURCE}")
    cst_node = SimpleNamespace(start_point=SimpleNamespace(line=10))

    @property
    def operands(self):
        raise RuntimeError("operand stream failed")


class MockFeatureReferenceExpression:
    qualified_name = "Probe::missing_reference"
    document = SimpleNamespace(url=f"file:{RAW_SOURCE}")
    cst_node = SimpleNamespace(start_point=SimpleNamespace(line=20))
    referent = None


def _force_exact_expression_failure(
    monkeypatch: pytest.MonkeyPatch,
    expression: object,
) -> None:
    exact = importlib.import_module("sysml_codegen.elaboration.elaborate")
    elaborator = object.__new__(exact._ExactElaborator)

    def fail_in_exact_route(*_args: object, **_kwargs: object) -> object:
        elaborator._expression_references(expression, plural=False)
        raise AssertionError("forced evidence failure returned a graph")

    monkeypatch.setattr(elaborated_pipeline, "_build_instance_graph", fail_in_exact_route)


def _assert_forced_expression_diagnostic(
    error: ElaborationDiagnosticError,
    *,
    code: SemanticEvidenceCode,
    reference: str,
    line: int,
) -> None:
    [diagnostic] = error.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == reference
    assert diagnostic.consumer_display == reference
    assert diagnostic.source_file == REFERENT
    assert diagnostic.source_line == line
    assert str(error).count("SI_EVIDENCE_INCOMPLETE") == 1
    semantic_error = error.__cause__
    assert isinstance(semantic_error, SemanticEvidenceError)
    assert semantic_error.code is code
    if code is SemanticEvidenceCode.OPERAND_ITERATION_FAILED:
        assert isinstance(semantic_error.cause, RuntimeError)
        assert semantic_error.__cause__ is semantic_error.cause
    else:
        assert semantic_error.cause is None
        assert semantic_error.__cause__ is None


@pytest.mark.parametrize("strict", [True, False])
def test_loaded_extractor_converts_semantic_evidence_once(strict: bool) -> None:
    extractor = _EvidenceFailingExtractor()

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_loaded_extractor(
            extractor,
            model_paths=(Path(RAW_SOURCE),),
            source_referents={RAW_SOURCE: REFERENT},
            strict=strict,
        )

    public_error = caught.value
    assert len(public_error.diagnostics) == 1
    diagnostic = public_error.diagnostics[0]
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.consumer_display == "plant::source"
    assert diagnostic.detail == (
        "is_instance: the installed parser rejected the metatype query"
    )
    assert diagnostic.reference == "plant::source"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 7
    assert "root-0/model.sysml:7" in str(public_error)
    assert str(public_error).count("SI_EVIDENCE_INCOMPLETE") == 1
    assert isinstance(public_error.__cause__, SemanticEvidenceError)
    semantic_error = public_error.__cause__
    assert semantic_error.cause is semantic_error.__cause__
    assert isinstance(semantic_error.cause, RuntimeError)


def test_live_and_admitted_routes_delegate_to_one_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[tuple[Path, ...], dict[str, str], bool]] = []
    marker = object()

    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _BoundaryExtractor)
    monkeypatch.setattr(
        elaborated_pipeline,
        "_live_source_referents",
        lambda _model, _paths: {RAW_SOURCE: REFERENT},
    )

    def fake_boundary(
        _extractor: object,
        *,
        model_paths: tuple[Path, ...],
        source_referents: dict[str, str],
        strict: bool,
    ) -> object:
        calls.append((model_paths, source_referents, strict))
        return marker

    monkeypatch.setattr(elaborated_pipeline, "elaborate_loaded_extractor", fake_boundary)

    assert elaborated_pipeline.elaborate_model_paths([Path(RAW_SOURCE)], strict=False) is marker

    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )
    assert elaborated_pipeline.elaborate_admitted_sources(admitted, strict=True) is marker
    assert calls == [
        ((Path(RAW_SOURCE),), {RAW_SOURCE: REFERENT}, False),
        ((Path(RAW_SOURCE),), {RAW_SOURCE: REFERENT}, True),
    ]


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("source_arm", ["live", "admitted"])
def test_public_source_arms_preserve_the_same_evidence_refusal(
    monkeypatch: pytest.MonkeyPatch,
    source_arm: str,
    strict: bool,
) -> None:
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _EvidenceFailingExtractor)
    monkeypatch.setattr(
        elaborated_pipeline,
        "_live_source_referents",
        lambda _model, _paths: {RAW_SOURCE: REFERENT},
    )
    verified: list[object] = []
    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=verified.append,
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        if source_arm == "live":
            elaborated_pipeline.elaborate_model_paths([Path(RAW_SOURCE)], strict=strict)
        else:
            elaborated_pipeline.elaborate_admitted_sources(admitted, strict=strict)

    assert [item.code for item in caught.value.diagnostics] == [
        ElaborationCode.SI_EVIDENCE_INCOMPLETE
    ]
    assert str(caught.value).count("SI_EVIDENCE_INCOMPLETE") == 1
    assert verified == []


def test_snapshot_evidence_refusal_preserves_existing_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from sysml_codegen.extraction import source_manifest

    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )

    @contextmanager
    def fake_admission(_model_paths: list[Path]):
        yield admitted

    monkeypatch.setattr(source_manifest, "admit_sources", fake_admission)
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _EvidenceFailingExtractor)
    output = tmp_path / "snapshot.json"
    output.write_bytes(b"existing snapshot")

    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([Path(RAW_SOURCE)], output)

    assert output.read_bytes() == b"existing snapshot"
    assert list(tmp_path.iterdir()) == [output]


def test_snapshot_capture_uses_the_admitted_route() -> None:
    capture_source = (
        Path(elaborated_pipeline.__file__).resolve().parents[1] / "snapshot" / "capture.py"
    ).read_text(encoding="utf-8")
    assert "elaborate_admitted_sources(admission)" in capture_source


@pytest.mark.parametrize(
    ("expression", "code", "reference", "line"),
    [
        (
            MockOperatorExpression(),
            SemanticEvidenceCode.OPERAND_ITERATION_FAILED,
            "Probe::broken_operands",
            11,
        ),
        (
            MockFeatureReferenceExpression(),
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            "Probe::missing_reference",
            21,
        ),
    ],
)
@pytest.mark.parametrize("source_arm", ["live", "admitted"])
def test_public_exact_expression_failures_return_no_graph(
    monkeypatch: pytest.MonkeyPatch,
    expression: object,
    code: SemanticEvidenceCode,
    reference: str,
    line: int,
    source_arm: str,
) -> None:
    _force_exact_expression_failure(monkeypatch, expression)
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _BoundaryExtractor)
    monkeypatch.setattr(
        elaborated_pipeline,
        "_live_source_referents",
        lambda _model, _paths: {RAW_SOURCE: REFERENT},
    )
    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        if source_arm == "live":
            elaborated_pipeline.elaborate_model_paths([Path(RAW_SOURCE)], strict=True)
        else:
            elaborated_pipeline.elaborate_admitted_sources(admitted, strict=True)

    _assert_forced_expression_diagnostic(
        caught.value,
        code=code,
        reference=reference,
        line=line,
    )


@pytest.mark.parametrize(
    "expression",
    [MockOperatorExpression(), MockFeatureReferenceExpression()],
)
def test_forced_expression_failure_preserves_existing_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    expression: object,
) -> None:
    from sysml_codegen.extraction import source_manifest

    _force_exact_expression_failure(monkeypatch, expression)
    admitted = SimpleNamespace(
        staged_files=(Path(RAW_SOURCE),),
        staged_to_referent={RAW_SOURCE: REFERENT},
        files=(SimpleNamespace(referent=REFERENT),),
        verify_after_parse=lambda _model: None,
    )

    @contextmanager
    def fake_admission(_model_paths: list[Path]):
        yield admitted

    monkeypatch.setattr(source_manifest, "admit_sources", fake_admission)
    monkeypatch.setattr(elaborated_pipeline, "SysMLDataExtractor", _BoundaryExtractor)
    output = tmp_path / "snapshot.json"
    output.write_bytes(b"existing snapshot")

    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([Path(RAW_SOURCE)], output)

    assert output.read_bytes() == b"existing snapshot"
    assert list(tmp_path.iterdir()) == [output]


def test_raw_builder_is_private_and_has_one_production_caller() -> None:
    import sysml_codegen.elaboration as elaboration

    assert "elaborate" not in elaboration.__all__
    package_root = Path(elaborated_pipeline.__file__).resolve().parents[1]
    callers = []
    for source_path in package_root.rglob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_build_instance_graph"
            for node in ast.walk(tree)
        ):
            callers.append(source_path.relative_to(package_root).as_posix())
    assert callers == ["orchestration/elaborated_pipeline.py"]


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic(
    strict: bool,
) -> None:
    fixture = FIXTURES_DIR / "indexed_expression_source"

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    assert diagnostic.consumer is None
    assert diagnostic.consumer_display == "<model>"
    assert diagnostic.param_name is None
    assert diagnostic.detail.endswith(
        "tests/fixtures/indexed_expression_source/model.sysml:17: "
        "indexed source '#(...)' is recognized but not implemented"
    )
    assert str(caught.value).count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1


# --- Indexed bare-chain red set (Phase 1) ------------------------------------
#
# Two kept tests, each red at C_base for its own stated reason.  See design.md's
# section "The indexed red set - both cases are required kept tests".
#
# Case 1 (`indexed_bare_chain_singular`, `cells : Cell[1]`, authored `cells#(2).mass`):
#   at C_base this produces a graph carrying ZERO diagnostics, in which the authored
#   index is silently rewritten to `cells[0].mass`.  That collapse is the escape.
# Case 2 (`indexed_bare_chain_plural`, `cells : Cell[3]`, same authored chain):
#   at C_base this refuses as SI_OCCURRENCE_AMBIGUOUS — a name about occurrence
#   selection raised for an index defect — followed by SI_OCCURRENCE_MISSING on the
#   typed alias.  The refusal must become SI_INDEXED_SOURCE_UNSUPPORTED, raised by the
#   inventory before any occurrence resolution runs.
#
# Operator-wrapped forms are NOT red-set members: they already refuse correctly and
# are kept below as positive regression coverage.

SINGULAR_SLOT_FIXTURE = "indexed_bare_chain_singular"
PLURAL_SLOT_FIXTURE = "indexed_bare_chain_plural"
OPERATOR_WRAPPED_FIXTURE = "indexed_bare_chain_operator"
AUTHORED_INDEXED_LINE = 15


class _CallSpy:
    """Record every call through one production seam without replacing its behavior."""

    def __init__(self) -> None:
        self.calls = 0

    @property
    def called(self) -> bool:
        return self.calls > 0


def _spy_on_expression_consumers(monkeypatch: pytest.MonkeyPatch) -> _CallSpy:
    """Spy the first downstream expression consumer after source admission."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    spy = _CallSpy()
    original = SysMLDataExtractor.extract_calculation_definitions

    def record(self: SysMLDataExtractor) -> Any:
        spy.calls += 1
        return original(self)

    monkeypatch.setattr(SysMLDataExtractor, "extract_calculation_definitions", record)
    return spy


def _spy_on_occurrence_resolution(monkeypatch: pytest.MonkeyPatch) -> _CallSpy:
    """Spy the occurrence-domain resolver that names SI_OCCURRENCE_* today."""
    from sysml_codegen.elaboration.occurrence import OccurrenceIndex

    spy = _CallSpy()
    original = OccurrenceIndex.resolve_address

    def record(self: OccurrenceIndex, *args: object, **kwargs: object) -> Any:
        spy.calls += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(OccurrenceIndex, "resolve_address", record)
    return spy


def _indexed_capability_detail(fixture_name: str) -> str:
    return (
        f"tests/fixtures/{fixture_name}/model.sysml:{AUTHORED_INDEXED_LINE}: "
        "indexed source '#(...)' is recognized but not implemented"
    )


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_indexed_bare_chain_singular_slot_refuses_before_consumers(
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case 1: an out-of-range index on a singular slot must refuse, not collapse.

    Recorded red at C_base: no exception is raised at all.  The route returns an
    InstanceGraph whose ``diagnostics`` is empty and whose attribute inventory holds
    ``IndexedBareChainSingular__array__cells[0]__mass`` — occurrence zero, minted for
    an authored ``#(2)`` that the model's ``Cell[1]`` slot cannot honor.
    """
    fixture = FIXTURES_DIR / SINGULAR_SLOT_FIXTURE
    consumers = _spy_on_expression_consumers(monkeypatch)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    assert [item.code for item in caught.value.diagnostics] == [
        ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    ]
    [diagnostic] = caught.value.diagnostics
    assert diagnostic.detail.endswith(_indexed_capability_detail(SINGULAR_SLOT_FIXTURE))
    assert str(caught.value).count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1
    assert not consumers.called


@requires_license
def test_indexed_bare_chain_singular_slot_writes_no_snapshot(tmp_path: Path) -> None:
    """Case 1, capture arm: the escape must not reach a sealed snapshot."""
    fixture = FIXTURES_DIR / SINGULAR_SLOT_FIXTURE
    output = tmp_path / "instance_graph_snapshot.json"

    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([fixture], output)

    assert not output.exists()


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution(
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case 2: the index defect must be named, and named before occurrence resolution.

    Recorded red at C_base: the route refuses with two diagnostics, the first
    ``SI_OCCURRENCE_AMBIGUOUS`` ("exact containment step ... has 3 concrete
    occurrences") and the second ``SI_OCCURRENCE_MISSING`` ("typed alias
    'IndexedBareChainPlural__array__picked' has no resolved target").  Both are
    occurrence-selection names raised for an unsupported authored index, and
    ``OccurrenceIndex.resolve_address`` has already run by the time either is built.
    """
    fixture = FIXTURES_DIR / PLURAL_SLOT_FIXTURE
    occurrence_resolution = _spy_on_occurrence_resolution(monkeypatch)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    assert [item.code for item in caught.value.diagnostics] == [
        ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    ]
    [diagnostic] = caught.value.diagnostics
    assert diagnostic.detail.endswith(_indexed_capability_detail(PLURAL_SLOT_FIXTURE))
    assert not occurrence_resolution.called


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_operator_wrapped_indexed_source_still_refuses_correctly(strict: bool) -> None:
    """Positive regression, not a red-set member: this shape already refuses correctly."""
    fixture = FIXTURES_DIR / OPERATOR_WRAPPED_FIXTURE

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    assert diagnostic.detail.endswith(_indexed_capability_detail(OPERATOR_WRAPPED_FIXTURE))
    assert str(caught.value).count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1


# --- Natural-route consumer closure table (Phase 1 seed) ---------------------
#
# Leg 3 of closure — routes.  Every consumer that reads an expression must prove four
# things through its natural public route, not through a directly called helper.  See
# `.project/active/stop-reinventing-the-parser/design.md#evidence-and-public-boundary-matrix`.
#
# A cell holds the `module::function` of the test that proves it, or an empty string
# while it is uncovered.  At `C_base` only the computed-attribute indexed-refusal cells
# are filled, by the two red-set tests above, so `test_every_consumer_cell_names_a_proof`
# is a recorded red listing every gap.  Phases 2-4 fill it.


@dataclass(frozen=True)
class ConsumerRow:
    """One consumer's four required proofs and the public arms they run through."""

    consumer: str
    exact_positive: str
    indexed_refusal: str
    operand_or_depth_failure: str
    missing_exact_target: str
    public_arms: tuple[str, ...]


CONSUMER_CLOSURE_TABLE: tuple[ConsumerRow, ...] = (
    ConsumerRow(
        consumer="calculation-definition dependency compiler",
        exact_positive="",
        indexed_refusal="",
        operand_or_depth_failure="",
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
    ConsumerRow(
        consumer="calculation and constraint binding",
        exact_positive="",
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic"
        ),
        operand_or_depth_failure="",
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
    ConsumerRow(
        consumer="alias",
        exact_positive="",
        indexed_refusal="",
        operand_or_depth_failure="",
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
    ConsumerRow(
        consumer="computed attribute",
        exact_positive="",
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_indexed_bare_chain_singular_slot_refuses_before_consumers"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_failures_return_no_graph"
        ),
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
    ConsumerRow(
        consumer="constraint predicate",
        exact_positive="",
        indexed_refusal="",
        operand_or_depth_failure="",
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
    ConsumerRow(
        consumer="deep literal override",
        exact_positive="",
        indexed_refusal="",
        operand_or_depth_failure="not an expression route",
        missing_exact_target="",
        public_arms=("live", "admitted/capture"),
    ),
)

_CELL_NAMES = (
    "exact_positive",
    "indexed_refusal",
    "operand_or_depth_failure",
    "missing_exact_target",
)


def _named_proof_exists(cell: str) -> bool:
    module_path, _, function = cell.partition("::")
    module_name = Path(module_path).with_suffix("").as_posix().replace("/", ".")
    return hasattr(importlib.import_module(module_name), function)


def test_the_consumer_closure_table_covers_every_reviewed_consumer() -> None:
    """The six consumers of the design's matrix, and no fewer."""
    assert [row.consumer for row in CONSUMER_CLOSURE_TABLE] == [
        "calculation-definition dependency compiler",
        "calculation and constraint binding",
        "alias",
        "computed attribute",
        "constraint predicate",
        "deep literal override",
    ]
    for row in CONSUMER_CLOSURE_TABLE:
        assert row.public_arms == ("live", "admitted/capture")


def test_every_named_proof_in_the_consumer_table_resolves() -> None:
    """A cell that names a test which does not exist is worse than an empty cell."""
    unresolved: list[str] = []
    for row in CONSUMER_CLOSURE_TABLE:
        for name in _CELL_NAMES:
            cell = getattr(row, name)
            if "::" in cell and not _named_proof_exists(cell):
                unresolved.append(f"{row.consumer}/{name}: {cell}")
    assert not unresolved, f"consumer table names tests that do not exist: {unresolved}"


def test_every_consumer_cell_names_a_proof() -> None:
    """Recorded red at `C_base`: most of the natural-route matrix is still uncovered."""
    uncovered = [
        f"{row.consumer}/{name}"
        for row in CONSUMER_CLOSURE_TABLE
        for name in _CELL_NAMES
        if not getattr(row, name)
    ]
    assert not uncovered, f"consumer closure cells with no proof: {uncovered}"
