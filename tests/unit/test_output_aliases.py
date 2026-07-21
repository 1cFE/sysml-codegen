"""Unit tests for ``_build_output_aliases`` — the Item 11 (SC-7) product.

Surfaces the modeler's EXPOSE_PURE name onto its canonical channel as an
``OutputAlias`` on the ComputationGraph. Two shapes, both driven from committed
extraction snapshots (license-free, no mocks):

- **Shape A** (part def): ``wi014_toy``'s ``total_cost`` and ``ife_plant``'s
  nested ``radial_build.tf_coil.volume`` — sourced from ``_scoped_alias``.
- **Shape B** (part usage): ``attr_expr_probe``'s three exposes and
  ``catf_mfe``'s nested plant-idiom exposes — sourced from ``expose_pure``
  ChannelAliases, resolved ``alias_lookup``-first (C1).

The run-mode dangling filter (D4) and the two-names-one-channel tie-break (M4)
are exercised on small hand-built registries + modules (real objects, controlled
inputs — the branch under test needs a pruned/duplicate channel the fixtures do
not carry).
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedAliasKey,
    ScopedKey,
)
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.resolution.graph_builder import _build_output_aliases
from sysml_codegen.resolution.models import (
    ModuleKind,
    ModuleOutput,
    OutputAlias,
    PipelineModule,
)
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Shape A (part def) — sourced from _scoped_alias, channel read straight
# ---------------------------------------------------------------------------


def test_shape_a_wi014_surfaces_total_cost() -> None:
    """wi014_toy's part-def EXPOSE ``total_cost = cost_calc.cost`` surfaces as one
    ``OutputAlias`` on ``demo_plant``, channel read from the registry (INV-2)."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("wi014_toy"))
    part_def = [a for a in graph.output_aliases if a.shape == "part_def"]
    assert len(part_def) == 1
    entry = part_def[0]
    assert entry.alias_name == "total_cost"
    assert entry.instance_path == "demo_plant"
    assert entry.canonical_channel.endswith("cost_calc__cost")
    assert entry.output_filename == "demo_plant__total_cost.json"


def test_shape_a_nested_ife_plant_resolves_nonnull() -> None:
    """ife_plant's nested part-def EXPOSE (``radial_build.tf_coil.volume``) surfaces
    with a non-null channel — the nested-scope shape-A guard. Its scope half keeps
    the full nested instance path."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("ife_plant"))
    part_def = [a for a in graph.output_aliases if a.shape == "part_def"]
    assert part_def, "ife_plant surfaces no part-def exposes"
    assert all(a.canonical_channel for a in part_def)
    nested = [a for a in part_def if a.instance_path == "radial_build.tf_coil"]
    assert len(nested) == 1
    assert nested[0].alias_name == "volume"
    assert nested[0].canonical_channel.endswith("tf_coil__volume_calc__volume")


# ---------------------------------------------------------------------------
# Shape B (part usage) — expose_pure ChannelAliases, alias_lookup-first (C1)
# ---------------------------------------------------------------------------


def test_shape_b_attr_expr_probe_surfaces_three() -> None:
    """attr_expr_probe's three part-usage exposes surface with non-null channels."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("attr_expr_probe"))
    part_usage = [a for a in graph.output_aliases if a.shape == "part_usage"]
    names = {a.alias_name for a in part_usage}
    assert names == {"scale_result", "half_vol", "quarter_vol"}
    assert all(a.canonical_channel for a in part_usage)
    assert all(a.instance_path == "probe_design" for a in part_usage)


def test_shape_b_resolves_via_alias_lookup_not_scoped() -> None:
    """C1 GUARD (first proof point): shape-B channels resolve through the persisted
    ``alias_lookup`` twin, **not** ``scoped_lookup``.

    Regression teeth: for every attr_expr_probe expose the bare ``canonical_name``
    is absent from ``scoped_lookup`` and present in ``alias_lookup``. If the
    resolver ever regresses to ``scoped_lookup``-only, every one of these drops to
    a null channel and the item no-ops exactly where it is meant to be populated.
    """
    graph, inputs = build_full_graph_from_snapshot(snapshot_fixture("attr_expr_probe"))
    registry = inputs["registry"]
    expose = [
        a for a in inputs["snap"]["channel_aliases"] if a.source == "expose_pure"
    ]
    assert expose, "attr_expr_probe carries no expose_pure ChannelAliases"
    for alias in expose:
        key = ScopedKey(alias.canonical_name)
        assert registry.scoped_lookup(key) is None, (
            f"{alias.canonical_name} unexpectedly resolvable via scoped_lookup — "
            "the C1 guard has lost its teeth"
        )
        assert registry.alias_lookup(key) is not None
    # And the surfaced entries carry those non-null channels.
    part_usage = [a for a in graph.output_aliases if a.shape == "part_usage"]
    assert part_usage and all(a.canonical_channel for a in part_usage)


# ---------------------------------------------------------------------------
# Cross-cutting invariants on real fixtures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model", ["wi014_toy", "attr_expr_probe", "ife_plant", "catf_mfe_model"]
)
def test_output_aliases_sorted_deterministic(model: str) -> None:
    """INV-5: output_aliases equals its ``(instance_path, alias_name)``-sorted copy,
    so regen never yields an ordering-only diff."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture(model))
    assert graph.output_aliases == sorted(
        graph.output_aliases, key=lambda a: (a.instance_path, a.alias_name)
    )


@pytest.mark.parametrize(
    "model", ["wi014_toy", "attr_expr_probe", "ife_plant", "catf_mfe_model"]
)
def test_every_surfaced_channel_is_declared(model: str) -> None:
    """INV-3: every emitted entry's channel is a declared graph output."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture(model))
    declared = {o.channel_name for m in graph.modules for o in m.outputs}
    for a in graph.output_aliases:
        assert a.canonical_channel in declared


def test_no_expose_fixture_is_empty_field() -> None:
    """A fixture with computed attributes but no EXPOSE_PURE serializes an empty
    (not absent) ``output_aliases`` — the D1 field-addition class, and a
    non-vacuous filter check (quoted_owner_formula carries 2 FORMULA attributes).
    solar_battery no longer serves: its shape-A EXPOSE surfaces post-Item-11."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("quoted_owner_formula"))
    assert graph.output_aliases == []


# ---------------------------------------------------------------------------
# Run-mode dangling filter (D4 / M3) and tie-break (M4) — controlled inputs
# ---------------------------------------------------------------------------


def _registry_with_scoped_alias(pairs: list[tuple[tuple[str, str], str]]) -> OutputRegistry:
    """Build a registry whose ``_scoped_alias`` carries ``pairs`` of
    ``((scope, leaf), channel)``, each channel pre-registered as canonical."""
    registry = OutputRegistry()
    for _key, channel in pairs:
        registry.register_scoped(ScopedKey(channel), CanonicalChannel(channel))
    for (scope, leaf), channel in pairs:
        registry.register_scoped_alias(
            ScopedAliasKey((scope, leaf)), CanonicalChannel(channel)
        )
    return registry


def _module_with_channels(channels: list[str]) -> PipelineModule:
    return PipelineModule(
        name="m",
        module_type="M",
        inputs=[],
        outputs=[
            ModuleOutput(field_name="root", python_type="float", channel_name=c)
            for c in channels
        ],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )


def test_dangling_targeted_run_silent(caplog: pytest.LogCaptureFixture) -> None:
    """D4: on a targeted (non-include_all) run, an alias whose channel was pruned is
    dropped with a DEBUG log — no raise (a pruned channel is legitimate there)."""
    registry = _registry_with_scoped_alias([(("plant", "cost"), "plant__cost_calc__cost")])
    modules = _module_with_channels([])  # channel absent → dangling
    with caplog.at_level(logging.DEBUG, logger="sysml_codegen.resolution.graph_builder"):
        result = _build_output_aliases(registry, [], [modules], include_all=False)
    assert result == []
    assert "dropping alias 'cost'" in caplog.text


def test_dangling_include_all_run_errors() -> None:
    """D4 / M3: on a full (include_all) run, a dangling alias is a real wiring
    regression — raise, do not silently swallow."""
    registry = _registry_with_scoped_alias([(("plant", "cost"), "plant__cost_calc__cost")])
    modules = _module_with_channels([])  # channel absent → dangling
    with pytest.raises(ValueError, match="not a declared graph output"):
        _build_output_aliases(registry, [], [modules], include_all=True)


def test_two_names_one_channel_both_retained() -> None:
    """M4: two names on one channel (two attributes exposing the same calc output
    under different names) both stay in output_aliases; the shared channel is
    declared, so neither drops."""
    channel = "plant__cost_calc__cost"
    registry = _registry_with_scoped_alias(
        [(("plant", "total_cost"), channel), (("plant", "grand_total"), channel)]
    )
    modules = _module_with_channels([channel])
    result = _build_output_aliases(registry, [], [modules], include_all=True)
    assert {a.alias_name for a in result} == {"total_cost", "grand_total"}
    assert all(a.canonical_channel == channel for a in result)
    # Distinct output filenames despite the shared channel (INV-4).
    assert len({a.output_filename for a in result}) == 2
