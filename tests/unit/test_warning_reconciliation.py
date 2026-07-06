"""Warning reconciliation: zero-WARNING clean fixtures + alias count-summary.

Item 7 / D5 / INV-5. After the matcher fixes and the Step-4 → DEBUG demotion,
clean fixtures generate with zero WARNING lines, and catf_mfe's ~25 per-collision
alias lines collapse to a single WARNING count-summary.

Scope (C1 / DEV-3): strict zero-WARNING applies to attr_expr_probe, sample_model,
chain_spike (no known cross-part gap). solar_battery emits two out-of-scope
WARNINGs this item does not own (EXPOSE_PURE misc_hardware_cost; module-class
collisions), so its assertion is scoped to *this item's* categories.

Real extraction snapshots — no mocks (R1).
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import snapshot_fixture


def _run(tmp_path, fixture: str) -> bool:
    config = GenerationConfig(
        output_path=tmp_path,
        from_snapshot=snapshot_fixture(fixture),
        package_name="wr",
        overwrite=True,
    )
    return run_codegen(config)


def _warning_messages(caplog) -> list[str]:
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


@pytest.mark.parametrize("fixture", ["attr_expr_probe", "sample_model", "chain_spike_model"])
def test_clean_fixture_zero_warnings(fixture, tmp_path, caplog):
    """A clean fixture generates with zero WARNING lines (INV-5).

    Its fell-through EPs (if any) carry values (not valueless), so no V11, no
    reconciliation summary; the per-binding Step-4 lines are DEBUG.
    """
    with caplog.at_level(logging.WARNING):
        assert _run(tmp_path, fixture) is True, f"{fixture} should generate cleanly"
    assert _warning_messages(caplog) == [], (
        f"{fixture} emitted WARNING lines: {_warning_messages(caplog)}"
    )


def test_solar_battery_zero_warnings_in_item7_categories(tmp_path, caplog):
    """solar_battery is silent in THIS item's warning categories (DEV-3).

    Out-of-scope WARNINGs (EXPOSE_PURE misc_hardware_cost, module-class
    collisions) are owned elsewhere and intentionally NOT silenced.
    """
    with caplog.at_level(logging.WARNING):
        assert _run(tmp_path, "solar_battery_model") is True
    warns = _warning_messages(caplog)
    assert not any("Registry unresolved" in m for m in warns), (
        "per-binding Step-4 line must be DEBUG, not WARNING"
    )
    assert not any("Unresolved after assembly" in m for m in warns), (
        "no reconciliation summary — solar's fell-through EPs are all valued"
    )
    assert not any("alias collision" in m for m in warns), (
        "solar has no alias collisions — no per-line and no summary"
    )


def test_alias_collisions_collapse_to_one_summary(tmp_path, caplog):
    """catf_mfe's per-collision alias lines collapse to one WARNING summary.

    Generation aborts with V11 (magnet_volume gap), but the registry — and its
    alias count-summary — is built before the boundary check, so the summary is
    logged regardless. The per-collision lines are DEBUG.
    """
    with caplog.at_level(logging.WARNING):
        # Returns False (V11 abort); the alias summary logs during registry build.
        _run(tmp_path, "catf_mfe_model")
    warns = _warning_messages(caplog)
    alias_lines = [m for m in warns if "alias collision" in m]
    assert len(alias_lines) == 1, (
        f"expected exactly one alias count-summary, got: {alias_lines}"
    )
    assert alias_lines[0].startswith("OutputRegistry:"), alias_lines[0]
    assert "resolved first-wins" in alias_lines[0], alias_lines[0]
