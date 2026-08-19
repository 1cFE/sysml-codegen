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

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    InstanceGraph,
    NodeRef,
    ValueSite,
)
from sysml_codegen.elaboration.expression_evidence import (
    ExpressionInventoryError,
    ExpressionSite,
    ExpressionSiteRole,
)
from sysml_codegen.orchestration import elaborated_pipeline
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, constraint

RAW_SOURCE = str(Path("/stage/model.sysml").resolve())
REFERENT = "root-0/model.sysml"

# Capture has one fixed strict route. Live and admitted elaboration expose both modes.
PUBLIC_ROUTE_CASES = (
    pytest.param("live", True, id="live-strict"),
    pytest.param("live", False, id="live-lenient"),
    pytest.param("admitted", True, id="admitted-strict"),
    pytest.param("admitted", False, id="admitted-lenient"),
    pytest.param("capture", True, id="capture"),
)


class _EmptyModel:
    """A model the inventory can enumerate and find no expression site in.

    The conversion boundary builds the evidence inventory before it extracts anything,
    so a double that stands in for a loaded model has to answer the enumeration.  An
    empty answer is the right one here: these tests force their failure at a later
    consumer, and an inventory that refused first would hide which stage converted.
    """

    def elements(self, _type: object, include_subtypes: bool = False) -> list[Any]:
        return []


class _EvidenceFailingExtractor:
    def __init__(self, _model_paths: list[Path] | None = None) -> None:
        self.model = _EmptyModel()
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
        self.model = _EmptyModel()
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
    """Make the pre-graph inventory acquire one expression that cannot be acquired.

    The acquisition step is the real one — the same call every site goes through — so
    what is forced is which expression reaches it, not how it fails.
    """
    evidence = importlib.import_module("sysml_codegen.elaboration.expression_evidence")

    def acquire_the_forced_expression(_model: object) -> object:
        evidence._acquire(expression)
        raise AssertionError("forced evidence failure produced an inventory")

    monkeypatch.setattr(
        elaborated_pipeline,
        "build_expression_evidence_inventory",
        acquire_the_forced_expression,
    )


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


@requires_license
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_unit_annotated_alias_survives_the_public_conversion_boundary(
    tmp_path: Path,
    arm: str,
    strict: bool,
) -> None:
    """A valid ``= reference [unit]`` value is an alias, not a missing computed row."""
    source = tmp_path / "model.sysml"
    source.write_text(
        """package UnitAnnotatedAlias {
    private import ScalarValues::*;
    private import SI::*;

    calc def Identity {
        in attribute x : Real;
        out attribute y : Real = x;
    }
    part def Inner {
        attribute width : Real = 2.0 [m];
    }
    part def Host {
        attribute base_len : Real = 1.0 [m];
        attribute mirror_len : Real = base_len [m];
        part inner : Inner;
        attribute mirror_width : Real = inner.width [m];
        calc identity : Identity { in x = mirror_width; }
    }
    part host : Host;
}
""",
        encoding="utf-8",
    )

    graph = _public_graph(
        arm,
        source,
        strict=strict,
        output=tmp_path / "instance_graph_snapshot.json",
    )
    base = attr(graph, "UnitAnnotatedAlias__host__base_len")
    mirror = attr(graph, "UnitAnnotatedAlias__host__mirror_len")
    width = attr(graph, "UnitAnnotatedAlias__host__inner__width")
    mirror_width = attr(graph, "UnitAnnotatedAlias__host__mirror_width")
    assert mirror.is_alias
    assert mirror.alias_target is not None
    assert mirror.alias_target.target == base.node_id
    assert mirror_width.is_alias
    assert mirror_width.alias_target is not None
    assert mirror_width.alias_target.target == width.node_id
    assert graph.diagnostics == []


def test_inventory_invariant_is_contained_with_authored_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An inventory/consumer defect still becomes one useful public diagnostic."""
    error = ExpressionInventoryError(
        "assigned site disappeared",
        reference="base_len [m]",
        location=(RAW_SOURCE, 6),
    )
    monkeypatch.setattr(
        elaborated_pipeline,
        "build_expression_evidence_inventory",
        lambda _model: (_ for _ in ()).throw(error),
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_loaded_extractor(
            _BoundaryExtractor(),
            model_paths=(Path(RAW_SOURCE),),
            source_referents={RAW_SOURCE: REFERENT},
            strict=True,
        )

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == "base_len [m]"
    assert diagnostic.consumer_display == "base_len [m]"
    assert diagnostic.source_file == REFERENT
    assert diagnostic.source_line == 6
    assert caught.value.__cause__ is error


@requires_license
def test_constraint_definition_index_refuses_at_pregraph_inventory(
    tmp_path: Path,
) -> None:
    """A definition body is a predicate site even before any usage can be lowered."""
    source = tmp_path / "model.sysml"
    source.write_text(
        """package IndexedConstraintDefinition {
    private import ScalarValues::*;

    part def Cell { attribute mass : Real = 3.0; }
    part def Host { part cells : Cell[3]; }

    constraint def IndexedGuard {
        in part h : Host;
        h.cells#(2).mass > 0.0
    }
}
""",
        encoding="utf-8",
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([source], strict=True)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    assert diagnostic.reference == "h.cells#(2).mass"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 9


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
    """A binding whose right-hand side is an authored index, refused by name.

    Tightened in this landing unit, as the Phase-1 record said it would be: the refusal
    now carries the authored reference and a root-relative place, where before it carried
    neither and hid the caller's absolute path inside ``detail``.
    """
    fixture = FIXTURES_DIR / "indexed_expression_source"

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    assert diagnostic.consumer is None
    assert diagnostic.param_name is None
    assert diagnostic.reference == "cells#(2).mass"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 17
    assert str(caught.value).count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1
    assert not diagnostic.detail.startswith("/")
    assert "/tmp/" not in str(caught.value)


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

#: The authored text the refusal must name back to the modeller, verbatim.
AUTHORED_INDEXED_REFERENCE = "cells#(2).mass"
AUTHORED_INDEXED_LINE = 15

#: The root-relative referent every public arm reports.  Measured, not assumed: the live
#: arm derives it from the caller's model root, and the admitted and capture arms map their
#: private staged copy back through ``staged_to_referent``.  All three produce this exact
#: value, so one constant is correct for all three rather than a per-arm table.
ROOT_RELATIVE_REFERENT = "root-0/model.sysml"

#: The three public arms the design requires for every consumer row.
PUBLIC_ARMS = ("live", "admitted", "capture")


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


def _elaborate_through_arm(arm: str, fixture: Path, *, strict: bool, output: Path) -> object:
    """Run one fixture through one public arm and return whatever that arm returns.

    The capture arm ignores ``strict``: it seals through the admitted route, which the
    design fixes at strict.  ``output`` is only written by the capture arm.
    """
    from sysml_codegen.extraction.source_manifest import admit_sources

    if arm == "live":
        return elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)
    if arm == "admitted":
        with admit_sources([fixture]) as admission:
            return elaborated_pipeline.elaborate_admitted_sources(admission, strict=strict)
    if arm == "capture":
        return capture_instance_graph_snapshot([fixture], output)
    raise AssertionError(f"unknown public arm: {arm}")


def _assert_named_indexed_refusal(
    error: ElaborationDiagnosticError,
    *,
    reference: str = AUTHORED_INDEXED_REFERENCE,
    line: int = AUTHORED_INDEXED_LINE,
) -> None:
    """The full green contract: one named refusal carrying the authored reference and place.

    Every field is compared for exact equality, never by suffix or substring.  That is the
    point of this helper.  The SI_INDEXED_SOURCE_UNSUPPORTED diagnostic `C_base` already
    produces carries ``reference=None`` and ``source_file=None`` and hides an absolute
    staged path inside ``detail`` — and an ``endswith`` on a relative tail matches that
    absolute path too.  An implementation that routes the bare chain into that existing
    shape must stay red here, in every arm.
    """
    assert [item.code for item in error.diagnostics] == [
        ElaborationCode.SI_INDEXED_SOURCE_UNSUPPORTED
    ]
    [diagnostic] = error.diagnostics
    assert diagnostic.reference == reference
    assert diagnostic.source_file == ROOT_RELATIVE_REFERENT
    assert diagnostic.source_line == line
    rendered = str(error)
    assert rendered.count("SI_INDEXED_SOURCE_UNSUPPORTED") == 1
    # The place must be root-relative in the rendered message too, never absolute and never
    # the private staged copy the admitted and capture arms parse from.
    assert "/tmp/" not in rendered
    assert not diagnostic.detail.startswith("/")
    semantic_error = error.__cause__
    assert isinstance(semantic_error, SemanticEvidenceError)
    assert semantic_error.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
    assert semantic_error.cause is None
    assert semantic_error.__cause__ is None


def _public_graph(
    arm: str,
    fixture: Path,
    *,
    strict: bool,
    output: Path,
) -> InstanceGraph:
    result = _elaborate_through_arm(arm, fixture, strict=strict, output=output)
    if arm == "capture":
        assert isinstance(result, Path)
        return load_instance_graph_snapshot(result)
    assert isinstance(result, InstanceGraph)
    return result


def _preserved_capture_output(arm: str, output: Path) -> bytes | None:
    if arm != "capture":
        return None
    original = b"pre-existing snapshot bytes"
    output.write_bytes(original)
    return original


def _assert_capture_output_preserved(
    arm: str,
    output: Path,
    original: bytes | None,
) -> None:
    if arm == "capture":
        assert original is not None
        assert output.read_bytes() == original
        assert not list(output.parent.glob(f".{output.name}.*.tmp"))
    else:
        assert original is None
        assert not output.exists()


@requires_license
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_unsupported_invocation_refuses_pregraph_with_authored_provenance(
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """``max(...)`` is valid SysML and an unsupported executable capability."""
    source = tmp_path / "model.sysml"
    source.write_text(
        """package UnsupportedInvocation {
    private import ScalarValues::*;
    private import NumericalFunctions::*;

    calc def Identity {
        in attribute x : Real;
        out attribute y : Real = x;
    }
    part def Cell { attribute capital_cost : Real = 1.0; }
    part def Bank {
        part cell : Cell[1];
        attribute capital_cost : Real = max(cell.capital_cost, 1.0);
    }
    part the_bank : Bank;
}
""",
        encoding="utf-8",
    )
    output = tmp_path / "instance_graph_snapshot.json"
    original_output = _preserved_capture_output(arm, output)
    downstream = _spy_on_expression_consumers(monkeypatch)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, source, strict=strict, output=output)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code.value == "SI_EXPRESSION_SOURCE_UNSUPPORTED"
    assert diagnostic.reference == "max(cell.capital_cost, 1.0)"
    assert diagnostic.source_file == ROOT_RELATIVE_REFERENT
    assert diagnostic.source_line == 12
    rendered = str(caught.value)
    assert rendered.count("SI_EXPRESSION_SOURCE_UNSUPPORTED") == 1
    assert "root-0/model.sysml:12" in rendered
    assert "/tmp/" not in rendered
    semantic_error = caught.value.__cause__
    assert isinstance(semantic_error, SemanticEvidenceError)
    assert semantic_error.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED
    assert not downstream.called
    _assert_capture_output_preserved(arm, output, original_output)


def _spy_on_adapter(
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
) -> _CallSpy:
    from sysml_codegen.elaboration.elaborate import _ExactElaborator

    spy = _CallSpy()
    original = getattr(_ExactElaborator, method_name)

    def record(self: object, *args: object, **kwargs: object) -> Any:
        spy.calls += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(_ExactElaborator, method_name, record)
    return spy


EXPRESSION_ADAPTER_BY_ROLE = {
    ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY: "_calc_dependencies",
    ExpressionSiteRole.BINDING: "_resolve_bindings",
    ExpressionSiteRole.ALIAS: "_resolve_aliases",
    ExpressionSiteRole.COMPUTED_ATTRIBUTE: "_resolve_computed_expressions",
    ExpressionSiteRole.CONSTRAINT_PREDICATE: "_resolve_computed_expressions",
}


@requires_license
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_public_exact_expression_consumers_preserve_edges(
    arm: str,
    strict: bool,
    tmp_path: Path,
) -> None:
    """One exact model reaches all five expression consumers through every public arm."""
    fixture = FIXTURES_DIR / "usage_owned_reference_consumers"
    graph = _public_graph(
        arm,
        fixture,
        strict=strict,
        output=tmp_path / "instance_graph_snapshot.json",
    )
    source = NodeRef(
        attr(
            graph,
            "UsageOwnedReferenceConsumers__plant__comp_a__length",
        ).node_id
    )

    compiled = calc(
        graph,
        "UsageOwnedReferenceConsumers__plant__comp_b__area_calc",
    )
    assert compiled.calc_expressions == ("area = length_in * 2.0",)
    assert len(compiled.compiled_output_ids) == 1
    assert compiled.input_by_name("length_in") == source
    bound = constraint(
        graph,
        "UsageOwnedReferenceConsumers__plant__comp_b__bound_check",
    )
    assert bound.input_by_name("length_in") == source

    alias = attr(
        graph,
        "UsageOwnedReferenceConsumers__plant__comp_b__aliased_length",
    )
    assert alias.is_alias
    assert alias.alias_target == source

    computed = calc(
        graph,
        "UsageOwnedReferenceConsumers__plant__comp_b__doubled_length",
    )
    assert computed.is_computed
    assert list(computed.inputs.values()) == [source]

    predicate = constraint(
        graph,
        "UsageOwnedReferenceConsumers__plant__comp_b__inline_check",
    )
    assert list(predicate.inputs.values()) == [source]
    assert graph.diagnostics == []


@requires_license
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_public_deep_literal_override_preserves_exact_path(
    arm: str,
    strict: bool,
    tmp_path: Path,
) -> None:
    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    graph = _public_graph(
        arm,
        fixture,
        strict=strict,
        output=tmp_path / "instance_graph_snapshot.json",
    )
    node = attr(
        graph,
        "source_identity_mixed_consumers__deep_design__panel_two__deep_rig__gain_setting",
    )
    assert node.value == 43.0
    assert node.value_site is ValueSite.OCCURRENCE_OVERRIDE
    assert graph.diagnostics == []


@dataclass(frozen=True)
class IndexedConsumerCase:
    role: ExpressionSiteRole
    fixture: str | None
    source: str | None
    indexed_reference: str
    site_reference: str
    line: int


INDEXED_CALC_DEPENDENCY_SOURCE = """package IndexedCalcDependency {
    private import ScalarValues::*;

    part def Cell { attribute mass : Real = 3.0; }

    calc def PickCell {
        in part cells : Cell[3];
        out attribute result : Real = cells#(2).mass;
    }
}
"""

INDEXED_PREDICATE_SOURCE = """package IndexedConstraintDefinition {
    private import ScalarValues::*;

    part def Cell { attribute mass : Real = 3.0; }
    part def Host { part cells : Cell[3]; }

    constraint def IndexedGuard {
        in part h : Host;
        h.cells#(2).mass > 0.0
    }
}
"""

INDEXED_CONSUMER_CASES = (
    IndexedConsumerCase(
        ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY,
        None,
        INDEXED_CALC_DEPENDENCY_SOURCE,
        "cells#(2).mass",
        "cells#(2).mass",
        8,
    ),
    IndexedConsumerCase(
        ExpressionSiteRole.BINDING,
        "indexed_expression_source",
        None,
        "cells#(2).mass",
        "cells#(2).mass",
        17,
    ),
    IndexedConsumerCase(
        ExpressionSiteRole.ALIAS,
        "indexed_bare_chain_singular",
        None,
        "cells#(2).mass",
        "cells#(2).mass",
        15,
    ),
    IndexedConsumerCase(
        ExpressionSiteRole.COMPUTED_ATTRIBUTE,
        "indexed_bare_chain_operator",
        None,
        "cells#(2).mass",
        "cells#(2).mass * 1.0",
        15,
    ),
    IndexedConsumerCase(
        ExpressionSiteRole.CONSTRAINT_PREDICATE,
        None,
        INDEXED_PREDICATE_SOURCE,
        "h.cells#(2).mass",
        "h.cells#(2).mass > 0.0",
        9,
    ),
)


def _indexed_fixture(case: IndexedConsumerCase, tmp_path: Path) -> Path:
    if case.fixture is not None:
        return FIXTURES_DIR / case.fixture
    assert case.source is not None
    fixture = tmp_path / case.role.value / "model.sysml"
    fixture.parent.mkdir()
    fixture.write_text(case.source, encoding="utf-8")
    return fixture


@requires_license
@pytest.mark.parametrize("case", INDEXED_CONSUMER_CASES, ids=lambda item: item.role.value)
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_public_indexed_expression_consumer_refuses_before_its_adapter(
    case: IndexedConsumerCase,
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Each natural indexed route is identified and refused before its real adapter."""
    import sysml_codegen.elaboration.expression_evidence as evidence

    fixture = _indexed_fixture(case, tmp_path)
    output = tmp_path / "instance_graph_snapshot.json"
    original_output = _preserved_capture_output(arm, output)
    downstream = _spy_on_adapter(monkeypatch, EXPRESSION_ADAPTER_BY_ROLE[case.role])
    acquired: list[ExpressionSite] = []
    original_acquire = evidence._acquire

    def record_acquisition(
        expression: object,
        *,
        site: ExpressionSite | None = None,
    ) -> object:
        assert site is not None
        acquired.append(site)
        return original_acquire(expression, site=site)

    monkeypatch.setattr(evidence, "_acquire", record_acquisition)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, fixture, strict=strict, output=output)

    _assert_named_indexed_refusal(
        caught.value,
        reference=case.indexed_reference,
        line=case.line,
    )
    assert acquired[-1].role is case.role
    assert acquired[-1].reference == case.site_reference
    assert acquired[-1].location is not None
    assert acquired[-1].location[1] == case.line
    assert not downstream.called
    _assert_capture_output_preserved(arm, output, original_output)


def _forced_site_expression(
    failure: SemanticEvidenceCode,
    site: ExpressionSite,
) -> object:
    assert site.location is not None
    source_file, source_line = site.location
    if failure is SemanticEvidenceCode.OPERAND_ITERATION_FAILED:
        expression = MockOperatorExpression()
    else:
        assert failure is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
        expression = MockFeatureReferenceExpression()
    expression.qualified_name = site.reference
    expression.document = SimpleNamespace(url=f"file:{Path(source_file).resolve()}")
    expression.cst_node = SimpleNamespace(
        start_point=SimpleNamespace(line=source_line - 1)
    )
    return expression


def _assert_site_failure(
    error: ElaborationDiagnosticError,
    *,
    site: ExpressionSite,
    failure: SemanticEvidenceCode,
) -> None:
    assert site.location is not None
    [diagnostic] = error.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == site.reference
    assert diagnostic.consumer_display == site.reference
    assert diagnostic.source_file == ROOT_RELATIVE_REFERENT
    assert diagnostic.source_line == site.location[1]
    assert str(error).count("SI_EVIDENCE_INCOMPLETE") == 1
    semantic_error = error.__cause__
    assert isinstance(semantic_error, SemanticEvidenceError)
    assert semantic_error.code is failure
    if failure is SemanticEvidenceCode.OPERAND_ITERATION_FAILED:
        assert isinstance(semantic_error.cause, RuntimeError)
        assert semantic_error.__cause__ is semantic_error.cause
    else:
        assert semantic_error.cause is None
        assert semantic_error.__cause__ is None


@requires_license
@pytest.mark.parametrize("role", tuple(ExpressionSiteRole), ids=lambda item: item.value)
@pytest.mark.parametrize(
    "failure",
    (
        SemanticEvidenceCode.OPERAND_ITERATION_FAILED,
        SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
    ),
    ids=lambda item: item.value.lower(),
)
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_public_expression_consumer_evidence_failure_returns_no_graph(
    role: ExpressionSiteRole,
    failure: SemanticEvidenceCode,
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Every enumerated role carries an Agentic failure through the public bridge."""
    import sysml_codegen.elaboration.expression_evidence as evidence

    fixture = FIXTURES_DIR / "usage_owned_reference_consumers"
    output = tmp_path / "instance_graph_snapshot.json"
    original_output = _preserved_capture_output(arm, output)
    downstream = _spy_on_adapter(monkeypatch, EXPRESSION_ADAPTER_BY_ROLE[role])
    original_acquire = evidence._acquire
    targeted: list[ExpressionSite] = []

    def fail_target_role(
        expression: object,
        *,
        site: ExpressionSite | None = None,
    ) -> object:
        assert site is not None
        if site.role is role:
            targeted.append(site)
            forced = _forced_site_expression(failure, site)
            return original_acquire(forced, site=site)
        return original_acquire(expression, site=site)

    monkeypatch.setattr(evidence, "_acquire", fail_target_role)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, fixture, strict=strict, output=output)

    assert len(targeted) == 1
    _assert_site_failure(caught.value, site=targeted[0], failure=failure)
    assert not downstream.called
    _assert_capture_output_preserved(arm, output, original_output)


@requires_license
@pytest.mark.parametrize(("arm", "strict"), PUBLIC_ROUTE_CASES)
def test_public_deep_literal_override_refuses_a_missing_segment(
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The deep-override factory's missing segment reaches every public boundary."""
    import sysml_codegen.elaboration.elaborate as elaborate_module

    fixture = FIXTURES_DIR / "source_identity_mixed_consumers"
    output = tmp_path / "instance_graph_snapshot.json"
    original_output = _preserved_capture_output(arm, output)
    original_factory = elaborate_module.exact_path_from_relationship

    def refuse_deep_path(redefined: object) -> object:
        from agentic_mbse.sysml.syside_adapter import SysideAdapter

        reference = SysideAdapter.authored_text(redefined)
        if reference != "deep_rig.gain_setting":
            return original_factory(redefined)
        raise SemanticEvidenceError(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            operation="exact_path_from_relationship",
            detail="deep relationship segment 1 has no exact target fact",
            location=SysideAdapter.get_source_location(redefined),
            reference=reference,
        )

    monkeypatch.setattr(elaborate_module, "exact_path_from_relationship", refuse_deep_path)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, fixture, strict=strict, output=output)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_EVIDENCE_INCOMPLETE
    assert diagnostic.reference == "deep_rig.gain_setting"
    assert diagnostic.source_file == ROOT_RELATIVE_REFERENT
    assert diagnostic.source_line == 217
    assert str(caught.value).count("SI_EVIDENCE_INCOMPLETE") == 1
    semantic_error = caught.value.__cause__
    assert isinstance(semantic_error, SemanticEvidenceError)
    assert semantic_error.code is SemanticEvidenceCode.RESOLVED_TARGET_MISSING
    assert semantic_error.cause is None
    assert semantic_error.__cause__ is None
    _assert_capture_output_preserved(arm, output, original_output)


@requires_license
@pytest.mark.parametrize("arm", PUBLIC_ARMS)
@pytest.mark.parametrize("strict", [True, False])
def test_indexed_bare_chain_singular_slot_refuses_before_consumers(
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Case 1: an out-of-range index on a singular slot must refuse, not collapse.

    Recorded red at `C_base`, identically in all three arms: no exception is raised at all.
    The live and admitted arms return an InstanceGraph whose ``diagnostics`` is empty and
    whose attribute inventory holds ``IndexedBareChainSingular__array__cells[0]__mass`` —
    occurrence zero, minted for an authored ``#(2)`` that the model's ``Cell[1]`` slot
    cannot honor.  The capture arm seals that collapsed graph into a snapshot.
    """
    fixture = FIXTURES_DIR / SINGULAR_SLOT_FIXTURE
    output = tmp_path / "instance_graph_snapshot.json"
    consumers = _spy_on_expression_consumers(monkeypatch)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, fixture, strict=strict, output=output)

    _assert_named_indexed_refusal(caught.value)
    assert not consumers.called
    assert not output.exists()


@requires_license
@pytest.mark.parametrize("arm", PUBLIC_ARMS)
@pytest.mark.parametrize("strict", [True, False])
def test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution(
    arm: str,
    strict: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Case 2: the index defect must be named, and named before occurrence resolution.

    Recorded red at `C_base`.  In the strict live, admitted and capture arms the route
    refuses with two diagnostics — first ``SI_OCCURRENCE_AMBIGUOUS`` ("exact containment
    step ... has 3 concrete occurrences") then ``SI_OCCURRENCE_MISSING`` on the typed alias
    ``IndexedBareChainPlural__array__picked``.  Both are occurrence-selection names raised
    for an unsupported authored index, and ``OccurrenceIndex.resolve_address`` has already
    run by the time either is built.  Under lenient the live and admitted arms do not refuse
    at all; they return a graph carrying those same two diagnostics.
    """
    fixture = FIXTURES_DIR / PLURAL_SLOT_FIXTURE
    output = tmp_path / "instance_graph_snapshot.json"
    occurrence_resolution = _spy_on_occurrence_resolution(monkeypatch)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        _elaborate_through_arm(arm, fixture, strict=strict, output=output)

    _assert_named_indexed_refusal(caught.value)
    assert not occurrence_resolution.called
    assert not output.exists()


@requires_license
@pytest.mark.parametrize("strict", [True, False])
def test_operator_wrapped_indexed_source_still_refuses_correctly(strict: bool) -> None:
    """The operator-wrapped form was always refused; now it is refused by the same name.

    It was never a red-set member — it already produced
    ``SI_INDEXED_SOURCE_UNSUPPORTED`` at `C_base`.  What changed here is the shape: it
    now carries the authored reference and a root-relative place like every other
    indexed refusal, instead of three empty fields and an absolute path in ``detail``.
    The Phase-1 record pinned the old shape exactly so this tightening could not happen
    silently, and this is the landing unit it named.
    """
    fixture = FIXTURES_DIR / OPERATOR_WRAPPED_FIXTURE

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([fixture], strict=strict)

    _assert_named_indexed_refusal(caught.value)


# --- Natural-route consumer closure table (Phase 1 seed) ---------------------
#
# Leg 3 of closure — routes.  Every consumer that reads an expression must prove four
# things through its natural public route, not through a directly called helper.  See
# `.project/active/stop-reinventing-the-parser/design.md#evidence-and-public-boundary-matrix`.
#
# A cell holds the `module::function` of the test that proves it. Public arms are recorded
# per cell: the deep-override grammar makes two failure shapes unavailable before public
# elaboration, so those cells name the measured parser/structure proofs instead.


_CELL_NAMES = (
    "exact_positive",
    "indexed_refusal",
    "operand_or_depth_failure",
    "missing_exact_target",
)
_ALL_PUBLIC_CELL_ARMS = tuple(
    (cell, ("live", "admitted/capture")) for cell in _CELL_NAMES
)


@dataclass(frozen=True)
class ConsumerRow:
    """One consumer's four proofs, with route strength stated for every cell."""

    consumer: str
    exact_positive: str
    indexed_refusal: str
    operand_or_depth_failure: str
    missing_exact_target: str
    cell_public_arms: tuple[tuple[str, tuple[str, ...]], ...]
    unavailable_reasons: tuple[tuple[str, str], ...] = ()


CONSUMER_CLOSURE_TABLE: tuple[ConsumerRow, ...] = (
    ConsumerRow(
        consumer="calculation-definition dependency compiler",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_consumers_preserve_edges"
        ),
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_indexed_expression_consumer_refuses_before_its_adapter"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        cell_public_arms=_ALL_PUBLIC_CELL_ARMS,
    ),
    ConsumerRow(
        consumer="calculation and constraint binding",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_consumers_preserve_edges"
        ),
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_valid_indexed_source_refuses_before_graph_with_exact_capability_diagnostic"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        cell_public_arms=_ALL_PUBLIC_CELL_ARMS,
    ),
    ConsumerRow(
        consumer="alias",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_consumers_preserve_edges"
        ),
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_indexed_expression_consumer_refuses_before_its_adapter"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        cell_public_arms=_ALL_PUBLIC_CELL_ARMS,
    ),
    ConsumerRow(
        consumer="computed attribute",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_consumers_preserve_edges"
        ),
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_indexed_expression_consumer_refuses_before_its_adapter"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_failures_return_no_graph"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        cell_public_arms=_ALL_PUBLIC_CELL_ARMS,
    ),
    ConsumerRow(
        consumer="constraint predicate",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_exact_expression_consumers_preserve_edges"
        ),
        indexed_refusal=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_indexed_expression_consumer_refuses_before_its_adapter"
        ),
        operand_or_depth_failure=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_expression_consumer_evidence_failure_returns_no_graph"
        ),
        cell_public_arms=_ALL_PUBLIC_CELL_ARMS,
    ),
    ConsumerRow(
        consumer="deep literal override",
        exact_positive=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_deep_literal_override_preserves_exact_path"
        ),
        indexed_refusal=(
            "tests/unit/test_expression_evidence_boundary.py"
            "::test_indexed_deep_override_is_rejected_by_the_parser"
        ),
        operand_or_depth_failure=(
            "tests/unit/test_expression_evidence_boundary.py"
            "::test_real_deep_override_relationships_contain_only_features"
        ),
        missing_exact_target=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_public_deep_literal_override_refuses_a_missing_segment"
        ),
        cell_public_arms=(
            ("exact_positive", ("live", "admitted/capture")),
            ("indexed_refusal", ()),
            ("operand_or_depth_failure", ()),
            ("missing_exact_target", ("live", "admitted/capture")),
        ),
        unavailable_reasons=(
            (
                "indexed_refusal",
                "SysIDE rejects an indexed deep override at parse before public elaboration",
            ),
            (
                "operand_or_depth_failure",
                "parsed deep-override paths contain only Features and never enter "
                "expression acquisition",
            ),
        ),
    ),
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
        arms = dict(row.cell_public_arms)
        reasons = dict(row.unavailable_reasons)
        assert set(arms) == set(_CELL_NAMES)
        assert set(reasons) == {cell for cell, public_arms in arms.items() if not public_arms}
        for cell, public_arms in arms.items():
            if public_arms:
                assert public_arms == ("live", "admitted/capture")
            else:
                assert reasons[cell]


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
    """Every cell resolves to a real test and states its executable route force."""
    defects: list[str] = []
    for row in CONSUMER_CLOSURE_TABLE:
        arms = dict(row.cell_public_arms)
        reasons = dict(row.unavailable_reasons)
        for name in _CELL_NAMES:
            proof = getattr(row, name)
            if proof.count("::") != 1 or not proof.split("::", 1)[1].startswith("test_"):
                defects.append(f"{row.consumer}/{name}: malformed proof {proof!r}")
            elif not _named_proof_exists(proof):
                defects.append(f"{row.consumer}/{name}: missing proof {proof!r}")
            if arms[name]:
                if arms[name] != ("live", "admitted/capture"):
                    defects.append(f"{row.consumer}/{name}: incomplete public arms {arms[name]!r}")
            elif not reasons.get(name, "").strip():
                defects.append(f"{row.consumer}/{name}: empty unavailability reason")
    assert not defects, f"consumer closure defects: {defects}"
