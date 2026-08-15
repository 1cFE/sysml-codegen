"""Extract calculation usages from SysML models with binding awareness.

This module provides structured extraction of CalculationUsage elements from
SysML v2 models, capturing comprehensive binding information for code generation.

Key features:
- Binding expression type tracking (chain, reference, literal, unbound)
- Cross-file reference detection via AST document URL comparison
- Unbound parameter identification for entry point candidates
"""

import copy
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.helpers import (
    get_calc_def_name,
    get_document_url,
    get_source_location,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

# CRITICAL: Import shared types from agentic-mbse
from agentic_mbse.sysml.types import BindingType

from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    sanitize_name,
)
from sysml_codegen.extraction import binding_evidence
from sysml_codegen.extraction.expression_utils import (
    extract_feature_chain_segments,
)
from sysml_codegen.extraction.expression_utils import (
    extract_literal_value as _extract_literal_value,
)
from sysml_codegen.extraction.expression_utils import (
    is_literal_expression as _is_literal_expression,
)
from sysml_codegen.extraction.source_evidence import SourceReferenceEvidence

logger = logging.getLogger(__name__)

__all__ = [
    "BindingType",  # Re-export from agentic-mbse
    "BindingInfo",
    "CalcUsageData",
    "ExtractionReport",
    "extract_calculation_usages",
]


@dataclass
class BindingInfo:
    """Information about a parameter binding.

    Attributes:
        param_name: Simple name of the bound parameter
        source_path: The binding source path
        binding_type: Classification of the binding expression
        is_cross_file: True if binding references element in different file
        raw_expression: Original expression text for debugging
        source_instance_elem: AST element for instance (CHAIN bindings)
        source_attribute_elem: AST element for attribute
        literal_value: Parsed literal value (LITERAL bindings)
        stored_source_attribute_name: Snapshot-supplied fallback for
            ``source_attribute_name``; see that property and DD-R27
    """

    param_name: str
    source_path: str | None  # None if unbound
    binding_type: BindingType
    is_cross_file: bool = False
    raw_expression: str = ""
    source_instance_elem: object | None = None
    source_attribute_elem: object | None = None
    literal_value: float | int | str | bool | None = None

    # Raw AST node for EXPRESSION bindings (Phase 2 will use this)
    expression_ast: Any = None

    # The written reference, when it comes from a snapshot rather than the AST
    # (DD-R27). Excluded from serialization so the wire form is unchanged: the
    # serializer already writes `source_attribute_name` from the property, and a
    # second key would appear in all 34 committed snapshots.
    stored_source_attribute_name: str | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    stored_source_instance_name: str | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    # The scope qualifier the model actually wrote, captured at extraction from the
    # CST byte span (audit F2). `None` for a bare leaf. This is the one thing
    # resolution destroys and no other field preserves.
    stored_source_written_qualifier: str | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )
    # Immutable semantic evidence (SOURCE-IDENTITY Item 4, Phase 1): the exact
    # SysIDE-resolved referent, bound formal, and authored source form, captured
    # before any rewrite runs. The frozen record is shared, never copied or
    # replaced — VBR stamping and rescue reassign the legacy scalars above but
    # cannot touch it (design I4). Excluded from the v5 wire format; the atomic
    # v6 snapshot cut owns its serialization. None on snapshot-loaded v5 data
    # and for the unhandled-expression arm.
    reference_evidence: SourceReferenceEvidence | None = field(
        default=None, metadata={"snapshot_exclude": True}
    )

    @property
    def source_written_qualifier(self) -> str | None:
        """The scope qualifier as written, or ``None`` for a bare leaf.

        Live it comes from the CST at extraction; offline the loader restores it
        from the snapshot, exactly as `source_attribute_name` works.
        """
        return self.stored_source_written_qualifier

    @property
    def source_instance_name(self) -> str | None:
        """Get name of source instance element if available."""
        if self.source_instance_elem and hasattr(self.source_instance_elem, "name"):
            return self.source_instance_elem.name
        return self.stored_source_instance_name

    @property
    def written_reference(self) -> str | None:
        """The **owner-relative** reference as written, or ``None`` when there isn't one.

        This feeds row 16 (``_occurrence_materialized_qn``), whose key form is
        ``{owner_path}__{name}``. That form only means anything for a reference
        written relative to its consumer's owner, so this property answers only
        for those and returns ``None`` otherwise. A ``None`` makes row 16 miss,
        which is safe: the binding falls through to the key forms that already
        resolve it (audit F2, and the same safe-miss pattern as a bracketed owner).

        Three shapes, three answers:

        * **Bare leaf** (``in gain = gain``) — owner-relative. Answer the leaf.
        * **Dotted chain** (``in cryo_pump_count = cryo_pumps.n_pumps``) —
          owner-relative through a sub-part. Answer qualifier *and* leaf. The leaf
          alone would re-anchor at the owner and select a same-named attribute
          elsewhere; that regression was measured (48.0 where the model means 32.0)
          and is why this property exists.
        * **``::``-qualified as written** (``in kappa = catf_radial_build::elongation``)
          — **not** owner-relative. It names its own scope, so re-anchoring it under
          the consumer's owner is wrong by construction: measured, it selected an
          owner-local shadow of the same name. Answer ``None``; row 17 keys it on
          exact identity, which is where it resolved before Item 4.

        The discriminator is `source_written_qualifier`, captured from the CST at
        extraction — **the written form, never the resolved one**. An earlier fix
        tested whether `source_path` contained ``::``, and a later one tested whether
        the resolved QN was indexed; both were wrong for the same reason, because
        resolution makes a bare leaf and a qualified reference identical
        (``shared_producer``'s ``gain`` resolves to
        ``SharedProducer::the_rig::scaler::gain``). Only the written form separates
        them (audit F2/F2b).
        """
        attribute_name = self.source_attribute_name
        if attribute_name is None:
            return None
        if self.source_written_qualifier is not None:
            return None
        instance_name = self.source_instance_name
        if instance_name:
            return f"{instance_name}.{attribute_name}"
        return attribute_name

    @property
    def source_attribute_name(self) -> str | None:
        """The referent's simple name — the binding's reference as written.

        Live, this reads the AST element. From a snapshot the AST is gone, so it
        falls back to the value the serializer already wrote into every
        committed snapshot (DD-R27). This is what makes the occurrence-
        materialized key form (row 16) reachable from the calculation consumer
        on unmodified v3 data.
        """
        if self.source_attribute_elem and hasattr(self.source_attribute_elem, "name"):
            return self.source_attribute_elem.name
        return self.stored_source_attribute_name


@dataclass
class CalcUsageData:
    """Enhanced calculation usage data with binding metadata.

    Attributes:
        instance_name: Instance name (e.g., "net_electric")
        calc_def_name: Calculation definition name (e.g., "NetElectricPower")
        calc_def_qualified_name: Full SysML qualified name of the calc def
        module_type: Namespaced module type for registry lookup
        bindings: List of BindingInfo for each parameter binding
        unbound_params: List of parameter names without bindings (entry points)
        source_file: Path to source SysML file
        source_line: Line number in source file
        parent_part_path: Dot-separated path of parent parts
        qualified_name: Full qualified path with __ separator
    """

    instance_name: str
    calc_def_name: str
    calc_def_qualified_name: str
    module_type: str
    bindings: list[BindingInfo] = field(default_factory=list)
    unbound_params: list[str] = field(default_factory=list)
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0
    parent_part_path: str = ""
    qualified_name: str = ""
    # Template detection fields (COST-PATTERN Item 2)
    is_template: bool = False
    owning_part_def_qn: str | None = None
    raw_element: object | None = None

    @property
    def parameter_bindings(self) -> dict[str, str]:
        """Backward-compatible dict of param_name -> source_path."""
        return {b.param_name: b.source_path for b in self.bindings if b.source_path}

    @property
    def has_cross_file_bindings(self) -> bool:
        """True if any binding references a cross-file element."""
        return any(b.is_cross_file for b in self.bindings)


@dataclass
class ExtractionReport:
    """Statistics from usage extraction."""

    total_usages: int
    total_bindings: int
    unbound_params: int
    cross_file_bindings: int
    warnings: list[str] = field(default_factory=list)


def owned_feature_typing_targets(usage: Any) -> list[Any]:
    """Return the target elements of a usage's *owned* FeatureTyping relationships.

    A part usage's declared type(s) are the targets of ``FeatureTyping`` relationships
    it owns via ``heritage`` — not a position in ``usage.types`` (which is an
    order-unstable, flattened view mixing declared, library, and inherited types).
    Walks ``usage.heritage`` and keeps FeatureTyping targets in heritage order.

    Probe-confirmed (SC-3 Phase 0, B1): ``heritage`` yields owned typings only, not
    typings inherited up the supertype chain — so a retyped ``part :>> driver : Sub``
    yields ``Sub`` alone, and a plain ``part x : Sub`` yields ``Sub`` alone. Mirrors the
    heritage walk in ``extractor.py`` ``_get_calc_def_name`` (which returns the first
    name); this returns all targets.
    """
    targets: list[Any] = []
    if not hasattr(usage, "heritage"):
        return targets
    for relationship, target in usage.heritage:
        if SysideAdapter.is_instance(relationship, "FeatureTyping") and target is not None:
            targets.append(target)
    return targets


def user_partdef_types(usage: Any, user_qn_set: set[str]) -> list[str]:
    """Return the ``__``-form QNs of the user-model PartDefinitions in ``usage.types``.

    Maps every entry of ``usage.types`` to its ``__``-form qualified name and keeps
    those present in ``user_qn_set`` (the QNs of user-model PartDefinitions). Library
    types (``Part``, ISQ bases) are absent from ``user_qn_set`` and thereby filtered
    out. Index projection only — the map is single-valued per usage elsewhere.

    Probe-confirmed (SC-3 Phase 0, Q4): ``elements_of_type(model, "PartDefinition")``
    excludes the standard library, so the ``user_qn_set`` intersection is the whole
    user filter.
    """
    result: list[str] = []
    try:
        types = list(usage.types)
    except (TypeError, AttributeError):
        return result
    for type_elem in types:
        qn = build_element_qualified_name(type_elem)
        if qn in user_qn_set:
            result.append(qn)
    return result


def _supertype_closure(qn: str, qn_to_partdef: dict[str, Any]) -> set[str]:
    """Return the transitive ``__``-form QNs of a PartDef's supertypes.

    Walks the PartDef's ``Subclassification`` relationships (``part def Sub :> Super``)
    via ``heritage``, transitively. Library supertypes (e.g. ``Parts__Part``) appear in
    the set but are harmless — membership is only ever tested against user QNs.
    """
    closure: set[str] = set()
    stack = [qn]
    while stack:
        current = stack.pop()
        part_def = qn_to_partdef.get(current)
        if part_def is None or not hasattr(part_def, "heritage"):
            continue
        for relationship, target in part_def.heritage:
            if not SysideAdapter.is_instance(relationship, "Subclassification"):
                continue
            super_qn = build_element_qualified_name(target)
            if super_qn and super_qn not in closure:
                closure.add(super_qn)
                stack.append(super_qn)
    return closure


def most_specific(
    qns: list[str], qn_to_partdef: dict[str, Any]
) -> tuple[str | None, bool]:
    """Pick the most-specific PartDef QN among a usage's owned typings.

    ``A`` is more specific than ``B`` iff ``B`` is in ``A``'s supertype closure. The
    most-specific PartDef is the one no other candidate specializes — the sink of a
    specialization chain. Returns ``(winner, incomparable)``:

    - Empty list → ``(None, False)`` (caller skips: no type).
    - Single QN → ``(qn, False)``.
    - All comparable (one chain) → ``(chain sink, False)``.
    - Two or more mutually incomparable maxima → ``(sorted-first, True)``; the caller
      emits V10. Sorting by QN string keeps the pick machine-independent — never rely
      on ``heritage``/``types`` iteration order.

    ``qn_to_partdef`` is a prebuilt ``{qn: PartDefElement}`` lookup (built once per
    extraction pass), so supertype-closure walks never scan all PartDefs per call.
    """
    if not qns:
        return None, False
    unique = sorted(set(qns))
    if len(unique) == 1:
        return unique[0], False

    closures = {qn: _supertype_closure(qn, qn_to_partdef) for qn in unique}
    # Maximal = not specialized by any other candidate = not in any other's closure.
    maximal = [
        qn
        for qn in unique
        if not any(qn in closures[other] for other in unique if other != qn)
    ]
    return maximal[0], len(maximal) > 1


def user_partdef_lookup(model: Any) -> dict[str, Any]:
    """Return a ``{__-form QN: PartDefElement}`` lookup for all user-model PartDefs.

    Probe-confirmed (SC-3 Phase 0, Q4): ``elements_of_type(model, "PartDefinition")``
    excludes the standard library, so this is exactly the user PartDef set. Its keys
    are the ``user_qn_set`` used to filter index keys to user types; its values drive
    ``most_specific``'s supertype-closure walk. Built once per extraction pass.
    """
    lookup: dict[str, Any] = {}
    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        qn = build_element_qualified_name(part_def)
        if qn:
            lookup[qn] = part_def
    return lookup


def _build_part_usage_index(model: Any) -> dict[str, list[Any]]:
    """Build index mapping PartDef qualified names to their PartUsage elements.

    Iterates all PartUsage elements. Keys each usage under **every user-model
    PartDefinition it carries** — the set union of its owned FeatureTyping targets
    and the user PartDefs in ``usage.types`` (both projected to ``__``-form QNs and
    filtered to ``user_qn_set``, so library types like ``Part`` are excluded). This
    is a superset of the old first-``.types`` key (REQ-EXT-13):

    - A plain ``part x : Sub`` carries only ``Sub`` (B2-plain) → one key, identical to
      before.
    - A retyped ``part :>> driver : Sub`` carries both ``Sub`` (owned typing) and its
      user supertype (present in ``.types``) → keyed under both, so the subtype's
      template calcs and the preserved supertype flow both find an instantiation path.

    The per-usage key set is a ``set``: the declared type is both an owned typing and
    a ``.types`` member, so the union dedups it (INV-1).

    Args:
        model: Parsed SysIDE model.

    Returns:
        Dict mapping PartDef QN to list of PartUsage AST elements.
    """
    from collections import defaultdict

    user_qn_set = set(user_partdef_lookup(model))
    index: dict[str, list[Any]] = defaultdict(list)

    for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
        key_qns: set[str] = set(user_partdef_types(usage, user_qn_set))
        for target in owned_feature_typing_targets(usage):
            target_qn = build_element_qualified_name(target)
            if target_qn in user_qn_set:
                key_qns.add(target_qn)
        for part_def_qn in key_qns:
            index[part_def_qn].append(usage)

    return dict(index)


def _find_instantiation_paths(
    target_part_def_qn: str,
    part_usage_index: dict[str, list[Any]],
    _visited: set[str] | None = None,
) -> list[str]:
    """Find all design-relative qualified paths to PartUsages of a target PartDef.

    Recursively resolves the instantiation chain from design root through
    intermediate PartDefs to the target. Returns fully qualified paths using
    the ``__`` separator per ADR-003.

    Args:
        target_part_def_qn: QN of the PartDef to find instantiation paths for.
        part_usage_index: Prebuilt index from :func:`_build_part_usage_index`.
        _visited: Recursion guard set (internal).

    Returns:
        List of design-relative qualified name prefixes (deduplicated).
    """
    if _visited is None:
        _visited = set()

    if target_part_def_qn in _visited:
        return []
    _visited = _visited | {target_part_def_qn}

    usages = part_usage_index.get(target_part_def_qn, [])
    if not usages:
        return []

    seen_paths: set[str] = set()
    result: list[str] = []

    for usage in usages:
        owning_type = getattr(usage, "owning_type", None)
        if owning_type is not None and SysideAdapter.is_instance(
            owning_type, "PartDefinition"
        ):
            # PartUsage inside another PartDef → recurse
            parent_def_qn = build_element_qualified_name(owning_type)
            parent_paths = _find_instantiation_paths(
                parent_def_qn, part_usage_index, _visited
            )
            usage_name = sanitize_name(getattr(usage, "name", ""))
            for parent_path in parent_paths:
                path = f"{parent_path}__{usage_name}"
                if path not in seen_paths:
                    seen_paths.add(path)
                    result.append(path)
        else:
            # Terminal node: owned by Package, PartUsage, or other non-PartDef
            path = build_element_qualified_name(usage)
            if path and path not in seen_paths:
                seen_paths.add(path)
                result.append(path)

    return result


def _create_virtual_calc_usage(
    template: CalcUsageData,
    instantiation_path: str,
) -> CalcUsageData:
    """Create a virtual CalcUsage for a specific instantiation path.

    Args:
        template: The template CalcUsageData from the PartDefinition.
        instantiation_path: Full design-relative path to the PartUsage.

    Returns:
        New CalcUsageData with design-relative qualified name and
        bindings copied from the template.
    """
    calc_name = sanitize_name(template.instance_name)
    qualified_name = f"{instantiation_path}__{calc_name}"

    # Build dot-separated parent_part_path from the instantiation path
    path_segments = instantiation_path.split("__")
    part_segments = path_segments[1:] if len(path_segments) > 1 else path_segments
    parent_part_path = ".".join(part_segments)

    return CalcUsageData(
        instance_name=qualified_name,
        calc_def_name=template.calc_def_name,
        calc_def_qualified_name=template.calc_def_qualified_name,
        module_type=template.module_type,
        # Shallow-copy each BindingInfo so sibling instances never share a binding
        # object (REQ-VBR-08 / D2). The rewrite reassigns only scalar fields, so a
        # shallow copy gives each instance independent scalars while the read-only
        # AST-node references stay shared (copy.deepcopy would recurse into the
        # SysIDE parse subgraph — slow and possibly cyclic).
        bindings=[copy.copy(b) for b in template.bindings],
        unbound_params=list(template.unbound_params),
        source_file=template.source_file,
        source_line=template.source_line,
        parent_part_path=parent_part_path,
        qualified_name=qualified_name,
        is_template=False,
        owning_part_def_qn=template.owning_part_def_qn,
        raw_element=template.raw_element,
    )


def _expand_template_calc_usages(
    model: Any,
    calc_usages: list[CalcUsageData],
    warnings: list[str],
) -> list[CalcUsageData]:
    """Replace template CalcUsages with virtual per-instance CalcUsages.

    Args:
        model: Parsed SysIDE model.
        calc_usages: Extracted CalcUsages (may include templates).
        warnings: List to append warnings to.

    Returns:
        Expanded list: concrete CalcUsages unchanged, templates replaced
        by virtual instances (one per PartUsage instantiation).
    """
    index = _build_part_usage_index(model)
    # Lookup for the collision tiebreak's most-specific-owner comparison (FIX 3).
    lookup = user_partdef_lookup(model)

    concrete: list[CalcUsageData] = []
    templates: list[CalcUsageData] = []
    for usage in calc_usages:
        if usage.is_template:
            templates.append(usage)
        else:
            concrete.append(usage)

    if templates:
        template_count = len(templates)
        logger.info(
            "Template detection: %d templates, %d concrete CalcUsages",
            template_count,
            len(concrete),
        )

    virtual_usages: list[CalcUsageData] = []
    # Virtual QN -> the winning virtual stored under it. A dict (not a set) so a
    # second template resolving to the same QN can be compared, not blindly dropped.
    seen_qns: dict[str, CalcUsageData] = {}
    # Collision classes already warned, keyed (owner_a, owner_b, calc_name), so a
    # usage instantiated N times warns once, not N times (V9 dedup).
    collisions_warned: set[tuple[str, str, str]] = set()

    for template in templates:
        owner_qn = template.owning_part_def_qn
        if not owner_qn:
            msg = (
                f"Template CalcUsage '{template.instance_name}' "
                f"has is_template=True but no owning_part_def_qn — skipped"
            )
            logger.warning(msg)
            warnings.append(msg)
            continue
        paths = _find_instantiation_paths(owner_qn, index)
        if not paths:
            msg = (
                f"Template CalcUsage '{template.instance_name}' "
                f"(PartDef '{owner_qn}') has no "
                f"PartUsage instantiations — dropped"
            )
            logger.warning(msg)
            warnings.append(msg)
            continue

        for path in paths:
            virtual = _create_virtual_calc_usage(template, path)
            existing = seen_qns.get(virtual.qualified_name)
            if existing is None:
                seen_qns[virtual.qualified_name] = virtual
                virtual_usages.append(virtual)
                continue

            existing_owner = existing.owning_part_def_qn
            assert existing_owner is not None  # virtuals always carry their owner
            if existing_owner == owner_qn:
                # Same owner arriving via another instantiation path — idempotent.
                continue

            # Genuine collision: two different owners resolve to the same virtual QN
            # (same instantiation path + same calc instance name). Keep the
            # most-specific owner; emit V9 once per collision class.
            winner_qn, _incomparable = most_specific([existing_owner, owner_qn], lookup)
            if winner_qn == owner_qn:
                for i, stored in enumerate(virtual_usages):
                    if stored is existing:
                        virtual_usages[i] = virtual
                        break
                seen_qns[virtual.qualified_name] = virtual

            owner_a, owner_b = sorted([existing_owner, owner_qn])
            calc_name = sanitize_name(template.instance_name)
            dedup_key = (owner_a, owner_b, calc_name)
            if dedup_key not in collisions_warned:
                collisions_warned.add(dedup_key)
                msg = (
                    f"Template collision on '{virtual.qualified_name}': owners "
                    f"'{owner_a}' and '{owner_b}' both define calc '{calc_name}'; "
                    f"kept most-specific owner '{winner_qn}'."
                )
                logger.warning(msg)
                warnings.append(msg)

    if virtual_usages:
        logger.info(
            "Template expansion: %d templates → %d virtual instances",
            len(templates),
            len(virtual_usages),
        )

    return concrete + virtual_usages


def extract_calculation_usages(
    model: Any,
    known_calc_defs: set[str] | None = None,
    calc_defs: list | None = None,
    expand_templates: bool = True,
) -> tuple[list[CalcUsageData], ExtractionReport]:
    """Extract all calculation usages from a SysML model.

    Args:
        model: Parsed SysIDE model
        known_calc_defs: Set of known calc def names for validation (optional)
        calc_defs: List of CalculationDefinitionData for detecting algorithm params
        expand_templates: If True, replace template CalcUsages (owned by PartDefs)
            with virtual per-instance CalcUsages. Default True.

    Returns:
        Tuple of (list of CalcUsageData, ExtractionReport with statistics)
    """
    usages: list[CalcUsageData] = []
    warnings: list[str] = []

    calc_def_map: dict[str, object] = {}
    if calc_defs:
        calc_def_map = {cd.name: cd for cd in calc_defs}

    for elem in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        usage_data = _extract_single_usage(elem, known_calc_defs, warnings, calc_def_map)
        if usage_data:
            usages.append(usage_data)

    if expand_templates:
        usages = _expand_template_calc_usages(model, usages, warnings)

    report = ExtractionReport(
        total_usages=len(usages),
        total_bindings=sum(len(u.bindings) for u in usages),
        unbound_params=sum(len(u.unbound_params) for u in usages),
        cross_file_bindings=sum(1 for u in usages for b in u.bindings if b.is_cross_file),
        warnings=warnings,
    )

    return usages, report


def _extract_single_usage(
    elem: Any,
    known_calc_defs: set[str] | None,
    warnings: list[str],
    calc_def_map: dict[str, object] | None = None,
) -> CalcUsageData | None:
    """Extract data from a single CalculationUsage element."""
    instance_name = sanitize_name(elem.name)
    if not instance_name:
        return None

    calc_def_name = sanitize_name(get_calc_def_name(elem))
    if not calc_def_name:
        warnings.append(f"Could not resolve calc def for usage '{instance_name}'")
        return None

    if known_calc_defs and calc_def_name not in known_calc_defs:
        warnings.append(
            f"Calc usage '{instance_name}' references unknown calc def '{calc_def_name}'"
        )

    # Get calc def qualified name from map
    if not calc_def_map or calc_def_name not in calc_def_map:
        warnings.append(f"Calc def '{calc_def_name}' not found in calc_def_map")
        calc_def_qualified_name = calc_def_name
        module_type = f"{calc_def_name}Module"
    else:
        calc_def = calc_def_map[calc_def_name]
        calc_def_qualified_name = getattr(calc_def, 'qualified_name', calc_def_name)
        module_type = derive_module_type(calc_def_qualified_name)

    source_file, source_line = get_source_location(elem)
    parent_part_path = _get_parent_part_path(elem)
    qualified_name = build_element_qualified_name(elem)

    bindings, unbound_params = _extract_bindings(elem, instance_name, warnings)

    # Detect algorithm params
    if calc_def_map and calc_def_name in calc_def_map:
        calc_def = calc_def_map[calc_def_name]
        expected_inputs: set[str] = set()
        if hasattr(calc_def, 'input_attributes'):
            for attr in calc_def.input_attributes:
                if hasattr(attr, 'name') and attr.name:
                    expected_inputs.add(attr.name)

        declared_params = {b.param_name for b in bindings}
        algorithm_params = expected_inputs - declared_params

        if algorithm_params:
            unbound_params.extend(sorted(algorithm_params))

    # Template detection: check if owning type is PartDefinition
    owning_type = getattr(elem, "owning_type", None)
    is_template = False
    owning_part_def_qn = None
    if owning_type is not None and SysideAdapter.is_instance(
        owning_type, "PartDefinition"
    ):
        is_template = True
        owning_part_def_qn = build_element_qualified_name(owning_type)

    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=calc_def_qualified_name,
        module_type=module_type,
        bindings=bindings,
        unbound_params=unbound_params,
        source_file=source_file,
        source_line=source_line,
        parent_part_path=parent_part_path,
        qualified_name=qualified_name,
        is_template=is_template,
        owning_part_def_qn=owning_part_def_qn,
        raw_element=elem,
    )


def _extract_bindings(
    elem: Any,
    instance_name: str,
    warnings: list[str],
) -> tuple[list[BindingInfo], list[str]]:
    """Extract all parameter bindings from a calc usage."""
    bindings: list[BindingInfo] = []
    unbound_params: list[str] = []

    if not hasattr(elem, "owned_members"):
        return bindings, unbound_params

    for member in elem.owned_members:
        if not (
            SysideAdapter.is_instance(member, "AttributeUsage")
            or SysideAdapter.is_instance(member, "ReferenceUsage")
        ):
            continue

        if not _is_input_parameter(member):
            continue

        param_name = sanitize_name(member.name)
        if not param_name:
            continue

        binding_info = _extract_single_binding(elem, member, param_name, warnings)

        if binding_info.binding_type == BindingType.UNBOUND:
            unbound_params.append(param_name)
        else:
            bindings.append(binding_info)

    return bindings, unbound_params


def _extract_single_binding(
    usage_elem: Any,
    param_elem: Any,
    param_name: str,
    warnings: list[str],
) -> BindingInfo:
    """Extract binding info from a single parameter element.

    INV-1 (totality): every terminal dispatch arm is total and loud. An
    unhandled binding-expression type (D3-1) and a 3+-segment chain the parser
    cannot represent (D3-2) each route to a *distinct*, warned disposition —
    never a silent UNBOUND reuse or a root-truncated CHAIN. `warnings` is the
    list `_extract_bindings` already threads.
    """
    if (
        not hasattr(param_elem, "feature_value_expression")
        or not param_elem.feature_value_expression
    ):
        return BindingInfo(
            param_name=param_name,
            source_path=None,
            binding_type=BindingType.UNBOUND,
        )

    expr = param_elem.feature_value_expression
    usage_name = getattr(usage_elem, "name", None) or "?"

    # FeatureChainExpression MUST be before OperatorExpression -- FCE is a
    # subtype of OE in SysIDE's type system (doc 19 invariant).
    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        # D1 (Item 2): a 3+-segment chain (station.array.derived_calc.derived_value)
        # survives extraction as a full-path CHAIN binding. The ≤2-segment parser
        # cannot represent it, so join the whole segment list into source_path and
        # let the backtracker resolve it (scoped_lookup + ancestor-scope climb).
        # The loud diagnostic for a genuinely unresolvable chain moved WITH the
        # resolution to the backtracker Step-4 fallback (D3): extraction has no
        # registry, so it cannot tell a resolvable chain from a dead one.
        #
        # N-1: the deep-chain arm intentionally sets ONLY source_path. It omits
        # source_instance_elem / source_attribute_elem / is_cross_file — the
        # backtracker consumes none of those for CHAIN resolution (only
        # source_path). Do NOT reach into _parse_chain_expression to populate them.
        evidence = binding_evidence.chain_evidence(param_elem, expr)
        segments = extract_feature_chain_segments(expr)
        if len(segments) > 2:
            full_path = ".".join(segments)
            return BindingInfo(
                param_name=param_name,
                source_path=full_path,
                binding_type=BindingType.CHAIN,
                raw_expression=f"FeatureChainExpression -> {full_path}",
                reference_evidence=evidence,
            )
        source_path, instance_elem, target_elem = _parse_chain_expression(expr)
        is_cross_file = _detect_cross_file_reference(usage_elem, instance_elem)
        return BindingInfo(
            param_name=param_name,
            source_path=source_path,
            binding_type=BindingType.CHAIN,
            is_cross_file=is_cross_file,
            raw_expression=f"FeatureChainExpression -> {source_path}",
            source_instance_elem=instance_elem,
            source_attribute_elem=target_elem,
            reference_evidence=evidence,
        )

    elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        source_path, referenced_elem = _parse_reference_expression(expr)
        is_cross_file = _detect_cross_file_reference(usage_elem, referenced_elem)
        return BindingInfo(
            param_name=param_name,
            source_path=source_path,
            binding_type=BindingType.REFERENCE,
            is_cross_file=is_cross_file,
            raw_expression=f"FeatureReferenceExpression -> {source_path}",
            source_attribute_elem=referenced_elem,
            stored_source_written_qualifier=binding_evidence.written_qualifier(expr),
            reference_evidence=binding_evidence.reference_evidence(param_elem, expr),
        )

    elif _is_literal_expression(expr):
        literal_value = _extract_literal_value(expr)
        return BindingInfo(
            param_name=param_name,
            source_path=str(literal_value) if literal_value is not None else None,
            binding_type=BindingType.LITERAL,
            is_cross_file=False,
            raw_expression=f"LiteralExpression -> {literal_value}",
            literal_value=literal_value,
            reference_evidence=binding_evidence.literal_evidence(param_elem, literal_value),
        )

    elif SysideAdapter.is_instance(expr, "OperatorExpression"):
        return BindingInfo(
            param_name=param_name,
            source_path=None,
            binding_type=BindingType.EXPRESSION,
            raw_expression=f"OperatorExpression: {type(expr).__name__}",
            expression_ast=expr,
            reference_evidence=binding_evidence.expression_evidence(param_elem, expr),
        )

    # INV-1 terminal arm (D3-1): the RHS is a binding expression of a type this
    # dispatch does not handle (e.g. an InvocationExpression `Doubler(v=a)`).
    # Doc 01-extraction.md:147 defines UNBOUND as "no binding expression at all"
    # — but one DOES exist here, so the *silent* fall-through fabricated a JSON
    # entry point with no diagnostic. WARN (naming param + node type) so the
    # unsupported binding is loud. ADR-003 requires every input param to resolve
    # to bound-or-entry-point (no third disposition), so it stays UNBOUND — but
    # now a loud, warned entry point, not a silent one. (Design D1's "distinct
    # disposition" is foreclosed by ADR-003; the finding's harm — the silence —
    # is what the warning fixes.)
    warnings.append(
        f"Unhandled binding-expression type '{type(expr).__name__}' for "
        f"parameter '{param_name}' on usage '{usage_name}' — not one of "
        f"CHAIN/REFERENCE/LITERAL/EXPRESSION; surfacing as an entry point."
    )
    return BindingInfo(
        param_name=param_name,
        source_path=None,
        binding_type=BindingType.UNBOUND,
        raw_expression=f"Unhandled expression type: {type(expr).__name__}",
    )


def _parse_chain_expression(
    expr: Any,
) -> tuple[str | None, object | None, object | None]:
    """Parse FeatureChainExpression to extract binding path and elements."""
    path_parts: list[str] = []
    instance_elem = None
    target_elem = None

    operands = list(expr.operands)
    if operands:
        first_operand = operands[0]
        if SysideAdapter.is_instance(first_operand, "FeatureReferenceExpression"):
            _, instance_elem = _parse_reference_expression(first_operand)
            if instance_elem and hasattr(instance_elem, "name") and instance_elem.name:
                path_parts.append(instance_elem.name)

    if hasattr(expr, "target_feature") and expr.target_feature:
        target = expr.target_feature
        if hasattr(target, "name") and target.name:
            path_parts.append(target.name)
            target_elem = target

    source_path = ".".join(path_parts) if path_parts else None
    return source_path, instance_elem, target_elem


def _parse_reference_expression(
    expr: Any,
) -> tuple[str | None, object | None]:
    """Parse FeatureReferenceExpression to extract qualified path and element."""
    if not SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        return None, None

    # D3-3 (closed-by-construction). Invariant: SysIDE guarantees a resolved
    # `referent` with a non-empty `qualified_name` for any
    # FeatureReferenceExpression in successfully-parsed SysML (doc
    # 16-computed-attributes.md:115-119). A (None, None) return below is
    # therefore unreachable without a parser bug or partial SysML — if it fires,
    # the param would double-vanish (filtered from both ledgers). Debug-guard it
    # so the invariant violation is visible rather than silent; no fires-on-shape
    # test (no reachable shape to feed).
    if not hasattr(expr, "referent") or expr.referent is None:
        logger.debug(
            "D3-3 invariant violation: FeatureReferenceExpression with no "
            "resolved referent (SysIDE parser bug or partial SysML)."
        )
        return None, None

    referent = expr.referent
    qname = getattr(referent, "qualified_name", None)

    if not qname:
        logger.debug(
            "D3-3 invariant violation: resolved referent has empty "
            "qualified_name (SysIDE parser bug or partial SysML)."
        )
        return None, None

    return str(qname), referent


def _detect_cross_file_reference(
    usage_elem: Any,
    referenced_elem: object | None,
) -> bool:
    """Detect if a binding references an element in a different file."""
    if not referenced_elem:
        return False

    usage_doc_url = get_document_url(usage_elem)
    if not usage_doc_url:
        return False

    ref_doc_url = get_document_url(referenced_elem)
    if not ref_doc_url:
        return False

    return usage_doc_url != ref_doc_url


def _is_input_parameter(member: Any) -> bool:
    """Check if member is an input parameter."""
    if not hasattr(member, "direction"):
        return False
    direction_str = str(member.direction)
    return "In" in direction_str or "inout" in direction_str.lower()


def _get_parent_part_path(elem: Any) -> str:
    """Get parent part path for nested calc usages."""
    parts: list[str] = []
    current = elem

    while hasattr(current, "owner") and current.owner:
        owner = current.owner
        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem and hasattr(owning_elem, "name") and owning_elem.name:
                if SysideAdapter.is_instance(owning_elem, "PartUsage"):
                    parts.insert(0, owning_elem.name)
        current = owner

    return ".".join(parts)


