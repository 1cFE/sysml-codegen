"""The one producer-resolution authority (Item 2).

Built incrementally, de-risk first. This module currently holds only the entry-point
QN rule (D9) — the single decision that can move every generated baseline, pinned
against all three current formulas before any consumer is cut over (risk R3).

The ordered key-form table, the request/result types, and the terminal fork land in
the cutover phases. Nothing here is wired into a consumer yet.
"""

from __future__ import annotations

__all__ = ["entry_point_qualified_name"]


def entry_point_qualified_name(
    *, consumer_eqn: str, reference: str, param_name: str | None
) -> str:
    """The QN of an entry point minted by a lenient terminal miss (D9).

    One rule for all three lenient consumers, chosen to reproduce every formula
    already in the tree byte-for-byte:

    - the calculation binding path (`dependency_backtracker.py:76`) keys on the
      consumer's declared formal, which a calc binding always has;
    - the aggregation term path (`input_resolver.py:281-282`) has no formal, so it
      keys on the reference with its dots flattened to underscores;
    - the aggregation LocalTerm path (`graph_builder.py:1524-1525`) also has no
      formal, and its reference is a bare attribute name, which flattens to itself.

    ``param_name`` is the consumer's declared formal name where it has one, and
    ``None`` where it does not.
    """
    key = param_name if param_name is not None else reference.replace(".", "_")
    return f"{consumer_eqn}__{key}"
