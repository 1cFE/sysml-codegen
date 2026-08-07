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
from agentic_mbse.sysml.expression import feature_chain_facts
from agentic_mbse.sysml.helpers import get_calc_def_name
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.analysis.part_instance_index import build_part_instance_index
from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    extract_simple_name,
    sanitize_name,
    sanitize_qualified_name,
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
    owned_feature_typing_targets,
    user_partdef_lookup,
    user_partdef_types,
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


@dataclass(frozen=True)
class _DefAttribute:
    """One attribute declaration: name, identity, and its declared-value facts.

    ``chain_root``/``chain_members`` are set only for a pure feature-chain
    value (an EXPOSE) — resolved into an alias edge per occurrence.
    """

    name: str
    decl_qn: str
    default: float | int | str | bool | None
    chain_root: ResolvedTargetFact | None
    chain_members: tuple[str, ...]


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
    model: Any,
    calc_defs: Sequence[CalculationDefinitionData],
    *,
    strict: bool = True,
) -> InstanceGraph:
    """Elaborate a loaded SysIDE model into an :class:`InstanceGraph`.

    ``calc_defs`` is the already-extracted calculation-definition list the
    pipeline holds (``SysMLDataExtractor.extract_calculation_definitions``);
    it supplies each calc node's definition qualified name.

    ``strict`` selects halt-vs-report for the contract's unsupported source
    forms (self-binding, indexed, expression — spec R3): strict raises
    :class:`ElaborationError`; lenient records the same findings as graph
    diagnostics and elaborates everything else, so the dual-run diff can
    compare fixtures that carry known SRC-01 modeling defects. The switch
    never changes identity (design D9) — an offending binding is skipped,
    never reinterpreted.

    Both modes propagate the index's non-finite / recursive-containment
    failures (block-loud stands).
    """
    return _Elaborator(model, calc_defs, strict=strict).run()


class _Elaborator:
    def __init__(
        self,
        model: Any,
        calc_defs: Sequence[CalculationDefinitionData],
        *,
        strict: bool,
    ) -> None:
        self._model = model
        self._calc_defs = calc_defs
        self._strict = strict
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
        self._user_qn_set = set(self._qn_to_partdef)
        # Untyped part usages (no user-definition typing) are invisible to the
        # typed occurrence index, yet real plant models declare attributes and
        # calcs on them (catf_mfe: every calc usage). They get elaboration-local
        # occurrence contexts at their def-context-remapped qualified names —
        # the legacy index is not touched.
        self._untyped_by_path: dict[str, Any] = {}
        for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
            if self._is_user_typed(usage):
                continue
            for path in self._untyped_usage_paths(usage):
                self._untyped_by_path[path] = usage
        self._context_paths = set(self._occ_by_path) | set(self._untyped_by_path)
        self._graph = InstanceGraph()
        # Winning occurrence-override anchor depth per node (tier-1 bookkeeping).
        self._anchor_depth: dict[str, int] = {}
        self._pending: list[_PendingInput] = []
        # EXPOSE edges awaiting resolution: (node_id, attr_name, chain root, members).
        self._alias_pending: list[
            tuple[str, str, ResolvedTargetFact | None, tuple[str, ...]]
        ] = []
        self._def_attrs_cache: dict[str, list[_DefAttribute]] = {}

    def run(self) -> InstanceGraph:
        self._build_attr_nodes()
        self._build_usage_attr_nodes()
        self._build_package_attr_nodes()
        self._apply_value_tiers()
        self._build_calc_nodes()
        self._build_constraint_nodes()
        self._resolve_aliases()
        self._resolve_pending()
        return self._graph

    # ---- occurrence contexts beyond the typed index ------------------------

    def _is_user_typed(self, usage: Any) -> bool:
        """True when the part usage carries a user-model definition typing."""
        if user_partdef_types(usage, self._user_qn_set):
            return True
        return any(
            build_element_qualified_name(target) in self._user_qn_set
            for target in owned_feature_typing_targets(usage)
        )

    def _untyped_usage_paths(self, usage: Any) -> list[str]:
        """Context paths for an untyped part usage.

        Its sanitized qualified name, def-context-remapped so an untyped part
        nested inside a definition lands one context per occurrence of that
        definition. A definition-nested untyped part whose definition has no
        occurrence yields no context (same disposition as an uninstantiated
        template).
        """
        declared = build_element_qualified_name(usage)
        if not declared:
            return []
        paths = self._expand_def_context(declared)
        if paths == [declared] and self._is_definition_nested(usage):
            return []
        return paths

    @staticmethod
    def _is_definition_nested(usage: Any) -> bool:
        """True when any owner on the chain is a part definition."""
        current = getattr(usage, "owning_type", None)
        while current is not None:
            if SysideAdapter.is_instance(current, "PartDefinition"):
                return True
            current = getattr(current, "owning_type", None)
        return False

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
            for attr in self._definition_attributes(occ.part_def_qn):
                self._add_attr_node(occ.instance_path, attr)

    def _build_usage_attr_nodes(self) -> None:
        """Nodes for attributes declared on part usages themselves.

        Both typed and untyped usages author inline attributes (catf_mfe's
        exposed channels, d316's ``exposed``); the definition walk never sees
        them. A definition-declared attribute of the same name keeps its node
        (a same-name value override is a ``:>>`` ReferenceUsage, handled by the
        value tiers — not an AttributeUsage, so no legitimate shape collides).
        """
        for usage in SysideAdapter.elements_of_type(self._model, "PartUsage"):
            attrs = [
                self._attribute_facts(member)
                for member in getattr(usage, "owned_members", None) or []
                if SysideAdapter.is_instance(member, "AttributeUsage")
                and getattr(member, "name", None)
            ]
            if not attrs:
                continue
            for path in self._usage_attr_paths(usage):
                for attr in attrs:
                    self._add_attr_node(path, attr, keep_existing=True)

    def _build_package_attr_nodes(self) -> None:
        """Nodes for package-owned attributes (d316's ``seed_src``).

        A package-level attribute is a singleton: its one node is its sanitized
        qualified name. Detected by having no owning *type* — every def-, calc-,
        and usage-owned AttributeUsage has one.
        """
        for member in SysideAdapter.elements_of_type(self._model, "AttributeUsage"):
            if getattr(member, "owning_type", None) is not None:
                continue
            if not getattr(member, "name", None):
                continue
            declared = build_element_qualified_name(member)
            if not declared or "__" not in declared:
                continue
            path, _, _leaf = declared.rpartition("__")
            self._add_attr_node(path, self._attribute_facts(member), keep_existing=True)

    def _usage_attr_paths(self, usage: Any) -> list[str]:
        """The occurrence paths a usage's inline attributes materialize at."""
        raw_qn = getattr(usage, "qualified_name", None)
        if raw_qn is not None and self._is_user_typed(usage):
            return [
                occ.instance_path
                for occ in self._index.occurrences_of_part_usage(str(raw_qn))
            ]
        return self._untyped_usage_paths(usage)

    def _add_attr_node(
        self, path: str, attr: _DefAttribute, *, keep_existing: bool = False
    ) -> None:
        node_id = f"{path}__{attr.name}"
        if keep_existing and node_id in self._graph.attrs:
            return
        self._graph.attrs[node_id] = AttrNode(
            node_id=node_id,
            occurrence_path=path,
            attr_name=attr.name,
            decl_qn=attr.decl_qn,
            value=attr.default,
            value_site=(
                ValueSite.DEFINITION_DEFAULT
                if attr.default is not None
                else ValueSite.NONE
            ),
        )
        if attr.chain_members:
            self._alias_pending.append(
                (node_id, attr.name, attr.chain_root, attr.chain_members)
            )

    def _definition_attributes(self, def_key: str) -> list[_DefAttribute]:
        """Owned + inherited attribute declarations, own shadowing inherited."""
        cached = self._def_attrs_cache.get(def_key)
        if cached is not None:
            return cached
        out: list[_DefAttribute] = []
        seen: set[str] = set()
        queue: list[Any] = [self._qn_to_partdef[def_key]]
        while queue:
            current = queue.pop(0)
            for member in getattr(current, "owned_members", None) or []:
                if not SysideAdapter.is_instance(member, "AttributeUsage"):
                    continue
                if not getattr(member, "name", None):
                    continue
                attr = self._attribute_facts(member)
                if attr.name in seen:
                    continue
                seen.add(attr.name)
                out.append(attr)
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
    def _attribute_facts(member: Any) -> _DefAttribute:
        """One attribute declaration's name, identity, and value facts.

        The declared value has three relevant shapes: a literal (from ``= v``
        or a ``default v`` membership — the same dual surface
        ``SysMLDataExtractor._extract_default_value`` reads) becomes the
        definition-default value tier; a pure feature chain is an EXPOSE and
        yields the alias facts; anything else (a FORMULA expression) is not a
        value here — computed attributes are calc nodes (D6, later leg).
        """
        name = sanitize_name(getattr(member, "name", ""))
        decl_qn = str(getattr(member, "qualified_name", "") or "")
        expr = getattr(member, "feature_value_expression", None)
        if expr is None:
            for membership in getattr(member, "owned_memberships", None) or []:
                if getattr(membership, "is_default", False):
                    value_expr = getattr(membership, "value", None)
                    if value_expr is not None:
                        expr = value_expr
                        break
        if expr is None:
            return _DefAttribute(name, decl_qn, None, None, ())
        if is_literal_expression(expr):
            return _DefAttribute(name, decl_qn, extract_literal_value(expr), None, ())
        if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
            root, _leaf, _qns, members, has_index = feature_chain_facts(expr)
            if not has_index:
                return _DefAttribute(name, decl_qn, None, root, members)
        return _DefAttribute(name, decl_qn, None, None, ())

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
        blocked: set[tuple[str, str]] = set()
        if findings:
            if self._strict:
                raise ElaborationError(findings)
            for finding in findings:
                blocked.add((finding.usage_qualified_name, finding.param_name))
                self._graph.diagnostics.append(
                    Diagnostic(
                        code=finding.code,
                        consumer=finding.usage_qualified_name,
                        param_name=finding.param_name,
                        detail=finding.detail,
                    )
                )

        for usage in usages:
            placed = False
            for path in self._calc_placement_paths(usage):
                parent, _, leaf = path.rpartition("__")
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
                    if (usage.qualified_name, binding.param_name) in blocked:
                        continue
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

    def _calc_placement_paths(self, usage: Any) -> list[str]:
        """Where a calc declaration materializes.

        One path per concrete occurrence context enclosing it, via the remap
        rule — plus the package-rooted case (``calc gen`` directly in a
        package: concrete, no parent part, no owning definition), which is its
        own single node.
        """
        paths = [
            path
            for path in self._expand_def_context(usage.qualified_name)
            if path.rpartition("__")[0] in self._context_paths
        ]
        if not paths and (
            not usage.is_template
            and not usage.parent_part_path
            and usage.owning_part_def_qn is None
        ):
            return [usage.qualified_name]
        return paths

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
                if parent not in self._context_paths:
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

    # ---- stage 5: alias + binding resolution (D5) --------------------------

    def _resolve_aliases(self) -> None:
        """Resolve every EXPOSE edge with the same chain rule consumers use.

        Alias targets are stored one hop deep (an expose of an expose stays a
        node reference); consumers follow chains transitively at resolution.
        """
        for node_id, attr_name, chain_root, chain_members in self._alias_pending:
            ref = self._resolve_chain(node_id, attr_name, chain_root, chain_members)
            if ref is not None:
                self._graph.attrs[node_id].alias_target = ref

    def _follow_aliases(self, ref: InputRef) -> InputRef:
        """The real source behind a resolved reference: exposed attributes are
        aliases, never sources of their own (spec R2)."""
        seen: set[str] = set()
        while isinstance(ref, NodeRef):
            node = self._graph.attrs.get(ref.node_id)
            if node is None or node.alias_target is None:
                return ref
            if ref.node_id in seen:
                logger.warning(
                    "Alias cycle through %s; leaving the reference on the "
                    "cycle node.",
                    ref.node_id,
                )
                return ref
            seen.add(ref.node_id)
            ref = node.alias_target
        return ref

    def _resolve_pending(self) -> None:
        for pending in self._pending:
            ref = self._resolve_evidence(
                pending.consumer_path,
                pending.param_name,
                pending.evidence,
                pending.literal_value,
            )
            if ref is not None:
                pending.inputs[pending.param_name] = self._follow_aliases(ref)

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
            finding = ReadinessFinding(
                code=unsupported,
                usage_qualified_name=consumer_path,
                param_name=param_name,
                detail=(
                    f"unsupported source form "
                    f"{evidence.source_form.value} "
                    f"({evidence.written_text or ''!r})"
                ),
            )
            if self._strict:
                raise ElaborationError([finding])
            self._graph.diagnostics.append(
                Diagnostic(
                    code=finding.code,
                    consumer=consumer_path,
                    param_name=param_name,
                    detail=finding.detail,
                )
            )
            return None
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
        """The consumer's enclosing occurrence contexts, innermost first."""
        segments = consumer_path.split("__")
        ancestors: list[str] = []
        for cut in range(len(segments) - 1, 0, -1):
            candidate = "__".join(segments[:cut])
            if candidate in self._context_paths:
                ancestors.append(candidate)
        return ancestors

    def _resolve_chain(
        self,
        consumer_path: str,
        param_name: str,
        root_fact: ResolvedTargetFact | None,
        members: tuple[str, ...],
    ) -> InputRef | None:
        """Chain rule (D5): anchor the root at the innermost enclosing
        occurrence that contains it, then descend resolved member names.

        The root may itself be a calc usage (sibling-calc chaining:
        ``in area = area_calc.area``) — that anchor IS the producer. A root on
        no enclosing context (cross-package: ``catf_blanket.pump_power``)
        anchors at the root element's own occurrence when unique.
        """
        if root_fact is None:
            self._miss(
                consumer_path,
                param_name,
                f"feature chain has no resolved root (members {members!r})",
            )
            return None
        root_feature = self._fact_leaf(root_fact)
        member_list = list(members)
        for ancestor in self._ancestors(consumer_path):
            candidate = f"{ancestor}__{root_feature}"
            if candidate in self._graph.calcs:
                return self._producer_from_chain(
                    consumer_path, param_name, candidate, member_list
                )
            if candidate in self._context_paths or any(
                path.startswith(f"{candidate}[") for path in self._occ_by_path
            ):
                return self._descend(
                    consumer_path, param_name, candidate, member_list
                )
        return self._resolve_chain_off_ancestor(
            consumer_path, param_name, root_fact, member_list
        )

    def _resolve_chain_off_ancestor(
        self,
        consumer_path: str,
        param_name: str,
        root_fact: ResolvedTargetFact,
        members: list[str],
    ) -> InputRef | None:
        """Anchor a chain whose root is on no enclosing context: the root
        element's own occurrence, when it is unique."""
        root_paths = self._element_context_paths(root_fact)
        calc_anchors = [path for path in root_paths if path in self._graph.calcs]
        part_anchors = [path for path in root_paths if path in self._context_paths]
        anchors = calc_anchors + part_anchors
        if len(anchors) == 1:
            if calc_anchors:
                return self._producer_from_chain(
                    consumer_path, param_name, anchors[0], members
                )
            return self._descend(consumer_path, param_name, anchors[0], members)
        if anchors:
            self._graph.diagnostics.append(
                Diagnostic(
                    code=ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    consumer=consumer_path,
                    param_name=param_name,
                    detail=(
                        f"chain root {root_fact.qualified_name!r} occurs at "
                        f"{sorted(anchors)!r} and none encloses the consumer"
                    ),
                )
            )
            return None
        self._miss(
            consumer_path,
            param_name,
            f"no enclosing occurrence contains chain root "
            f"{root_fact.qualified_name!r} and it has no occurrence of its own",
        )
        return None

    def _producer_from_chain(
        self,
        consumer_path: str,
        param_name: str,
        calc_node_id: str,
        members: list[str],
    ) -> InputRef | None:
        """A chain anchored AT a calc node: exactly one member (the output)."""
        if len(members) == 1:
            return ProducerRef(calc_node_id, sanitize_name(members[0]))
        self._miss(
            consumer_path,
            param_name,
            f"chain continues past producer {calc_node_id!r} with tail "
            f"{members!r}",
        )
        return None

    def _element_context_paths(self, fact: ResolvedTargetFact) -> list[str]:
        """The concrete paths where a referenced element itself materializes."""
        raw_qn = str(fact.qualified_name)
        if fact.element_kind == "PartUsage":
            occurrences = self._index.occurrences_of_part_usage(raw_qn)
            if occurrences:
                return [occ.instance_path for occ in occurrences]
        return self._expand_def_context(sanitize_qualified_name(raw_qn))

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
                    occurrence = self._occ_by_path.get(ancestor)
                    if occurrence is None:
                        continue  # an untyped context has no definition
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
        if not fact.owner_qualified_name:
            # Package-level referent: a package-owned attribute is a singleton
            # node at its own sanitized qualified name.
            node = self._graph.attrs.get(
                sanitize_qualified_name(str(fact.qualified_name))
            )
            if node is not None:
                return NodeRef(node.node_id)
            self._miss(
                consumer_path,
                param_name,
                f"package-level referent {fact.qualified_name!r} has no node",
            )
            return None
        # Usage-level referent (D5): the owner usage's occurrence on the
        # consumer's ancestor chain; unique otherwise; else ambiguous. An
        # untyped owner has no entry in the typed index — its contexts come
        # from the remapped qualified name.
        occurrences = self._index.occurrences_of_part_usage(
            fact.owner_qualified_name
        )
        candidates = [occ.instance_path for occ in occurrences]
        if not candidates:
            candidates = [
                path
                for path in self._expand_def_context(
                    sanitize_qualified_name(fact.owner_qualified_name)
                )
                if path in self._context_paths
            ]
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
