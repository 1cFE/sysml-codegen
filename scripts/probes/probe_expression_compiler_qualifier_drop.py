"""Dry run: what a pure `Exact`-qualifier drop would do to rows L-281 and L-284.

The Gate 4A carried-input note describes each retained 3C dual as "one behavior under two
names" and prescribes "delete the legacy member and drop the `Exact` qualifier from the
survivor". This probe checks that description against the expression compiler's three duals
before the rename is scheduled, by rebinding the legacy names to the survivors inside the
module the tests import from — which is exactly what the rename leaves behind — and running
the two affected test modules against it.

The measurement, not the argument, is the point: run it and read the failure classes.

    python scripts/probes/probe_expression_compiler_qualifier_drop.py

Recorded output at Gate 4C part 7 chunk 12 (2026-08-11): 48 passed, 26 failed, 5 errors.
Node list archived at
`.project/active/cutover-recovery/evidence/expression-compiler-qualifier-drop-dryrun.txt`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import sysml_codegen.extraction.expression_compiler as compiler  # noqa: E402

compiler.CompilationResult = compiler.ExactCompilationResult
compiler.CalcDefCompilationResult = compiler.ExactCalcDefCompilationResult
compiler.compile_calc_def = compiler.compile_calc_def_exact

raise SystemExit(
    pytest.main(
        [
            "-q",
            "tests/unit/test_expression_compiler.py",
            "tests/conformance/test_expression_compiler.py",
            "-p",
            "no:cacheprovider",
        ]
    )
)
