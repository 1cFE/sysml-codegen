"""Frozen cross-revision probes for GAP-CLOSE Item 2.

Run this file outside the selected detached worktrees.  It imports only seams present at the
coordinated baseline and detects the candidate-only explicit source-route arguments by signature.
"""

from __future__ import annotations

import hashlib
import inspect
import logging
import os
import subprocess
from pathlib import Path

import agentic_mbse
import agentic_mbse.sysml.constraint_facts as constraint_facts_module
import agentic_mbse.sysml.executable_profile as executable_profile_module
import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.executable_profile import PROFILE_SEMANTIC_VERSION
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

import sysml_codegen
import sysml_codegen.analysis.constraint_lowering as lowering_module
from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

CODEGEN_REVISION = "6db321225a5c8568db0287b67ed1d04c03079cc2"
COMPANION_REVISION = "4ed2a0728ea49298666415cd389d9a6173a81a3e"
PRODUCTION_PATHS = (
    "src/sysml_codegen/analysis/constraint_lowering.py",
    "src/sysml_codegen/analysis/source_referent.py",
    "src/sysml_codegen/orchestration/pipeline_builder.py",
    "src/sysml_codegen/snapshot/capture.py",
    "src/sysml_codegen/snapshot/serializer.py",
    "src/sysml_codegen/snapshot/graph_rebuild.py",
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _assert_selected_sources() -> None:
    codegen_repo = Path(os.environ["EXPECTED_CODEGEN_REPO"]).resolve()
    companion_repo = Path(os.environ["EXPECTED_COMPANION_REPO"]).resolve()
    assert _git(codegen_repo, "rev-parse", "HEAD") == CODEGEN_REVISION
    assert _git(companion_repo, "rev-parse", "HEAD") == COMPANION_REVISION
    assert _git(companion_repo, "status", "--porcelain") == ""
    if not os.environ.get("EXPECTED_PATCH_SHA"):
        assert _git(codegen_repo, "status", "--porcelain") == ""

    codegen_src = (codegen_repo / "src").resolve()
    companion_src = (companion_repo / "src").resolve()
    for module in (sysml_codegen, lowering_module):
        source = inspect.getsourcefile(module)
        assert source is not None
        assert Path(source).resolve().is_relative_to(codegen_src)
    for module in (agentic_mbse, constraint_facts_module, executable_profile_module):
        source = inspect.getsourcefile(module)
        assert source is not None
        assert Path(source).resolve().is_relative_to(companion_src)
    assert PROFILE_SEMANTIC_VERSION == "executable-profile/v3"

    expected_overlay_sha = os.environ["EXPECTED_OVERLAY_SHA"]
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == expected_overlay_sha
    expected_patch_sha = os.environ.get("EXPECTED_PATCH_SHA")
    if expected_patch_sha:
        diff = subprocess.run(
            [
                "git",
                "-C",
                str(codegen_repo),
                "diff",
                "--binary",
                CODEGEN_REVISION,
                "--",
                *PRODUCTION_PATHS,
            ],
            check=True,
            capture_output=True,
        ).stdout
        assert hashlib.sha256(diff).hexdigest() == expected_patch_sha


_assert_selected_sources()


def _identity(name: str | None = None, qualified_name: str | None = None) -> IdentityFact:
    return IdentityFact(kind="AssertConstraintUsage", name=name, qualified_name=qualified_name)


def _literal(value: object, category: str) -> LiteralNode:
    kind = {
        "boolean": "LiteralBoolean",
        "real": "LiteralRational",
    }[category]
    return LiteralNode(
        literal=LiteralFact(kind=kind, value=value, result_type=category),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


def _comparison(operator: str, category: str) -> OperatorNode:
    values = (True, False) if category == "boolean" else (1.0, 2.0)
    return OperatorNode(
        operator=operator,
        operands=[_literal(values[0], category), _literal(values[1], category)],
        operand_type=None,
    )


def _usage(
    *,
    file: Path,
    line: int,
    column: int,
    source_form: str,
    owner_kind: str,
    predicate: OperatorNode | None,
    qualified_name: str | None = None,
) -> ConstraintUsageFact:
    identity = _identity(None, qualified_name)
    effective = identity if source_form == "inline" else None
    return ConstraintUsageFact(
        identity=identity,
        location=LocationFact(file=str(file), line=line, column=column),
        source=ConstraintSource(
            form=source_form,
            effective_predicate_source=effective,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=effective,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(
                kind=owner_kind, qualified_name="Evidence::Owner"
            ),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False if predicate is not None else None,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts(usages: list[ConstraintUsageFact]) -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=usages, contexts=[], diagnostics=[])


def _lower(facts: ConstraintFacts, root: Path):
    kwargs = dict(occ_index=None, registry=None, design_attrs={}, calc_usages=[])
    parameters = inspect.signature(lower_constraints).parameters
    if "source_location_mode" in parameters:
        kwargs["source_location_mode"] = "live"
        kwargs["source_roots"] = [root]
    return lower_constraints(facts, **kwargs)


class _EventHandler(logging.Handler):
    def __init__(self, events: list[str]) -> None:
        super().__init__()
        self.events = events

    def emit(self, record: logging.LogRecord) -> None:
        self.events.append(record.getMessage())


def test_f4_warnings_precede_block(tmp_path: Path) -> None:
    model = tmp_path / "model.sysml"
    usages = [
        _usage(
            file=model,
            line=line,
            column=2,
            source_form="inline",
            owner_kind="package",
            predicate=_comparison("==", "boolean"),
            qualified_name=f"Evidence__warning_{line}",
        )
        for line in (10, 20)
    ]
    usages.append(
        _usage(
            file=model,
            line=30,
            column=2,
            source_form="inline",
            owner_kind="package",
            predicate=_comparison("==", "real"),
            qualified_name="Evidence__blocked",
        )
    )
    events: list[str] = []
    handler = _EventHandler(events)
    logger = logging.getLogger("sysml_codegen.analysis.constraint_lowering")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    try:
        with pytest.raises(CodeGenerationError) as error:
            _lower(_facts(usages), tmp_path)
        events.append("raised")
    finally:
        logger.removeHandler(handler)
    assert events == [
        f"Constraint Evidence__warning_10 at {model}:10:2 is not numerical and will not "
        "execute: warn_non_numerical_equality",
        f"Constraint Evidence__warning_20 at {model}:20:2 is not numerical and will not "
        "execute: warn_non_numerical_equality",
        "raised",
    ]
    message = str(error.value)
    assert "Evidence__blocked" in message
    assert "block_real_equality_requires_tolerance" in message
    assert "two-inequality" in message


@pytest.mark.parametrize(
    ("kind", "source_form", "owner_kind", "predicate"),
    (
        ("non_numerical", "inline", "package", _comparison("==", "boolean")),
        ("unassessed_form", "satisfy", "package", None),
        ("unsupported_owner", "inline", "requirement_def", _comparison("<=", "real")),
    ),
)
def test_f5_anonymous_pair_is_distinct(
    tmp_path: Path,
    kind: str,
    source_form: str,
    owner_kind: str,
    predicate: OperatorNode | None,
) -> None:
    model = tmp_path / "model.sysml"
    usages = [
        _usage(
            file=model,
            line=line,
            column=2,
            source_form=source_form,
            owner_kind=owner_kind,
            predicate=predicate,
        )
        for line in (10, 20)
    ]
    for usage in usages:
        assert usage.identity.name is None
        assert usage.identity.qualified_name is None
        assert usage.location is not None
        assert usage.location.file == str(model)
        assert usage.location.column == 2

    records = _lower(_facts(usages), tmp_path)
    assert len(records) == 2
    assert len({record.constraint_id for record in records}) == 2
    assert all(record.exclusion is not None for record in records)
    assert [record.exclusion.kind for record in records] == [kind, kind]


def test_non_blocking_warnings_are_exactly_once(tmp_path: Path, caplog) -> None:
    model = tmp_path / "model.sysml"
    usages = [
        _usage(
            file=model,
            line=line,
            column=2,
            source_form="inline",
            owner_kind="package",
            predicate=_comparison("==", "boolean"),
            qualified_name=f"Evidence__warning_{line}",
        )
        for line in (10, 20)
    ]
    with caplog.at_level(logging.WARNING, logger="sysml_codegen.analysis.constraint_lowering"):
        _lower(_facts(usages), tmp_path)
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "sysml_codegen.analysis.constraint_lowering"
    ]
    assert len(messages) == 2
    assert "Evidence__warning_10" in messages[0]
    assert "Evidence__warning_20" in messages[1]
