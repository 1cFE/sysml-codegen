#!/usr/bin/env python3
"""Capture what the shipped resolver actually does at every usage-owned one-segment site.

This is acceptance evidence for
``.project/completed/20260816_qualified-reference-occurrence-anchoring/``. Run it once before the
resolver repair (``before.json``) and once after (``after.json``); every difference is
then adjudicated as a fix or a regression.

**It is not a second resolver.** It never predicts an edge, never re-implements owner
selection, and never decides anything from source text. For each site it records the
exact leaf and owner declaration IDs, the caller lane, and then reads back what the
shipped elaborator produced: a typed edge, the full diagnostic that replaced it, or a
named structural reason why neither exists. Written reference text is carried as a
classification key for a human reader and is never compared.

Sites are keyed by typed identity — ``(root, lane, consumer node, reference ordinal,
leaf declaration)`` — so a run compares to a previous run without depending on file
offsets, ordering, or names.

Usage::

    set -a; source ../agentic-mbse/.env; set +a
    uv run python .project/completed/20260816_qualified-reference-occurrence-anchoring/\
verification/corpus_compare.py --output <path>

Output is canonical JSON: sorted keys, sorted rows, repository-relative paths, no
timestamps. Two runs of the same tree are byte-identical.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.elaborate import (
    _blocking_model_validation_diagnostics,
    _ExactElaborator,
    _UnsupportedExpressionError,
)
from sysml_codegen.elaboration.graph import (
    ConstraintNode,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    ProducerRef,
)
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    OccurrenceId,
)
from sysml_codegen.extraction.binding_evidence import WRITTEN_UNKNOWN, written_reference_text
from sysml_codegen.extraction.extractor import SysMLDataExtractor

REPO = Path(__file__).resolve().parents[4]
ROOTS_FILE = Path(__file__).with_name("corpus_roots.json")
PROMOTED_ROOTS_FILE = Path(__file__).with_name("promoted_roots.json")

#: The metatypes a leaf's live semantic owner is reported as. Anything else is reported
#: by its Python class name, which keeps an unexpected owner kind visible rather than
#: collapsing it into "other".
OWNER_METATYPES = (
    "PartUsage",
    "PartDefinition",
    "AttributeUsage",
    "ReferenceUsage",
    "CalculationUsage",
    "CalculationDefinition",
    "ConstraintUsage",
    "ConstraintDefinition",
)

#: Closed vocabulary for a site that has neither an edge nor a diagnostic. Every one of
#: these is a structural fact about the model, not a resolution outcome.
NO_EDGE_REASONS = (
    "expression_unsupported",  # the caller refused the whole expression before resolving
    "fact_without_leaf",  # the resolved reference carries no leaf declaration
    "port_absent_without_diagnostic",  # unexplained: the resolver produced neither
)


# --------------------------------------------------------------------------- roots


def frozen_roots() -> dict[str, Any]:
    """The pre-existing tracked root set, frozen before this item promoted any fixture."""
    if not ROOTS_FILE.exists():
        raise FileNotFoundError(
            f"{ROOTS_FILE} is missing; the corpus root set is frozen evidence and is "
            "never rediscovered at run time"
        )
    payload: dict[str, Any] = json.loads(ROOTS_FILE.read_text())
    return payload


def promoted_roots() -> list[str]:
    """Fixture roots this item added, frozen independently of later work."""
    if not PROMOTED_ROOTS_FILE.exists():
        raise FileNotFoundError(
            f"{PROMOTED_ROOTS_FILE} is missing; the promoted root set is frozen "
            "evidence and is never rediscovered at run time"
        )
    payload: dict[str, Any] = json.loads(PROMOTED_ROOTS_FILE.read_text())
    return payload["roots"]


# --------------------------------------------------------------------------- helpers


def owner_metatype(element: Any) -> str:
    for name in OWNER_METATYPES:
        if SysideAdapter.is_instance(element, name):
            return name
    return type(element).__name__


def semantic_owner(element: Any) -> Any:
    return getattr(element, "owning_type", None) or getattr(element, "owner", None)


def edge_wire(edge: Any) -> str:
    if isinstance(edge, NodeRef):
        return "node:" + str(edge.target.to_wire())
    if isinstance(edge, ProducerRef):
        return "producer:" + str(edge.target.output.to_wire())
    if isinstance(edge, LiteralInput):
        return "literal:" + repr(edge.value)
    raise TypeError(f"unknown edge kind {type(edge).__name__}")


def scope_wire(scope: Any) -> str:
    if isinstance(scope, OccurrenceId):
        return "occurrence:" + str(scope.to_wire())
    return "package:" + str(scope.package_declaration.to_wire())


def diagnostic_rows(
    graph: InstanceGraph, consumer_id: Any, param_name: str | None
) -> list[list[str | None]]:
    """The full diagnostics the shipped elaborator attributed to this consumer port.

    A diagnostic with no ``param_name`` belongs to the whole consumer — an expression or
    predicate lane reports that way — so it is attributed to every site on that consumer.
    """
    return sorted(
        [
            diagnostic.code.value,
            diagnostic.param_name,
            diagnostic.detail,
        ]
        for diagnostic in graph.diagnostics
        if diagnostic.consumer == consumer_id and diagnostic.param_name in (None, param_name)
    )


def outcome(
    graph: InstanceGraph,
    edges: list[Any],
    consumer_id: Any,
    param_name: str | None,
) -> dict[str, Any]:
    """One site's shipped result: an edge, the diagnostic that replaced it, or a reason.

    The order matters and is the whole point. An edge is the answer when there is one; a
    diagnostic is the answer when the resolver refused; a named reason is what is left,
    and ``port_absent_without_diagnostic`` exists so that "left" is never silent.
    """
    if edges:
        return {"kind": "edge", "edges": sorted(edge_wire(edge) for edge in edges)}
    found = diagnostic_rows(graph, consumer_id, param_name)
    if found:
        return {"kind": "diagnostic", "diagnostics": found}
    return {"kind": "no_edge", "reason": "port_absent_without_diagnostic"}


def site_row(
    *,
    root: str,
    lane: str,
    consumer: str | None,
    consumer_scope: str,
    reference_ordinal: int,
    leaf: DeclarationId,
    owner: Any,
    plural_caller: bool,
    written: str | None,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "root": root,
        "lane": lane,
        "consumer": consumer,
        "consumer_scope": consumer_scope,
        "reference_ordinal": reference_ordinal,
        "leaf_declaration": leaf.to_wire(),
        "owner_declaration": None if owner is None else str(SysideAdapter.element_id(owner)),
        "owner_metatype": None if owner is None else owner_metatype(owner),
        "plural_caller": plural_caller,
        "written_text": written,  # classification metadata for a reader; never compared
        "outcome": result,
    }


def site_key(row: dict[str, Any]) -> tuple:
    return (
        row["root"],
        row["lane"],
        row["consumer"] or "",
        row["reference_ordinal"],
        row["leaf_declaration"],
    )


# ------------------------------------------------------------------- site discovery


def live_features(model: Any) -> dict[DeclarationId, Any]:
    """Every live ``Feature`` keyed by its parser element ID.

    Deliberately wider than the elaborator's own ``_elements`` index, which drops any
    Feature without a ``qualified_name``. Looking a leaf up here rather than there is
    what keeps this ledger from sharing the resolver's blind spot: a leaf the elaborator
    cannot see is still measured, and its shipped outcome recorded, instead of silently
    leaving the population.
    """
    return {
        DeclarationId(SysideAdapter.element_id(element)): element
        for element in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
    }


def usage_owned_one_segment(
    elements: dict[DeclarationId, Any], fact: Any
) -> tuple[Any, Any] | None:
    """``(leaf declaration, live owner)`` when the site is in the branch's population.

    The population is exactly what the repaired branch will act on: a reference of one
    segment whose exact leaf is owned by a live ``PartUsage``. Everything else is out of
    scope for this ledger and is counted, not rowed.
    """
    if fact.leaf is None or len(fact.segment_element_ids) != 1:
        return None
    leaf = DeclarationId(fact.leaf.element_id)
    element = elements.get(leaf)
    if element is None:
        return None
    owner = semantic_owner(element)
    if owner is None or not SysideAdapter.is_instance(owner, "PartUsage"):
        return None
    return leaf, owner


def written_text(expression: Any) -> str | None:
    written = written_reference_text(expression)
    return None if written is WRITTEN_UNKNOWN else str(written)


def alias_sites(
    elaborator: Any, graph: InstanceGraph, root: str, elements: dict[DeclarationId, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pending in elaborator._pending_aliases:
        for ordinal, leaf, owner, plural in _reference_terms(
            elaborator, pending.expression, elements
        ):
            target = pending.node.alias_target
            rows.append(
                site_row(
                    root=root,
                    lane="alias",
                    consumer=pending.node.node_id.to_wire(),
                    consumer_scope=scope_wire(pending.node.scope),
                    reference_ordinal=ordinal,
                    leaf=leaf,
                    owner=owner,
                    plural_caller=plural,
                    written=written_text(pending.expression),
                    result=outcome(
                        graph,
                        [] if target is None else [target],
                        pending.node.node_id,
                        None,
                    ),
                )
            )
    return rows


def expression_sites(
    elaborator: Any, graph: InstanceGraph, root: str, elements: dict[DeclarationId, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pending in elaborator._pending_expressions:
        consumer = pending.consumer
        is_predicate = isinstance(consumer, ConstraintNode)
        for ordinal, leaf, owner, plural in _reference_terms(
            elaborator, pending.expression, elements
        ):
            if is_predicate:
                port = ConsumerPortId(consumer.node_id, leaf)
                edges = [consumer.inputs[port]] if port in consumer.inputs else []
            else:
                edges = [
                    edge
                    for port, edge in consumer.inputs.items()
                    if isinstance(port, ExpressionPortId)
                    and port.reference_ordinal == ordinal
                    and port.referenced_declaration == leaf
                ]
            rows.append(
                site_row(
                    root=root,
                    lane="constraint_predicate" if is_predicate else "computed_expression",
                    consumer=consumer.node_id.to_wire(),
                    consumer_scope=scope_wire(consumer.scope),
                    reference_ordinal=ordinal,
                    leaf=leaf,
                    owner=owner,
                    plural_caller=plural,
                    written=written_text(pending.expression),
                    result=outcome(graph, edges, consumer.node_id, None),
                )
            )
    return rows


def binding_sites(
    elaborator: Any, graph: InstanceGraph, root: str, elements: dict[DeclarationId, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pending in elaborator._pending_bindings:
        fact = pending.evidence.semantic_reference
        if fact is None:
            continue
        found = usage_owned_one_segment(elements, fact)
        if found is None:
            continue
        leaf, owner = found
        consumer = pending.consumer
        edges = [consumer.inputs[pending.port]] if pending.port in consumer.inputs else []
        param = consumer.input_names.get(pending.port)
        rows.append(
            site_row(
                root=root,
                lane=(
                    "constraint_binding" if isinstance(consumer, ConstraintNode) else "calc_binding"
                ),
                consumer=consumer.node_id.to_wire(),
                consumer_scope=scope_wire(consumer.scope),
                reference_ordinal=0,
                leaf=leaf,
                owner=owner,
                plural_caller=False,
                written=pending.evidence.written_text,
                result=outcome(graph, edges, consumer.node_id, param),
            )
        )
    return rows


def _reference_terms(
    elaborator: Any, expression: Any, elements: dict[DeclarationId, Any]
) -> list[tuple[int, Any, Any, bool]]:
    """In-population reference terms of one authored expression, with their ordinals.

    The ordinal comes from the shipped fact walk, which is the same walk the resolver
    used to mint ``ExpressionPortId``s — so the join back to a port is exact rather than
    reconstructed. Producing facts is not resolving: no edge is chosen here.
    """
    try:
        facts = elaborator._expression_references(expression, plural=False)
    except _UnsupportedExpressionError:
        return []
    terms: list[tuple[int, Any, Any, bool]] = []
    for ordinal, (fact, plural) in enumerate(facts):
        found = usage_owned_one_segment(elements, fact)
        if found is None:
            continue
        leaf, owner = found
        terms.append((ordinal, leaf, owner, plural))
    return terms


def unsupported_expression_consumers(elaborator: Any) -> list[str]:
    """Consumers whose whole expression the caller refused before any site could resolve."""
    refused: list[str] = []
    for pending in (*elaborator._pending_aliases, *elaborator._pending_expressions):
        node = getattr(pending, "node", None) or pending.consumer
        try:
            elaborator._expression_references(pending.expression, plural=False)
        except _UnsupportedExpressionError:
            refused.append(node.node_id.to_wire())
    return sorted(refused)


def deep_override_accounting(elaborator: Any) -> dict[str, Any]:
    """How many deep-literal-override targets there are, and how long their paths are.

    The deep-override caller shares the repaired resolver, but D11's bounded search found
    no one-segment usage-owned target for it. This counts the lane's live sites and their
    segment lengths so that "none" stays a measurement rather than an omission.
    """
    lengths: list[int] = []
    for feature in SysideAdapter.elements_of_type(
        elaborator._model, "Feature", include_subtypes=True
    ):
        if getattr(feature, "qualified_name", None) is not None:
            continue
        if getattr(feature, "feature_value_expression", None) is None:
            continue
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = getattr(relationship, "redefined_feature", None)
            chain = list(getattr(redefined, "chaining_features", ()) or ())
            if chain:
                lengths.append(len(chain))
    return {
        "sites": len(lengths),
        "one_segment_sites": sum(1 for length in lengths if length == 1),
        "segment_lengths": sorted(set(lengths)),
    }


# --------------------------------------------------------------------------- capture


def capture_root(root: str) -> dict[str, Any]:
    """Everything one model root contributes to the ledger, or why it contributes nothing."""
    result: dict[str, Any] = {"root": root}
    path = REPO / root
    extractor = SysMLDataExtractor([path])
    try:
        if not extractor.load_models():
            result["refused"] = "load_models returned false"
            return result
        definitions = extractor.extract_calculation_definitions()
    except Exception as error:  # noqa: BLE001 - a refusing root is a row, not a crash
        result["refused"] = f"{type(error).__name__}: {error}"
        return result

    blocking = _blocking_model_validation_diagnostics(
        extractor.model, extractor.diagnostics.validation
    )
    if blocking:
        result["refused"] = "model validation blocked"
        result["blocking_codes"] = sorted(item.code.value for item in blocking)
        return result

    try:
        elaborator = _ExactElaborator(
            extractor.model, definitions, model_paths=[path], strict=False
        )
        graph = elaborator.run()
    except Exception as error:  # noqa: BLE001 - a refusing root is a row, not a crash
        result["refused"] = f"elaboration raised {type(error).__name__}: {error}"
        return result

    elements = live_features(extractor.model)
    rows = [
        *alias_sites(elaborator, graph, root, elements),
        *expression_sites(elaborator, graph, root, elements),
        *binding_sites(elaborator, graph, root, elements),
    ]
    result["sites"] = sorted(rows, key=site_key)
    result["diagnostics"] = sorted(
        [
            diagnostic.code.value,
            diagnostic.consumer_display,
            diagnostic.param_name,
            diagnostic.detail,
        ]
        for diagnostic in graph.diagnostics
    )
    result["unsupported_expression_consumers"] = unsupported_expression_consumers(elaborator)
    result["deep_override_lane"] = deep_override_accounting(elaborator)
    result["identity"] = identity_records(graph)
    return result


def identity_records(graph: InstanceGraph) -> dict[str, Any]:
    """The identities the repair is forbidden to move.

    Occurrence records and slot-derived node IDs are frozen here so a later run can
    compare them exactly, rather than a reader comparing them by eye.
    """
    return {
        "occurrences": sorted(
            "|".join(
                [
                    record.occurrence_id.to_wire(),
                    "" if record.parent_id is None else record.parent_id.to_wire(),
                    record.containment_slot.root_declaration.to_wire(),
                    repr(record.occurrence_index),
                    record.effective_usage_id.to_wire(),
                ]
            )
            for record in graph.occurrences.values()
        ),
        "attribute_nodes": sorted(node.node_id.to_wire() for node in graph.attrs.values()),
        "calculation_nodes": sorted(node.node_id.to_wire() for node in graph.calcs.values()),
        "constraint_nodes": sorted(node.node_id.to_wire() for node in graph.constraints.values()),
    }


def totals(sections: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    counts: dict[str, Any] = {}
    for name, captured in sections.items():
        rows = [row for item in captured for row in item.get("sites", [])]
        counts[name] = {
            "roots": len(captured),
            "roots_refused": sum(1 for item in captured if "refused" in item),
            "sites": len(rows),
            "by_lane": {
                lane: sum(1 for row in rows if row["lane"] == lane)
                for lane in sorted({row["lane"] for row in rows})
            },
            "by_outcome": {
                kind: sum(1 for row in rows if row["outcome"]["kind"] == kind)
                for kind in sorted({row["outcome"]["kind"] for row in rows})
            },
            "deep_override_one_segment_sites": sum(
                item.get("deep_override_lane", {}).get("one_segment_sites", 0) for item in captured
            ),
        }
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    roots = frozen_roots()
    corpus = [capture_root(root) for root in roots["roots"]]
    added = [capture_root(root) for root in promoted_roots()]

    payload = {
        "corpus_roots": roots,
        "corpus": corpus,
        "promoted": added,
        "totals": totals({"corpus": corpus, "promoted": added}),
    }
    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["totals"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
