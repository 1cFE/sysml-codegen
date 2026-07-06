"""D3-4: the usage-extraction report is DISCARDED on the live path.

pipeline_builder.py: ``calc_usages, _report = extract_calculation_usages(...)``.
The ExtractionReport (and its ``warnings`` list) is thrown away. When a
CalculationUsage fails to resolve its calc def, ``_extract_single_usage``
appends "Could not resolve calc def for usage '<name>'" to that report's
warnings AND returns None (usage_extractor.py ~580-582) — the usage is dropped
from the pipeline. Because the report is discarded, the drop is silent.

This probe loads a REAL fixture, forces calc-def resolution to fail (monkeypatch
``get_calc_def_name`` -> ""), and shows: (a) every usage is dropped, (b) the
report.warnings hold the only record of it, (c) NOTHING is logged at WARNING.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _caplog import capture_all  # noqa: E402

from sysml_codegen.extraction import usage_extractor  # noqa: E402
from sysml_codegen.extraction.extractor import SysMLDataExtractor  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "solar_battery_model"


def main() -> None:
    print("=" * 72)
    print("D3-4: discarded ExtractionReport -> silent usage drop")
    print("=" * 72)
    print(f"fixture: {FIXTURE}")

    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models(), "model failed to load"
    calc_defs = extractor.extract_calculation_definitions()
    model = extractor.model

    # Baseline: how many CalculationUsage elements exist in the model?
    from agentic_mbse.sysml.syside_adapter import SysideAdapter
    n_elems = len(list(SysideAdapter.elements_of_type(model, "CalculationUsage")))
    print(f"\nCalculationUsage elements in model: {n_elems}")

    # Force calc-def resolution to fail for every usage (simulates an unresolved
    # / renamed / missing calc def — the exact condition at usage_extractor ~580).
    orig = usage_extractor.get_calc_def_name
    usage_extractor.get_calc_def_name = lambda elem: ""  # type: ignore[assignment]

    sink, _ = capture_all()
    try:
        calc_usages, report = usage_extractor.extract_calculation_usages(
            model, calc_defs=calc_defs
        )
    finally:
        usage_extractor.get_calc_def_name = orig  # type: ignore[assignment]

    print("\n--- OBSERVED ---")
    print(f"usages surviving into pipeline : {len(calc_usages)}  (dropped: {n_elems})")
    print(f"report.warnings count          : {len(report.warnings)}")
    if report.warnings:
        print(f"  sample warning: {report.warnings[0]!r}")

    warn_records = sink.at_or_above(logging.WARNING)
    resolve_logs = sink.containing("could not resolve calc def")
    print(f"log records at >= WARNING      : {len(warn_records)}")
    print(f"log records mentioning drop    : {len(resolve_logs)}")

    # Confirm the discard site statically.
    pb = (FIXTURE.parents[2] / "src" / "sysml_codegen" / "orchestration"
          / "pipeline_builder.py").read_text()
    discard_line = next(
        (ln.strip() for ln in pb.splitlines()
         if "extract_calculation_usages(" in ln and "_report" in ln),
        "<not found>",
    )
    print(f"\npipeline_builder discard site  : {discard_line}")

    print("\n--- VERDICT ---")
    silent = len(calc_usages) == 0 and len(report.warnings) > 0 and len(resolve_logs) == 0
    if silent:
        print("CONFIRMED: all usages dropped; the ONLY record lives in the discarded")
        print("report.warnings; zero WARNING-level log surfaces to the user.")
    else:
        print("NOT-REPRODUCED: see numbers above.")


if __name__ == "__main__":
    main()
