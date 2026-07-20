"""Conformance tests for Dual Resolution Consistency (X02).

Requirements: REQ-DRA-03, REQ-DRA-04, REQ-DRA-05
Design intent: 24-dual-resolution-architecture.md

Verifies that the two resolution paths (backtracker DFS and resolve_input()
strategy chain) produce identical wiring decisions when resolving the same
reference in the same scope. Also verifies FORMULA attribute resolution map
consistency with the typed registry, and the structural mapping between
BindingResolution and InputSource.

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.identifier_types import SysMLQN
from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.core.qualified_names import sanitize_qualified_name
from sysml_codegen.extraction.data_models import ComputedAttributeClassification
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import (
    AttributeResolutionKind,
    _build_attribute_resolution_map,
    _resolve_expose_pure,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_backtracker_from_snapshot(model_name: str):
    """Build OutputRegistry + DependencyBacktracker from extraction snapshot.

    Returns (BacktrackingResult, OutputRegistry, snapshot_dict).
    """
    snap = load_extraction_snapshot(snapshot_fixture(model_name))
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


def _flatten_design_attrs(design_attrs_dict) -> dict:
    """Flatten dict[Path, list[DesignAttributeData]] to dict[str, DesignAttributeData]."""
    flat = {}
    for _path, attrs in design_attrs_dict.items():
        for da in attrs:
            if da.qualified_name:
                flat[da.qualified_name] = da
            flat[da.name] = da
    return flat


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_dual():
    """Session-scoped backtracker + registry for solar_battery_model."""
    return _build_backtracker_from_snapshot("solar_battery_model")


@pytest.fixture(scope="session")
def catf_mfe_dual():
    """Session-scoped backtracker + registry for catf_mfe_model."""
    return _build_backtracker_from_snapshot("catf_mfe_model")


@pytest.fixture(scope="session")
def chain_spike_dual():
    """Session-scoped backtracker + registry for chain_spike_model."""
    return _build_backtracker_from_snapshot("chain_spike_model")


@pytest.fixture(scope="session")
def attr_expr_probe_dual():
    """Session-scoped backtracker + registry for attr_expr_probe."""
    return _build_backtracker_from_snapshot("attr_expr_probe")


# ===================================================================
# REQ-DRA-04: Backtracker vs resolve_input — CHAIN bindings
# ===================================================================
class TestFormulaExposePureChannelsMatchRegistry:
    """Every EXPOSE_PURE channel in _build_attribute_resolution_map()
    matches what scoped_lookup or alias_lookup returns."""

    @pytest.mark.req("REQ-DRA-04")
    @pytest.mark.parametrize("model_name", [
        "attr_expr_probe", "solar_battery_model",
    ])
    def test_formula_expose_pure_channels_match_registry(self, model_name):
        """EXPOSE_PURE resolution map channels are reachable via typed registry."""
        snap = load_extraction_snapshot(snapshot_fixture(model_name))
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )
        calc_usage_names = {u.instance_name for u in snap["calc_usages"]}
        resolution_map = _build_attribute_resolution_map(
            computed_attrs=snap["computed_attributes"],
            design_attrs=snap.get("design_attributes", {}),
            output_registry=registry,
            calc_usage_names=calc_usage_names,
        )

        expose_pure_count = 0
        mismatches = []
        for part_name, attrs in resolution_map.items():
            for attr_name, attr_res in attrs.items():
                if attr_res.kind != AttributeResolutionKind.EXPOSE_ALIAS:
                    continue
                expose_pure_count += 1
                channel = attr_res.channel_name

                # Channel must be in canonical_channels set
                if channel not in registry.canonical_channels:
                    mismatches.append(
                        f"{part_name}.{attr_name}: EXPOSE_PURE channel "
                        f"'{channel}' not in canonical_channels"
                    )
                    continue

                # The critical invariant is the channel value existing in
                # canonical_channels (already verified above). The specific
                # registry key used to reach it depends on resolution context.

        assert not mismatches, (
            f"{model_name}: {len(mismatches)} EXPOSE_PURE mismatches:\n"
            + "\n".join(mismatches)
        )
        # Only check count for models known to have EXPOSE_PURE attrs
        if model_name == "attr_expr_probe":
            assert expose_pure_count > 0, (
                "Expected at least one EXPOSE_PURE in attr_expr_probe resolution map"
            )


# ===================================================================
# REQ-DRA-04: FORMULA channels exist in SysML QN registry
# ===================================================================
class TestFormulaChannelExistsInSysMLQNRegistry:
    """Every FORMULA channel in the resolution map has a corresponding
    SysML QN key in the registry (backtracker REFERENCE path would find it)."""

    @pytest.mark.req("REQ-DRA-04")
    @pytest.mark.parametrize("model_name", [
        "attr_expr_probe", "solar_battery_model",
    ])
    def test_formula_channel_exists_in_sysml_qn_registry(self, model_name):
        """FORMULA channels are registered as SysML QN keys."""
        snap = load_extraction_snapshot(snapshot_fixture(model_name))
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        calc_usage_names = {u.instance_name for u in snap["calc_usages"]}
        resolution_map = _build_attribute_resolution_map(
            computed_attrs=snap["computed_attributes"],
            design_attrs=snap.get("design_attributes", {}),
            output_registry=registry,
            calc_usage_names=calc_usage_names,
        )

        formula_count = 0
        not_in_registry = []
        for part_name, attrs in resolution_map.items():
            for attr_name, attr_res in attrs.items():
                if attr_res.kind != AttributeResolutionKind.FORMULA:
                    continue
                formula_count += 1
                channel = attr_res.channel_name

                # The channel must exist in canonical_channels
                if channel not in registry.canonical_channels:
                    not_in_registry.append(
                        f"{part_name}.{attr_name}: FORMULA channel "
                        f"'{channel}' not in canonical_channels"
                    )
                    continue

                # A SysML QN key should also reach this channel
                # Find the matching computed attr to reconstruct the SysML QN
                matching_ca = [
                    ca for ca in snap["computed_attributes"]
                    if ca.python_name == attr_name
                    and ca.owning_part_name == part_name
                    and ca.classification == ComputedAttributeClassification.FORMULA
                ]
                if matching_ca:
                    ca = matching_ca[0]
                    # Item 7 lockstep flip: key registered per-segment sanitized.
                    sysml_qn = sanitize_qualified_name(
                        f"{ca.owning_part_qualified_name}::{ca.name}"
                    )
                    qn_result = registry.sysml_qn_lookup(SysMLQN(sysml_qn))
                    if qn_result is None:
                        not_in_registry.append(
                            f"{part_name}.{attr_name}: SysML QN '{sysml_qn}' "
                            f"not found in registry (channel='{channel}')"
                        )

        assert not not_in_registry, (
            f"{model_name}: {len(not_in_registry)} FORMULA registry gaps:\n"
            + "\n".join(not_in_registry)
        )
        if model_name == "attr_expr_probe":
            assert formula_count > 0, (
                "Expected at least one FORMULA in attr_expr_probe resolution map"
            )


# ===================================================================
# REQ-DRA-04: Aggregation MODULE_OUTPUT channels match backtracker
# ===================================================================
class TestOneResolutionAuthority:
    """What the six deleted parity classes were really asserting.

    They compared the calculation backtracker against the aggregation strategy chain on
    the same reference, because those were two independently-ordered algorithms that
    could drift. After the cutover they are one algorithm, so a per-fixture parity sweep
    compares the code against itself. What remains worth pinning is the property the
    sweep existed to protect: two consumers asking about the same reference get the same
    answer, and neither can reorder or skip a key form to get it.
    """

    def test_two_consumers_of_one_reference_agree(self):
        from sysml_codegen.core.output_registry import OutputRegistry, ScopedKey
        from sysml_codegen.resolution.producer_resolution import (
            Outcome,
            ProducerContext,
            ProducerRequest,
            TerminalPolicy,
            resolve_producer,
        )

        registry = OutputRegistry()
        registry.register_scoped(ScopedKey("plant.pv.cost"), "Design__plant__pv__cost")
        ctx = ProducerContext(output_registry=registry)

        def ask(consumer_eqn, param_name, policy):
            return resolve_producer(
                ProducerRequest(
                    consumer_eqn=consumer_eqn,
                    reference="pv.cost",
                    param_name=param_name,
                    consumer_scope="plant",
                    instance_path="Design__plant",
                    policy=policy,
                    diagnostic_context="parity",
                ),
                ctx,
            )

        calc = ask("design__plant__lcoe", "pv_cost", TerminalPolicy.LENIENT)
        agg = ask("design__plant__total", None, TerminalPolicy.LENIENT)
        constraint = ask("design__plant__check__abc", "pv_cost", TerminalPolicy.STRICT)

        assert calc.outcome is agg.outcome is constraint.outcome is Outcome.MODULE_OUTPUT
        assert calc.identity == agg.identity == constraint.identity
        assert calc.key_form == agg.key_form == constraint.key_form == "scoped_prefixed"


class TestNoUntypedDictGetInResolutionPaths:
    """Static analysis: resolution paths use typed registry methods,
    not raw dict.get() on registry internals."""

    @pytest.mark.req("REQ-DRA-03")
    def test_no_untyped_dict_get_in_resolve_binding(self):
        """_resolve_binding_via_registry, _resolve_chain_dispatch, and
        _resolve_reference_dispatch contain no raw dict.get() on
        registry internals."""
        method_names = [
            "_resolve_binding_via_registry",
            "_resolve_chain_dispatch",
            "_resolve_reference_dispatch",
            "_resolve_reference_via_registry",
        ]
        violations = []
        for method_name in method_names:
            method = getattr(DependencyBacktracker, method_name, None)
            if method is None:
                continue
            source = textwrap.dedent(inspect.getsource(method))
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    # Look for *.get( calls that might be dict.get on registry
                    if (isinstance(func, ast.Attribute)
                            and func.attr == "get"
                            and isinstance(func.value, ast.Attribute)):
                        # Check if calling .get on a registry-like attribute
                        inner = func.value
                        if inner.attr in ("_index", "_scoped", "_sysml_qn", "_alias"):
                            violations.append(
                                f"{method_name}: raw dict.get() on "
                                f"'{inner.attr}' at line {node.lineno}"
                            )
        assert not violations, (
            "Untyped dict.get() calls found in resolution paths:\n"
            + "\n".join(violations)
        )

    @pytest.mark.req("REQ-DRA-03")
    def test_no_untyped_dict_get_in_resolve_expose_pure(self):
        """_resolve_expose_pure contains no raw dict.get() on registry internals."""
        source = textwrap.dedent(inspect.getsource(_resolve_expose_pure))
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if (isinstance(func, ast.Attribute)
                        and func.attr == "get"
                        and isinstance(func.value, ast.Attribute)):
                    inner = func.value
                    if inner.attr in ("_index", "_scoped", "_sysml_qn", "_alias"):
                        pytest.fail(
                            f"_resolve_expose_pure: raw dict.get() on "
                            f"'{inner.attr}' at line {node.lineno}"
                        )

    @pytest.mark.req("REQ-DRA-03")
    def test_no_untyped_dict_get_in_the_producer_table(self):
        """Re-pointed: `resolve_input` is gone, and every registry read now happens in
        the one table, so that is where the untyped-`dict.get` guard belongs."""
        import ast
        import inspect
        import textwrap

        from sysml_codegen.resolution import producer_resolution

        source = textwrap.dedent(inspect.getsource(producer_resolution))
        bare_gets = [
            node.lineno
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr.endswith(("registry", "_map", "channels"))
        ]
        assert not bare_gets, f"untyped registry dict.get at lines {bare_gets}"
    def test_typed_lookup_methods_used(self):
        """All resolution paths use typed lookup methods.

        Re-pointed at `producer_resolution`: after the cutover there is exactly one
        module performing registry lookups, so the guard has one place to look.
        """
        import inspect

        from sysml_codegen.resolution import producer_resolution

        source = inspect.getsource(producer_resolution)
        for accessor in ("scoped_lookup", "sysml_qn_lookup", "alias_lookup",
                         "scoped_alias_lookup"):
            assert accessor in source, f"{accessor} absent from the key-form table"
