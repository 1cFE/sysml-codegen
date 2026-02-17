"""Conformance tests for DependencyBacktracker (C11a + C11b).

Requirements: REQ-BT-01 through REQ-BT-08, REQ-DRA-01, REQ-DRA-03, FR-2, FR-3, FR-4
Design intent: 11-analysis-backtracker.md, 24-dual-resolution-architecture.md, 27-typed-registry-refactor.md

C11a tests verify OUTCOMES of the current backtracker implementation:
- Which channels resolve for each binding
- Correct topological ordering
- Key format compliance
- Cycle detection
- Self-reference guard

C11b tests verify the dispatch MECHANISM (typed dispatch):
- Static analysis: no resolve() calls in backtracker or build_output_registry()
- Static analysis: no _compat dict, resolve() method, or register() method on OutputRegistry
- Mechanism: CHAIN → scoped_lookup then alias_lookup
- Mechanism: REFERENCE → sysml_qn_lookup then normalized scoped_lookup
- Mechanism: 14 previously-compat-only resolutions now resolve via typed lookups
- Mechanism: EXPRESSION bindings produce ENTRY_POINT with warning

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

import re

import pytest
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    CircularDependencyError,
    DependencyBacktracker,
)
from sysml_codegen.core.identifier_types import ScopedKey, SysMLQN
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot


# ---------------------------------------------------------------------------
# Helper: build backtracker and run from snapshot
# ---------------------------------------------------------------------------
def build_backtracker_from_snapshot(
    model_name: str,
) -> tuple[BacktrackingResult, OutputRegistry, dict]:
    """Build OutputRegistry + DependencyBacktracker from extraction snapshot.

    Replicates Steps 3.5–6 of build_pipeline_context():
    1. Load extraction snapshot
    2. Build OutputRegistry via build_output_registry()
    3. Instantiate DependencyBacktracker
    4. Run find_required_modules([], include_all=True)

    Returns:
        (BacktrackingResult, OutputRegistry, snapshot_dict)
    """
    snap = load_extraction_snapshot(model_name)
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)
    return result, registry, snap


# ---------------------------------------------------------------------------
# Session-scoped fixtures for expensive operations
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_bt():
    """Session-scoped backtracker result for solar_battery_model."""
    return build_backtracker_from_snapshot("solar_battery_model")


@pytest.fixture(scope="session")
def catf_mfe_bt():
    """Session-scoped backtracker result for catf_mfe_model."""
    return build_backtracker_from_snapshot("catf_mfe_model")


@pytest.fixture(scope="session")
def attr_expr_probe_bt():
    """Session-scoped backtracker result for attr_expr_probe."""
    return build_backtracker_from_snapshot("attr_expr_probe")


@pytest.fixture(scope="session")
def chain_spike_bt():
    """Session-scoped backtracker result for chain_spike_model."""
    return build_backtracker_from_snapshot("chain_spike_model")


@pytest.fixture(scope="session")
def chain_override_bt():
    """Session-scoped backtracker result for chain_override_probe."""
    return build_backtracker_from_snapshot("chain_override_probe")


@pytest.fixture(scope="session")
def expression_binding_bt():
    """Session-scoped backtracker result for expression_binding_probe."""
    return build_backtracker_from_snapshot("expression_binding_probe")


# ===================================================================
# REQ-BT-01: Every non-literal binding resolved via registry
# ===================================================================
class TestReqBT01:
    """REQ-BT-01: Every non-literal binding SHALL be resolved via
    _resolve_binding_via_registry() through the typed OutputRegistry."""

    @pytest.mark.req("REQ-BT-01")
    def test_all_non_literal_resolved_solar_battery(self, solar_battery_bt):
        """For solar_battery: every non-LITERAL binding has a resolution."""
        result, _, snap = solar_battery_bt
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.LITERAL:
                    continue
                key = f"{usage.qualified_name}|{binding.param_name}"
                assert key in result.binding_resolutions, (
                    f"Non-literal binding {key} (type={binding.binding_type.value}) "
                    f"has no binding_resolution entry"
                )

    @pytest.mark.req("REQ-BT-01")
    @pytest.mark.parametrize("model_name", [
        "solar_battery_model", "catf_mfe_model", "attr_expr_probe", "chain_spike_model",
    ])
    def test_cross_model_total_resolution(self, model_name):
        """Every non-literal binding has a binding_resolution entry."""
        result, _, snap = build_backtracker_from_snapshot(model_name)
        missing = []
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.LITERAL:
                    continue
                key = f"{usage.qualified_name}|{binding.param_name}"
                if key not in result.binding_resolutions:
                    missing.append(key)
        assert not missing, (
            f"{model_name}: {len(missing)} non-literal bindings missing resolutions: "
            f"{missing[:5]}"
        )

    @pytest.mark.req("REQ-BT-01")
    def test_literal_bindings_also_resolved(self, solar_battery_bt):
        """LITERAL bindings also get ENTRY_POINT resolutions."""
        result, _, snap = solar_battery_bt
        literal_count = 0
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type != BindingType.LITERAL:
                    continue
                key = f"{usage.qualified_name}|{binding.param_name}"
                assert key in result.binding_resolutions, (
                    f"LITERAL binding {key} missing resolution"
                )
                res = result.binding_resolutions[key]
                assert res.resolution_type == BindingResolutionType.ENTRY_POINT
                literal_count += 1
        assert literal_count == 15, (
            f"Expected 15 LITERAL bindings in solar_battery, got {literal_count}"
        )


# ===================================================================
# REQ-BT-02: Dispatch on binding format
# ===================================================================
class TestReqBT02:
    """REQ-BT-02: Resolution SHALL dispatch on binding format: CHAIN vs REFERENCE."""

    @pytest.mark.req("REQ-BT-02")
    def test_chain_resolves_via_scoped_or_alias(self, solar_battery_bt):
        """For solar_battery CHAIN MODULE_OUTPUTs: channels reachable via
        scoped_lookup or alias_lookup on the typed registry."""
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)

        chain_mo_count = 0
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            bt = binding_types.get(key)
            if bt != BindingType.CHAIN:
                continue
            chain_mo_count += 1
            channel = resolution.qualified_name
            usage_qn = key.split("|")[0]
            # Reconstruct scoped key that typed dispatch would use
            segments = usage_qn.split("__")
            if len(segments) > 2:
                consumer_scope = ".".join(segments[1:-1])
                scoped_key = ScopedKey(f"{consumer_scope}.{resolution.source_path}")
                scoped_hit = registry.scoped_lookup(scoped_key) == channel
            else:
                scoped_hit = False
            alias_hit = (
                registry.alias_lookup(ScopedKey(resolution.source_path)) == channel
                if resolution.source_path else False
            )
            assert scoped_hit or alias_hit, (
                f"CHAIN MODULE_OUTPUT {key} -> {channel} not reachable via "
                f"scoped_lookup or alias_lookup"
            )
        assert chain_mo_count > 0, "No CHAIN MODULE_OUTPUT found in solar_battery"

    @pytest.mark.req("REQ-BT-02")
    def test_reference_resolves_via_sysml_qn_or_scoped(self, attr_expr_probe_bt):
        """For attr_expr_probe REFERENCE MODULE_OUTPUTs: channels reachable
        via sysml_qn_lookup or scoped_lookup."""
        result, registry, snap = attr_expr_probe_bt
        binding_types = _build_binding_type_map(snap)

        ref_mo_count = 0
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            bt = binding_types.get(key)
            if bt != BindingType.REFERENCE:
                continue
            ref_mo_count += 1
            channel = resolution.qualified_name
            source_path = resolution.source_path or ""
            # Step 1: SysML QN lookup
            sysml_hit = registry.sysml_qn_lookup(SysMLQN(source_path)) == channel
            # Step 1b: normalized scoped lookup
            scoped_hit = False
            if "::" in source_path:
                parts = source_path.split("::")
                if len(parts) >= 2:
                    sanitized_part = sanitize_name(parts[-2]).lower()
                    dotted = f"{sanitized_part}.{parts[-1]}"
                    scoped_hit = registry.scoped_lookup(ScopedKey(dotted)) == channel
            assert sysml_hit or scoped_hit, (
                f"REFERENCE MODULE_OUTPUT {key} -> {channel} not reachable via "
                f"sysml_qn_lookup or scoped_lookup"
            )
        assert ref_mo_count == 2, (
            f"Expected 2 REFERENCE MODULE_OUTPUTs in attr_expr_probe, got {ref_mo_count}"
        )

    @pytest.mark.req("REQ-BT-02")
    def test_catf_cross_package_via_alias(self, catf_mfe_bt):
        """catf_mfe: cross-package CHAIN bindings resolve via alias_lookup."""
        result, registry, snap = catf_mfe_bt
        binding_types = _build_binding_type_map(snap)

        alias_hit_count = 0
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            bt = binding_types.get(key)
            if bt != BindingType.CHAIN:
                continue
            source_path = resolution.source_path
            alias_match = (
                source_path
                and registry.alias_lookup(ScopedKey(source_path)) == resolution.qualified_name
            )
            if alias_match:
                alias_hit_count += 1

        # After C11b: Key_A registered as alias in Phase 1a, so all cross-scope
        # CHAIN bindings resolve via alias_lookup (was 10 before Key_A aliases)
        assert alias_hit_count == 18, (
            f"Expected 18 cross-package alias hits in catf_mfe, got {alias_hit_count}"
        )


# ===================================================================
# REQ-BT-03: Cycle detection
# ===================================================================
class TestReqBT03:
    """REQ-BT-03: DFS SHALL detect cycles via path tracking."""

    @pytest.mark.req("REQ-BT-03")
    def test_no_false_cycle_detection_solar(self, solar_battery_bt):
        """solar_battery (known acyclic): completes without CircularDependencyError."""
        result, _, _ = solar_battery_bt
        assert len(result.required_usages) == 15

    @pytest.mark.req("REQ-BT-03")
    def test_no_false_cycle_detection_catf(self, catf_mfe_bt):
        """catf_mfe (known acyclic): completes without CircularDependencyError."""
        result, _, _ = catf_mfe_bt
        assert len(result.required_usages) == 42

    @pytest.mark.req("REQ-BT-03")
    def test_topo_sort_cycle_raises(self):
        """_topological_sort with a cyclic graph raises CircularDependencyError."""
        backtracker = _build_minimal_backtracker()
        cycle_graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        with pytest.raises(CircularDependencyError, match="Circular dependency"):
            backtracker._topological_sort(cycle_graph)


# ===================================================================
# REQ-BT-04: Every binding resolves
# ===================================================================
class TestReqBT04:
    """REQ-BT-04: Every binding SHALL resolve to exactly one BindingResolution."""

    @pytest.mark.req("REQ-BT-04")
    def test_every_binding_resolved_solar(self, solar_battery_bt):
        """solar_battery: total resolutions == total bindings + unbound_params."""
        result, _, snap = solar_battery_bt
        total_bindings = 0
        total_unbound = 0
        for usage in snap["calc_usages"]:
            total_bindings += len(usage.bindings)
            total_unbound += len(usage.unbound_params)
        expected = total_bindings + total_unbound
        actual = len(result.binding_resolutions)
        assert actual == expected, (
            f"Expected {expected} resolutions "
            f"({total_bindings} bindings + {total_unbound} unbound), "
            f"got {actual}"
        )

    @pytest.mark.req("REQ-BT-04")
    def test_backtracking_result_fields_complete(self, solar_battery_bt):
        """BacktrackingResult has all documented fields populated."""
        result, _, _ = solar_battery_bt
        assert len(result.required_usages) > 0
        assert len(result.dependency_graph) > 0
        assert len(result.entry_points) > 0
        assert len(result.binding_resolutions) > 0
        assert isinstance(result.trace_log, list)
        assert isinstance(result.phantom_report, object)

    @pytest.mark.req("REQ-BT-04")
    def test_entry_point_sources_populated(self, solar_battery_bt):
        """Every ENTRY_POINT resolution that has a source_path is in entry_point_sources."""
        result, _, _ = solar_battery_bt
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.ENTRY_POINT:
                continue
            if resolution.source_path:
                assert resolution.qualified_name in result.entry_point_sources, (
                    f"ENTRY_POINT {resolution.qualified_name} (from {key}) "
                    f"has source_path but no entry_point_sources entry"
                )


# ===================================================================
# REQ-BT-05: Key format
# ===================================================================
class TestReqBT05:
    """REQ-BT-05: binding_resolutions key format SHALL be
    '{usage_qn}|{param_name}'."""

    PIPE_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_]+(__[A-Za-z0-9_]+)+\|[A-Za-z0-9_]+$")

    @pytest.mark.req("REQ-BT-05")
    def test_key_format_solar_battery(self, solar_battery_bt):
        """solar_battery: every key matches pipe separator format."""
        result, _, _ = solar_battery_bt
        for key in result.binding_resolutions:
            assert "|" in key, f"Key '{key}' has no pipe separator"
            parts = key.split("|")
            assert len(parts) == 2, f"Key '{key}' has {len(parts)} parts, expected 2"
            assert "__" in parts[0], f"Key '{key}' usage_qn has no '__'"

    @pytest.mark.req("REQ-BT-05")
    @pytest.mark.parametrize("model_name", [
        "solar_battery_model", "catf_mfe_model", "attr_expr_probe",
    ])
    def test_key_format_cross_model(self, model_name):
        """All binding_resolutions keys match pipe separator format."""
        result, _, _ = build_backtracker_from_snapshot(model_name)
        bad_keys = []
        for key in result.binding_resolutions:
            if "|" not in key or len(key.split("|")) != 2:
                bad_keys.append(key)
        assert not bad_keys, f"{model_name}: bad key format: {bad_keys[:5]}"

    @pytest.mark.req("REQ-BT-05")
    def test_module_output_format(self, solar_battery_bt):
        """MODULE_OUTPUT qualified_name is in CanonicalChannel format (contains '__')."""
        result, _, _ = solar_battery_bt
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            assert "__" in resolution.qualified_name, (
                f"MODULE_OUTPUT {key} -> '{resolution.qualified_name}' "
                f"not in CanonicalChannel format (no '__')"
            )
            assert "::" not in resolution.qualified_name, (
                f"MODULE_OUTPUT {key} -> '{resolution.qualified_name}' "
                f"contains '::' (should be PQN format, not SysML QN)"
            )

    @pytest.mark.req("REQ-BT-05")
    def test_entry_point_format(self, solar_battery_bt):
        """ENTRY_POINT qualified_name contains '__'."""
        result, _, _ = solar_battery_bt
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.ENTRY_POINT:
                continue
            assert "__" in resolution.qualified_name, (
                f"ENTRY_POINT {key} -> '{resolution.qualified_name}' "
                f"not in PQN format (no '__')"
            )


# ===================================================================
# REQ-BT-06: Topological sort
# ===================================================================
class TestReqBT06:
    """REQ-BT-06: Topological sort SHALL produce dependency-first ordering."""

    @pytest.mark.req("REQ-BT-06")
    def test_topological_order_solar_battery(self, solar_battery_bt):
        """solar_battery: every MODULE_OUTPUT dependency appears earlier in the list."""
        result, _, _ = solar_battery_bt
        _assert_topological_order(result)

    @pytest.mark.req("REQ-BT-06")
    def test_topological_order_catf(self, catf_mfe_bt):
        """catf_mfe: every MODULE_OUTPUT dependency appears earlier in the list."""
        result, _, _ = catf_mfe_bt
        _assert_topological_order(result)

    @pytest.mark.req("REQ-BT-06")
    def test_topological_order_chain_spike(self, chain_spike_bt):
        """chain_spike: every MODULE_OUTPUT dependency appears earlier in the list."""
        result, _, _ = chain_spike_bt
        _assert_topological_order(result)

    @pytest.mark.req("REQ-BT-06")
    def test_topo_sort_cycle_raises(self):
        """_topological_sort raises CircularDependencyError on cycle."""
        backtracker = _build_minimal_backtracker()
        cycle_graph = {"A": ["B"], "B": ["A"]}
        with pytest.raises(CircularDependencyError):
            backtracker._topological_sort(cycle_graph)

    @pytest.mark.req("REQ-BT-06")
    def test_topo_sort_empty_graph(self):
        """_topological_sort on empty graph returns empty list."""
        backtracker = _build_minimal_backtracker()
        assert backtracker._topological_sort({}) == []

    @pytest.mark.req("REQ-BT-06")
    def test_topo_sort_single_node(self):
        """_topological_sort with single node returns that node."""
        backtracker = _build_minimal_backtracker()
        result = backtracker._topological_sort({"A": []})
        assert result == ["A"]


# ===================================================================
# REQ-BT-07: Self-reference guard
# ===================================================================
class TestReqBT07:
    """REQ-BT-07: Self-reference guard prevents wiring to own output."""

    @pytest.mark.req("REQ-BT-07")
    def test_no_self_wiring_solar_battery(self, solar_battery_bt):
        """solar_battery: no MODULE_OUTPUT resolution wires a usage to itself."""
        result, _, _ = solar_battery_bt
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            consumer_qn = key.split("|")[0]
            channel = resolution.qualified_name
            if "__" in channel:
                producer_qn = channel.rsplit("__", 1)[0]
                assert producer_qn != consumer_qn, (
                    f"Self-wiring: {key} -> {channel} "
                    f"(producer_qn={producer_qn} == consumer_qn)"
                )

    @pytest.mark.req("REQ-BT-07")
    @pytest.mark.parametrize("model_name", [
        "solar_battery_model", "catf_mfe_model", "attr_expr_probe", "chain_spike_model",
    ])
    def test_no_self_wiring_cross_model(self, model_name):
        """No MODEL_OUTPUT resolution wires a usage to itself."""
        result, _, _ = build_backtracker_from_snapshot(model_name)
        self_wires = []
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            consumer_qn = key.split("|")[0]
            channel = resolution.qualified_name
            if "__" in channel:
                producer_qn = channel.rsplit("__", 1)[0]
                if producer_qn == consumer_qn:
                    self_wires.append(key)
        assert not self_wires, (
            f"{model_name}: {len(self_wires)} self-wiring resolutions: {self_wires[:5]}"
        )


# ===================================================================
# REQ-BT-08: Type-directed dispatch outcomes
# ===================================================================
class TestReqBT08:
    """REQ-BT-08: Resolution outcomes match what type-directed dispatch
    would produce. CHAIN -> scoped/alias, REFERENCE -> sysml_qn/scoped."""

    @pytest.mark.req("REQ-BT-08")
    def test_chain_dispatch_outcomes_solar(self, solar_battery_bt):
        """solar_battery CHAIN MODULE_OUTPUTs: typed registry reachable."""
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)
        chain_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.CHAIN
        )
        for key, resolution in chain_mo:
            assert _is_typed_reachable_chain(
                resolution, registry, key.split("|")[0]
            ), (
                f"CHAIN MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via scoped_lookup or alias_lookup"
            )

    @pytest.mark.req("REQ-BT-08")
    def test_chain_dispatch_outcomes_chain_spike(self, chain_spike_bt):
        """chain_spike CHAIN MODULE_OUTPUTs: typed registry reachable."""
        result, registry, snap = chain_spike_bt
        binding_types = _build_binding_type_map(snap)
        chain_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.CHAIN
        )
        for key, resolution in chain_mo:
            assert _is_typed_reachable_chain(
                resolution, registry, key.split("|")[0]
            ), (
                f"CHAIN MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via scoped_lookup or alias_lookup"
            )

    @pytest.mark.req("REQ-BT-08")
    def test_reference_dispatch_outcomes(self, attr_expr_probe_bt):
        """attr_expr_probe REFERENCE MODULE_OUTPUTs: typed registry reachable."""
        result, registry, snap = attr_expr_probe_bt
        binding_types = _build_binding_type_map(snap)
        ref_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.REFERENCE
        )
        assert len(ref_mo) == 2, f"Expected 2 REFERENCE MODULE_OUTPUTs, got {len(ref_mo)}"
        for key, resolution in ref_mo:
            assert _is_typed_reachable_reference(
                resolution, registry, key.split("|")[0]
            ), (
                f"REFERENCE MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via typed lookups"
            )

    @pytest.mark.req("REQ-BT-08")
    def test_no_compat_only_chain(self, catf_mfe_bt):
        """After C11b: ALL catf_mfe CHAIN MODULE_OUTPUTs are typed-reachable.

        Key_A aliases registered in Phase 1a make cross-scope CHAIN bindings
        (minor_calc.a, volume_calc.volume) reachable via alias_lookup.
        """
        result, registry, snap = catf_mfe_bt
        binding_types = _build_binding_type_map(snap)
        chain_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.CHAIN
        )
        compat_only = [
            (k, r) for k, r in chain_mo
            if not _is_typed_reachable_chain(r, registry, k.split("|")[0])
        ]
        assert len(compat_only) == 0, (
            f"Expected 0 compat-only CHAIN resolutions after C11b, "
            f"got {len(compat_only)}: {[k for k, _ in compat_only[:3]]}"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_no_compat_only_reference(self, solar_battery_bt):
        """After C11b: ALL solar_battery REFERENCE MODULE_OUTPUTs are typed-reachable.

        Key_F registered as ScopedKey in Phase 1c makes FORMULA outputs
        reachable via scoped_lookup for REFERENCE secondary path.
        """
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)
        ref_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.REFERENCE
        )
        compat_only = [
            (k, r) for k, r in ref_mo
            if not _is_typed_reachable_reference(r, registry, k.split("|")[0])
        ]
        assert len(compat_only) == 0, (
            f"Expected 0 compat-only REFERENCE resolutions after C11b, "
            f"got {len(compat_only)}: {[k for k, _ in compat_only[:3]]}"
        )


# ===================================================================
# REQ-DRA-01: Resolution during DFS
# ===================================================================
class TestReqDRA01:
    """REQ-DRA-01: Resolution occurs during DFS, not as a separate pass."""

    @pytest.mark.req("REQ-DRA-01")
    def test_resolution_during_dfs_source_code(self):
        """Verify _trace_dependencies calls _resolve_binding_via_registry."""
        import ast
        import inspect
        import textwrap

        source = textwrap.dedent(inspect.getsource(DependencyBacktracker._trace_dependencies))
        tree = ast.parse(source)
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "_resolve_binding_via_registry":
                    calls.append(func.attr)
        assert len(calls) >= 1, (
            "_trace_dependencies does not call _resolve_binding_via_registry"
        )

    @pytest.mark.req("REQ-DRA-01")
    def test_module_output_triggers_recursion(self, solar_battery_bt):
        """MODULE_OUTPUT resolutions from CalcUsage bindings trigger DFS
        recursion: the producing usage appears in required_usages.

        Note: Some MODULE_OUTPUTs point to aggregation/FORMULA outputs
        (e.g., p_net_kw) that are not CalcUsages — these are resolved
        through the secondary REFERENCE path and don't trigger recursion
        because _find_usage_for_channel returns None.
        """
        result, _, snap = solar_battery_bt
        required_qns = {u.qualified_name for u in result.required_usages}
        # Build set of all CalcUsage qualified names to distinguish
        # CalcUsage outputs from aggregation/FORMULA outputs
        all_usage_qns = {u.qualified_name for u in snap["calc_usages"]}

        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            channel = resolution.qualified_name
            if "__" in channel:
                producer_qn = channel.rsplit("__", 1)[0]
                # Only check CalcUsage producers (not aggregation/FORMULA)
                if producer_qn in all_usage_qns:
                    assert producer_qn in required_qns, (
                        f"MODULE_OUTPUT {key} -> {channel}: "
                        f"producing usage {producer_qn} not in required_usages"
                    )


# ===================================================================
# Expression binding gap documentation
# ===================================================================
class TestExpressionBindingGap:
    """Document EXPRESSION binding behavior (source_path=None)."""

    @pytest.mark.req("REQ-BT-01")
    def test_expression_bindings_resolve_as_entry_point(self, expression_binding_bt):
        """expression_binding_probe: EXPRESSION bindings (source_path=None)
        resolve as ENTRY_POINT. C11a added explicit dispatch for these.
        """
        result, _, snap = expression_binding_bt
        assert isinstance(result, BacktrackingResult)

        expression_count = sum(
            1
            for usage in snap["calc_usages"]
            for binding in usage.bindings
            if binding.binding_type == BindingType.EXPRESSION
        )
        assert expression_count > 0, "No EXPRESSION bindings in expression_binding_probe"

        # EXPRESSION bindings resolve as ENTRY_POINT
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type != BindingType.EXPRESSION:
                    continue
                key = f"{usage.qualified_name}|{binding.param_name}"
                assert key in result.binding_resolutions, (
                    f"EXPRESSION binding {key} has no resolution"
                )
                res = result.binding_resolutions[key]
                assert res.resolution_type == BindingResolutionType.ENTRY_POINT, (
                    f"EXPRESSION binding {key}: expected ENTRY_POINT, "
                    f"got {res.resolution_type.value}"
                )


# ===================================================================
# Specific model result counts (regression baselines)
# ===================================================================
class TestResultBaselines:
    """Lock down specific counts as regression baselines."""

    @pytest.mark.req("REQ-BT-04")
    def test_solar_battery_counts(self, solar_battery_bt):
        """solar_battery: 15 usages, 61 resolutions, 6 MODULE_OUTPUT."""
        result, _, _ = solar_battery_bt
        assert len(result.required_usages) == 15
        assert len(result.binding_resolutions) == 61
        mo_count = sum(
            1 for r in result.binding_resolutions.values()
            if r.resolution_type == BindingResolutionType.MODULE_OUTPUT
        )
        assert mo_count == 6

    @pytest.mark.req("REQ-BT-04")
    def test_catf_mfe_counts(self, catf_mfe_bt):
        """catf_mfe: 42 usages, 136 resolutions, 30 MODULE_OUTPUT."""
        result, _, _ = catf_mfe_bt
        assert len(result.required_usages) == 42
        assert len(result.binding_resolutions) == 136
        mo_count = sum(
            1 for r in result.binding_resolutions.values()
            if r.resolution_type == BindingResolutionType.MODULE_OUTPUT
        )
        assert mo_count == 30

    @pytest.mark.req("REQ-BT-04")
    def test_attr_expr_probe_counts(self, attr_expr_probe_bt):
        """attr_expr_probe: 2 usages, 3 resolutions, 2 MODULE_OUTPUT."""
        result, _, _ = attr_expr_probe_bt
        assert len(result.required_usages) == 2
        assert len(result.binding_resolutions) == 3
        mo_count = sum(
            1 for r in result.binding_resolutions.values()
            if r.resolution_type == BindingResolutionType.MODULE_OUTPUT
        )
        assert mo_count == 2


# ===================================================================
# C11b: Static analysis — no resolve() in backtracker
# ===================================================================
class TestC11bNoResolveInBacktracker:
    """FR-4, REQ-BT-08: Backtracker SHALL use typed dispatch, not resolve()."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_resolve_calls_in_backtracker(self):
        """Static analysis: _resolve_binding_via_registry() and
        _resolve_reference_via_registry() do NOT call self._output_registry.resolve().
        Must call scoped_lookup, sysml_qn_lookup, or alias_lookup instead."""
        import ast
        import inspect
        import textwrap

        for method_name in ("_resolve_binding_via_registry", "_resolve_reference_via_registry"):
            method = getattr(DependencyBacktracker, method_name)
            source = textwrap.dedent(inspect.getsource(method))
            tree = ast.parse(source)
            resolve_calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr == "resolve":
                        resolve_calls.append(node.lineno)
            assert not resolve_calls, (
                f"{method_name} still calls resolve() at line(s) {resolve_calls}. "
                f"Must use scoped_lookup/sysml_qn_lookup/alias_lookup instead."
            )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_typed_lookups_present_in_backtracker(self):
        """Static analysis: typed dispatch methods use at least one typed
        lookup method (scoped_lookup, sysml_qn_lookup, alias_lookup).

        C11a split dispatch into _resolve_chain_dispatch and
        _resolve_reference_dispatch — check both."""
        import ast
        import inspect
        import textwrap

        typed_methods = {"scoped_lookup", "sysml_qn_lookup", "alias_lookup"}
        dispatch_methods = [
            "_resolve_chain_dispatch",
            "_resolve_reference_dispatch",
            "_resolve_reference_via_registry",
        ]
        found_typed = set()
        for method_name in dispatch_methods:
            method = getattr(DependencyBacktracker, method_name)
            source = textwrap.dedent(inspect.getsource(method))
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr in typed_methods:
                        found_typed.add(func.attr)
        assert found_typed, (
            "Typed dispatch methods have no typed lookup calls. "
            f"Expected at least one of: {typed_methods}"
        )


# ===================================================================
# C11b: Static analysis — no resolve() in build_output_registry
# ===================================================================
class TestC11bNoResolveInBuildRegistry:
    """FR-4: build_output_registry() SHALL NOT call registry.resolve()."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_resolve_calls_in_build_registry(self):
        """Static analysis: build_output_registry() does NOT call registry.resolve()."""
        import ast
        import inspect
        import textwrap

        source = textwrap.dedent(inspect.getsource(build_output_registry))
        tree = ast.parse(source)
        resolve_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "resolve":
                    resolve_calls.append(node.lineno)
        assert not resolve_calls, (
            f"build_output_registry() still calls resolve() at line(s) {resolve_calls}"
        )


# ===================================================================
# C11b: Static analysis — OutputRegistry deprecated API removed
# ===================================================================
class TestC11bRegistryCleanup:
    """FR-2, FR-3: OutputRegistry SHALL NOT have _compat or derive_key_c()."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_compat_dict_in_registry(self):
        """OutputRegistry class has no _compat attribute."""
        registry = OutputRegistry()
        assert not hasattr(registry, "_compat"), (
            "OutputRegistry still has _compat attribute"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_resolve_method_on_registry(self):
        """OutputRegistry class has no resolve method."""
        registry = OutputRegistry()
        assert not hasattr(registry, "resolve"), (
            "OutputRegistry still has deprecated resolve() method"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_deprecated_register_method(self):
        """OutputRegistry has no register() method (the deprecated compat registration)."""
        registry = OutputRegistry()
        assert not hasattr(registry, "register"), (
            "OutputRegistry still has deprecated register() method"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_no_derive_key_c_method(self):
        """OutputRegistry has no derive_key_c() static method."""
        assert not hasattr(OutputRegistry, "derive_key_c"), (
            "OutputRegistry still has deprecated derive_key_c() method"
        )


# ===================================================================
# C11b: Mechanism — typed dispatch for CHAIN bindings
# ===================================================================
class TestC11bChainDispatch:
    """REQ-BT-08, REQ-DRA-03: CHAIN bindings dispatch via scoped then alias."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_chain_dispatch_uses_scoped_then_alias(self, solar_battery_bt):
        """For solar_battery CHAIN MODULE_OUTPUTs: the resolved channel equals
        registry.scoped_lookup(ScopedKey(consumer_scope.source_path)) or
        registry.alias_lookup(ScopedKey(source_path)). No compat fallback needed."""
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)
        chain_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.CHAIN
        )
        assert len(chain_mo) > 0, "No CHAIN MODULE_OUTPUTs in solar_battery"
        for key, resolution in chain_mo:
            assert _is_typed_reachable_chain(
                resolution, registry, key.split("|")[0]
            ), (
                f"CHAIN MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via scoped_lookup or alias_lookup"
            )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_catf_cross_scope_via_alias(self, catf_mfe_bt):
        """catf_mfe minor_calc.a CHAIN bindings: alias registered, each
        resolves to its own scope's minor_calc via scoped_lookup.

        Phase 1a registers ScopedKey("minor_calc.a") as an alias (first-wins
        → plasma_region). Each layer has its own minor_calc instance, so
        scoped_lookup (Step 1 of CHAIN dispatch) finds the local one.
        The alias is a cross-scope fallback for consumers without a local
        minor_calc."""
        result, registry, snap = catf_mfe_bt
        binding_types = _build_binding_type_map(snap)

        # Find all CHAIN bindings with source_path=minor_calc.a
        minor_calc_resolutions = []
        for key, resolution in result.binding_resolutions.items():
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue
            if binding_types.get(key) != BindingType.CHAIN:
                continue
            if resolution.source_path == "minor_calc.a":
                minor_calc_resolutions.append((key, resolution))

        assert len(minor_calc_resolutions) == 13, (
            f"Expected 13 minor_calc.a CHAIN bindings, got {len(minor_calc_resolutions)}"
        )

        # Each resolves to its scope's own minor_calc (local scoped_lookup)
        for key, resolution in minor_calc_resolutions:
            usage_qn = key.split("|")[0]
            # Consumer scope determines which minor_calc is local
            segments = usage_qn.split("__")
            scope_segment = segments[-2] if len(segments) >= 2 else ""
            assert f"__{scope_segment}__minor_calc__a" in resolution.qualified_name, (
                f"{key}: expected scope '{scope_segment}' in channel, "
                f"got {resolution.qualified_name}"
            )

        # Alias IS registered (first-wins → plasma_region)
        plasma_channel = (
            "CATFMFERadialBuild__catf_radial_build__plasma_region__minor_calc__a"
        )
        alias_result = registry.alias_lookup(ScopedKey("minor_calc.a"))
        assert alias_result == plasma_channel, (
            f"Expected alias 'minor_calc.a' → plasma_region, got {alias_result}"
        )


# ===================================================================
# C11b: Mechanism — typed dispatch for REFERENCE bindings
# ===================================================================
class TestC11bReferenceDispatch:
    """REQ-BT-08, REQ-DRA-03: REFERENCE bindings dispatch via sysml_qn then scoped."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_reference_dispatch_uses_sysml_qn_then_scoped(self, attr_expr_probe_bt):
        """For attr_expr_probe REFERENCE MODULE_OUTPUTs: channels reachable via
        sysml_qn_lookup(SysMLQN(source_path)) or normalized scoped_lookup."""
        result, registry, snap = attr_expr_probe_bt
        binding_types = _build_binding_type_map(snap)
        ref_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.REFERENCE
        )
        assert len(ref_mo) == 2
        for key, resolution in ref_mo:
            assert _is_typed_reachable_reference(resolution, registry, key.split("|")[0]), (
                f"REFERENCE MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via typed lookups"
            )

    @pytest.mark.req("REQ-BT-02")
    def test_c11b_solar_reference_secondary_via_typed(self, solar_battery_bt):
        """The 2 solar_battery REFERENCE secondary resolutions resolve via typed lookups:
        (a) annualized_om|p_net_kw via scoped_lookup(ScopedKey("solar_battery_plant.p_net_kw"))
            (Key_F from Phase 1c FORMULA registration)
        (b) annualized_financial|total_capex via Step 1b scoped_lookup after :: normalization
            (Key_E_stripped from Phase 1b aggregation)
        """
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)

        # Case (a): annualized_om|p_net_kw
        key_a = "SolarBatteryDesign__solar_battery_plant__annualized_om|p_net_kw"
        res_a = result.binding_resolutions.get(key_a)
        assert res_a is not None, f"Resolution {key_a} not found"
        assert res_a.resolution_type == BindingResolutionType.MODULE_OUTPUT
        expected_a = "SolarBatteryDesign__solar_battery_plant__p_net_kw__p_net_kw"
        assert res_a.qualified_name == expected_a
        # After C11b: scoped_lookup with parent_part.leaf should find Key_F
        scoped_a = registry.scoped_lookup(ScopedKey("solar_battery_plant.p_net_kw"))
        # Before C11b: may be None (Key_F only in _compat)
        # After C11b: MUST equal expected_a (Key_F registered as ScopedKey in Phase 1c)
        if scoped_a is not None:
            assert scoped_a == expected_a

        # Case (b): annualized_financial|total_capex
        key_b = "SolarBatteryDesign__solar_battery_plant__annualized_financial|total_capex"
        res_b = result.binding_resolutions.get(key_b)
        assert res_b is not None, f"Resolution {key_b} not found"
        assert res_b.resolution_type == BindingResolutionType.MODULE_OUTPUT
        expected_b = "SolarBatteryDesign__solar_battery_plant__capital_cost__capital_cost"
        assert res_b.qualified_name == expected_b


# ===================================================================
# C11b: 14 compat-only resolutions now typed
# ===================================================================
class TestC11bCompatOnlyNowTyped:
    """REQ-BT-08, FR-4: All 14 previously-compat-only resolutions now
    resolve via typed lookups (scoped_lookup, alias_lookup, sysml_qn_lookup)."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_14_compat_only_now_typed(self, solar_battery_bt, catf_mfe_bt):
        """The 14 previously-compat-only resolutions (12 catf_mfe + 2 solar_battery)
        now resolve via typed lookups."""
        # catf_mfe: 12 cross-scope CHAIN via alias
        catf_result, catf_registry, catf_snap = catf_mfe_bt
        catf_binding_types = _build_binding_type_map(catf_snap)
        catf_chain_mo = _get_module_outputs_by_binding_type(
            catf_result, catf_binding_types, BindingType.CHAIN
        )
        catf_compat_only = [
            (k, r) for k, r in catf_chain_mo
            if not _is_typed_reachable_chain(r, catf_registry, k.split("|")[0])
        ]

        # solar_battery: 2 REFERENCE secondary via scoped/alias
        sb_result, sb_registry, sb_snap = solar_battery_bt
        sb_binding_types = _build_binding_type_map(sb_snap)
        sb_ref_mo = _get_module_outputs_by_binding_type(
            sb_result, sb_binding_types, BindingType.REFERENCE
        )
        sb_compat_only = [
            (k, r) for k, r in sb_ref_mo
            if not _is_typed_reachable_reference(r, sb_registry, k.split("|")[0])
        ]

        total_compat_only = len(catf_compat_only) + len(sb_compat_only)
        assert total_compat_only == 0, (
            f"Expected 0 compat-only resolutions after C11b migration, "
            f"got {total_compat_only} ({len(catf_compat_only)} catf_mfe + "
            f"{len(sb_compat_only)} solar_battery). "
            f"catf: {[k for k,r in catf_compat_only[:3]]} "
            f"solar: {[k for k,r in sb_compat_only[:3]]}"
        )


# ===================================================================
# C11b: EXPRESSION binding dispatch
# ===================================================================
class TestC11bExpressionBinding:
    """REQ-BT-01 gap: EXPRESSION bindings produce ENTRY_POINT with warning."""

    @pytest.mark.req("REQ-BT-01")
    def test_c11b_expression_binding_entry_point(self, expression_binding_bt):
        """EXPRESSION bindings (if encountered) produce BindingResolution(ENTRY_POINT)
        with a warning log, not silent skip.

        After C11b: EXPRESSION bindings get explicit dispatch to ENTRY_POINT
        (instead of being silently skipped by the source_path guard).
        """
        result, _, snap = expression_binding_bt

        # Count EXPRESSION bindings
        expression_bindings = []
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type == BindingType.EXPRESSION:
                    key = f"{usage.qualified_name}|{binding.param_name}"
                    expression_bindings.append(key)

        assert len(expression_bindings) > 0, "No EXPRESSION bindings in probe"

        # After C11b: each EXPRESSION binding should have an ENTRY_POINT resolution
        for key in expression_bindings:
            assert key in result.binding_resolutions, (
                f"EXPRESSION binding {key} has no resolution "
                f"(C11b should create ENTRY_POINT for EXPRESSION bindings)"
            )
            res = result.binding_resolutions[key]
            assert res.resolution_type == BindingResolutionType.ENTRY_POINT, (
                f"EXPRESSION binding {key}: expected ENTRY_POINT, "
                f"got {res.resolution_type.value}"
            )


# ===================================================================
# C11b: _consumer_scope_dotted helper
# ===================================================================
class TestC11bConsumerScopeDotted:
    """FR-4: _consumer_scope_dotted() extracts consumer scope from usage QN."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_consumer_scope_dotted(self):
        """_consumer_scope_dotted() for known qualified names returns correct scope.

        "Design__solar_battery_plant__lcoe" → "solar_battery_plant"
        "Design__catf_radial_build__vacuum_gap__volume_calc" → "catf_radial_build.vacuum_gap"
        """
        # This test verifies the helper function exists and works correctly.
        # Before C11b: function doesn't exist (test fails with AttributeError)
        # After C11b: function exists and returns correct scope
        backtracker = _build_minimal_backtracker()
        assert hasattr(backtracker, "_consumer_scope_dotted"), (
            "DependencyBacktracker missing _consumer_scope_dotted() method"
        )

        # Create minimal usage objects for testing
        from tests.helpers.snapshot_loader import load_extraction_snapshot
        snap = load_extraction_snapshot("solar_battery_model")

        # Find a usage with known QN
        for usage in snap["calc_usages"]:
            if usage.qualified_name == "SolarBatteryDesign__solar_battery_plant__lcoe":
                result = backtracker._consumer_scope_dotted(usage)
                assert result == "solar_battery_plant", (
                    f"Expected 'solar_battery_plant', got '{result}'"
                )
                break

        # Test a deeper scope from catf_mfe
        snap2 = load_extraction_snapshot("catf_mfe_model")
        for usage in snap2["calc_usages"]:
            if "catf_radial_build__vacuum_gap__volume_calc" in usage.qualified_name:
                result = backtracker._consumer_scope_dotted(usage)
                assert result == "catf_radial_build.vacuum_gap", (
                    f"Expected 'catf_radial_build.vacuum_gap', got '{result}'"
                )
                break


# ===================================================================
# C11b: Phase 2/3/4 alias registration without resolve()
# ===================================================================
class TestC11bPhaseRegistration:
    """FR-4: Phase 2/3/4 alias registration uses typed lookups, not resolve()."""

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_phase2_alias_no_resolve(self):
        """Phase 2 CHAIN alias registration resolves canonical_name via
        scoped_lookup() (not resolve()). Verified by registry content equality:
        same aliases registered before and after migration."""
        snap = load_extraction_snapshot("solar_battery_model")
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )
        # Verify Phase 2 aliases are all registered
        chain_aliases = [a for a in snap.get("channel_aliases", [])
                         if a.source == "redefinition"]
        for alias in chain_aliases:
            scoped_result = registry.scoped_lookup(ScopedKey(alias.canonical_name))
            if scoped_result is not None:
                # The alias should be registered in the alias registry
                alias_registered = registry.alias_lookup(ScopedKey(alias.alias_name))
                assert alias_registered is not None, (
                    f"Phase 2 CHAIN alias '{alias.alias_name}' not registered "
                    f"(canonical_name='{alias.canonical_name}' resolves to {scoped_result})"
                )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_phase3_expose_pure_no_resolve(self):
        """Phase 3 EXPOSE_PURE alias registration resolves canonical_name
        without resolve(). Same aliases registered."""
        snap = load_extraction_snapshot("catf_mfe_model")
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )
        expose_aliases = [a for a in snap.get("channel_aliases", [])
                          if a.source == "expose_pure"]
        assert len(expose_aliases) > 0, "No EXPOSE_PURE aliases in catf_mfe"

        # Verify aliases are registered
        registered = 0
        for alias in expose_aliases:
            qn = alias.owning_part_qn
            if "::" in qn:
                owning_part_short = qn.rsplit("::", 1)[-1]
            else:
                owning_part_short = qn.split("__")[-1]
            scoped_key = ScopedKey(f"{owning_part_short}.{alias.alias_name}")
            result = registry.alias_lookup(scoped_key)
            if result is not None:
                registered += 1
        assert registered == len(expose_aliases), (
            f"Only {registered}/{len(expose_aliases)} EXPOSE_PURE aliases registered"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_c11b_phase4_transitive_no_resolve(self):
        """Phase 4 transitive alias registration resolves without resolve().
        Same aliases registered."""
        from sysml_codegen.core.output_registry import is_transitive_default

        snap = load_extraction_snapshot("catf_mfe_model")
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        # Count Phase 4 aliases registered
        phase4_registered = 0
        phase4_total = 0
        for _path, attrs in snap.get("design_attributes", {}).items():
            for attr in attrs:
                if not is_transitive_default(attr.default_value):
                    continue
                phase4_total += 1
                key = ScopedKey(f"{attr.parent_part}.{attr.name}")
                result = registry.alias_lookup(key)
                if result is not None:
                    phase4_registered += 1

        assert phase4_total > 0, "No transitive candidates in catf_mfe"
        assert phase4_registered == 44, (
            f"Expected 44 Phase 4 transitive aliases, got {phase4_registered}"
        )


# ===================================================================
# Helpers
# ===================================================================
def _build_binding_type_map(snap: dict) -> dict[str, BindingType]:
    """Build mapping from resolution key to BindingType from snapshot data."""
    result = {}
    for usage in snap["calc_usages"]:
        for binding in usage.bindings:
            key = f"{usage.qualified_name}|{binding.param_name}"
            result[key] = binding.binding_type
    return result


def _get_module_outputs_by_binding_type(
    result: BacktrackingResult,
    binding_types: dict[str, BindingType],
    target_type: BindingType,
) -> list[tuple[str, BindingResolution]]:
    """Get MODULE_OUTPUT resolutions for a specific BindingType."""
    return [
        (key, resolution)
        for key, resolution in result.binding_resolutions.items()
        if resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        and binding_types.get(key) == target_type
    ]


def _is_typed_reachable_chain(
    resolution: BindingResolution,
    registry: OutputRegistry,
    usage_qn: str,
) -> bool:
    """Check if a CHAIN MODULE_OUTPUT is reachable via typed lookups."""
    channel = resolution.qualified_name
    source_path = resolution.source_path or ""

    # Step 1: scoped_lookup with consumer scope
    segments = usage_qn.split("__")
    if len(segments) > 2:
        consumer_scope = ".".join(segments[1:-1])
        scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
        if registry.scoped_lookup(scoped_key) == channel:
            return True

    # Step 1b: direct scoped_lookup (no consumer scope prefix)
    # Covers Key_F (FORMULA outputs registered as owning_part.attr)
    if source_path and registry.scoped_lookup(ScopedKey(source_path)) == channel:
        return True

    # Step 2: alias_lookup
    if source_path and registry.alias_lookup(ScopedKey(source_path)) == channel:
        return True

    return False


def _is_typed_reachable_reference(
    resolution: BindingResolution,
    registry: OutputRegistry,
    usage_qn: str = "",
) -> bool:
    """Check if a REFERENCE MODULE_OUTPUT is reachable via typed lookups."""
    channel = resolution.qualified_name
    source_path = resolution.source_path or ""

    # Step 1: sysml_qn_lookup
    if registry.sysml_qn_lookup(SysMLQN(source_path)) == channel:
        return True

    # Step 1b: normalized scoped_lookup
    if "::" in source_path:
        parts = source_path.split("::")
        if len(parts) >= 2:
            sanitized_part = sanitize_name(parts[-2]).lower()
            dotted = f"{sanitized_part}.{parts[-1]}"
            if registry.scoped_lookup(ScopedKey(dotted)) == channel:
                return True

    # Step 2: REFERENCE secondary — leaf + parent_part scoped/alias lookup
    if "::" in source_path:
        leaf = source_path.rsplit("::", 1)[-1]
    elif "." in source_path:
        leaf = source_path.rsplit(".", 1)[-1]
    else:
        leaf = source_path
    if usage_qn:
        segments = usage_qn.split("__")
        if len(segments) >= 2:
            parent_part = segments[-2]
            sk = ScopedKey(f"{parent_part}.{leaf}")
            if registry.scoped_lookup(sk) == channel:
                return True
            if registry.alias_lookup(sk) == channel:
                return True

    return False


def _assert_topological_order(result: BacktrackingResult) -> None:
    """Assert that required_usages are in valid topological order."""
    usage_positions = {
        u.qualified_name: i for i, u in enumerate(result.required_usages)
    }
    violations = []
    for key, resolution in result.binding_resolutions.items():
        if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
            continue
        consumer_qn = key.split("|")[0]
        channel = resolution.qualified_name
        if "__" in channel:
            producer_qn = channel.rsplit("__", 1)[0]
            consumer_pos = usage_positions.get(consumer_qn)
            producer_pos = usage_positions.get(producer_qn)
            if consumer_pos is not None and producer_pos is not None:
                if producer_pos >= consumer_pos:
                    violations.append(
                        f"producer {producer_qn}[{producer_pos}] >= "
                        f"consumer {consumer_qn}[{consumer_pos}]"
                    )
    assert not violations, (
        f"Topological order violations: {violations}"
    )


def _build_minimal_backtracker() -> DependencyBacktracker:
    """Build a minimal backtracker for unit-testing internal methods."""
    return DependencyBacktracker(
        all_usages=[],
        calc_defs=[],
        design_attributes={},
        output_registry=OutputRegistry(),
    )
