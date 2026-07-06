"""Unit tests for the Item 11 (SC-7) exit-point filename override.

An aliased channel's exit line renders the modeler's instance-qualified name as
its output filename (``{instance_path}__{alias_name}.json``); the exit **key**
stays the canonical channel (D3 — verified against simkit). Unaliased lines are
byte-identical to today's ``{channel}.json``.

Two layers:
- Mechanism (``_build_alias_filename_map`` / ``_build_exit_points``) on controlled
  inputs — for the tie-break and default-filename branches.
- End-to-end (``generate_pipeline_yaml``) on committed snapshots — wi014_toy
  (shape A), attr_expr_probe (shape B), sibling_channel_ambiguity (D5 collision),
  catf_mfe (nested shape B).
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.pipeline import (
    _build_alias_filename_map,
    _build_exit_points,
    generate_pipeline_yaml,
)
from sysml_codegen.resolution.models import (
    ModuleOutput,
    OutputAlias,
    PipelineModule,
)
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

TEMPLATE_DIR = Path("src/sysml_codegen/templates")


def _template_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _module_with_channel(channel: str) -> PipelineModule:
    return PipelineModule(
        name="m",
        module_type="M",
        inputs=[],
        outputs=[
            ModuleOutput(field_name="root", python_type="float", channel_name=channel)
        ],
        execution_order=0,
    )


# ---------------------------------------------------------------------------
# Mechanism
# ---------------------------------------------------------------------------


def test_aliased_channel_gets_alias_filename() -> None:
    """The exit line's filename is overridden while its key stays the channel."""
    channel = "plant__cost_calc__cost"
    exits = _build_exit_points(
        [_module_with_channel(channel)],
        {channel: "demo_plant__total_cost.json"},
    )
    line = next(e for e in exits if e["name"] == channel)
    assert line["name"] == channel
    assert line["filename"] == "demo_plant__total_cost.json"


def test_unaliased_channel_keeps_default_filename() -> None:
    """A channel absent from the override map keeps today's ``{channel}.json``."""
    channel = "plant__area_calc__area"
    exits = _build_exit_points([_module_with_channel(channel)], {})
    line = next(e for e in exits if e["name"] == channel)
    assert line["filename"] == f"{channel}.json"


def test_alias_filename_map_tiebreak_first_by_sorted() -> None:
    """M4: one channel, two names → the filename is the first by
    ``(instance_path, alias_name)``; both names still exist upstream in
    output_aliases (the map just picks one filename per channel)."""
    channel = "plant__cost_calc__cost"
    # Passed pre-sorted (INV-5 order), as generate_pipeline_yaml receives them.
    aliases = [
        OutputAlias(
            alias_name="grand_total",
            canonical_channel=channel,
            instance_path="plant",
            shape="part_def",
        ),
        OutputAlias(
            alias_name="total_cost",
            canonical_channel=channel,
            instance_path="plant",
            shape="part_def",
        ),
    ]
    filenames = _build_alias_filename_map(sorted(aliases, key=lambda a: (a.instance_path, a.alias_name)))
    assert filenames[channel] == "plant__grand_total.json"  # 'grand_total' < 'total_cost'


# ---------------------------------------------------------------------------
# End-to-end YAML
# ---------------------------------------------------------------------------


def _exit_line(yaml_text: str, channel: str) -> str:
    for line in yaml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{channel}:"):
            return stripped
    raise AssertionError(f"no exit line for channel {channel}")


def test_wi014_yaml_renames_total_cost() -> None:
    """Shape A end-to-end: the cost channel's exit filename is the modeler's name;
    the key stays the channel."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("wi014_toy"))
    yaml_text = generate_pipeline_yaml(graph, "wi014_toy", _template_env())
    channel = "toy_plant__demo_plant__cost_calc__cost"
    line = _exit_line(yaml_text, channel)
    assert line.endswith(" demo_plant__total_cost.json")
    assert line.startswith(f"{channel}: ")


def test_attr_expr_probe_yaml_renames_three_only() -> None:
    """Shape B end-to-end: the three aliased channels rename; every other exit line
    keeps its ``{channel}.json`` default."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("attr_expr_probe"))
    yaml_text = generate_pipeline_yaml(graph, "attr_expr_probe", _template_env())
    renamed = {
        "AttrExprProbeDesign__probe_design__scale_calc__result": "probe_design__scale_result.json",
        "AttrExprProbeDesign__probe_design__split__half": "probe_design__half_vol.json",
        "AttrExprProbeDesign__probe_design__split__quarter": "probe_design__quarter_vol.json",
    }
    for channel, filename in renamed.items():
        assert _exit_line(yaml_text, channel).endswith(f" {filename}")

    # Every unaliased channel keeps the default filename.
    declared = {o.channel_name for m in graph.modules for o in m.outputs}
    for channel in declared - set(renamed):
        assert _exit_line(yaml_text, channel).endswith(f" {channel}.json")


def test_sibling_channel_ambiguity_distinct_filenames() -> None:
    """D5: two siblings exposing the same name (``power`` on ``chamber_a`` /
    ``chamber_b``) produce two distinct exit filenames — no duplicate (INV-4)."""
    graph, _ = build_full_graph_from_snapshot(
        snapshot_fixture("sibling_channel_ambiguity")
    )
    files = {a.output_filename for a in graph.output_aliases}
    assert files == {
        "twin_plant.chamber_a__power.json",
        "twin_plant.chamber_b__power.json",
    }
    yaml_text = generate_pipeline_yaml(graph, "sibling", _template_env())
    for a in graph.output_aliases:
        assert _exit_line(yaml_text, a.canonical_channel).endswith(
            f" {a.output_filename}"
        )


def test_nested_shape_b_catf_no_dropped_exit() -> None:
    """Nested shape-B (catf_mfe) renders aliased filenames and drops no exit line —
    every declared channel still has an exit, aliased or not."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("catf_mfe_model"))
    yaml_text = generate_pipeline_yaml(graph, "catf_mfe", _template_env())
    declared = {o.channel_name for m in graph.modules for o in m.outputs}
    for channel in declared:
        _exit_line(yaml_text, channel)  # raises if any channel lost its exit
    # At least one aliased channel renders a modeler filename.
    aliased = _build_alias_filename_map(graph.output_aliases)
    assert aliased
    sample_channel, sample_file = next(iter(aliased.items()))
    assert _exit_line(yaml_text, sample_channel).endswith(f" {sample_file}")
