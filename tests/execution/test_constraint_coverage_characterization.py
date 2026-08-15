"""The two defects that motivated Item 3, now pinned as the behaviour that replaced them.

Two defects, one per test. Both were pinned `xfail(strict=True)` in Phase 0 and both now
pass as ordinary assertions — Phase 3 fixed the first, Phase 4 the second. The tests are kept,
strengthened, because they are the two shapes that motivated the item:

1. A model with one gate assessed and one gate never checked used to report `all_satisfied`,
   because the headline was computed from the statuses that happened to arrive — so a
   shrinking denominator was invisible. It now reads `partial_coverage` and states its counts.
2. A model that authored constraints but had nothing eligible emitted no report at all, which
   a consumer read as "this model has no constraints" — the same reading a genuinely
   constraint-free model gets. It now ships a `not_assessed` report.

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


def test_partial_assessment_does_not_read_as_full_satisfaction(tmp_path):
    """`constraint_domain_detached_owner`: one gate assessed and passing, one never checked.

    **Fixed in Phase 3** — the `xfail` is removed and the assertion strengthened from "not the
    old token" to the exact account. Ledger entry:
    2 / 2 / 1 / 1 / 0 / `{owner_has_no_occurrences: 1}` / `partial`. The unchecked gate is
    `vacuous_gate` (`model.sysml:14`), asserted on a `part def` nothing instantiates.

    This is spec success criterion 3 through a real executed package: every gate that ran
    passed, and full satisfaction is still unclaimable.
    """
    report = _execute("constraint_domain_detached_owner", "partial_probe", tmp_path).outputs[
        REPORT_CH
    ]
    assert report.headline == "partial_coverage"
    assert report.coverage.model_dump() == {
        "authored_usage_total": 2,
        "applicable_gate_total": 2,
        "assessed_gate_count": 1,
        "unassessed_gate_count": 1,
        "inapplicable_gate_count": 0,
        "unassessed_reasons": {"owner_has_no_occurrences": 1},
        "coverage_state": "partial",
    }
    assert [r.status for r in report.results] == ["satisfied"]


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
