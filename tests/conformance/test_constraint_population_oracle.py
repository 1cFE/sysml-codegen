"""Totality, checked against evidence that does not descend from the domain.

Every other artifact in this chain — catalog, snapshot, requirement rows — is a projection
of the elaborated domain. Comparing any two of them compares two views of one population,
so a truncation upstream of all of them passes every such check. That is precisely how
``catf_mfe_d5`` shipped 9 carriers for 65 authored usages without a single test failing.

The expectation files here are the outside evidence. They hold one row per authored
constraint usage, read from the `.sysml` source, and the domain is asserted against them
**by identity list** rather than by count, so swapping one usage for another fails.

Four rules keep the oracle from quietly shrinking:

1. A constraint-bearing fixture directory with no expectation file is a failure naming the
   directory. A newly added fixture cannot become silent coverage.
2. An expectation file whose rows no longer match the source is a failure. Fixtures drift.
3. An ``@inapplicable`` marker written in source that produced no ``Inapplicability`` on
   the record is a failure. SysIDE drops a ``doc`` comment inside an inline-predicate
   constraint body, so on that one shape the marker never reaches elaboration and the
   strict parse's near-miss halt cannot fire. This is what makes that gap loud.
4. Every fixture exempted from the domain comparison must still actually refuse. An
   exemption that silently stops being true is coverage lost without a failure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.elaboration.elaborate import (
    ElaborationDiagnosticError,
    ElaborationError,
)
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.constraint_source_scan import (
    scan_constraint_declarations,
    scan_inapplicable_markers,
)

EXPECTATIONS = Path(__file__).parents[1] / "expectations/constraint_population"

# Fixtures whose whole point is that elaboration refuses them — fail-closed probes, halting
# authoring errors, and models that are not loadable on their own. Their expectation file
# still records the authored population and rule 2 still guards it; only the domain
# comparison is skipped, because there is no domain to compare.
REFUSED_BY_DESIGN = frozenset(
    {
        "catf_mfe_model",
        "constraint_blocked_owner",
        "constraint_blocked_profile",
        "constraint_domain_calc_def_owner",
        "constraint_domain_inapplicable_late_marker",
        "constraint_domain_inapplicable_malformed",
        "constraint_domain_inapplicable_plain_form",
        "constraint_domain_inapplicable_unattachable",
        "constraint_malformed_mixed",
        "constraint_name_collision_probe",
        "constraint_occurrence_demand",
        "elab_payload_identity",
        "gate_a",
        "gate_a_package_owner",
        "instance_index_probe",
        "item4_require",
        "non_finite_literal",
        "plant_values",
        "shared_producer",
    }
)


def _fixture_dirs() -> list[Path]:
    return sorted(path for path in FIXTURES_DIR.iterdir() if path.is_dir())


def _constraint_bearing() -> list[Path]:
    return [path for path in _fixture_dirs() if scan_constraint_declarations(path)]


def _expectation(fixture: Path) -> dict:
    return json.loads((EXPECTATIONS / f"{fixture.name}.json").read_text())


def _identities(rows) -> list[tuple[str, str, int]]:
    return sorted(
        (row["usage_qualified_name"], row["source_file"], row["source_line"])
        for row in rows
    )


CONSTRAINT_BEARING = _constraint_bearing()
COMPARABLE = [path for path in CONSTRAINT_BEARING if path.name not in REFUSED_BY_DESIGN]


def test_every_constraint_bearing_fixture_has_an_expectation_file():
    missing = [
        path.name
        for path in CONSTRAINT_BEARING
        if not (EXPECTATIONS / f"{path.name}.json").exists()
    ]
    assert not missing, f"no expectation file: {missing}"


def test_no_expectation_file_is_stranded():
    """The other direction: a file for a fixture that no longer declares constraints."""
    named = {path.stem for path in EXPECTATIONS.glob("*.json")}
    stranded = sorted(named - {path.name for path in CONSTRAINT_BEARING})
    assert not stranded, f"expectation file with no constraint-bearing fixture: {stranded}"


@pytest.mark.parametrize("fixture", CONSTRAINT_BEARING, ids=lambda path: path.name)
def test_the_expectation_file_still_matches_its_source(fixture: Path):
    scanned = [item.as_row() for item in scan_constraint_declarations(fixture)]
    assert _identities(scanned) == _identities(_expectation(fixture)["constraint_usages"])


@pytest.mark.parametrize("fixture", COMPARABLE, ids=lambda path: path.name)
@requires_license
def test_the_domain_matches_the_reviewed_expectation(fixture: Path):
    graph = elaborate_model_paths([fixture])
    actual = sorted(
        (
            record.usage_qualified_name,
            Path(record.source_file).name,
            record.source_line,
        )
        for record in graph.constraint_usages.values()
    )
    expected = sorted(
        (row["usage_qualified_name"], Path(row["source_file"]).name, row["source_line"])
        for row in _expectation(fixture)["constraint_usages"]
    )
    assert actual == expected


@pytest.mark.parametrize("fixture", COMPARABLE, ids=lambda path: path.name)
@requires_license
def test_every_authored_inapplicable_marker_reached_the_domain(fixture: Path):
    """A marker the parser swallowed is the one silent failure the strict parse cannot catch."""
    written = len(scan_inapplicable_markers(fixture))
    carried = sum(
        1
        for record in elaborate_model_paths([fixture]).constraint_usages.values()
        if record.inapplicability is not None
    )
    assert carried == written, (
        f"{written} @inapplicable marker(s) in source, {carried} on the domain — a marker "
        "inside an inline-predicate constraint body is dropped by the parser"
    )


def test_catf_mfe_d5_expects_all_sixty_five():
    """The headline, stated in the oracle rather than only in the code that produces it."""
    assert len(_expectation(FIXTURES_DIR / "catf_mfe_d5")["constraint_usages"]) == 65


@pytest.mark.parametrize("fixture", sorted(REFUSED_BY_DESIGN), ids=lambda name: name)
@requires_license
def test_every_exempt_fixture_actually_refuses(fixture: str):
    """Rule 4: the exemption set is checked, not asserted.

    `REFUSED_BY_DESIGN` removes 18 of the 42 constraint-bearing fixtures from the domain
    comparison. Nothing verified that a member still refuses, so a fixture that started
    elaborating cleanly would stay silently exempt — and this epic will do exactly that:
    `constraint_domain_calc_def_owner` is exempt because the asserted calc-def-owner case
    halts today, and Item 6 stages that capability to execute later.

    Added with the A3 cure, which changed *why* two members refuse: a malformed
    `@inapplicable:` marker now halts per usage rather than raising out of the mint, so
    those two produce a full domain plus one error-grade disposition. They still refuse
    under strict elaboration, and this is what keeps that true.
    """
    with pytest.raises((ElaborationDiagnosticError, ElaborationError)):
        elaborate_model_paths([FIXTURES_DIR / fixture])
