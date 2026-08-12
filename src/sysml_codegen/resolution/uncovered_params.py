"""Params-coverage collectors for the fell-through, valueless entry points.

The two halves of the M1 partition (Item 7 / D4). Both are pure: they read a
``ComputationGraph`` and return findings, and the generation boundary decides
what a finding means — V11 abort for the wired half, a WARNING summary for the
unwired remainder.

They lived in ``resolution/graph_builder.py`` until Gate 4B-G0 moved them here, ahead
of that module's retirement with the v5 family (retirement step 2), because they are
live public-route code the CLI calls on every run.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ComputationGraph


@dataclass(frozen=True)
class UncoveredInput:
    """A module input wired to a params key that no parameter group provides.

    A genuine coverage gap (Item 7 / D4): a bound binding that fell through all
    resolution (its EP QN is in ``fallback_entry_points``), carries no value
    (EP ``default_value is None``), and is still referenced by a surviving
    module input. The pipeline emits the params key but the JSON never mints it
    — a guaranteed runtime ``KeyError`` at load. Names the offender precisely.
    """

    module: str
    input: str
    missing_key: str


def collect_uncovered_params(graph: ComputationGraph) -> list[UncoveredInput]:
    """Return every module input wired to an uncovered params key.

    Pure (INV-3): returns a (possibly empty) list, raises nothing. Only the
    generation boundary raises V11 on a non-empty result.

    A module ``entry_point`` input is a violation when all three hold:
    - its ``qualified_name`` is in ``graph.fallback_entry_points`` (fell through
      Step-4),
    - its entry point carries no value (``default_value is None`` — valueless),
    - a surviving module input references it (wired — the iteration itself).

    Fell-through EPs that carry a value (a bound literal parsed to a float, or a
    deriver-back-filled default) and non-fall-through null-default EPs
    (legitimate user-fill) are not violations.
    """
    # Index entry point default values by qualified name (valueless test).
    ep_default: dict[str, float | None] = {}
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            ep_default[ep.qualified_name] = ep.default_value

    violations: list[UncoveredInput] = []
    for module in graph.modules:
        for inp in module.inputs:
            src = inp.source
            if src.source_type != "entry_point" or not src.qualified_name:
                continue
            qn = src.qualified_name
            if qn not in graph.fallback_entry_points:
                continue
            # Valueless: the entry point carries no default (None). A fell-through
            # EP that got a value is minted normally and is not a gap.
            if ep_default.get(qn) is not None:
                continue
            missing_key = (
                f"{src.param_group}.{qn}" if src.param_group else qn
            )
            violations.append(
                UncoveredInput(
                    module=module.name,
                    input=inp.param_name,
                    missing_key=missing_key,
                )
            )
    return violations


def collect_unwired_fallthrough(graph: ComputationGraph) -> list[str]:
    """Return fell-through, valueless entry points that no module input wires.

    The other half of the M1 partition (Item 7): fell-through ∧ valueless ∧
    **unwired**. These carry no value but nothing references them, so they are
    tracked residue (reconciliation summary, WARNING) — not a runtime
    ``KeyError`` like the wired half (V11). Pure; returns a sorted QN list.
    """
    ep_default: dict[str, float | None] = {}
    for group in graph.entry_point_groups:
        for ep in group.parameters:
            ep_default[ep.qualified_name] = ep.default_value

    wired: set[str] = {
        inp.source.qualified_name
        for module in graph.modules
        for inp in module.inputs
        if inp.source.source_type == "entry_point" and inp.source.qualified_name
    }

    remainder: list[str] = []
    for qn in graph.fallback_entry_points:
        if qn in wired:
            continue
        if ep_default.get(qn) is not None:  # valueless only
            continue
        remainder.append(qn)
    return sorted(remainder)


__all__ = ["UncoveredInput", "collect_uncovered_params", "collect_unwired_fallthrough"]
