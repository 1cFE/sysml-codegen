"""The aggregation LocalTerm mint resolves its modeled default (Item 2, obligation 4).

`agg_localterm_probe` is the only committed model that reaches that mint: `markup` is a
plain literal attribute on the aggregating part def, so it is neither a sibling
aggregation output nor an EXPOSE alias. Before Item 2 the mint ignored the modeled
literal entirely and produced a defaultless entry point with no diagnostic — the exact
"silent LocalTerm mint" inventory row 6 names.

The default now comes from the shared producer-resolution table, not from a bespoke
literal grab, so it is the same machinery every other consumer's default comes from.
"""

from __future__ import annotations

from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

_MARKUP_QN = "AggLocalTermProbe__the_bank__capital_cost__markup"


def _entry_points(fixture: str) -> dict[str, object]:
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture(fixture))
    return {
        ep.qualified_name: ep
        for group in graph.entry_point_groups
        for ep in group.parameters
    }


def test_localterm_entry_point_carries_its_modeled_default():
    """SR-R16: an entry point is created once, with its modeled default resolved at
    creation. `markup = 1.15` is declared on the part def and must reach the parameter."""
    entry_point = _entry_points("agg_localterm_probe")[_MARKUP_QN]
    assert entry_point.default_value == 1.15


def test_localterm_entry_point_is_rendered_in_a_parameter_group():
    """The parameter reaches a rendered group, so it is a usable typed entry point.

    Recorded as unchanged: the `param_group` *field* on a LocalTerm mint is `None` both
    before and after Item 2 — `group_deriver.classify` does not claim this QN shape. The
    parameter is still emitted, via the group rebuild that follows aggregation module
    construction. Item 2 fixed the missing default, not the field; whether that field
    should be populated is a classification question, not a resolution one.
    """
    assert _MARKUP_QN in _entry_points("agg_localterm_probe")
    assert _entry_points("agg_localterm_probe")[_MARKUP_QN].param_group is None


def test_solar_battery_local_terms_never_reach_the_mint():
    """The preservation half of obligation 4.

    `solar_battery_model`'s five local terms all resolve positively — three as sibling
    aggregation outputs, one through an EXPOSE alias — so none of them reaches the
    LocalTerm mint and none of their bytes moved. If a future change routes them through
    the mint, this fails rather than silently re-keying them.
    """
    minted = [
        qn
        for qn in _entry_points("solar_battery_model")
        if qn.endswith(("__capital_cost", "__raw_material_cost", "__misc_hardware_cost"))
        and "__idiot_index__" in qn
    ]
    assert minted == [], f"solar_battery local terms reached the mint: {minted}"
