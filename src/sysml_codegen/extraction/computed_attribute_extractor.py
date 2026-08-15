"""Computed attribute extraction for PartDef/PartUsage attributes.

Classifies attribute expressions (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED,
LITERAL, UNRESOLVABLE) using qualified-name resolution and compiles
FORMULA patterns to Python via the Phase 1 expression compiler.

This module is a leaf in the extraction layer — it does NOT import from
analysis/, resolution/, or generation/.

**Off the shipped route, retained, and here is the measurement (Revise step 6d).** Nothing
in ``src/`` imports it. The shipped route lifts computed attributes in the elaborator, which
resolves references against occurrence identity rather than by qualified-name matching, and
projects each one as its own node (``tests/conformance/test_elaboration_computed_attrs.py``,
``tests/integration/test_computed_attributes_exact_route.py``). Three test modules keep this
classifier alive — ``test_computed_attribute_golden.py``, ``test_silent_failure_d316.py``,
``test_silent_failure_family1.py`` — and what they pin is the *classification taxonomy*
(FORMULA / EXPOSE_PURE / EXPOSE_COMPUTED / EXPOSE_CHAIN_TENTATIVE / LITERAL / UNRESOLVABLE)
against a golden file, plus the silent-failure shapes that taxonomy was hardened against.
The elaborator has no equivalent taxonomy surface to move that coverage onto, so deleting
this module would delete the coverage rather than relocate it.

Retained on that reason, not because anything ships it. Whether the taxonomy should be
re-expressed against the elaborator, or retired with its classifier, is an open disposition
with no recorded authority (Revise step 6d stage note).
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_mbse.sysml.constraint_extraction import extract_expression_ir
from agentic_mbse.sysml.expression import extract_feature_refs
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ExpressionRef

from sysml_codegen.core.models import ChannelAlias

from .calc_compat_renderer import render_calc_expression
from .data_models import ComputedAttributeClassification, ComputedAttributeData
from .expression_compiler import Compilability, CompilationError, _sanitize_name
from .expression_utils import (
    extract_feature_chain_segments,
    is_literal_expression,
    reconstruct_expression,
)

logger = logging.getLogger(__name__)


def _is_wellformed_multihop_chain(
    expression_ast: Any,
    reference_chain: list[str] | None,
    calc_usage_names: set[str],
) -> bool:
    """INV-E gate: is this a well-formed multi-hop EXPOSE candidate?

    True when the root is a pure FeatureChainExpression whose captured segments
    (reference_chain) form a chain of >= 2 segments rooted at a part waypoint
    (segment[0] is NOT a calc-usage instance — that is the simple EXPOSE_PURE
    ``calc.output`` case handled elsewhere). A linear FeatureChainExpression has
    a single terminal leaf by construction, so the "single terminal" arm of INV-E
    is implied by the root-node type check.

    Deciding EXPOSE-ness here is impossible (the leaf lacks the registry, B5) —
    this only detects the STRUCTURE. Over-tagging is safe: the confirm pass
    reverts an unresolvable candidate to FORMULA (INV-D).
    """
    if not SysideAdapter.is_instance(expression_ast, "FeatureChainExpression"):
        return False
    if reference_chain is None or len(reference_chain) < 2:
        return False
    return reference_chain[0] not in calc_usage_names


def _ancestor_part_qns(part_element: Any) -> set[str]:
    """Transitive ``::``-form QNs of a part's ancestor PartDefs.

    Walks ``heritage`` for ``:>`` generalizations (``Subclassification``
    relationships), keeps each supertype ``target``'s raw ``::``-form
    ``qualified_name``, and recurses on the target element.

    Deliberately NOT a clone of ``usage_extractor._supertype_closure`` — do not
    unify them. Two intentional divergences:
    - It recurses on the raw ``target`` element (there is no ``qn_to_partdef``
      map at this leaf), so it also descends into library supertypes. Harmless:
      a stdlib QN is never the namespace of a user inherited-attr ref.
    - It returns raw ``::``-form QNs (via ``str(target.qualified_name)``), NOT
      the sanitized ``__``-form ``build_element_qualified_name`` produces. The
      classifier prefix-matches these against ``ref.qualified_name``, which is
      also ``::``-form — routing through the ``__``-form helper would never
      match (the ``::``-vs-``__`` trap).
    """
    result: set[str] = set()
    stack: list[Any] = [part_element]
    while stack:
        for rel, target in getattr(stack.pop(), "heritage", []):
            if not SysideAdapter.is_instance(rel, "Subclassification"):
                continue
            qn = str(getattr(target, "qualified_name", "") or "")
            if qn and qn not in result:
                result.add(qn)
                stack.append(target)
    return result


def _classify_attribute_expression(
    refs: list[ExpressionRef],
    owning_part_qualified_name: str,
    calc_usage_names: set[str],
    sibling_attr_names: set[str],
    expression_ast: Any,
    reference_chain: list[str] | None,
    ancestor_part_qns: set[str] | None = None,
) -> ComputedAttributeClassification:
    """Classify an attribute expression by analyzing its feature references.

    Uses qualified-name resolution with positive identification:
    - Step 2a: filter CalcUsage instance refs (traversal artifacts)
    - Step 2b: QN starts with owning part QN — or an ancestor PartDef QN, so an
      inherited attr (which SysIDE files under the supertype namespace) is a
      sibling → sibling_ref
    - Step 2c: QN non-empty but different namespace → calc_ref
    - Step 2d: empty QN fallback to simple name matching

    Args:
        refs: Feature references from extract_feature_refs().
        owning_part_qualified_name: QN of the owning PartDef/PartUsage.
        calc_usage_names: CalcUsage instance names on this part.
        sibling_attr_names: All AttributeUsage names on this part.
        expression_ast: Raw syside AST root node (for EXPOSE_PURE vs
            EXPOSE_COMPUTED distinction).
        reference_chain: Full dotted segments of a FeatureChainExpression (D9),
            or None. Drives the multi-hop EXPOSE_CHAIN_TENTATIVE gate (INV-E).
        ancestor_part_qns: ``::``-form QNs of the owning part's ancestor
            PartDefs (from ``_ancestor_part_qns``). A ref whose QN sits under
            one of these is an inherited-attr sibling, not a cross-namespace
            calc output. ``None``/empty for a part with no supertypes — then
            Step-2b behaves exactly as the pre-inheritance-fix prefix check.

    Returns:
        Classification enum value.
    """
    # Step 1: no refs → LITERAL (the documented, intended behavior, REQ-CA-04).
    if not refs:
        # D3-9 tripwire: a genuine literal has a literal AST root. A *non*-literal
        # root with zero extracted refs is suspicious — it means extract_feature_refs
        # under-reported, and a real computed attribute is about to be silently
        # dropped as a constant. Warn (does not change the classification).
        if expression_ast is not None and not is_literal_expression(expression_ast):
            logger.warning(
                "Computed attribute has a non-literal expression root "
                "(%s) but zero extracted references; classifying as LITERAL "
                "may silently drop a real computed attribute (D3-9 tripwire).",
                type(expression_ast).__name__,
            )
        return ComputedAttributeClassification.LITERAL

    sibling_refs: list[str] = []
    calc_refs: list[str] = []
    unresolvable_refs: list[str] = []

    part_qn_prefix = owning_part_qualified_name + "::"
    # Inherited attrs resolve into an ancestor PartDef's namespace, so a ref
    # under any ancestor prefix is still a sibling. str.startswith accepts a
    # tuple, so both checks are one call each.
    ancestor_prefixes = tuple(a + "::" for a in (ancestor_part_qns or set()))

    # Step 2: classify each ref by positive identification
    for ref in refs:
        # 2a: filter CalcUsage instance refs
        if ref.name in calc_usage_names:
            continue

        qn = ref.qualified_name
        if qn:
            # 2b: QN starts with owning part OR an ancestor PartDef namespace → sibling
            if qn.startswith(part_qn_prefix) or qn.startswith(ancestor_prefixes):
                sibling_refs.append(ref.name)
            else:
                # 2c: QN in different namespace → calc output ref
                calc_refs.append(ref.name)
        else:
            # 2d: empty QN fallback to simple name matching
            if ref.name in sibling_attr_names:
                sibling_refs.append(ref.name)
            elif ref.name in calc_usage_names:
                # Already handled by 2a, but safety net for empty QN case
                continue
            else:
                unresolvable_refs.append(ref.name)

    # Step 3: decide classification
    if unresolvable_refs:
        return ComputedAttributeClassification.UNRESOLVABLE

    if not calc_refs:
        # Only sibling refs (or no refs after filtering). This is where a
        # multi-hop chain like `tf_coil.volume_calc.volume` lands today — its
        # part-typed waypoint (tf_coil) is a sibling ref and `references` is
        # truncated to the root, so calc_refs is empty (C4). Before dropping to
        # FORMULA, tag a well-formed multi-hop chain as a tentative EXPOSE for
        # the confirm pass to finalize (D6/INV-E). An arithmetic-over-chain root
        # is an OperatorExpression, not a FeatureChainExpression, so it fails the
        # gate and stays FORMULA (INV-D negative).
        if _is_wellformed_multihop_chain(
            expression_ast, reference_chain, calc_usage_names
        ):
            return ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE
        return ComputedAttributeClassification.FORMULA

    # calc_refs present → EXPOSE variant
    if not sibling_refs and SysideAdapter.is_instance(
        expression_ast, "FeatureChainExpression"
    ):
        return ComputedAttributeClassification.EXPOSE_PURE

    return ComputedAttributeClassification.EXPOSE_COMPUTED


def extract_computed_attributes(
    adapter: SysideAdapter,
    part_element: Any,
    calc_usage_names: set[str],
) -> tuple[list[ComputedAttributeData], list[ChannelAlias]]:
    """Extract and classify computed attributes from a PartDef/PartUsage.

    Iterates owned_members, classifies each AttributeUsage expression,
    and returns ComputedAttributeData for all non-LITERAL attributes.
    EXPOSE_PURE attributes also produce ChannelAlias objects.

    Args:
        adapter: SysIDE adapter for type checking.
        part_element: Raw syside PartDef/PartUsage element.
        calc_usage_names: CalcUsage instance names on this part.

    Returns:
        Tuple of (computed_attributes, channel_aliases).
        EXPOSE_PURE attrs appear in BOTH lists (CAD for graph builder compat,
        ChannelAlias for OutputRegistry in Item 3).
    """
    # Build context
    sibling_attr_names: set[str] = set()
    for member in part_element.owned_members:
        if SysideAdapter.is_instance(member, "AttributeUsage"):
            sibling_attr_names.add(member.name)

    part_name = _sanitize_name(part_element.name)
    part_qn = str(getattr(part_element, "qualified_name", "") or part_name)
    is_part_def = SysideAdapter.is_instance(part_element, "PartDefinition")

    # Ancestor PartDef QNs (transient, computed once per part). An inherited attr
    # resolves into an ancestor's namespace, so the classifier needs these to
    # recognize it as a sibling rather than a cross-namespace calc output.
    ancestor_part_qns = _ancestor_part_qns(part_element)

    results: list[ComputedAttributeData] = []
    aliases: list[ChannelAlias] = []

    for member in part_element.owned_members:
        if not SysideAdapter.is_instance(member, "AttributeUsage"):
            continue

        # Guard: must have an expression
        if (
            not hasattr(member, "feature_value_expression")
            or member.feature_value_expression is None
        ):
            continue

        expr = member.feature_value_expression
        attr_name = member.name

        # Extract refs
        refs = extract_feature_refs(expr, ignore_std_lib=True)

        # Full chain segments for a FeatureChainExpression (Item 10, D9). The
        # multi-hop EXPOSE confirm walk reads this; None for non-chain exprs.
        # Computed before classification because the INV-E tentative gate reads it.
        reference_chain = extract_feature_chain_segments(expr) or None

        # Classify
        classification = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name=part_qn,
            calc_usage_names=calc_usage_names,
            sibling_attr_names=sibling_attr_names,
            expression_ast=expr,
            reference_chain=reference_chain,
            ancestor_part_qns=ancestor_part_qns,
        )

        # Skip LITERAL
        if classification == ComputedAttributeClassification.LITERAL:
            continue

        # Expression text (display only)
        expression_text = reconstruct_expression(expr)

        # Compilation: FORMULA only
        compiled_expression = None
        compilability = Compilability.MANUAL_REQUIRED

        if classification == ComputedAttributeClassification.FORMULA:
            # Self-exclusion: exclude the attribute being classified from
            # input_names so self-references raise (unresolved reference).
            # Sanitize names so they match the renderer's own _sanitize_name().
            input_names = {
                _sanitize_name(n) for n in sibling_attr_names
            } - {_sanitize_name(attr_name)}
            try:
                # Empty member_names: any non-input reference errors -> MANUAL_REQUIRED,
                # matching today's output_names=set()/all_member_names=None behavior.
                ir = extract_expression_ir(expr)
                if ir is None:
                    raise CompilationError(
                        f"extract_expression_ir returned None for {attr_name!r}"
                    )
                compiled_expression = render_calc_expression(ir, input_names, set())
                compilability = Compilability.FULLY_COMPILABLE
            except CompilationError as e:
                compiled_expression = None
                compilability = Compilability.MANUAL_REQUIRED
                logger.warning(
                    "FORMULA compilation failed for '%s' on '%s': %s",
                    attr_name,
                    part_name,
                    e,
                )

        if classification == ComputedAttributeClassification.UNRESOLVABLE:
            unresolvable_names = [r.name for r in refs]
            logger.warning(
                "Unresolvable attribute '%s' on '%s': refs=%s",
                attr_name,
                part_name,
                unresolvable_names,
            )

        logger.debug(
            "Classified '%s' on '%s': %s (compiled=%s)",
            attr_name,
            part_name,
            classification.value,
            compiled_expression,
        )

        python_name = _sanitize_name(attr_name)

        results.append(
            ComputedAttributeData(
                name=attr_name,
                python_name=python_name,
                owning_part_name=part_name,
                owning_part_qualified_name=part_qn,
                expression_ast=expr,
                expression_text=expression_text,
                references=refs,
                classification=classification,
                compilability=compilability,
                compiled_expression=compiled_expression,
                is_on_part_definition=is_part_def,
                reference_chain=reference_chain,
            )
        )

        # EXPOSE_PURE → ChannelAlias production
        if classification == ComputedAttributeClassification.EXPOSE_PURE and not is_part_def:
            if len(refs) < 2:
                logger.warning(
                    "EXPOSE_PURE '%s' on '%s' has fewer than 2 references, "
                    "skipping alias production: refs=%s",
                    attr_name,
                    part_name,
                    [r.name for r in refs],
                )
            else:
                # Classify refs by role, not index position.
                # Use calc_usage_names to identify the instance ref — same proven
                # pattern as graph_builder._resolve_expose_pure() (line 630-634).
                instance_name = None
                output_name = None
                for ref in refs:
                    if ref.name in calc_usage_names:
                        instance_name = ref.name
                    else:
                        output_name = ref.name

                if instance_name and output_name:
                    # Bare alias_name per C2 resolution — scoping at Phase 3 registration
                    aliases.append(ChannelAlias(
                        alias_name=python_name,
                        canonical_name=f"{instance_name}.{output_name}",
                        owning_part_qn=part_qn,
                        source="expose_pure",
                    ))
                else:
                    # D3-16: classification (EXPOSE_PURE) and alias production
                    # disagree. No local ref matched calc_usage_names, so no
                    # instance was identified — a cross-part single-hop calc-refs
                    # EXPOSE_PURE that the Item-10 tentative gate does not cover.
                    # Was silent (alias skipped, param never wired); warn instead.
                    logger.warning(
                        "EXPOSE_PURE '%s' on '%s' classified as an alias but no "
                        "local instance ref matched (refs=%s); the alias is "
                        "skipped and the channel left unwired — a cross-part "
                        "single-hop EXPOSE_PURE the Item-10 gate misses (D3-16).",
                        attr_name,
                        part_name,
                        [r.name for r in refs],
                    )

    return (results, aliases)
