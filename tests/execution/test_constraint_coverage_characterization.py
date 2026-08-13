"""What the report gets wrong today, pinned so we are told the moment it stops being wrong.

Two defects, one per test, both `xfail(strict=True)`:

1. A model with one gate assessed and one gate never checked reports `all_satisfied`. The
   headline is computed from the statuses that happened to arrive
   (`templates/report_aggregator.py.jinja2:44-58`), so a shrinking denominator is invisible.
2. A model that authors constraints but has nothing eligible emits no report at all
   (`elaboration/project.py:892`), which a consumer reads as "this model has no constraints"
   — the same reading a genuinely constraint-free model gets.

Strict xfail is the point: when Item 3's Phases 3 and 4 land, these start passing and pytest
fails them loudly rather than letting a stale characterization sit green.

Expected accounts for both fixtures are hand-written from source in
`.project/active/constraint-coverage-policy/expected-coverage.md`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.execution.real_teax import generate_package_from_models, load_sealed_package

pytestmark = pytest.mark.execution

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

REPORT_CH = "constraint_report"


def _execute(fixture: str, package_name: str, root: Path):
    """Generate, seal, load, and execute a fixture against its emitted input files."""
    from simkit.core.pipeline import execute_pipeline

    package = generate_package_from_models(
        FIXTURES / fixture, root / package_name, package_name
    )
    module, _fingerprint = load_sealed_package(package, package_name, root / "link_files")
    registry = getattr(module, f"create_{package_name}_registry")()
    return execute_pipeline(
        package / "pipelines" / "pipeline.yaml",
        root / "run_files",
        registry=registry,
        custom_schema_types=module.CUSTOM_SCHEMA_TYPES,
    )


@pytest.mark.xfail(
    strict=True,
    reason="Item 3: the report can lie — partial assessment reads all_satisfied",
)
def test_partial_assessment_does_not_read_as_full_satisfaction(tmp_path):
    """`constraint_domain_detached_owner`: one gate assessed and passing, one never checked.

    Ledger entry: 2 / 2 / 1 / 1 / 0 / `{owner_has_no_occurrences: 1}` / `partial`. The
    unchecked gate is `vacuous_gate` (`model.sysml:14`), asserted on a `part def` nothing
    instantiates. Today the headline reads `all_satisfied` off the one status that arrived.
    """
    result = _execute("constraint_domain_detached_owner", "partial_probe", tmp_path)
    assert result.outputs[REPORT_CH].headline != "all_satisfied"


def test_excluded_only_model_ships_a_report():
    """`constraint_domain_plain_forms`: two authored usages, nothing eligible, now a report.

    **Fixed in Phase 4** — the `xfail` is removed and the assertion kept. Ledger entry:
    2 / 0 / 0 / 0 / 0 / `{}` / `none`, headline `not_assessed`. The graph is the observation
    surface here rather than an executed package, because the defect was that the aggregator
    module was never minted.
    """
    from sysml_codegen.elaboration import project
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
    from sysml_codegen.resolution.models import ModuleKind

    graph = project(elaborate_model_paths([FIXTURES / "constraint_domain_plain_forms"]))
    assert any(
        module.module_kind is ModuleKind.REPORT_AGGREGATOR for module in graph.modules
    )
