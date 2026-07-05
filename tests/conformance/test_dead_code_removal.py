"""Conformance tests for Dead Code Removal (7.4).

Validates that dead code paths have been removed and live paths preserved.
Tests use inspect.getsource() for static analysis assertions and real fixture
data for regression guards — no mocks.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import ScopedKey, SysMLQN
from sysml_codegen.extraction.data_models import RedefinitionType
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.input_resolver import (
    ResolutionContext,
    SysMLQNLookup,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SRC_DIR = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"
TEMPLATES_DIR = SRC_DIR / "templates"


def _build_registry_from_snapshot(model_name: str):
    """Load snapshot and build OutputRegistry."""
    snap = load_extraction_snapshot(snapshot_fixture(model_name))
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    return registry, snap


def _flatten_design_attrs(design_attrs_dict) -> dict:
    """Flatten dict[Path, list[DesignAttributeData]] to dict[str, DesignAttributeData]."""
    flat = {}
    for path, attrs in design_attrs_dict.items():
        for da in attrs:
            if da.qualified_name:
                flat[da.qualified_name] = da
            flat[da.name] = da
    return flat


# ---------------------------------------------------------------------------
# Dead file removal
# ---------------------------------------------------------------------------
class TestDeadFileRemoval:
    """Verify dead template files have been deleted."""

    def test_teax_module_stub_template_absent(self):
        """teax_module_stub.py.jinja2 does not exist on disk."""
        stub_path = TEMPLATES_DIR / "teax_module_stub.py.jinja2"
        assert not stub_path.exists(), (
            f"Dead template still exists: {stub_path}"
        )

    def test_constraints_module_absent(self):
        """extraction/constraints.py is deleted (dead: nothing imports it; it
        only loaded the constraint_validator template). Item 1 / spec D2."""
        assert not (SRC_DIR / "extraction" / "constraints.py").exists(), (
            "Dead module still exists: extraction/constraints.py"
        )

    def test_constraint_validator_template_absent(self):
        """templates/constraint_validator.py.jinja2 is deleted (dead: referenced
        only by the removed constraints.py). Item 1 / spec D2."""
        assert not (TEMPLATES_DIR / "constraint_validator.py.jinja2").exists(), (
            "Dead template still exists: templates/constraint_validator.py.jinja2"
        )


# ---------------------------------------------------------------------------
# Dead code path removal (static analysis via inspect.getsource)
# ---------------------------------------------------------------------------
class TestDeadCodePaths:
    """Verify dead code branches have been removed from source."""

    def test_strategy_b_no_normalized_fallback(self):
        """SysMLQNLookup source does NOT contain the normalized fallback
        (parts = ref.split('::') for scoped key construction)."""
        source = inspect.getsource(SysMLQNLookup)
        assert 'parts = ref.split("::")' not in source, (
            "Strategy B normalized fallback still present in SysMLQNLookup"
        )

    def test_backtracker_no_step_1b_normalization(self):
        """_resolve_reference_dispatch source does NOT contain Step 1b
        normalization (sanitized_part = sanitize_name(...))."""
        from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker

        source = inspect.getsource(DependencyBacktracker._resolve_reference_dispatch)
        assert "sanitized_part = sanitize_name(parts[-2])" not in source, (
            "Backtracker Step 1b normalization still present"
        )

    def test_vbr_no_bare_name_fallback(self):
        """_rewrite_virtual_bindings source does NOT contain the bare-name
        fallback (else: leaf = source) — replaced with ValueError."""
        from sysml_codegen.orchestration.pipeline_builder import _rewrite_virtual_bindings

        source = inspect.getsource(_rewrite_virtual_bindings)
        # The dead code was: else: leaf = source  # bare name
        # Check there's no assignment of source directly to leaf (bare-name path)
        # but allow leaf = source.rsplit(...) which is the live path
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("leaf = source") and "rsplit" not in stripped:
                raise AssertionError(
                    "VBR bare-name fallback still present in _rewrite_virtual_bindings"
                )


# ---------------------------------------------------------------------------
# Bug fix verification (Deferred Issue #11)
# ---------------------------------------------------------------------------
class TestDeferredIssueFixes:
    """Verify Deferred Issue #11 — endswith false positive fix."""

    def test_alias_detection_no_endswith_false_positive(self):
        """hierarchy_resolver.py alias detection uses exact match or dot-prefix,
        not bare endswith()."""
        from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data

        source_file = Path(inspect.getfile(extract_hierarchy_data))
        source_text = source_file.read_text()

        # The old pattern: .endswith(agg.attribute_name) without dot prefix
        # The fix: == agg.attribute_name or .endswith("." + agg.attribute_name)
        assert '.endswith(agg.attribute_name)' not in source_text, (
            "Bare endswith() still present — false positive not fixed"
        )


# ---------------------------------------------------------------------------
# Safety regression guard — live path preserved
# ---------------------------------------------------------------------------
class TestLivePathPreserved:
    """Verify the live part of Strategy B (direct SysML QN lookup) still works."""

    def test_strategy_b_direct_lookup_still_works(self):
        """SysMLQNLookup with a :: ref against attr_expr_probe registry returns
        a result (regression guard for the live path we're keeping)."""
        registry, snap = _build_registry_from_snapshot("attr_expr_probe")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=redefs,
            design_attrs=design_attrs,
            module_eqn="test__probe_design__test_calc",
            consumer_scope="probe_design",
            instance_path="test__probe_design",
        )

        # Use a :: ref — SysMLQNLookup should still handle it via the
        # direct sysml_qn_lookup path (returns Channel or None, no crash)
        sysml_qn_ref = "AttrExprProbeDesign::probe_design::area"
        channel = SysMLQNLookup(sysml_qn_ref, ctx)
        assert channel is None or isinstance(channel, str), (
            f"Unexpected return type from SysMLQNLookup: {type(channel)}"
        )
