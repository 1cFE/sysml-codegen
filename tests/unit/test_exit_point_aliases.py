"""Unit tests for the Item 11 (SC-7) exit-point filename override.

An aliased channel's exit line renders the modeler's instance-qualified name as
its output filename (``{instance_path}__{alias_name}.json``); the exit **key**
stays the canonical channel (D3 — verified against simkit). Unaliased lines are
byte-identical to today's ``{channel}.json``.

One layer: mechanism (``_build_alias_filename_map`` / ``_build_exit_points``) on
controlled inputs — the alias, tie-break and default-filename branches. The end-to-end
layer rendered ``generate_pipeline_yaml`` over committed v5 snapshots and retired with
the v5 family (retirement step 1).
"""

from __future__ import annotations

from sysml_codegen.generation.pipeline import (
    _build_alias_filename_map,
    _build_exit_points,
)
from sysml_codegen.resolution.models import (
    ModuleKind,
    ModuleOutput,
    OutputAlias,
    PipelineModule,
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
        module_kind=ModuleKind.CALCULATION,
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
