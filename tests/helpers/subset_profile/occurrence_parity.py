"""One schema for both occurrence answers: agentic-mbse's port and codegen's own (Item 2a D6).

agentic-mbse's ``extract_occurrence_structure`` ports codegen's occurrence, attachment and
writer logic so the screen can reason about instantiation without the generator. This module
renders each side's answer for one loaded model in the same schema, so a parity test compares
like with like:

- ``normalize_agentic`` renders an ``OccurrenceStructure`` or ``OccurrenceFailure``;
- ``normalize_codegen`` asks codegen itself, through ``build_feature_slot_index``,
  ``build_occurrence_index`` and the elaborator's attachment and writer methods.

Both moved here from agentic-mbse (``tests/helpers/occurrence_oracle_schema.py`` and
``scripts/subset_profile/occurrence_oracle.py``), where codegen's side had to be captured into
stored files because agentic-mbse cannot import codegen. Here both sides run live.

Schema:

- ``roots``: generator root usage ids, sorted.
- ``visits``: ``[usage, parent path or null]`` per visit, sorted.
- ``unexpandable``: ``[usage, parent path or null, SI code]`` per visit that does not expand.
- ``occurrences``: ``{path, usage, type, closure, children}`` per occurrence, sorted by path.
- ``counts``: occurrences per effective usage.
- ``def_occurrences``: occurrences per part definition (closure membership).
- ``writers``: ``[scope key, base, selected, applicable]`` per (scope, calc slot), sorted.
- ``writers_status``: ``ok`` when any writer was selected, else ``no_calc_usages_selected``.
- ``calc_attachment``: per calc usage, ``[scope keys, cause or null]``.
- ``strict``: ``{"ok": true}``, or ``{"ok": false, "code"}`` for the first unexpandable visit
  in traversal order, which is the error the unpatched generator raises.
- An abort is ``{"fatal": {"stage", "code"}}`` only, and matches on stage and code.

A path renders as ``slot[index]/slot[index]...`` with an empty index for an unindexed step; a
scope as ``occ:<path>`` or ``pkg:<package id>``.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from agentic_mbse.sysml.occurrence_facts import (
    MultiplicityResolution,
    OccurrenceAbort,
    OccurrenceFailure,
    OccurrenceScope,
    OccurrenceStructure,
    PathStep,
    Scope,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import elaborate as cg_elaborate
from sysml_codegen.elaboration import occurrence as cg_occurrence
from sysml_codegen.elaboration.identity import OccurrenceId, PackageScopeId, declaration_id_for

#: ``elaboration/occurrence.py`` ``_multiplicity_indices``: the code it raises for each
#: multiplicity the port classes as unexpandable.
RESOLUTION_TO_CODE: Mapping[MultiplicityResolution, str] = {
    MultiplicityResolution.ORDERED: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.NONUNIQUE: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.RANGE: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.UNRESOLVED_UPPER: "SI_MULTIPLICITY_UNRESOLVED",
    MultiplicityResolution.UNRESOLVED_LOWER: "SI_MULTIPLICITY_UNRESOLVED",
    MultiplicityResolution.NEGATIVE: "SI_MULTIPLICITY_INVALID",
}

#: The code each port abort mirrors (``InvalidRedefinitionFamilyError``,
#: ``RecursiveContainmentError``, ``ElaborationInvariantError``, ``IdentityBoundaryError``).
ABORT_TO_CODE: Mapping[OccurrenceAbort, str] = {
    OccurrenceAbort.SPECIALIZATION_CYCLE: "SI_CONTAINMENT_RECURSIVE",
    OccurrenceAbort.RECURSIVE_CONTAINMENT: "SI_CONTAINMENT_RECURSIVE",
    OccurrenceAbort.INCOMPARABLE_TYPINGS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.REPEATED_NATIVE_DECLARATION: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.DUPLICATE_OCCURRENCE_IDENTITY: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.REDEFINITION_ROOT_FAMILY: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.EFFECTIVE_DECLARATION_AMBIGUOUS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.WRITER_AMBIGUOUS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.IDENTITY_UNSTABLE: "SI_ID_UNSTABLE",
}


# ---- agentic-mbse's port ------------------------------------------------------------------------


def _render_path(path: tuple[PathStep, ...]) -> str:
    return "/".join(f"{step.slot}[{'' if step.index is None else step.index}]" for step in path)


def _render_scope(scope: Scope) -> str:
    if isinstance(scope, OccurrenceScope):
        return "occ:" + _render_path(scope.path)
    return f"pkg:{scope.package_id}"


def _parent_key(parent: tuple[PathStep, ...] | None) -> str | None:
    return None if parent is None else _render_path(parent)


def normalize_agentic(result: OccurrenceStructure | OccurrenceFailure) -> dict[str, Any]:
    """Render the port's answer for one model.

    Only generator reach has a codegen equivalent, so a structure with caller roots is refused
    rather than rendered with them dropped.
    """
    if isinstance(result, OccurrenceFailure):
        return {"fatal": {"stage": result.stage.value, "code": ABORT_TO_CODE[result.abort]}}
    if result.caller_root_ids:
        raise ValueError("codegen has no caller roots to compare; got caller roots")
    unexpandable = [v for v in result.visits if v.count is None]
    first = unexpandable[0] if unexpandable else None
    return {
        "roots": sorted(str(r) for r in result.generator_root_ids),
        "visits": sorted(
            ([str(v.usage_id), _parent_key(v.parent)] for v in result.visits),
            key=lambda c: (c[0] or "", c[1] or ""),
        ),
        "unexpandable": sorted(
            (
                [str(v.usage_id), _parent_key(v.parent), RESOLUTION_TO_CODE[v.reading.resolution]]
                for v in unexpandable
            ),
            key=lambda c: (c[0] or "", c[1] or ""),
        ),
        "occurrences": sorted(
            (
                {
                    "path": _render_path(n.path),
                    "usage": str(n.usage_id),
                    "type": None if n.type_id is None else str(n.type_id),
                    "closure": sorted(str(t) for t in n.type_closure),
                    "children": sorted(str(c) for c in n.child_ids),
                }
                for n in result.nodes
            ),
            key=lambda r: str(r["path"]),
        ),
        "counts": {
            str(k): v
            for k, v in sorted(result.occurrence_counts().items(), key=lambda i: str(i[0]))
        },
        "def_occurrences": {
            str(d): result.definition_occurrence_count(d) for d in result.part_definition_ids
        },
        "writers": sorted(
            [
                _render_scope(w.scope),
                str(w.base_id),
                str(w.selected_id),
                sorted(str(a) for a in w.applicable_ids),
            ]
            for w in result.writers
        ),
        "writers_status": "ok" if result.writers else "no_calc_usages_selected",
        "calc_attachment": {
            str(a.usage_id): [
                sorted(_render_scope(s) for s in a.scopes),
                None if a.cause is None else a.cause.value,
            ]
            for a in result.calc_attachments
        },
        "strict": (
            {"ok": True}
            if first is None
            else {"ok": False, "code": RESOLUTION_TO_CODE[first.reading.resolution]}
        ),
    }


# ---- codegen ------------------------------------------------------------------------------------


def _uuid(declaration: Any) -> str:
    return str(declaration.value if hasattr(declaration, "value") else declaration)


def _did(element: Any) -> str:
    return _uuid(declaration_id_for(element))


def _occurrence_path(occurrence_id: OccurrenceId) -> str:
    return "/".join(
        f"{_uuid(step.containment_slot.root_declaration)}"
        f"[{'' if step.occurrence_index is None else step.occurrence_index}]"
        for step in occurrence_id.steps
    )


def _scope_key(scope: OccurrenceId | PackageScopeId) -> str:
    if isinstance(scope, PackageScopeId):
        return "pkg:" + _uuid(scope.package_declaration)
    return "occ:" + _occurrence_path(scope)


def _error_code(error: BaseException) -> str:
    code = getattr(error, "code", None)
    return str(getattr(code, "value", code))


class _StopAfterWritersError(Exception):
    """Ends ``_build_calculation_nodes`` once its writer-selection loop has run."""


def _codegen_writers(model: Any, slots: Any, index: Any) -> tuple[list[list[Any]], str, dict]:
    """Writer selection and attachment, from codegen's own elaborator methods.

    Runs on a bare elaborator carrying only the slot and occurrence indexes. Its
    ``_typed_definition`` raises once the writer-selection loop, which runs before that call,
    has finished.
    """
    elaborator = cg_elaborate._ExactElaborator.__new__(cg_elaborate._ExactElaborator)
    elaborator._model = model
    elaborator._slots = slots
    elaborator._occurrences = index
    elaborator._scope_display = {o.occurrence_id: o.display_path for o in index.occurrences()}
    selections: list[list[Any]] = []
    select_writer = elaborator._select_writer

    def recording_select(base: Any, applicable: Any, scope: Any) -> Any:
        chosen = select_writer(base, applicable, scope)
        selections.append(
            [_scope_key(scope), _did(base), _did(chosen), sorted(_did(a) for a in applicable)]
        )
        return chosen

    def stop(*_args: Any, **_kwargs: Any) -> Any:
        raise _StopAfterWritersError

    elaborator._select_writer = recording_select  # type: ignore[method-assign]
    elaborator._typed_definition = stop  # type: ignore[method-assign]
    try:
        elaborator._build_calculation_nodes()
        status = "no_calc_usages_selected"
    except _StopAfterWritersError:
        status = "ok"
    attachment = {}
    for usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        scopes, cause = elaborator._attachment(cg_occurrence.semantic_owner(usage))
        attachment[_did(usage)] = [sorted(_scope_key(s) for s in scopes), cause]
    return sorted(selections), status, dict(sorted(attachment.items()))


def normalize_codegen(model: Any) -> dict[str, Any]:
    """Render codegen's own occurrence answer for one model.

    The strict build is codegen's unpatched behaviour: success, or the first multiplicity
    error. The per-usage answer comes from a second build in which ``_multiplicity_indices``
    records a ``MultiplicityExpansionError`` and yields no occurrences for that usage instead of
    aborting, so every unexpandable visit is reported, not only the first.
    """
    try:
        slots = cg_occurrence.build_feature_slot_index(model)
    except Exception as error:
        return {"fatal": {"stage": "slots", "code": _error_code(error)}}
    try:
        cg_occurrence.build_occurrence_index(model, slots)
        strict: dict[str, Any] = {"ok": True}
    except cg_occurrence.MultiplicityExpansionError as error:
        strict = {"ok": False, "code": _error_code(error)}
    except Exception as error:
        return {"fatal": {"stage": "occurrences", "code": _error_code(error)}}

    multiplicity_indices = cg_occurrence._multiplicity_indices
    visits: list[list[Any]] = []
    unexpandable: list[list[Any]] = []

    def recording(usage: Any, *, parent: Any, **kwargs: Any) -> Any:
        parent_path = _occurrence_path(parent.occurrence_id) if parent else None
        visits.append([_did(usage), parent_path])
        try:
            return multiplicity_indices(usage, parent=parent, **kwargs)
        except cg_occurrence.MultiplicityExpansionError as error:
            unexpandable.append([_did(usage), parent_path, error.code.value])
            return ()

    cg_occurrence._multiplicity_indices = recording
    try:
        index = cg_occurrence.build_occurrence_index(model, slots)
    finally:
        cg_occurrence._multiplicity_indices = multiplicity_indices

    counts: dict[str, int] = defaultdict(int)
    for occurrence in index.occurrences():
        counts[_uuid(occurrence.effective_usage_id)] += 1
    writers, writers_status, attachment = _codegen_writers(model, slots, index)
    return {
        "roots": sorted({usage for usage, parent in visits if parent is None}),
        "visits": sorted(visits, key=lambda c: (c[0], c[1] or "")),
        "unexpandable": sorted(unexpandable, key=lambda c: (c[0], c[1] or "")),
        "occurrences": sorted(
            (
                {
                    "path": _occurrence_path(o.occurrence_id),
                    "usage": _uuid(o.effective_usage_id),
                    "type": _uuid(o.effective_type_id) if o.effective_type_id else None,
                    "closure": sorted(_uuid(t) for t in o.type_closure),
                    "children": sorted(_uuid(c) for c in o.child_declaration_ids),
                }
                for o in index.occurrences()
            ),
            key=lambda r: r["path"],
        ),
        "counts": dict(sorted(counts.items())),
        "def_occurrences": {
            _did(d): len(index.occurrences_for_type(declaration_id_for(d)))
            for d in SysideAdapter.elements_of_type(model, "PartDefinition")
            if getattr(d, "qualified_name", None) is not None
        },
        "writers": writers,
        "writers_status": writers_status,
        "calc_attachment": attachment,
        "strict": strict,
    }


def differences(codegen: Mapping[str, Any], agentic: Mapping[str, Any]) -> list[str]:
    """One line per item where the two renderings differ."""
    lines: list[str] = []
    for key in sorted(set(codegen) | set(agentic)):
        want, got = codegen.get(key), agentic.get(key)
        if want == got:
            continue
        if isinstance(want, list) and isinstance(got, list):
            want_set, got_set = {repr(x) for x in want}, {repr(x) for x in got}
            lines += [f"{key}: codegen only {x}" for x in sorted(want_set - got_set)]
            lines += [f"{key}: agentic-mbse only {x}" for x in sorted(got_set - want_set)]
        elif isinstance(want, dict) and isinstance(got, dict):
            for sub in sorted(set(want) | set(got)):
                if want.get(sub) != got.get(sub):
                    lines.append(
                        f"{key}[{sub}]: codegen {want.get(sub)!r} agentic-mbse {got.get(sub)!r}"
                    )
        else:
            lines.append(f"{key}: codegen {want!r} agentic-mbse {got!r}")
    return lines
