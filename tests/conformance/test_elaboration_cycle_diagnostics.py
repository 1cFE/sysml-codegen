"""A producer cycle refuses as a named model diagnostic, not a traceback (F-3).

The specimen is ``sibling_formal_cycle``: a D-5 rename whose bare right-hand
side collides with the calc def's own ``out`` formal, so the renamed input
consumes its own calculation's output. Before the repair this escaped
``elaborate()`` as a raw ``GraphValidationError`` naming no file, no binding,
and no participant — an author migrating a model had nothing to act on.

All tests require a live SysIDE license.
"""

from __future__ import annotations

import argparse

import pytest

from sysml_codegen.cli import cmd_generate
from sysml_codegen.elaboration import ElaborationDiagnosticError, InstanceGraph, elaborate
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = "sibling_formal_cycle"
PARTICIPANT = "sibling_formal_cycle__plant__revenue_calc"


def _elaborate_fixture(name: str) -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models(), f"fixture {name} failed to load"
    calc_defs = extractor.extract_calculation_definitions()
    return elaborate(
        extractor.model,
        calc_defs,
        validation_diagnostics=extractor.diagnostics.validation,
    )


def _cycle_diagnostics() -> list:
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate_fixture(FIXTURE)
    return list(excinfo.value.diagnostics)


def test_cycle_surfaces_as_elaboration_diagnostic_naming_its_participant() -> None:
    """The error boundary converts final graph validation into the authored-model
    refusal class, and the cycle diagnostic names the participating consumer
    instead of the anonymous ``<instance-graph>`` display."""
    diagnostics = _cycle_diagnostics()
    cycles = [d for d in diagnostics if "typed producer dependency cycle" in d.detail]
    assert len(cycles) == 1, diagnostics
    diagnostic = cycles[0]
    assert diagnostic.consumer_display == PARTICIPANT
    assert diagnostic.detail == f"typed producer dependency cycle: {PARTICIPANT}"


def test_cycle_diagnostics_are_deterministic_across_independent_loads() -> None:
    def observed() -> list[tuple[str, str, str | None, str]]:
        return [
            (d.code.value, d.consumer_display, d.param_name, d.detail)
            for d in _cycle_diagnostics()
        ]

    assert observed() == observed()


def test_generate_cli_exits_one_with_named_diagnostic_and_writes_nothing(
    tmp_path, caplog
) -> None:
    output = tmp_path / "generated"
    args = argparse.Namespace(
        models=FIXTURES_DIR / FIXTURE,
        from_snapshot=None,
        output=output,
        package_name="sibling_formal_cycle_pkg",
        schema_class="Params",
        pipeline_name="pipeline",
        overwrite=False,
        preserve_handwritten=False,
        smart_regen=False,
        verbose=False,
    )

    with caplog.at_level("ERROR"):
        rc = cmd_generate(args)

    assert rc == 1
    assert not output.exists(), "a refused model must generate no package"
    joined = "\n".join(record.getMessage() for record in caplog.records)
    assert "Model failed exact-route validation" in joined
    assert "typed producer dependency cycle" in joined
    assert PARTICIPANT in joined
    assert "Traceback" not in joined
