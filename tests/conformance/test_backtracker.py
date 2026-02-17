"""Conformance tests for DependencyBacktracker (C11a).

Requirements: REQ-BT-01 through REQ-BT-08, REQ-DRA-01
Design intent: 11-analysis-backtracker.md, 24-dual-resolution-architecture.md

C11a tests verify OUTCOMES of the current backtracker implementation:
- Which channels resolve for each binding
- Correct topological ordering
- Key format compliance
- Cycle detection
- Self-reference guard

C11a does NOT test the dispatch MECHANISM (which registry is queried).
That is C11b's scope. When C11b migrates to typed dispatch, these
outcome tests must still pass.

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

        assert alias_hit_count == 10, (
            f"Expected 10 cross-package alias hits in catf_mfe, got {alias_hit_count}"
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
                resolution, registry
            ), (
                f"REFERENCE MODULE_OUTPUT {key} -> {resolution.qualified_name} "
                f"not reachable via sysml_qn_lookup or scoped_lookup"
            )

    @pytest.mark.req("REQ-BT-08")
    def test_compat_only_count_documented(self, catf_mfe_bt):
        """catf_mfe has exactly 12 CHAIN MODULE_OUTPUTs that are compat-only.

        These resolve through _compat (bare Key_A format: 'minor_calc.a')
        because the consumers are in different sub-scopes than the producer.
        Documented for C11b migration planning.
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
        assert len(compat_only) == 12, (
            f"Expected 12 compat-only CHAIN resolutions in catf_mfe, "
            f"got {len(compat_only)}"
        )

    @pytest.mark.req("REQ-BT-08")
    def test_solar_compat_only_count(self, solar_battery_bt):
        """solar_battery has exactly 1 REFERENCE MODULE_OUTPUT that is compat-only.

        The binding SolarBatteryDesign::solar_battery_plant::annualized_om::p_net_kw
        resolves through secondary _resolve_reference_via_registry() using
        parent_part.leaf format which hits _compat.
        """
        result, registry, snap = solar_battery_bt
        binding_types = _build_binding_type_map(snap)
        ref_mo = _get_module_outputs_by_binding_type(
            result, binding_types, BindingType.REFERENCE
        )
        compat_only = [
            (k, r) for k, r in ref_mo
            if not _is_typed_reachable_reference(r, registry)
        ]
        assert len(compat_only) == 1, (
            f"Expected 1 compat-only REFERENCE resolution in solar_battery, "
            f"got {len(compat_only)}"
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
    """Document the current behavior gap for EXPRESSION bindings."""

    @pytest.mark.req("REQ-BT-01")
    def test_expression_bindings_silently_skipped(self, expression_binding_bt):
        """expression_binding_probe: EXPRESSION bindings have no source_path,
        so they are silently skipped by the backtracker. No crash, but no
        resolution either. This is a known gap for C11b.
        """
        result, _, snap = expression_binding_bt
        # The backtracker completes without error
        assert isinstance(result, BacktrackingResult)

        # Count EXPRESSION bindings in the snapshot
        expression_count = sum(
            1
            for usage in snap["calc_usages"]
            for binding in usage.bindings
            if binding.binding_type == BindingType.EXPRESSION
        )
        # Verify EXPRESSION bindings exist but are NOT in resolutions
        assert expression_count > 0, "No EXPRESSION bindings in expression_binding_probe"

        # EXPRESSION bindings have source_path=None, so the
        # `if binding.source_path:` guard in _trace_dependencies skips them
        for usage in snap["calc_usages"]:
            for binding in usage.bindings:
                if binding.binding_type != BindingType.EXPRESSION:
                    continue
                key = f"{usage.qualified_name}|{binding.param_name}"
                assert key not in result.binding_resolutions, (
                    f"EXPRESSION binding {key} unexpectedly has a resolution"
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

    # Step 2: alias_lookup
    if source_path and registry.alias_lookup(ScopedKey(source_path)) == channel:
        return True

    return False


def _is_typed_reachable_reference(
    resolution: BindingResolution,
    registry: OutputRegistry,
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
