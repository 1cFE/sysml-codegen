"""Dry run: what an `identified`-qualifier drop would do to the four agentic-mbse duals.

Same method as `probe_expression_compiler_qualifier_drop.py`, applied to the duals the Gate
4A carried-input note describes the same way — "one behavior under two names", to be retired
by "delete the legacy member and drop the qualifier from the survivor". The four live in
rows L-036 (`extract_identified_constraint_facts` / `extract_constraint_facts`) and L-037
(`evaluate_identified_profile` / `evaluate_profile`, `IdentifiedProfileResult` /
`ProfileResult`, `preflight_identified` / `preflight`).

The probe rebinds one legacy name at a time to its survivor, inside both the defining module
and the `agentic_mbse.sysml` package that re-exports it — which is exactly what the rename
leaves behind — and runs the consumers against it. One dual per run, so the failure classes
attribute to a single rename rather than to the pile.

    python scripts/probes/probe_constraint_profile_qualifier_drop.py <dual>

where <dual> is one of: facts, profile, result, preflight, all.

Runs in the paired worktree (`/home/reid/1cfe/agentic-mbse-item7-rebuild`), because the
consumers under measurement are that repo's own suites plus validation levels 4 and 6.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PAIR = Path("/home/reid/1cfe/agentic-mbse-item7-rebuild")

DUALS = {
    # legacy name -> survivor name, per module
    "facts": (
        "constraint_extraction",
        "extract_constraint_facts",
        "extract_identified_constraint_facts",
    ),
    "profile": ("executable_profile", "evaluate_profile", "evaluate_identified_profile"),
    "result": ("executable_profile", "ProfileResult", "IdentifiedProfileResult"),
    "preflight": ("executable_profile", "preflight", "preflight_identified"),
}

CONSUMERS = [
    "tests/test_sysml/test_constraint_extraction.py",
    "tests/test_sysml/test_constraint_extraction_ordering.py",
    "tests/test_sysml/test_constraint_fact_shapes.py",
    "tests/test_sysml/test_executable_profile.py",
    "tests/test_sysml/test_executable_profile_v3.py",
    "tests/test_sysml/test_executable_profile_v4.py",
    "tests/test_sysml/test_executable_profile_arithmetic.py",
    "tests/test_sysml/test_expression_ir_extraction.py",
    "tests/test_sysml/test_public_api_exports.py",
    "tests/test_validation/test_level4_reconciliation.py",
    "tests/test_validation/test_item12_checks.py",
]


def main() -> int:
    selected = sys.argv[1] if len(sys.argv) > 1 else "all"
    names = list(DUALS) if selected == "all" else [selected]
    if any(name not in DUALS for name in names):
        raise SystemExit(f"unknown dual {selected!r}; pick one of {', '.join(DUALS)} or 'all'")

    sys.path.insert(0, str(PAIR / "src"))
    os.chdir(PAIR)

    import agentic_mbse.sysml as package
    import agentic_mbse.sysml.constraint_extraction as constraint_extraction
    import agentic_mbse.sysml.executable_profile as executable_profile

    modules = {
        "constraint_extraction": constraint_extraction,
        "executable_profile": executable_profile,
    }
    for name in names:
        module_name, legacy, survivor = DUALS[name]
        module = modules[module_name]
        setattr(module, legacy, getattr(module, survivor))
        if hasattr(package, legacy):
            setattr(package, legacy, getattr(module, survivor))

    return pytest.main(["-q", *CONSUMERS, "-p", "no:cacheprovider"])


if __name__ == "__main__":
    raise SystemExit(main())
