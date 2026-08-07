"""The one elaboration pass (ELABORATE-FIRST Item 4 design, D2–D5).

``elaborate(model, calc_defs)`` walks the live SysIDE model once and produces
an :class:`~sysml_codegen.elaboration.graph.InstanceGraph`:

1. Occurrence expansion — ``PartInstanceIndex``, the one existing walker.
2. Attribute nodes per occurrence, with the definition-default value tier.
3. Value tiers, innermost-wins (D4): occurrence ``:>>`` (deepest anchor) >
   specialized-def ``:>>`` > definition default.
4. Calc/constraint nodes from AST *declarations* (D2): calc usages extracted
   with ``expand_templates=False`` and ``ConstraintUsage`` swept with subtypes,
   each expanded per occurrence by the def-context remap rule (D3) — never the
   legacy virtual expansion, which half-misses def-nested-usage calcs.
5. Binding resolution over the shared Item-2 evidence: one contextualization
   rule per referent class (D5). Misses are named diagnostics, never fallback
   inputs; unsupported source forms (contract D8) hard-fail.

The def-context remap rule (D3) does two jobs with one mechanism: it anchors
definition-relative occurrence overrides (the C19 fix) and it places
def-declared calcs/constraints onto concrete occurrences. No other bridge
between definition space and occurrence space exists.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from agentic_mbse.sysml.data_models import ResolvedTargetFact
from agentic_mbse.sysml.helpers import get_calc_def_name
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.analysis.part_instance_index import build_part_instance_index
from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    extract_simple_name,
    sanitize_name,
)
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    Diagnostic,
    ElaborationCode,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    ProducerRef,
    ValueSite,
)
from sysml_codegen.extraction import binding_evidence
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.expression_utils import (
    extract_literal_value,
    is_literal_expression,
)
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.source_evidence import (
    ReadinessCode,
    ReadinessFinding,
    SourceForm,
    SourceReferenceEvidence,
    screen_source_readiness,
)
from sysml_codegen.extraction.usage_extractor import (
    _supertype_closure,
    extract_calculation_usages,
    user_partdef_lookup,
)

logger = logging.getLogger(__name__)

__all__ = ["ElaborationError", "elaborate"]


class ElaborationError(Exception):
    """Hard elaboration failure: unsupported source forms (contract D8, spec R3).

    Carries every finding so the caller sees all offending bindings at once,
    not the first one per rerun.
    """

    def __init__(self, findings: Sequence[ReadinessFinding]) -> None:
        self.findings = tuple(findings)
        super().__init__(
            "; ".join(
                f"{f.code.value}: {f.usage_qualified_name}.{f.param_name}"
                for f in self.findings
            )
        )


@dataclass
class _PendingInput:
    """One binding awaiting resolution after every node exists (two-pass).

    Resolution needs the complete calc-node population — a chain into a
    producer output (C24) must find the producer's node regardless of the
    order declarations came off the AST.
    """

    inputs: dict[str, InputRef]
    consumer_path: str
    param_name: str
    evidence: SourceReferenceEvidence | None
    literal_value: float | int | str | bool | None


def elaborate(
    model: Any, calc_defs: Sequence[CalculationDefinitionData]
) -> InstanceGraph:
    """Elaborate a loaded SysIDE model into an :class:`InstanceGraph`.

    ``calc_defs`` is the already-extracted calculation-definition list the
    pipeline holds (``SysMLDataExtractor.extract_calculation_definitions``);
    it supplies each calc node's definition qualified name.

    Raises :class:`ElaborationError` for unsupported source forms (self-binding,
    indexed, expression — spec R3) and propagates the index's non-finite /
    recursive-containment failures (block-loud stands).
    """
    return _Elaborator(model, calc_defs).run()


class _Elaborator:
    def __init__(
        self, model: Any, calc_defs: Sequence[CalculationDefinitionData]
    ) -> None:
        self._model = model
        self._calc_defs = calc_defs
        self._index = build_part_instance_index(model)
        self._hier = extract_hierarchy_data(model)
        self._qn_to_partdef = user_partdef_lookup(model)
        self._def_raw_to_key = {
            str(raw): key
            for key, part_def in self._qn_to_partdef.items()
            if (raw := getattr(part_def, "qualified_name", None)) is not None
        }
        self._occs_by_def = {
            key: self._index.occurrences_of(key) for key in self._qn_to_partdef
        }
        self._occ_by_path = {
            occ.instance_path: occ
            for occs in self._occs_by_def.values()
            for occ in occs
        }
        self._graph = InstanceGraph()
        # Winning occurrence-override anchor depth per node (tier-1 bookkeeping).
        self._anchor_depth: dict[str, int] = {}
        self._pending: list[_PendingInput] = []
        self._def_attrs_cache: dict[
            str, list[tuple[str, str, float | int | str | bool | None]]
        ] = {}

    def run(self) -> InstanceGraph:
        self._build_attr_nodes()
        self._apply_value_tiers()
        self._build_calc_nodes()
        self._build_constraint_nodes()
        self._resolve_pending()
        return self._graph

    # ---- the def-context remap rule (D3) ---------------------------------

    def _expand_def_context(self, sanitized_path: str) -> list[str]:
        """Longest def-key prefix of a definition-relative path -> one path per
        occurrence of that definition; occurrence-rooted paths pass through
        unchanged.

        THE rule that fixes C19 (definition-relative capture vs occurrence-
        relative demand), also used to place def-declared calcs and
        constraints — one rule, two jobs (D3).
        """
        segments = sanitized_path.split("__")
        for cut in range(len(segments) - 1, 0, -1):
            prefix = "__".join(segments[:cut])
            if prefix in self._occs_by_def:
                tail = segments[cut:]
                return [
                    "__".join([occ.instance_path, *tail])
                    for occ in self._occs_by_def[prefix]
                ]
        return [sanitized_path]

    # ---- stage 2: attribute nodes ----------------------------------------

    def _build_attr_nodes(self) -> None:
        for occ in self._occ_by_path.values():
            for name, decl_qn, default in self._definition_attributes(
                occ.part_def_qn
            ):
                node_id = f"{occ.instance_path}__{name}"
                self._graph.attrs[node_id] = AttrNode(
                    node_id=node_id,
                    occurrence_path=occ.instance_path,
                    attr_name=name,
                    decl_qn=decl_qn,
                    value=default,
                    value_site=(
                        ValueSite.DEFINITION_DEFAULT
                        if default is not None
                        else ValueSite.NONE
                    ),
                )

    def _definition_attributes(
        self, def_key: str
    ) -> list[tuple[str, str, float | int | str | bool | None]]:
        """(name, declaration raw QN, default literal) for owned + inherited
        attributes, own declarations shadowing inherited ones."""
        cached = self._def_attrs_cache.get(def_key)
        if cached is not None:
            return cached
        out: list[tuple[str, str, float | int | str | bool | None]] = []
        seen: set[str] = set()
        queue: list[Any] = [self._qn_to_partdef[def_key]]
        while queue:
            current = queue.pop(0)
            for member in getattr(current, "owned_members", None) or []:
                if not SysideAdapter.is_instance(member, "AttributeUsage"):
                    continue
                raw_name = getattr(member, "name", None)
                if not raw_name:
                    continue
                name = sanitize_name(raw_name)
                if name in seen:
                    continue
                seen.add(name)
                decl_qn = str(getattr(member, "qualified_name", "") or "")
                out.append((name, decl_qn, self._attribute_default(member)))
            for relationship, target in getattr(current, "heritage", None) or []:
                if (
                    SysideAdapter.is_instance(relationship, "Subclassification")
                    and target is not None
                    # User definitions only: following implicit specialization
                    # into the standard library would mint nodes for library
                    # attributes (Part::isSolid etc.) no consumer can reach.
                    and build_element_qualified_name(target) in self._qn_to_partdef
                ):
                    queue.append(target)
        self._def_attrs_cache[def_key] = out
        return out

    @staticmethod
    def _attribute_default(member: Any) -> float | int | str | bool | None:
        """The declaration's literal default, from ``= v`` or ``default v``.

        A ``default`` keyword value lives on a default-membership, not on
        ``feature_value_expression`` (same dual surface
        ``SysMLDataExtractor._extract_default_value`` reads). A non-literal
        value expression (a FORMULA attribute) is not a default — computed
        attributes are calc nodes (D6, Item-5 Phase 2).
        """
        expr = getattr(member, "feature_value_expression", None)
        if expr is not None and is_literal_expression(expr):
            return extract_literal_value(expr)
        for membership in getattr(member, "owned_memberships", None) or []:
            if not getattr(membership, "is_default", False):
                continue
            value_expr = getattr(membership, "value", None)
            if value_expr is not None and is_literal_expression(value_expr):
                return extract_literal_value(value_expr)
        return None

    # ---- stage 3: value tiers, innermost-wins (D4) ------------------------

    def _apply_value_tiers(self) -> None:
        # Tier 2 first (specialized-def :>> literals), so tier 1 overwrites.
        # Multi-level def-tier shadowing (a :>> on both a def and its subtype)
        # is the Phase-2 spec-chain leg; no Phase-1 fixture authors it.
        for redefinition in self._hier.redefinitions:
            if redefinition.literal_value is None:
                continue
            attr_name = sanitize_name(redefinition.attribute_name)
            for path in self._expand_def_context(redefinition.owning_part_qn):
                node = self._graph.attrs.get(f"{path}__{attr_name}")
                if node is None:
                    continue
                node.value = redefinition.literal_value
                node.value_site = ValueSite.SPECIALIZED_DEF

        # Tier 1: occurrence :>> overrides; the deepest anchor wins.
        for override in self._hier.design_overrides:
            if override.literal_value is None:
                continue
            if override.is_deep_path:
                tail = [sanitize_name(seg) for seg in override.target_path[:-1]]
                leaf = sanitize_name(override.target_path[-1])
            else:
                tail = []
                leaf = sanitize_name(override.attribute_name)
            for anchor in self._expand_def_context(override.owning_part_qn):
                depth = anchor.count("__")
                node_path = "__".join([anchor, *tail]) if tail else anchor
                node_id = f"{node_path}__{leaf}"
                node = self._graph.attrs.get(node_id)
                if node is None:
                    self._graph.diagnostics.append(
                        Diagnostic(
                            code=ElaborationCode.OVERRIDE_TARGET_MISSING,
                            consumer=node_id,
                            param_name=None,
                            detail=(
                                f"{override.owning_part_qn} :>> "
                                f"{'.'.join([*tail, leaf])} = "
                                f"{override.literal_value!r} has no target "
                                "attribute node"
                            ),
                        )
                    )
                    continue
                if (
                    node.value_site is ValueSite.OCCURRENCE_OVERRIDE
                    and self._anchor_depth[node_id] >= depth
                ):
                    continue
                node.value = override.literal_value
                node.value_site = ValueSite.OCCURRENCE_OVERRIDE
                self._anchor_depth[node_id] = depth

    # ---- stage 4: calc + constraint nodes (D2) -----------------------------

    def _build_calc_nodes(self) -> None:
        usages, _report = extract_calculation_usages(
            self._model, calc_defs=list(self._calc_defs), expand_templates=False
        )
        findings = screen_source_readiness(usages)
        if findings:
            raise ElaborationError(findings)

        for usage in usages:
            placed = False
            for path in self._expand_def_context(usage.qualified_name):
                parent, _, leaf = path.rpartition("__")
                if parent not in self._occ_by_path:
                    continue
                node = CalcNode(
                    node_id=path,
                    calc_name=leaf,
                    calc_def_name=usage.calc_def_name,
                    calc_def_qualified_name=usage.calc_def_qualified_name,
                    unbound_params=tuple(usage.unbound_params),
                )
                self._graph.calcs[path] = node
                placed = True
                for binding in usage.bindings:
                    self._pending.append(
                        _PendingInput(
                            inputs=node.inputs,
                            consumer_path=path,
                            param_name=binding.param_name,
                            evidence=binding.reference_evidence,
                            literal_value=binding.literal_value,
                        )
                    )
            if not placed:
                logger.warning(
                    "Calc usage '%s' has no concrete occurrence context; "
                    "no node elaborated.",
                    usage.qualified_name,
                )

    def _build_constraint_nodes(self) -> None:
        for constraint in SysideAdapter.elements_of_type(
            self._model, "ConstraintUsage", include_subtypes=True
        ):
            declared_path = build_element_qualified_name(constraint)
            if not declared_path:
                continue
            def_name = sanitize_name(get_calc_def_name(constraint) or "")
            actuals = self._constraint_actuals(constraint)
            placed = False
            for path in self._expand_def_context(declared_path):
                parent, _, _leaf = path.rpartition("__")
                if parent not in self._occ_by_path:
                    continue
                node = ConstraintNode(node_id=path, constraint_def_name=def_name)
                self._graph.constraints[path] = node
                placed = True
                for param_name, evidence, literal_value in actuals:
                    self._pending.append(
                        _PendingInput(
                            inputs=node.inputs,
                            consumer_path=path,
                            param_name=param_name,
                            evidence=evidence,
                            literal_value=literal_value,
                        )
                    )
            if not placed:
                logger.debug(
                    "Constraint usage '%s' has no concrete occurrence context; "
                    "no node elaborated.",
                    declared_path,
                )

    @staticmethod
    def _constraint_actuals(
        constraint: Any,
    ) -> list[
        tuple[str, SourceReferenceEvidence, float | int | str | bool | None]
    ]:
        """(param, evidence, literal) for each bound constraint parameter.

        Built with the same shared evidence builders as calc bindings, so
        constraint actuals ride the identical resolution rules (D7) — including
        the hard failure for unsupported source forms. Parameters with no value
        expression are unbound formals, not actuals.
        """
        actuals: list[
            tuple[str, SourceReferenceEvidence, float | int | str | bool | None]
        ] = []
        for member in getattr(constraint, "owned_members", None) or []:
            expr = getattr(member, "feature_value_expression", None)
            if expr is None:
                continue
            raw_name = getattr(member, "name", None)
            if not raw_name:
                continue
            param_name = sanitize_name(raw_name)
            # FeatureChainExpression MUST be before OperatorExpression -- FCE
            # is a subtype of OE in SysIDE's type system (doc 19 invariant).
            if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
                actuals.append(
                    (param_name, binding_evidence.chain_evidence(member, expr), None)
                )
            elif SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
                actuals.append(
                    (
                        param_name,
                        binding_evidence.reference_evidence(member, expr),
                        None,
                    )
                )
            elif is_literal_expression(expr):
                literal = extract_literal_value(expr)
                actuals.append(
                    (
                        param_name,
                        binding_evidence.literal_evidence(member, literal),
                        literal,
                    )
                )
            elif SysideAdapter.is_instance(expr, "OperatorExpression"):
                # Expression actual: unsupported source form — resolution
                # hard-fails it with the contract code (spec R3).
                actuals.append(
                    (
                        param_name,
                        binding_evidence.expression_evidence(member, expr),
                        None,
                    )
                )
        return actuals

    # ---- stage 5: binding resolution (D5) ----------------------------------

    def _resolve_pending(self) -> None:
        for pending in self._pending:
            ref = self._resolve_evidence(
                pending.consumer_path,
                pending.param_name,
                pending.evidence,
                pending.literal_value,
            )
            if ref is not None:
                pending.inputs[pending.param_name] = ref

    def _resolve_evidence(
        self,
        consumer_path: str,
        param_name: str,
        evidence: SourceReferenceEvidence | None,
        literal_value: float | int | str | bool | None,
    ) -> InputRef | None:
        if evidence is None:
            raise RuntimeError(
                f"binding {consumer_path}.{param_name} carries no source "
                "evidence; live elaboration always captures evidence"
            )
        if evidence.source_form is SourceForm.AUTHORED_LITERAL:
            if literal_value is None:
                raise RuntimeError(
                    f"authored literal {consumer_path}.{param_name} has no value"
                )
            return LiteralInput(literal_value)
        unsupported = self._unsupported_form_code(evidence)
        if unsupported is not None:
            # Calc bindings are screened wholesale before node creation; this
            # arm enforces the same contract codes for constraint actuals.
            raise ElaborationError(
                [
                    ReadinessFinding(
                        code=unsupported,
                        usage_qualified_name=consumer_path,
                        param_name=param_name,
                        detail=(
                            f"unsupported source form "
                            f"{evidence.source_form.value} "
                            f"({evidence.written_text or ''!r})"
                        ),
                    )
                ]
            )
        if evidence.source_form is SourceForm.FEATURE_CHAIN:
            return self._resolve_chain(
                consumer_path,
                param_name,
                evidence.chain_root,
                evidence.resolved_member_names,
            )
        if evidence.referent is not None:
            return self._resolve_reference(
                consumer_path, param_name, evidence.referent
            )
        raise RuntimeError(
            f"evidence for {consumer_path}.{param_name} has form "
            f"{evidence.source_form.value} but no referent to resolve"
        )

    @staticmethod
    def _unsupported_form_code(
        evidence: SourceReferenceEvidence,
    ) -> ReadinessCode | None:
        if evidence.is_self_binding:
            return ReadinessCode.SI_SELF_BINDING
        if evidence.source_form is SourceForm.INDEXED_SOURCE:
            return ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED
        if evidence.source_form is SourceForm.EXPRESSION_SOURCE:
            return ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED
        return None

    def _ancestors(self, consumer_path: str) -> list[str]:
        """The consumer's enclosing occurrence paths, innermost first."""
        segments = consumer_path.split("__")
        ancestors: list[str] = []
        for cut in range(len(segments) - 1, 0, -1):
            candidate = "__".join(segments[:cut])
            if candidate in self._occ_by_path:
                ancestors.append(candidate)
        return ancestors

    def _resolve_chain(
        self,
        consumer_path: str,
        param_name: str,
        root_fact: ResolvedTargetFact | None,
        members: tuple[str, ...],
    ) -> InputRef | None:
        """Chain rule (D5): anchor the root usage at the innermost enclosing
        occurrence that contains it, then descend resolved member names."""
        if root_fact is None:
            self._miss(
                consumer_path,
                param_name,
                f"feature chain has no resolved root (members {members!r})",
            )
            return None
        root_feature = self._fact_leaf(root_fact)
        for ancestor in self._ancestors(consumer_path):
            candidate = f"{ancestor}__{root_feature}"
            if candidate in self._occ_by_path or any(
                path.startswith(f"{candidate}[") for path in self._occ_by_path
            ):
                return self._descend(
                    consumer_path, param_name, candidate, list(members)
                )
        self._miss(
            consumer_path,
            param_name,
            f"no enclosing occurrence contains chain root "
            f"{root_fact.qualified_name!r}",
        )
        return None

    def _descend(
        self,
        consumer_path: str,
        param_name: str,
        base_path: str,
        members: list[str],
    ) -> InputRef | None:
        path = base_path
        for i, raw_member in enumerate(members):
            member = sanitize_name(raw_member)
            calc_candidate = f"{path}__{member}"
            if calc_candidate in self._graph.calcs:
                rest = members[i + 1 :]
                if len(rest) == 1:
                    return ProducerRef(calc_candidate, sanitize_name(rest[0]))
                self._miss(
                    consumer_path,
                    param_name,
                    f"chain continues past producer {calc_candidate!r} "
                    f"with tail {rest!r}",
                )
                return None
            if i == len(members) - 1:
                node = self._graph.attrs.get(f"{path}__{member}")
                if node is not None:
                    return NodeRef(node.node_id)
                self._miss(
                    consumer_path,
                    param_name,
                    f"chain member {path}__{member} is not an attribute node",
                )
                return None
            path = f"{path}__{member}"
        self._miss(consumer_path, param_name, f"empty chain at {base_path!r}")
        return None

    def _resolve_reference(
        self, consumer_path: str, param_name: str, fact: ResolvedTargetFact
    ) -> InputRef | None:
        leaf = self._fact_leaf(fact)
        if fact.owner_is_definition:
            # Def-level referent (D5): innermost enclosing occurrence whose
            # definition (incl. supertype closure) declares the referent.
            owner_key = self._def_raw_to_key.get(fact.owner_qualified_name)
            if owner_key is not None:
                for ancestor in self._ancestors(consumer_path):
                    occurrence = self._occ_by_path[ancestor]
                    if self._def_declares(occurrence.part_def_qn, owner_key):
                        node = self._graph.attr_at(ancestor, leaf)
                        if node is not None:
                            return NodeRef(node.node_id)
            self._miss(
                consumer_path,
                param_name,
                f"no enclosing occurrence's definition declares "
                f"{fact.qualified_name!r}",
            )
            return None
        # Usage-level referent (D5): the owner usage's occurrence on the
        # consumer's ancestor chain; unique otherwise; else ambiguous.
        occurrences = self._index.occurrences_of_part_usage(
            fact.owner_qualified_name
        )
        candidates = [occ.instance_path for occ in occurrences]
        on_chain = [
            path
            for path in candidates
            if consumer_path == path or consumer_path.startswith(f"{path}__")
        ]
        picks = on_chain or candidates
        if len(picks) == 1:
            node = self._graph.attr_at(picks[0], leaf)
            if node is not None:
                return NodeRef(node.node_id)
            self._miss(
                consumer_path,
                param_name,
                f"referent owner occurrence {picks[0]!r} has no attribute "
                f"{leaf!r}",
            )
            return None
        if not picks:
            self._miss(
                consumer_path,
                param_name,
                f"referent owner {fact.owner_qualified_name!r} has no "
                "concrete occurrence",
            )
            return None
        self._graph.diagnostics.append(
            Diagnostic(
                code=ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                consumer=consumer_path,
                param_name=param_name,
                detail=(
                    f"{fact.qualified_name!r} owner occurs at "
                    f"{sorted(picks)!r} and none encloses the consumer"
                ),
            )
        )
        return None

    def _def_declares(self, part_def_qn: str, owner_key: str) -> bool:
        """True when ``part_def_qn`` is ``owner_key`` or specializes it."""
        if part_def_qn == owner_key:
            return True
        return owner_key in _supertype_closure(part_def_qn, self._qn_to_partdef)

    @staticmethod
    def _fact_leaf(fact: ResolvedTargetFact) -> str:
        return sanitize_name(
            fact.element_name or extract_simple_name(fact.qualified_name)
        )

    def _miss(self, consumer_path: str, param_name: str, detail: str) -> None:
        self._graph.diagnostics.append(
            Diagnostic(
                code=ElaborationCode.SI_OCCURRENCE_MISSING,
                consumer=consumer_path,
                param_name=param_name,
                detail=detail,
            )
        )
