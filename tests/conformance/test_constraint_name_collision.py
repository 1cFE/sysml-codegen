"""R10: two same-named constraint usages under one owner must not share one key.

The constraint entry-point key is ``{owner}__{usage}__{formal}``, so two usages named
``viability`` under ``the_host`` would both ask for
``ConstraintNameCollision__the_host__viability__threshold``. One key standing for two
constraints is the defect class this recovery exists to undo: the second declaration
silently replaces the first and the shipped JSON says nothing about it.

No corpus model has the shape, which is why nothing pinned it. These nodes pin what the
product does today, measured rather than chosen:

- **The collision is refused**, typed, at elaboration, before anything is generated.
  SysIDE leaves the shadowed usage's qualified name null, and the identity boundary
  (``elaboration/identity.py:66``) refuses it with ``SI_ID_UNSTABLE``.
- **A non-colliding pair mints two distinct keys.** The control fixture is the probe with
  the second usage renamed and nothing else changed, and it produces
  ``…__viability__threshold`` and ``…__backup_viability__threshold`` side by side.

The control is what makes the refusal a statement about the *name*: the strip check below
proves the rename is the sole difference between the two models.

Recorded for `.project/active/cutover-recovery/owner-disposition-20260811.md` step 4 (R10).
"""

from __future__ import annotations

import re
from collections import Counter

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

PROBE = FIXTURES_DIR / "constraint_name_collision_probe"
CONTROL = FIXTURES_DIR / "constraint_name_collision_control"

COLLIDING_NAME = "viability"
DISTINCT_NAME = "backup_viability"

#: Every entry point the control mints, in full. The two constraint keys differ only in
#: the usage segment, which is exactly the segment the probe makes ambiguous.
CONTROL_ENTRY_POINT_KEYS = {
    "ConstraintNameCollision__the_host__primary_gain",
    "ConstraintNameCollision__the_host__backup_gain",
    "ConstraintNameCollision__the_host__viability__threshold",
    "ConstraintNameCollision__the_host__backup_viability__threshold",
    "ConstraintNameCollision__the_other__seed",
}

CONTROL_CONSTRAINT_IDS = {
    "ConstraintNameCollision__the_host__viability__fb8eee6519fa76c7",
    "ConstraintNameCollision__the_host__backup_viability__63ab135fa7b82888",
}

SI_ID_UNSTABLE_DETAIL = (
    "AssertConstraintUsage has no reload-stable qualified declaration identity"
)


def _model_lines(fixture) -> list[str]:
    """The fixture's model, comments and blank lines removed.

    Comments carry the two fixtures' different explanations; the strip check is a claim
    about the SysML, so it reads the SysML only.
    """
    text = (fixture / "model.sysml").read_text()
    text = re.sub(r"doc /\*.*?\*/", "", text, flags=re.DOTALL)
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line and not line.startswith("//")]


def test_the_control_is_the_probe_with_one_name_changed() -> None:
    """The rename is the sole edit, so the name is the sole cause of what follows."""
    control_renamed_back = [
        line.replace(DISTINCT_NAME, COLLIDING_NAME) for line in _model_lines(CONTROL)
    ]
    assert control_renamed_back == _model_lines(PROBE)


def test_the_collision_is_refused_before_generation() -> None:
    """Two same-named usages under one owner: typed refusal, not one shared key.

    The mechanism, end to end: SysIDE reports the shadowing as a *warning* and leaves the
    second usage's qualified name null; ``_index_constraint_associations``
    (``elaboration/elaborate.py:278``) asks the identity boundary for a reload-stable
    declaration ID, and that refuses. Elaboration wraps it as a validation diagnostic, so
    the user sees a typed refusal with no package written.
    """
    extractor = SysMLDataExtractor([PROBE])
    assert extractor.load_models()
    assert extractor.diagnostics is not None

    # The parser notices, but only as a warning — it is not the refusal mechanism.
    shadowing = [
        diagnostic
        for diagnostic in extractor.diagnostics.validation
        if diagnostic.code == "namespace-distinguishability"
    ]
    assert len(shadowing) == 1
    assert shadowing[0].message == (
        "Member name 'viability' shadows ConstraintNameCollision::the_host::viability"
    )

    # Exactly one of the two same-named usages loses its qualified name. That is what
    # the identity boundary refuses, and it is why the collision cannot reach a key.
    usages = [
        usage
        for usage in SysideAdapter.elements_of_type(
            extractor.model, "ConstraintUsage", include_subtypes=True
        )
        if usage.name == COLLIDING_NAME
    ]
    assert len(usages) == 2
    assert Counter(
        str(usage.qualified_name) if usage.qualified_name is not None else None
        for usage in usages
    ) == Counter({None: 1, "ConstraintNameCollision::the_host::viability": 1})

    with pytest.raises(ElaborationDiagnosticError) as refusal:
        build_elaborated_pipeline([PROBE])
    diagnostics = refusal.value.diagnostics
    assert [diagnostic.code for diagnostic in diagnostics] == [ElaborationCode.SI_ID_UNSTABLE]
    assert diagnostics[0].detail == SI_ID_UNSTABLE_DETAIL


def test_the_public_route_writes_nothing_for_the_collision(tmp_path) -> None:
    """The refusal reaches the shipped surface: `run_codegen` fails and leaves no tree."""
    output = tmp_path / "package"
    assert not run_codegen(
        GenerationConfig(
            output_path=output,
            models_path=PROBE,
            package_name="collision_probe",
        )
    )
    assert not output.exists()


def test_distinct_usage_names_mint_distinct_constraint_keys() -> None:
    """The control's key multiset, in full — two `…__threshold` keys, not one."""
    graph = build_elaborated_pipeline([CONTROL])

    keys = [
        parameter.qualified_name
        for group in graph.entry_point_groups
        for parameter in group.parameters
    ]
    assert len(keys) == len(set(keys))
    assert set(keys) == CONTROL_ENTRY_POINT_KEYS

    assert graph.constraint_catalog is not None
    entries = graph.constraint_catalog.concrete_entries
    assert {entry.constraint_id for entry in entries} == CONTROL_CONSTRAINT_IDS
    assert {entry.source_local_identity for entry in entries} == {
        COLLIDING_NAME,
        DISTINCT_NAME,
    }
    assert {entry.usage_qualified_name for entry in entries} == {
        "ConstraintNameCollision::the_host::viability",
        "ConstraintNameCollision::the_host::backup_viability",
    }
    assert {entry.owner_qualified_name for entry in entries} == {
        "ConstraintNameCollision::the_host"
    }
    assert len({entry.evaluation_channel for entry in entries}) == 2
