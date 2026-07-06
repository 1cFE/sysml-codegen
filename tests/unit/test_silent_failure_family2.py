"""Family 2 — Gated-report silences / zero-found sentinels (PIPELINE-TRUTH Item 5).

D3-4 surfaces the discarded usage-extraction report; D3-13 gives the phantom
catalog a "scanned N, skipped K" sentinel so a broken scan is distinguishable from
a clean one. Both use the Item-4 house style: always-present INFO summary + WARN
only when there is a real gap (INV-6: clean stays zero-WARNING). Expectations are
anchored to constructed inputs, never computed by the code under test (R1).
"""

from __future__ import annotations

import logging

from sysml_codegen.extraction.usage_extractor import CalcUsageData, ExtractionReport


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


# --- D3-4: the usage-extraction report is rendered, not discarded ---------------


def test_d34_report_with_warnings_surfaces_each(caplog):
    from sysml_codegen.orchestration.pipeline_builder import _render_extraction_report

    report = ExtractionReport(
        total_usages=3,
        total_bindings=2,
        unbound_params=1,
        cross_file_bindings=0,
        warnings=["dropped usage 'foo'", "unresolved calc def 'Bar'"],
    )
    with caplog.at_level(logging.INFO):
        _render_extraction_report(report)
    warns = _warns(caplog)
    assert any("dropped usage 'foo'" in w for w in warns), warns
    assert any("unresolved calc def 'Bar'" in w for w in warns), warns
    # always-present summary INFO
    assert any("Usage extraction:" in r.message for r in caplog.records)


def test_d34_clean_report_no_warn(caplog):
    from sysml_codegen.orchestration.pipeline_builder import _render_extraction_report

    report = ExtractionReport(
        total_usages=2, total_bindings=2, unbound_params=0,
        cross_file_bindings=0, warnings=[],
    )
    with caplog.at_level(logging.INFO):
        _render_extraction_report(report)
    assert _warns(caplog) == []  # INV-6: no warnings on a clean report
    assert any("Usage extraction:" in r.message for r in caplog.records)


# --- D3-13: phantom catalog zero-found sentinel ---------------------------------


def _usage(calc_def_name: str) -> CalcUsageData:
    return CalcUsageData(
        instance_name="inst",
        calc_def_name=calc_def_name,
        calc_def_qualified_name=calc_def_name,
        module_type=f"{calc_def_name}Module",
    )


def test_d313_unknown_calc_def_warns_catalog_blind(caplog):
    """A usage whose calc def is missing is silently omitted from the catalog —
    a broken scan that would read as 'no phantoms'. The sentinel WARNs on it."""
    from sysml_codegen.analysis.phantom_detector import PhantomDetector

    with caplog.at_level(logging.INFO):
        PhantomDetector(all_usages=[_usage("MissingDef")], calc_defs=[])
    warns = _warns(caplog)
    assert any("unknown calc def" in w for w in warns), warns
    assert any("Phantom catalog: scanned" in r.message for r in caplog.records)


def test_d313_all_known_no_warn(caplog):
    """When every usage's calc def is present, only the INFO summary logs — no
    WARN (INV-6). A calc def with a matching name and no outputs is enough."""
    from types import SimpleNamespace

    from sysml_codegen.analysis.phantom_detector import PhantomDetector

    calc_def = SimpleNamespace(name="KnownDef", output_attributes=[])
    with caplog.at_level(logging.INFO):
        PhantomDetector(all_usages=[_usage("KnownDef")], calc_defs=[calc_def])
    assert _warns(caplog) == []
    assert any("Phantom catalog: scanned" in r.message for r in caplog.records)
