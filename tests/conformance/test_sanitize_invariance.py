"""Phase-0 static de-risk scans for Identifier Sanitization (Item 5).

Two license-free scans that gate the whole direction, proven against the
committed corpus rather than by regex reasoning:

1. INV-1 (no-op precondition). A per-segment ``sanitize_name`` is byte-identity
   on every *already-identifier-safe* segment in every committed extraction
   snapshot. This is the property that makes the derivation-layer sanitize a
   true no-op on existing models (INV-4). Segments that DO change under sanitize
   are exactly the quoted SysML names (``'Unit Cost Calc'`` -> ``Unit_Cost_Calc``),
   which is the fix's target; those are the intentional-change class, not the
   dangerous one. The dangerous class -- an identifier-safe segment that still
   changes (leading/trailing ``_``, an internal ``__`` run, or a Python keyword)
   -- must be empty, because such a change would silently alter a generating
   model's output.

2. B4/D5 gate. No committed model hits the SC-11 grandparent-collision case
   (two same-named class scopes under different grandparents sharing a parent),
   which the alias scheme -- keyed on the parent segment only
   (``registry.py:103-108``) -- cannot disambiguate. A clean scan lets the
   Phase-3 post-alias re-check land as a hard fail-fast; any hit would demote it
   to WARN-first. Recorded outcome: CLEAN.

Requirements: REQ-NC-08 (precondition), REQ-REG-08 (gate).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import pytest

from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.resolution.models import ModuleKind

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
_IDENTIFIER_SAFE = re.compile(r"[A-Za-z0-9_]+")


def _committed_snapshots() -> list[Path]:
    """Every committed extraction snapshot (12 at Item 5 implement time)."""
    return sorted(FIXTURES_DIR.glob("*/extraction_snapshot.json"))


def _raw_segments(snapshot: Path) -> list[tuple[str, str]]:
    """Yield (field, segment) for every raw ``::``-form QN segment in a snapshot.

    Only the raw (``::``-separator) qualified names reach the sanitizing
    derivation layer. The ``__``-form fields (e.g. ``calc_usage.qualified_name``,
    ``design_attribute.qualified_name``) are already per-segment sanitized by
    ``build_element_qualified_name`` and are deliberately excluded -- splitting
    them on ``::`` would wrongly feed a joined EQN through ``sanitize_name``.
    """
    data = json.loads(snapshot.read_text())
    out: list[tuple[str, str]] = []

    for cd in data.get("calc_defs") or []:
        for seg in (cd.get("qualified_name") or "").split("::"):
            out.append(("calc_def.qualified_name", seg))

    for cu in data.get("calc_usages") or []:
        for seg in (cu.get("calc_def_qualified_name") or "").split("::"):
            out.append(("calc_usage.calc_def_qualified_name", seg))

    for ca in data.get("computed_attributes") or []:
        for seg in (ca.get("owning_part_qualified_name") or "").split("::"):
            out.append(("computed_attribute.owning_part_qualified_name", seg))
        out.append(("computed_attribute.name", ca.get("name") or ""))
        out.append(("computed_attribute.owning_part_name", ca.get("owning_part_name") or ""))

    return out


def _build_all_modules(graph) -> list[dict]:
    """Rebuild the registry's (class_name, module_type) list for a graph.

    Mirrors ``generate_registry`` (``registry.py:195-255``) exactly: CalcUsage
    modules dedup by ``calc_def_name`` and key on ``{calc_def_name}Module``;
    FORMULA and aggregation modules key on the last segment of ``module_type``.
    """
    all_modules: list[dict] = []
    seen: set[str] = set()
    for m in graph.modules:
        if m.module_kind == ModuleKind.CALCULATION:
            if m.calc_def_name in seen:
                continue
            seen.add(m.calc_def_name)
            all_modules.append(
                {"class_name": f"{m.calc_def_name}Module", "module_type": m.module_type}
            )
    for m in graph.modules:
        if m.module_kind == ModuleKind.FORMULA:
            all_modules.append(
                {"class_name": m.module_type.split(".")[-1], "module_type": m.module_type}
            )
    for m in graph.modules:
        if m.module_kind == ModuleKind.AGGREGATION:
            all_modules.append(
                {"class_name": m.module_type.split(".")[-1], "module_type": m.module_type}
            )
    return all_modules


def _residual_grandparent_collisions(all_modules: list[dict]) -> dict[str, list[str]]:
    """Apply the parent-segment alias scheme; return class names that still collide.

    Replicates ``_resolve_class_name_collisions`` (``registry.py:98-116``): a
    colliding class name is aliased to ``PascalCase(parent_segment)_{class_name}``
    where ``parent_segment`` is the second-to-last ``module_type`` segment. Two
    modules with the same class name AND the same parent but different
    grandparents alias identically -- the residual SC-11 hole.
    """
    by_name: dict[str, list[int]] = defaultdict(list)
    for i, mod in enumerate(all_modules):
        by_name[mod["class_name"]].append(i)
    collisions = {n: idx for n, idx in by_name.items() if len(idx) > 1}

    aliased = [dict(m) for m in all_modules]
    for class_name, indices in collisions.items():
        for idx in indices:
            segments = aliased[idx]["module_type"].split(".")
            if len(segments) >= 2:
                parent = segments[-2]
            else:
                parent = segments[0] if segments else "unknown"
            pascal = "".join(word.capitalize() for word in parent.split("_"))
            aliased[idx]["class_name"] = f"{pascal}_{class_name}"

    regrouped: dict[str, list[int]] = defaultdict(list)
    for i, mod in enumerate(aliased):
        regrouped[mod["class_name"]].append(i)
    return {
        name: [all_modules[i]["module_type"] for i in idx]
        for name, idx in regrouped.items()
        if len(idx) > 1
    }


@pytest.mark.req("REQ-NC-08")
def test_no_identifier_safe_segment_changes_under_sanitize() -> None:
    """INV-1: no already-identifier-safe committed segment changes under sanitize.

    The per-segment sanitize is a byte-level no-op on every existing model
    precisely because the dangerous accidental-change forms are absent. A segment
    that is already ``[A-Za-z0-9_]+`` yet changes would be one of ``sanitize_name``'s
    accidental transforms (edge-underscore strip, ``_+`` collapse, reserved-word
    suffix) firing on a name a modeler did not quote -- and that WOULD move a
    baseline. Quoted names changing is expected and is what this item fixes.
    """
    offenders = []
    for snapshot in _committed_snapshots():
        for field, seg in _raw_segments(snapshot):
            if _IDENTIFIER_SAFE.fullmatch(seg) and sanitize_name(seg) != seg:
                offenders.append(
                    f"{snapshot.parent.name}:{field}: {seg!r} -> {sanitize_name(seg)!r}"
                )
    assert offenders == [], (
        "identifier-safe segments change under sanitize (would break INV-4 "
        f"byte-identity): {offenders}"
    )


@pytest.mark.req("REQ-NC-08")
def test_every_changed_segment_is_a_quoted_name() -> None:
    """INV-1 corollary: the only committed segments that change are quoted names.

    Pins the *reason* byte-identity holds -- every non-identity segment carries a
    character outside ``[A-Za-z0-9_]`` (a quote, space, or ``&``), i.e. a
    genuinely-quoted SysML name. If a future corpus edit introduced a bare-name
    change this fails alongside the accidental-form scan, localizing the risk.
    """
    unexplained = []
    for snapshot in _committed_snapshots():
        for field, seg in _raw_segments(snapshot):
            if sanitize_name(seg) != seg and _IDENTIFIER_SAFE.fullmatch(seg):
                unexplained.append(f"{snapshot.parent.name}:{field}: {seg!r}")
    assert unexplained == [], f"non-quoted segment changed under sanitize: {unexplained}"


@pytest.mark.req("REQ-REG-08")
def test_no_committed_model_hits_grandparent_collision() -> None:
    """B4/D5 gate: no committed model has a residual post-alias class collision.

    Decides the Phase-3 SC-11 branch. CLEAN (this asserts empty) -> the re-check
    lands as a hard fail-fast. Any hit here would mean a currently-generating
    model already relies on the silent overwrite, forcing WARN-first instead.
    """
    hits = {}
    for snapshot in _committed_snapshots():
        ctx = build_pipeline_context_from_snapshot(snapshot)
        residual = _residual_grandparent_collisions(
            _build_all_modules(ctx.computation_graph)
        )
        if residual:
            hits[snapshot.parent.name] = residual
    assert hits == {}, (
        "committed model hits the SC-11 grandparent-collision case; the Phase-3 "
        f"re-check must land WARN-first, not fail-fast: {hits}"
    )
