"""Sweep legal SysML scoping/redefinition shapes for a bare-reference discriminator.

For every candidate directory beside this file this driver reports, by exact
element ID only:

* whether the model loads,
* each ``FeatureReferenceExpression``: its written text, whether the extractor
  classifies it as a bare (one-segment, unqualified) reference, the exact
  referent declaration ID and the referent's live owner ID and metatype,
* the edge the shipped resolver actually produces for the consumer, and
* the edge exact-owner selection would produce, derived from the occurrence
  whose ``effective_usage_id`` is that live owner.

A candidate discriminates when those last two disagree. Qualified names appear
only as human-readable labels; every comparison is on IDs.
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    AttrNode,
    InstanceGraph,
    NodeRef,
    ProducerRef,
    elaborate,
)
from sysml_codegen.extraction.binding_evidence import (
    WRITTEN_UNKNOWN,
    written_qualifier,
    written_reference_text,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor

ROOT = Path(__file__).parent

OWNER_METATYPES = (
    "PartUsage",
    "PartDefinition",
    "AttributeUsage",
    "ReferenceUsage",
    "CalculationUsage",
    "ConstraintUsage",
)


@dataclass(frozen=True)
class ReferenceRow:
    written: str
    bare: bool
    referent_id: str
    referent_label: str
    owner_id: str
    owner_label: str
    owner_metatype: str


def _metatype(element: Any) -> str:
    for name in OWNER_METATYPES:
        if SysideAdapter.is_instance(element, name):
            return name
    return type(element).__name__


def _element_id(element: Any) -> str:
    try:
        return str(SysideAdapter.element_id(element))
    except Exception:  # noqa: BLE001 - probe reports rather than fails
        return "<no-id>"


def _reference_rows(model: Any) -> list[ReferenceRow]:
    rows: list[ReferenceRow] = []
    for expression in SysideAdapter.elements_of_type(
        model, "FeatureReferenceExpression", include_subtypes=True
    ):
        referent = getattr(expression, "referent", None)
        if referent is None:
            continue
        owner = getattr(referent, "owning_type", None)
        written = written_reference_text(expression)
        qualifier = written_qualifier(expression)
        rows.append(
            ReferenceRow(
                written="<unknown>" if written is WRITTEN_UNKNOWN else str(written),
                bare=qualifier is None,
                referent_id=_element_id(referent),
                referent_label=str(getattr(referent, "qualified_name", None)),
                owner_id="<none>" if owner is None else _element_id(owner),
                owner_label=str(getattr(owner, "qualified_name", None)),
                owner_metatype="<none>" if owner is None else _metatype(owner),
            )
        )
    return rows


def _describe_edge(graph: InstanceGraph, edge: Any) -> str:
    if isinstance(edge, NodeRef):
        node = graph.attrs.get(edge.target)
        if node is None:
            return f"NodeRef(non-attr {edge.target.to_wire()})"
        return (
            f"attr[{node.display_path}] declaration={node.declaration_id.value} "
            f"value={node.value}"
        )
    if isinstance(edge, ProducerRef):
        return f"ProducerRef({edge.target.output.value})"
    return repr(edge)


def _owner_anchored_attr(
    graph: InstanceGraph, owner_id: str, leaf_id: str
) -> tuple[str, list[AttrNode]]:
    """The attribute exact-owner selection would reach for this leaf.

    Occurrences are matched by ``effective_usage_id`` against the live owner's
    exact element ID; the slot comes from the leaf's own node.
    """
    leaf_nodes = [
        node for node in graph.attrs.values() if str(node.declaration_id.value) == leaf_id
    ]
    if not leaf_nodes:
        return ("leaf declaration has no attribute node", [])
    slot = leaf_nodes[0].slot_id
    owner_occurrences = [
        record.occurrence_id
        for record in graph.occurrences.values()
        if str(record.effective_usage_id.value) == owner_id
    ]
    if not owner_occurrences:
        return (f"no occurrence has effective_usage_id {owner_id}", [])
    matches = [
        node
        for node in graph.attrs.values()
        if node.slot_id == slot and node.scope in owner_occurrences
    ]
    return (f"{len(owner_occurrences)} owner occurrence(s)", matches)


def _consumer_edges(graph: InstanceGraph) -> list[tuple[str, Any]]:
    edges: list[tuple[str, Any]] = []
    for node in graph.attrs.values():
        if node.alias_target is not None:
            edges.append((f"alias {node.display_path}", node.alias_target))
    for calc in graph.calcs.values():
        for port, edge in calc.inputs.items():
            name = calc.input_names.get(port, "?")
            edges.append((f"calc {calc.display_path}.{name}", edge))
    for constraint in graph.constraints.values():
        for port, edge in constraint.inputs.items():
            name = constraint.input_names.get(port, "?")
            edges.append((f"constraint {constraint.display_path}.{name}", edge))
    return edges


def run(case: Path) -> None:
    print(f"\n{'=' * 78}\n## {case.name}\n{'=' * 78}")
    print(f"command: uv run python {Path(__file__).name}  (case dir {case.name}/)")
    extractor = SysMLDataExtractor([case])
    loaded = extractor.load_models()
    print(f"loaded: {loaded}")
    for diagnostic in extractor.diagnostics.warnings:
        print(f"  load-warning: {diagnostic}")
    if not loaded:
        for diagnostic in extractor.diagnostics.errors:
            print(f"  load-error: {diagnostic}")
        return

    rows = _reference_rows(extractor.model)
    for row in rows:
        print(
            f"  ref written={row.written!r} bare={row.bare}\n"
            f"    referent id={row.referent_id} ({row.referent_label})\n"
            f"    owner    id={row.owner_id} ({row.owner_label}) metatype={row.owner_metatype}"
        )

    try:
        graph = elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
            strict=False,
        )
    except Exception:  # noqa: BLE001 - probe reports rather than fails
        print("  elaboration raised:")
        traceback.print_exc(file=sys.stdout)
        return

    for diagnostic in graph.diagnostics:
        print(f"  diagnostic: {diagnostic.code.value} {diagnostic.detail}")

    for label, edge in _consumer_edges(graph):
        print(f"  edge {label} -> {_describe_edge(graph, edge)}")

    for row in rows:
        if not row.bare or row.owner_metatype != "PartUsage":
            continue
        note, matches = _owner_anchored_attr(graph, row.owner_id, row.referent_id)
        described = [
            f"attr[{node.display_path}] declaration={node.declaration_id.value} "
            f"value={node.value}"
            for node in matches
        ]
        print(f"  owner-anchored target for {row.written!r}: {note} -> {described}")


def main() -> None:
    cases = sorted(path for path in ROOT.iterdir() if path.is_dir())
    for case in cases:
        if not any(case.glob("*.sysml")):
            continue
        run(case)


if __name__ == "__main__":
    main()
