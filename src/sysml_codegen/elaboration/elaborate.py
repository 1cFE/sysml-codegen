"""One exact-ID elaboration pass from the live SysIDE model to direct edges."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.constraint_extraction import (
    extract_constraint_facts,
    extract_expression_ir,
)
from agentic_mbse.sysml.data_models import ResolvedSemanticReferenceFact
from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_profile
from agentic_mbse.sysml.expression import (
    feature_chain_facts,
    is_literal_node,
    resolved_target_fact,
)
from agentic_mbse.sysml.expression_ir import serialize_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.analysis.constraint_lowering import resolve_modeled_default
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.display import display_name, display_qualified_name
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
    PortMetadata,
    ProducerRef,
    ValueSite,
)
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    FeatureSlotId,
    IdentityBoundaryError,
    NodeId,
    NodeKind,
    OccurrenceId,
    OutputPortId,
    PackageScopeId,
    ResolvedSemanticReference,
    ScopeId,
    declaration_id_for,
)
from sysml_codegen.elaboration.occurrence import (
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction import binding_evidence
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.expression_compiler import Compilability, compile_calc_def
from sysml_codegen.extraction.expression_utils import extract_literal_value
from sysml_codegen.extraction.source_evidence import (
    ReadinessCode,
    ReadinessFinding,
    SourceForm,
    SourceReferenceEvidence,
)

__all__ = ["ElaborationDiagnosticError", "ElaborationError", "elaborate"]


class ElaborationError(Exception):
    """A strict elaboration stopped on every collected blocking binding form."""

    def __init__(self, findings: Sequence[ReadinessFinding]) -> None:
        self.findings = tuple(findings)
        super().__init__(
            "; ".join(
                f"{finding.code.value}: {finding.usage_qualified_name}.{finding.param_name}"
                for finding in self.findings
            )
        )


class ElaborationDiagnosticError(Exception):
    """Strict elaboration stopped on named graph/identity diagnostics."""

    def __init__(self, diagnostics: Sequence[Diagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__(
            "; ".join(
                f"{diagnostic.code.value}: {diagnostic.consumer_display}: {diagnostic.detail}"
                for diagnostic in diagnostics
            )
        )


class _ReferenceResolutionError(Exception):
    def __init__(self, code: ElaborationCode, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(detail)


class _UnsupportedExpressionError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


_SUM_FUNCTION_ID = DeclarationId(UUID("6d745ea3-e265-5ddd-aa6c-b3fe29dc4272"))
_NAMESPACE_DISTINGUISHABILITY_CODE = "namespace-distinguishability"


@dataclass(frozen=True)
class _PendingBinding:
    consumer: CalcNode | ConstraintNode
    port: ConsumerPortId
    evidence: SourceReferenceEvidence
    literal_value: float | int | str | bool | None


@dataclass(frozen=True)
class _PendingExpression:
    consumer: CalcNode | ConstraintNode
    expression: Any


@dataclass(frozen=True)
class _PendingAlias:
    node: AttrNode
    expression: Any


def elaborate(
    model: Any,
    calc_defs: Sequence[CalculationDefinitionData],
    *,
    validation_diagnostics: Sequence[Any],
    strict: bool = True,
) -> InstanceGraph:
    """Resolve a live model into one typed instance graph.

    ``calc_defs`` remains the verified integration argument until projection
    replaces the current call sites. Semantic construction reads exact live
    declarations and does not use extraction names for identity.
    """
    model_diagnostics = _blocking_model_validation_diagnostics(model, validation_diagnostics)
    if model_diagnostics:
        if strict:
            raise ElaborationDiagnosticError(model_diagnostics)
        return InstanceGraph(diagnostics=list(model_diagnostics))

    try:
        return _ExactElaborator(model, calc_defs, strict=strict).run()
    except ElaborationInvariantError as error:
        raise ElaborationDiagnosticError(
            (
                Diagnostic(
                    code=error.code,
                    consumer=None,
                    consumer_display="<model>",
                    param_name=None,
                    detail=error.detail,
                ),
            )
        ) from error


def _blocking_model_validation_diagnostics(
    model: Any,
    validation_diagnostics: Sequence[Any],
) -> tuple[Diagnostic, ...]:
    """Promote SysIDE's invalid inherited/owned part conflicts."""
    part_locations = {
        (str(Path(source_location[0]).resolve()), source_location[1])
        for part in SysideAdapter.elements_of_type(model, "PartUsage")
        if (source_location := SysideAdapter.get_source_location(part)) is not None
    }
    result: list[Diagnostic] = []
    for upstream in validation_diagnostics:
        if getattr(upstream, "code", None) != _NAMESPACE_DISTINGUISHABILITY_CODE:
            continue
        filename = getattr(upstream, "filename", None)
        line = getattr(upstream, "line", 0)
        if filename is None or (str(Path(filename).resolve()), line) not in part_locations:
            continue
        diagnostic_location = f"{filename}:{line}:{getattr(upstream, 'col', 0)}"
        result.append(
            Diagnostic(
                code=ElaborationCode.SYSML_NAMESPACE_NOT_DISTINGUISHABLE,
                consumer=None,
                consumer_display="<model>",
                param_name=None,
                detail=(
                    f"{diagnostic_location}: {getattr(upstream, 'message', '')}. "
                    "Resolve the inherited/owned member conflict with an explicit `:>>` "
                    "redefinition."
                ),
            )
        )
    return tuple(result)


class _ExactElaborator:
    def __init__(
        self,
        model: Any,
        calc_defs: Sequence[CalculationDefinitionData],
        *,
        strict: bool,
    ) -> None:
        self._model = model
        self._strict = strict
        self._calc_defs = {item.qualified_name: item for item in calc_defs}
        self._compilation_results = {
            item.qualified_name: compile_calc_def(
                item,
                item.output_expression_asts,
                item.all_member_names,
                item.member_expressions,
            )
            for item in calc_defs
        }
        constraint_facts = extract_constraint_facts(model)
        self._constraint_decisions = {
            decision.identity.qualified_name: decision
            for decision in evaluate_profile(constraint_facts).decisions
            if decision.identity.qualified_name is not None
        }
        self._slots = build_feature_slot_index(model)
        self._occurrences = build_occurrence_index(model, self._slots)
        self._graph = InstanceGraph()
        self._elements = self._stable_elements()
        self._scope_display: dict[ScopeId, str] = {
            occurrence.occurrence_id: occurrence.display_path
            for occurrence in self._occurrences.occurrences()
        }
        self._attrs: dict[tuple[ScopeId, FeatureSlotId], AttrNode] = {}
        self._computed: dict[tuple[ScopeId, FeatureSlotId], CalcNode] = {}
        self._calcs: dict[tuple[ScopeId, DeclarationId], CalcNode] = {}
        self._pending_bindings: list[_PendingBinding] = []
        self._pending_expressions: list[_PendingExpression] = []
        self._pending_aliases: list[_PendingAlias] = []
        self._readiness: list[ReadinessFinding] = []
        self._readiness_keys: set[tuple[DeclarationId, ReadinessCode]] = set()

    def run(self) -> InstanceGraph:
        self._build_value_nodes()
        self._apply_deep_literal_redefinitions()
        self._build_calculation_nodes()
        self._build_constraint_nodes()
        self._resolve_aliases()
        self._resolve_computed_expressions()
        self._resolve_bindings()
        self._finish_readiness()
        self._graph.validate()
        if self._strict and self._graph.diagnostics:
            raise ElaborationDiagnosticError(self._graph.diagnostics)
        return self._graph

    def _stable_elements(self) -> dict[DeclarationId, Any]:
        result: dict[DeclarationId, Any] = {}
        for element in SysideAdapter.elements_of_type(
            self._model, "Feature", include_subtypes=True
        ):
            if getattr(element, "qualified_name", None) is None:
                continue
            result[declaration_id_for(element)] = element
        for type_name in (
            "PartDefinition",
            "CalculationDefinition",
            "ConstraintDefinition",
            "Package",
        ):
            for element in SysideAdapter.elements_of_type(self._model, type_name):
                if getattr(element, "qualified_name", None) is not None:
                    result[declaration_id_for(element)] = element
        return result

    # ---- exact scopes -----------------------------------------------------

    @staticmethod
    def _semantic_owner(element: Any) -> Any:
        return getattr(element, "owning_type", None) or getattr(element, "owner", None)

    def _package_scope(self, package: Any) -> PackageScopeId:
        package_id = declaration_id_for(package)
        scope = PackageScopeId(package_id)
        self._scope_display.setdefault(scope, display_qualified_name(str(package.qualified_name)))
        return scope

    def _scopes_for_owner(self, owner: Any) -> tuple[ScopeId, ...]:
        if owner is None:
            return ()
        if SysideAdapter.is_instance(owner, "PartDefinition"):
            owner_id = declaration_id_for(owner)
            return tuple(
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_type(owner_id)
            )
        if SysideAdapter.is_instance(owner, "PartUsage"):
            owner_id = declaration_id_for(owner)
            return tuple(
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_declaration(owner_id)
            )
        if SysideAdapter.is_instance(owner, "Package"):
            return (self._package_scope(owner),)
        return ()

    def _scope_lineage(self, scope: ScopeId) -> tuple[OccurrenceId, ...]:
        if not isinstance(scope, OccurrenceId):
            return ()
        return (scope,) + tuple(
            occurrence.occurrence_id for occurrence in self._occurrences.ancestors(scope)
        )

    def _display_path(self, scope: ScopeId, name: str) -> str:
        return f"{self._scope_display[scope]}__{display_name(name)}"

    @staticmethod
    def _source_location(element: Any) -> tuple[str, int]:
        location = SysideAdapter.get_source_location(element)
        return location if location is not None else ("unknown", 0)

    # ---- value population and precedence --------------------------------

    def _build_value_nodes(self) -> None:
        features = [
            feature
            for feature in SysideAdapter.elements_of_type(
                self._model, "Feature", include_subtypes=True
            )
            if getattr(feature, "qualified_name", None) is not None
        ]
        feature_scopes = {
            declaration_id_for(feature): self._scopes_for_owner(self._semantic_owner(feature))
            for feature in features
        }
        features_by_slot: dict[FeatureSlotId, list[Any]] = defaultdict(list)
        for feature in features:
            feature_id = declaration_id_for(feature)
            if feature_id not in self._elements:
                continue
            try:
                slot = self._slots.slot_of(feature_id)
            except KeyError:
                continue
            features_by_slot[slot].append(feature)

        base_by_slot: dict[FeatureSlotId, Any] = {}
        for attribute in SysideAdapter.elements_of_type(self._model, "AttributeUsage"):
            if getattr(attribute, "qualified_name", None) is None:
                continue
            scopes = self._scopes_for_owner(self._semantic_owner(attribute))
            if not scopes:
                continue
            slot = self._slots.slot_of(declaration_id_for(attribute))
            current = base_by_slot.get(slot)
            if current is None or declaration_id_for(attribute) == slot.root_declaration:
                base_by_slot[slot] = attribute

        for slot, base in sorted(
            base_by_slot.items(), key=lambda item: item[0].root_declaration.to_wire()
        ):
            base_scopes = self._scopes_for_owner(self._semantic_owner(base))
            for scope in base_scopes:
                candidates = [
                    feature
                    for feature in features_by_slot[slot]
                    if scope in feature_scopes[declaration_id_for(feature)]
                    and (
                        declaration_id_for(feature) == declaration_id_for(base)
                        or getattr(feature, "feature_value_expression", None) is not None
                    )
                ]
                writer = self._select_writer(base, candidates, scope)
                self._create_value_node(scope, slot, base, writer)

    def _select_writer(self, base: Any, candidates: list[Any], scope: ScopeId) -> Any:
        if not candidates:
            return base
        occurrence = (
            self._occurrences.occurrence(scope) if isinstance(scope, OccurrenceId) else None
        )
        usage_writers = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(self._semantic_owner(candidate), "PartUsage")
        ]
        if occurrence is not None:
            exact_usage_writers = [
                candidate
                for candidate in usage_writers
                if declaration_id_for(self._semantic_owner(candidate))
                == occurrence.effective_usage_id
            ]
            if exact_usage_writers:
                return self._require_one_writer(exact_usage_writers, scope)
        if usage_writers:
            return self._require_one_writer(usage_writers, scope)

        definition_writers = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(self._semantic_owner(candidate), "PartDefinition")
        ]
        if definition_writers:
            owner = self._occurrences.most_specific_definition(
                {
                    declaration_id_for(self._semantic_owner(candidate))
                    for candidate in definition_writers
                }
            )
            return self._require_one_writer(
                [
                    candidate
                    for candidate in definition_writers
                    if declaration_id_for(self._semantic_owner(candidate)) == owner
                ],
                scope,
            )
        return self._require_one_writer(candidates, scope)

    @staticmethod
    def _require_one_writer(candidates: list[Any], scope: ScopeId) -> Any:
        if len(candidates) != 1:
            ids = sorted(declaration_id_for(candidate).to_wire() for candidate in candidates)
            raise ElaborationInvariantError(
                ElaborationCode.SI_REDEFINITION_INVALID,
                f"exact scope {scope!r} has incomparable value writers {ids}",
            )
        return candidates[0]

    def _create_value_node(
        self, scope: ScopeId, slot: FeatureSlotId, base: Any, writer: Any
    ) -> None:
        writer_id = declaration_id_for(writer)
        name = str(getattr(base, "name", None) or getattr(writer, "name", None) or "value")
        display_path = self._display_path(scope, name)
        expression = getattr(writer, "feature_value_expression", None)
        value_site = self._value_site(base, writer, scope)
        literal = extract_literal_value(expression) if expression is not None else None
        source_file, source_line = self._source_location(writer)

        if expression is not None and not is_literal_node(expression):
            if self._is_reference_expression(expression):
                node_id = NodeId(NodeKind.ATTRIBUTE, scope, slot)
                alias_node = AttrNode(
                    node_id=node_id,
                    scope=scope,
                    declaration_id=writer_id,
                    slot_id=slot,
                    display_path=display_path,
                    display_name=display_name(name),
                    declaration_qn=str(getattr(base, "qualified_name", "")),
                    value_site=value_site,
                    is_alias=True,
                    alias_shape=(
                        "part_usage"
                        if SysideAdapter.is_instance(self._semantic_owner(writer), "PartUsage")
                        else "part_def"
                    ),
                    source_file=source_file,
                    source_line=source_line,
                )
                self._register_attr(alias_node)
                self._pending_aliases.append(_PendingAlias(alias_node, expression))
                return
            node_id = NodeId(NodeKind.CALCULATION, scope, slot)
            output = OutputPortId(node_id, writer_id)
            neutral_expression = extract_expression_ir(expression)
            if neutral_expression is None:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_REDEFINITION_INVALID,
                    f"computed value {display_path!r} has no representable expression IR",
                )
            computed_node = CalcNode(
                node_id=node_id,
                scope=scope,
                declaration_id=writer_id,
                display_path=display_path,
                display_name=display_name(name),
                calc_def_name=name,
                calc_def_qualified_name=str(
                    getattr(self._semantic_owner(writer), "qualified_name", None) or ""
                ),
                outputs={writer_id: output},
                output_names={writer_id: display_name(name)},
                output_metadata={
                    writer_id: PortMetadata(
                        python_type="float",
                        qualified_name=str(getattr(writer, "qualified_name", None) or ""),
                    )
                },
                is_computed=True,
                expression_ir=serialize_expression(neutral_expression),
                source_file=source_file,
                source_line=source_line,
            )
            self._graph.calcs[node_id] = computed_node
            self._computed[(scope, slot)] = computed_node
            self._pending_expressions.append(_PendingExpression(computed_node, expression))
            return

        node_id = NodeId(NodeKind.ATTRIBUTE, scope, slot)
        attr_node = AttrNode(
            node_id=node_id,
            scope=scope,
            declaration_id=writer_id,
            slot_id=slot,
            display_path=display_path,
            display_name=display_name(name),
            declaration_qn=str(getattr(base, "qualified_name", "")),
            value=literal,
            value_site=value_site if expression is not None else ValueSite.NONE,
            source_file=source_file,
            source_line=source_line,
        )
        self._register_attr(attr_node)

    @staticmethod
    def _is_reference_expression(expression: Any) -> bool:
        return SysideAdapter.is_instance(
            expression, "FeatureChainExpression"
        ) or SysideAdapter.is_instance(expression, "FeatureReferenceExpression")

    def _value_site(self, base: Any, writer: Any, scope: ScopeId) -> ValueSite:
        owner = self._semantic_owner(writer)
        if isinstance(scope, OccurrenceId) and SysideAdapter.is_instance(owner, "PartUsage"):
            return ValueSite.OCCURRENCE_OVERRIDE
        if declaration_id_for(writer) != declaration_id_for(base):
            return ValueSite.SPECIALIZED_DEF
        return ValueSite.DEFINITION_DEFAULT

    def _register_attr(self, node: AttrNode) -> None:
        key = (node.scope, node.slot_id)
        existing = self._attrs.get(key)
        if existing is not None and existing.node_id != node.node_id:
            raise ValueError(f"duplicate exact attribute slot {key!r}")
        self._attrs[key] = node
        self._graph.attrs[node.node_id] = node

    def _apply_deep_literal_redefinitions(self) -> None:
        for feature in SysideAdapter.elements_of_type(
            self._model, "Feature", include_subtypes=True
        ):
            if getattr(feature, "qualified_name", None) is not None:
                continue
            expression = getattr(feature, "feature_value_expression", None)
            if expression is None or not is_literal_node(expression):
                continue
            literal = extract_literal_value(expression)
            owner = self._semantic_owner(feature)
            for relationship in getattr(feature, "owned_redefinitions", ()) or ():
                redefined = getattr(relationship, "redefined_feature", None)
                chain = list(getattr(redefined, "chaining_features", ()) or ())
                if not chain:
                    continue
                chain_fact = self._reference_from_elements(chain)
                for scope in self._scopes_for_owner(owner):
                    try:
                        edges = self._resolve_semantic_reference(chain_fact, scope, plural=True)
                    except _ReferenceResolutionError as error:
                        self._diagnose(
                            ElaborationCode.OVERRIDE_TARGET_MISSING,
                            None,
                            self._scope_display[scope],
                            None,
                            error.detail,
                        )
                        continue
                    if not all(isinstance(edge, NodeRef) for edge in edges):
                        self._diagnose(
                            ElaborationCode.OVERRIDE_TARGET_MISSING,
                            None,
                            self._scope_display[scope],
                            None,
                            "deep literal override does not target an attribute node",
                        )
                        continue
                    for edge in edges:
                        if not isinstance(edge, NodeRef):
                            raise AssertionError(
                                "deep literal target kind changed after validation"
                            )
                        node = self._graph.attrs.get(edge.target)
                        if node is None:
                            raise RuntimeError("literal override targets a computed value")
                        node.value = literal
                        node.value_site = ValueSite.OCCURRENCE_OVERRIDE

    @staticmethod
    def _reference_from_elements(elements: list[Any]) -> ResolvedSemanticReferenceFact:
        facts = tuple(
            fact for element in elements if (fact := resolved_target_fact(element)) is not None
        )
        if not facts:
            raise IdentityBoundaryError("deep reference has no stable endpoint declarations")
        return ResolvedSemanticReferenceFact(
            root=facts[0],
            segments=facts,
            leaf=facts[-1],
            resolved_member_names=tuple(fact.element_name for fact in facts[1:]),
            has_index_segment=False,
        )

    # ---- calculation and constraint population ---------------------------

    def _build_calculation_nodes(self) -> None:
        usages = list(SysideAdapter.elements_of_type(self._model, "CalculationUsage"))
        scopes_by_usage = {
            declaration_id_for(usage): self._scopes_for_owner(self._semantic_owner(usage))
            for usage in usages
        }
        usages_by_slot: dict[FeatureSlotId, list[Any]] = defaultdict(list)
        for usage in usages:
            usages_by_slot[self._slots.slot_of(declaration_id_for(usage))].append(usage)

        selected: list[tuple[Any, ScopeId, list[Any]]] = []
        for slot, alternatives in usages_by_slot.items():
            base = next(
                (
                    usage
                    for usage in alternatives
                    if declaration_id_for(usage) == slot.root_declaration
                ),
                alternatives[0],
            )
            scopes = {
                scope
                for usage in alternatives
                for scope in scopes_by_usage[declaration_id_for(usage)]
            }
            for scope in scopes:
                applicable = [
                    usage
                    for usage in alternatives
                    if scope in scopes_by_usage[declaration_id_for(usage)]
                ]
                selected.append((self._select_writer(base, applicable, scope), scope, applicable))

        for usage, scope, applicable in sorted(
            selected,
            key=lambda item: (repr(item[1]), declaration_id_for(item[0]).to_wire()),
        ):
            usage_id = declaration_id_for(usage)
            definition = self._typed_definition(usage, "CalculationDefinition")
            node_id = NodeId(NodeKind.CALCULATION, scope, usage_id)
            outputs, output_names, output_metadata = self._output_ports(node_id, definition)
            name = str(getattr(usage, "name", None) or "calculation")
            definition_qn = str(getattr(definition, "qualified_name", None) or "")
            calc_data = self._calc_defs.get(definition_qn)
            compilation = self._compilation_results.get(definition_qn)
            node = CalcNode(
                node_id=node_id,
                scope=scope,
                declaration_id=usage_id,
                display_path=self._display_path(scope, name),
                display_name=display_name(name),
                calc_def_name=str(getattr(definition, "name", None) or ""),
                calc_def_qualified_name=definition_qn,
                outputs=outputs,
                output_names=output_names,
                output_metadata=output_metadata,
                compilability=(
                    compilation.overall_compilability
                    if compilation is not None
                    else Compilability.UNKNOWN
                ),
                auto_impl_context=(
                    self._calculation_auto_impl_context(compilation)
                    if compilation is not None
                    else None
                ),
                doc_comment=calc_data.doc_comment if calc_data is not None else None,
                calc_expressions=(
                    tuple(calc_data.calc_expressions) if calc_data is not None else ()
                ),
                source_file=(
                    str(calc_data.source_file)
                    if calc_data is not None
                    else self._source_location(definition)[0]
                ),
                source_line=(
                    calc_data.source_line
                    if calc_data is not None
                    else self._source_location(definition)[1]
                ),
            )
            self._graph.calcs[node_id] = node
            for declaration in applicable:
                self._calcs[(scope, declaration_id_for(declaration))] = node
            self._collect_bound_members(usage, node)
            self._collect_unbound_calculation_formals(definition, node)

    def _build_constraint_nodes(self) -> None:
        for usage in SysideAdapter.elements_of_type(
            self._model, "ConstraintUsage", include_subtypes=True
        ):
            if getattr(usage, "qualified_name", None) is None:
                continue
            usage_id = declaration_id_for(usage)
            definition = self._typed_definition(usage, "ConstraintDefinition", required=False)
            for scope in self._scopes_for_owner(self._semantic_owner(usage)):
                node_id = NodeId(NodeKind.CONSTRAINT, scope, usage_id)
                name = str(getattr(usage, "name", None) or "constraint")
                metadata = self._constraint_metadata(usage, definition)
                node = ConstraintNode(
                    node_id=node_id,
                    scope=scope,
                    declaration_id=usage_id,
                    display_path=self._display_path(scope, name),
                    display_name=display_name(name),
                    constraint_def_name=str(getattr(definition, "name", None) or ""),
                    **metadata,
                )
                self._graph.constraints[node_id] = node
                self._collect_bound_members(usage, node)
                if definition is not None:
                    self._collect_unbound_constraint_formals(definition, node)
                if node.source_form in ("inline", "requirement_constraint"):
                    predicate_expression = getattr(usage, "result_expression", None)
                    if predicate_expression is not None:
                        self._pending_expressions.append(
                            _PendingExpression(node, predicate_expression)
                        )

    @staticmethod
    def _typed_definition(usage: Any, type_name: str, *, required: bool = True) -> Any | None:
        candidates = [
            target
            for relationship, target in (getattr(usage, "heritage", None) or ())
            if SysideAdapter.is_instance(relationship, "FeatureTyping")
            and SysideAdapter.is_instance(target, type_name)
            and getattr(target, "qualified_name", None) is not None
        ]
        if len(candidates) > 1 or (required and not candidates):
            raise ValueError(
                f"{getattr(usage, 'qualified_name', None)!r} has "
                f"{len(candidates)} exact {type_name} typings"
            )
        return candidates[0] if candidates else None

    @staticmethod
    def _direction(member: Any) -> str:
        return str(getattr(member, "direction", "")).rsplit(".", 1)[-1].lower()

    @staticmethod
    def _calculation_auto_impl_context(compilation: Any) -> dict | None:
        if compilation.overall_compilability is not Compilability.FULLY_COMPILABLE:
            return None
        output_expressions = [
            {"name": result.output_name, "expression": result.python_expression}
            for result in compilation.output_results
            if result.python_expression is not None
        ]
        return {
            "execution_steps": [],
            "output_expressions": output_expressions,
            "output_count": len(output_expressions),
            "single_output_expression": (
                output_expressions[0]["expression"] if len(output_expressions) == 1 else None
            ),
        }

    def _constraint_metadata(self, usage: Any, definition: Any | None) -> dict[str, Any]:
        membership = getattr(usage, "owning_feature_membership", None)
        if SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
            source_form = "requirement_constraint"
        elif SysideAdapter.is_instance(usage, "AssertConstraintUsage"):
            asserted = getattr(usage, "asserted_constraint", None)
            if asserted is not usage:
                source_form = "named_usage_reference"
            elif getattr(usage, "result_expression", None) is None:
                source_form = "definition_typed"
            else:
                source_form = "inline"
        else:
            source_form = "plain_usage"

        if source_form in ("inline", "requirement_constraint"):
            predicate_source = usage
        elif source_form == "definition_typed":
            predicate_source = definition
        elif source_form == "named_usage_reference":
            asserted = getattr(usage, "asserted_constraint", None)
            predicate_source = getattr(asserted, "constraint_definition", None)
        else:
            predicate_source = None
        usage_qn = str(getattr(usage, "qualified_name", None) or "<anonymous>")
        decision = self._constraint_decisions.get(usage_qn)
        predicate_ir = (
            serialize_expression(decision.effective_predicate)
            if decision is not None and decision.effective_predicate is not None
            else None
        )
        if predicate_ir is None:
            predicate_expression = getattr(predicate_source, "result_expression", None)
            if predicate_expression is not None:
                neutral_predicate = extract_expression_ir(predicate_expression)
                if neutral_predicate is None:
                    raise ElaborationInvariantError(
                        ElaborationCode.SI_REDEFINITION_INVALID,
                        f"constraint {usage_qn!r} has no representable predicate IR",
                    )
                predicate_ir = serialize_expression(neutral_predicate)
        owner = self._semantic_owner(usage)
        owner_kind = {
            "PartDefinition": "part_def",
            "CalculationDefinition": "calc_def",
            "Package": "package",
            "RequirementDefinition": "requirement_def",
        }.get(type(owner).__name__, type(owner).__name__.lower())
        source_file, source_line = self._source_location(usage)
        exclusion_reasons = (
            tuple(diagnostic.reason for diagnostic in decision.diagnostics)
            if decision is not None and decision.eligibility is Eligibility.NON_NUMERICAL
            else ()
        )
        membership_kind = None
        if SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
            raw_kind = getattr(membership, "kind", None)
            membership_kind = str(getattr(raw_kind, "name", raw_kind)).lower()
        definition_qn = (
            str(getattr(definition, "qualified_name", None) or "")
            if source_form == "definition_typed"
            else None
        )
        predicate_qn = str(getattr(predicate_source, "qualified_name", None) or "")
        source_key = (
            f"definition:{predicate_qn}"
            if source_form == "definition_typed" and predicate_qn
            else f"inline:{predicate_qn}"
            if source_form in ("inline", "requirement_constraint") and predicate_qn
            else declaration_id_for(usage).to_wire()
        )
        return {
            "predicate_ir": predicate_ir,
            "source_form": source_form,
            "owner_kind": owner_kind,
            "owner_qualified_name": str(getattr(owner, "qualified_name", None) or ""),
            "usage_qualified_name": usage_qn,
            "membership_kind": membership_kind,
            "predicate_source_key": source_key,
            "is_negated": bool(getattr(usage, "is_negated", False)),
            "definition_qualified_name": definition_qn,
            "eligibility": (
                decision.eligibility.value if decision is not None else Eligibility.ADMIT.value
            ),
            "exclusion_reasons": exclusion_reasons,
            "exclusion_location": (f"{source_file}:{source_line}" if exclusion_reasons else None),
            "source_file": source_file,
            "source_line": source_line,
        }

    def _output_ports(
        self, node_id: NodeId, definition: Any
    ) -> tuple[
        dict[DeclarationId, OutputPortId],
        dict[DeclarationId, str],
        dict[DeclarationId, PortMetadata],
    ]:
        outputs: dict[DeclarationId, OutputPortId] = {}
        names: dict[DeclarationId, str] = {}
        metadata: dict[DeclarationId, PortMetadata] = {}
        calc_data = self._calc_defs.get(str(getattr(definition, "qualified_name", None) or ""))
        output_data = (
            {item.name: item for item in calc_data.output_attributes}
            if calc_data is not None
            else {}
        )
        for member in getattr(definition, "owned_members", None) or ():
            if self._direction(member) not in ("out", "return"):
                continue
            output_id = declaration_id_for(member)
            outputs[output_id] = OutputPortId(node_id, output_id)
            raw_name = str(getattr(member, "name", None) or "result")
            names[output_id] = display_name(raw_name)
            extracted = output_data.get(names[output_id]) or output_data.get(raw_name)
            metadata[output_id] = PortMetadata(
                python_type=extracted.python_type if extracted is not None else "float",
                description=extracted.description if extracted is not None else None,
                default_value=extracted.default_value if extracted is not None else None,
                unit=extracted.unit if extracted is not None else None,
                qualified_name=str(getattr(member, "qualified_name", None) or ""),
            )
        return outputs, names, metadata

    def _collect_bound_members(self, usage: Any, consumer: CalcNode | ConstraintNode) -> None:
        unbound: list[DeclarationId] = []
        for member in getattr(usage, "owned_members", None) or ():
            if self._direction(member) != "in":
                continue
            formal_id = declaration_id_for(member)
            port = ConsumerPortId(consumer.node_id, formal_id)
            name = str(getattr(member, "name", None) or "input")
            consumer.input_names[port] = display_name(name)
            extracted = None
            if isinstance(consumer, CalcNode):
                calc_data = self._calc_defs.get(consumer.calc_def_qualified_name)
                if calc_data is not None:
                    extracted = next(
                        (
                            item
                            for item in calc_data.input_attributes
                            if item.name in (name, display_name(name))
                        ),
                        None,
                    )
            consumer.input_metadata[port] = PortMetadata(
                python_type=(extracted.python_type if extracted is not None else "float"),
                description=(extracted.description if extracted is not None else None),
                default_value=(extracted.default_value if extracted is not None else None),
                unit=extracted.unit if extracted is not None else None,
                qualified_name=str(getattr(member, "qualified_name", None) or ""),
            )
            expression = getattr(member, "feature_value_expression", None)
            if expression is None:
                unbound.append(formal_id)
                continue
            evidence = self._binding_evidence(member, expression)
            literal = extract_literal_value(expression)
            unsupported = self._unsupported_code(evidence)
            if unsupported is not None:
                self._record_readiness(consumer, port, unsupported, evidence)
                continue
            self._pending_bindings.append(_PendingBinding(consumer, port, evidence, literal))
        consumer.unbound_formals = tuple(unbound)

    def _collect_unbound_constraint_formals(
        self, definition: Any, consumer: ConstraintNode
    ) -> None:
        occupied_slots = {
            self._slots.slot_of(port.formal)
            for port in consumer.input_names
            if isinstance(port, ConsumerPortId)
        }
        unbound = list(consumer.unbound_formals)
        formals = [
            formal
            for formal in SysideAdapter.elements_of_type(
                self._model, "AttributeUsage", include_subtypes=True
            )
            if getattr(formal, "owner", None) is definition and self._direction(formal) == "in"
        ]
        for formal in formals:
            formal_id = declaration_id_for(formal)
            slot = self._slots.slot_of(formal_id)
            if slot in occupied_slots:
                continue
            port = ConsumerPortId(consumer.node_id, formal_id)
            name = str(getattr(formal, "name", None) or "input")
            expression = getattr(formal, "feature_value_expression", None)
            serialized_default = None
            if expression is not None:
                default_ir = extract_expression_ir(expression)
                if default_ir is not None:
                    serialized_default = serialize_expression(default_ir)
            resolved_default = resolve_modeled_default(serialized_default)
            consumer.input_names[port] = display_name(name)
            consumer.input_metadata[port] = PortMetadata(
                python_type="float",
                default_value=resolved_default.value,
                unit=resolved_default.unit_text,
                qualified_name=str(getattr(formal, "qualified_name", None) or ""),
                unresolved_default_kind=resolved_default.unresolved_node_kind,
            )
            unbound.append(formal_id)
            occupied_slots.add(slot)
        consumer.unbound_formals = tuple(unbound)

    def _collect_unbound_calculation_formals(self, definition: Any, consumer: CalcNode) -> None:
        occupied_slots = {
            self._slots.slot_of(port.formal)
            for port in consumer.input_names
            if isinstance(port, ConsumerPortId)
        }
        calc_data = self._calc_defs.get(consumer.calc_def_qualified_name)
        extracted_inputs = (
            {item.name: item for item in calc_data.input_attributes}
            if calc_data is not None
            else {}
        )
        unbound = list(consumer.unbound_formals)
        formals = [
            formal
            for formal in SysideAdapter.elements_of_type(
                self._model, "AttributeUsage", include_subtypes=True
            )
            if getattr(formal, "owner", None) is definition and self._direction(formal) == "in"
        ]
        for formal in formals:
            formal_id = declaration_id_for(formal)
            slot = self._slots.slot_of(formal_id)
            if slot in occupied_slots:
                continue
            port = ConsumerPortId(consumer.node_id, formal_id)
            name = str(getattr(formal, "name", None) or "input")
            extracted = extracted_inputs.get(display_name(name)) or extracted_inputs.get(name)
            expression = getattr(formal, "feature_value_expression", None)
            serialized_default = None
            if expression is not None:
                default_ir = extract_expression_ir(expression)
                if default_ir is not None:
                    serialized_default = serialize_expression(default_ir)
            resolved_default = resolve_modeled_default(serialized_default)
            consumer.input_names[port] = display_name(name)
            consumer.input_metadata[port] = PortMetadata(
                python_type=extracted.python_type if extracted is not None else "float",
                description=extracted.description if extracted is not None else None,
                default_value=(
                    resolved_default.value
                    if expression is not None
                    else extracted.default_value
                    if extracted is not None
                    else None
                ),
                unit=resolved_default.unit_text
                or (extracted.unit if extracted is not None else None),
                qualified_name=str(getattr(formal, "qualified_name", None) or ""),
                unresolved_default_kind=resolved_default.unresolved_node_kind,
            )
            unbound.append(formal_id)
            occupied_slots.add(slot)
        consumer.unbound_formals = tuple(unbound)

    @staticmethod
    def _binding_evidence(member: Any, expression: Any) -> SourceReferenceEvidence:
        if SysideAdapter.is_instance(expression, "FeatureChainExpression"):
            return binding_evidence.chain_evidence(member, expression)
        if SysideAdapter.is_instance(expression, "FeatureReferenceExpression"):
            return binding_evidence.reference_evidence(member, expression)
        if is_literal_node(expression):
            return binding_evidence.literal_evidence(member, extract_literal_value(expression))
        return binding_evidence.expression_evidence(member, expression)

    @staticmethod
    def _unsupported_code(
        evidence: SourceReferenceEvidence,
    ) -> ReadinessCode | None:
        if evidence.is_self_binding:
            return ReadinessCode.SI_SELF_BINDING
        if evidence.source_form is SourceForm.INDEXED_SOURCE:
            return ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED
        if evidence.source_form is SourceForm.EXPRESSION_SOURCE:
            return ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED
        return None

    def _record_readiness(
        self,
        consumer: CalcNode | ConstraintNode,
        port: ConsumerPortId,
        code: ReadinessCode,
        evidence: SourceReferenceEvidence,
    ) -> None:
        key = (DeclarationId(evidence.bound_formal_id), code)
        if key in self._readiness_keys:
            return
        self._readiness_keys.add(key)
        param_name = consumer.input_names[port]
        owner_qn, _separator, _formal_name = evidence.bound_formal_qn.rpartition("::")
        usage_display = display_qualified_name(owner_qn)
        self._readiness.append(
            ReadinessFinding(
                code=code,
                usage_qualified_name=usage_display,
                param_name=param_name,
                detail=(
                    f"unsupported exact source form {evidence.source_form.value} "
                    f"({evidence.written_text or ''!r})"
                ),
            )
        )
        if not self._strict:
            self._graph.diagnostics.append(
                Diagnostic(
                    code=code,
                    consumer=None,
                    consumer_display=usage_display,
                    param_name=param_name,
                    detail=self._readiness[-1].detail,
                )
            )

    # ---- exact reference resolution --------------------------------------

    @staticmethod
    def _exact_reference(
        fact: ResolvedSemanticReferenceFact,
    ) -> ResolvedSemanticReference:
        if fact.root is None or fact.leaf is None:
            raise IdentityBoundaryError("resolved reference is missing root or leaf identity")
        return ResolvedSemanticReference(
            root_id=DeclarationId(fact.root.element_id),
            segment_ids=tuple(DeclarationId(value) for value in fact.segment_element_ids),
            leaf_id=DeclarationId(fact.leaf.element_id),
        )

    def _resolve_semantic_reference(
        self,
        fact: ResolvedSemanticReferenceFact,
        consumer_scope: ScopeId,
        *,
        plural: bool,
    ) -> list[NodeRef | ProducerRef]:
        reference = self._exact_reference(fact)
        if len(reference.segment_ids) == 1:
            return [
                self._resolve_leaf(
                    reference.leaf_id,
                    consumer_scope,
                )
            ]
        states: list[OccurrenceId | CalcNode] = self._contextualize_root(
            reference.root_id, consumer_scope, plural=plural
        )
        for segment_id in reference.segment_ids[1:]:
            next_states: list[OccurrenceId | CalcNode | InputRef] = []
            for state in states:
                next_states.extend(self._transition(state, segment_id))
            if not next_states:
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_MISSING,
                    f"exact segment {segment_id.to_wire()} has no target",
                )
            if all(isinstance(state, NodeRef | ProducerRef) for state in next_states):
                edges: list[NodeRef | ProducerRef] = [
                    state for state in next_states if isinstance(state, NodeRef | ProducerRef)
                ]
                if not plural and len(edges) != 1:
                    raise _ReferenceResolutionError(
                        ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                        f"exact segment {segment_id.to_wire()} has {len(edges)} targets",
                    )
                return edges
            unresolved_states = [
                state for state in next_states if isinstance(state, OccurrenceId | CalcNode)
            ]
            if len(unresolved_states) != len(next_states):
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    "semantic path produced both intermediate states and value edges",
                )
            if not plural and len(unresolved_states) != 1:
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    f"exact segment {segment_id.to_wire()} has "
                    f"{len(unresolved_states)} intermediate targets",
                )
            states = unresolved_states
        raise _ReferenceResolutionError(
            ElaborationCode.SI_OCCURRENCE_MISSING,
            "semantic path ended before reaching a graph value",
        )

    def _contextualize_root(
        self, root_id: DeclarationId, consumer_scope: ScopeId, *, plural: bool
    ) -> list[OccurrenceId | CalcNode]:
        element = self._elements.get(root_id)
        if element is None:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"exact root {root_id.to_wire()} is not an executable declaration",
            )
        if SysideAdapter.is_instance(element, "PartUsage"):
            occurrence_candidates = [
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_declaration(root_id)
            ]
            selected_occurrences: list[OccurrenceId | CalcNode] = [
                *self._select_occurrences(occurrence_candidates, consumer_scope, plural=plural)
            ]
            return selected_occurrences
        if SysideAdapter.is_instance(element, "CalculationUsage"):
            calc_candidates = list(
                {
                    node.node_id: node
                    for (scope, declaration), node in self._calcs.items()
                    if declaration == root_id
                }.values()
            )
            selected_calcs: list[OccurrenceId | CalcNode] = [
                *self._select_calc_nodes(calc_candidates, consumer_scope)
            ]
            return selected_calcs
        raise _ReferenceResolutionError(
            ElaborationCode.SI_OCCURRENCE_MISSING,
            f"exact root {root_id.to_wire()} cannot anchor a semantic path",
        )

    def _select_occurrences(
        self,
        candidates: list[OccurrenceId],
        consumer_scope: ScopeId,
        *,
        plural: bool,
    ) -> list[OccurrenceId]:
        if not candidates:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                "exact containment declaration has no concrete occurrence",
            )
        if not isinstance(consumer_scope, OccurrenceId):
            if plural:
                return candidates
            if len(candidates) != 1:
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    f"package context contains {len(candidates)} candidate occurrences",
                )
            return candidates
        lineage = self._scope_lineage(consumer_scope)
        for scope in lineage:
            if scope in candidates:
                return [scope]
        for anchor in lineage:
            under = [
                candidate
                for candidate in candidates
                if self._occurrences.is_descendant(candidate, anchor)
            ]
            if under:
                if plural or len(under) == 1:
                    return under
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    f"consumer context contains {len(under)} candidate occurrences",
                )
        if plural:
            return candidates
        if len(candidates) != 1:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"permitted scope contains {len(candidates)} candidate occurrences",
            )
        return candidates

    def _select_calc_nodes(
        self, candidates: list[CalcNode], consumer_scope: ScopeId
    ) -> list[CalcNode]:
        if not candidates:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                "exact calculation declaration has no concrete node",
            )
        by_scope = {node.scope: node for node in candidates}
        if isinstance(consumer_scope, OccurrenceId):
            for scope in self._scope_lineage(consumer_scope):
                if scope in by_scope:
                    return [by_scope[scope]]
            for anchor in self._scope_lineage(consumer_scope):
                under = [
                    node
                    for node in candidates
                    if isinstance(node.scope, OccurrenceId)
                    and self._occurrences.is_descendant(node.scope, anchor)
                ]
                if len(under) == 1:
                    return under
                if len(under) > 1:
                    raise _ReferenceResolutionError(
                        ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                        f"consumer context contains {len(under)} calculation nodes",
                    )
        if len(candidates) != 1:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"permitted scope contains {len(candidates)} calculation nodes",
            )
        return candidates

    def _transition(
        self, state: OccurrenceId | CalcNode, segment_id: DeclarationId
    ) -> list[OccurrenceId | CalcNode | NodeRef | ProducerRef]:
        if isinstance(state, CalcNode):
            output = state.outputs.get(segment_id)
            return [ProducerRef(output)] if output is not None else []

        element = self._elements.get(segment_id)
        if element is not None and SysideAdapter.is_instance(element, "PartUsage"):
            slot = self._slots.slot_of(segment_id)
            return [
                child.occurrence_id
                for child in self._occurrences.children(state)
                if child.occurrence_id.steps[-1].containment_slot == slot
            ]
        if element is not None and SysideAdapter.is_instance(element, "CalculationUsage"):
            node = self._calcs.get((state, segment_id))
            return [node] if node is not None else []
        edge = self._target_at(state, segment_id)
        return [edge] if edge is not None else []

    def _resolve_leaf(
        self,
        declaration_id: DeclarationId,
        consumer_scope: ScopeId,
    ) -> NodeRef | ProducerRef:
        producing_calcs = [
            node for node in self._graph.calcs.values() if declaration_id in node.outputs
        ]
        if producing_calcs:
            [producer] = self._select_calc_nodes(producing_calcs, consumer_scope)
            return ProducerRef(producer.outputs[declaration_id])
        try:
            slot = self._slots.slot_of(declaration_id)
        except KeyError:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"leaf declaration {declaration_id.to_wire()} has no feature slot",
            ) from None
        if isinstance(consumer_scope, OccurrenceId):
            for scope in self._scope_lineage(consumer_scope):
                edge = self._target_for_slot(scope, slot)
                if edge is not None:
                    return edge
            for anchor in self._scope_lineage(consumer_scope):
                descendants = [
                    occurrence.occurrence_id
                    for occurrence in self._occurrences.occurrences()
                    if self._occurrences.is_descendant(occurrence.occurrence_id, anchor)
                    and self._target_for_slot(occurrence.occurrence_id, slot) is not None
                ]
                if len(descendants) == 1:
                    target = self._target_for_slot(descendants[0], slot)
                    if target is not None:
                        return target
                if len(descendants) > 1:
                    raise _ReferenceResolutionError(
                        ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                        f"consumer context contains {len(descendants)} leaf occurrences",
                    )
        edge = self._target_for_slot(consumer_scope, slot)
        if edge is not None:
            return edge
        raise _ReferenceResolutionError(
            ElaborationCode.SI_OCCURRENCE_MISSING,
            f"consumer context has no occurrence of leaf slot {slot!r}",
        )

    def _target_at(
        self, scope: OccurrenceId, declaration_id: DeclarationId
    ) -> NodeRef | ProducerRef | None:
        try:
            slot = self._slots.slot_of(declaration_id)
        except KeyError:
            return None
        return self._target_for_slot(scope, slot)

    def _target_for_slot(self, scope: ScopeId, slot: FeatureSlotId) -> NodeRef | ProducerRef | None:
        attr = self._attrs.get((scope, slot))
        if attr is not None:
            return NodeRef(attr.node_id)
        computed = self._computed.get((scope, slot))
        if computed is not None:
            return ProducerRef(computed.outputs[computed.declaration_id])
        return None

    # ---- bind aliases, expressions, and consumer ports -------------------

    def _resolve_aliases(self) -> None:
        for pending in self._pending_aliases:
            facts = self._expression_references(pending.expression, plural=False)
            if len(facts) != 1:
                self._diagnose(
                    ElaborationCode.SI_OCCURRENCE_MISSING,
                    pending.node.node_id,
                    pending.node.display_path,
                    pending.node.display_name,
                    "alias expression does not contain one exact reference",
                )
                continue
            fact, plural = facts[0]
            try:
                edges = self._resolve_semantic_reference(fact, pending.node.scope, plural=plural)
            except _ReferenceResolutionError as error:
                self._diagnose(
                    error.code,
                    pending.node.node_id,
                    pending.node.display_path,
                    pending.node.display_name,
                    error.detail,
                )
                continue
            pending.node.alias_target = edges[0]

        resolved_aliases: dict[NodeId, InputRef | None] = {}
        for pending in self._pending_aliases:
            if pending.node.alias_target is None:
                continue
            try:
                resolved_aliases[pending.node.node_id] = self._follow_alias(
                    pending.node.alias_target, {pending.node.node_id}
                )
            except _ReferenceResolutionError as error:
                resolved_aliases[pending.node.node_id] = None
                self._diagnose(
                    error.code,
                    pending.node.node_id,
                    pending.node.display_path,
                    pending.node.display_name,
                    error.detail,
                )
        for pending in self._pending_aliases:
            if pending.node.node_id in resolved_aliases:
                pending.node.alias_target = resolved_aliases[pending.node.node_id]

    def _follow_alias(self, edge: InputRef, active: set[NodeId]) -> InputRef:
        if not isinstance(edge, NodeRef):
            return edge
        node = self._graph.attrs.get(edge.target)
        if node is None or not node.is_alias:
            return edge
        if node.alias_target is None:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"typed alias {node.display_path!r} has no resolved target",
            )
        if node.node_id in active:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_ALIAS_CYCLE,
                f"typed alias cycle reaches {node.display_path!r}",
            )
        return self._follow_alias(node.alias_target, active | {node.node_id})

    def _resolve_computed_expressions(self) -> None:
        for pending in self._pending_expressions:
            try:
                facts = self._expression_references(pending.expression, plural=False)
            except _UnsupportedExpressionError as error:
                self._diagnose(
                    ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED,
                    pending.consumer.node_id,
                    pending.consumer.display_path,
                    None,
                    error.detail,
                )
                continue
            aggregation_ordinals: list[int] = []
            for reference_ordinal, (fact, plural) in enumerate(facts):
                if plural:
                    aggregation_ordinals.append(reference_ordinal)
                try:
                    edges = self._resolve_semantic_reference(
                        fact, pending.consumer.scope, plural=plural
                    )
                except _ReferenceResolutionError as error:
                    self._diagnose(
                        error.code,
                        pending.consumer.node_id,
                        pending.consumer.display_path,
                        None,
                        error.detail,
                    )
                    continue
                leaf_fact = fact.leaf
                if leaf_fact is None:
                    continue
                leaf = DeclarationId(leaf_fact.element_id)
                for edge_ordinal, edge in enumerate(edges):
                    target_scope = (
                        edge.target.scope
                        if isinstance(edge, NodeRef) and isinstance(edge.target.scope, OccurrenceId)
                        else None
                    )
                    port: ConsumerPortId | ExpressionPortId
                    if isinstance(pending.consumer, ConstraintNode):
                        port = ConsumerPortId(pending.consumer.node_id, leaf)
                    else:
                        port = ExpressionPortId(
                            pending.consumer.node_id,
                            reference_ordinal,
                            edge_ordinal,
                            leaf,
                            target_scope,
                        )
                    input_name = (
                        fact.resolved_member_names[-1]
                        if fact.resolved_member_names
                        else leaf_fact.element_name
                    )
                    pending.consumer.input_names[port] = input_name
                    pending.consumer.input_metadata[port] = PortMetadata(
                        python_type="float",
                        qualified_name=leaf_fact.qualified_name,
                    )
                    try:
                        pending.consumer.inputs[port] = self._follow_alias(edge, set())
                    except _ReferenceResolutionError as error:
                        self._diagnose(
                            error.code,
                            pending.consumer.node_id,
                            pending.consumer.display_path,
                            pending.consumer.input_names.get(port),
                            error.detail,
                        )
                        continue
            if isinstance(pending.consumer, CalcNode):
                pending.consumer.aggregation_reference_ordinals = tuple(aggregation_ordinals)

    def _expression_references(
        self, expression: Any, *, plural: bool
    ) -> list[tuple[ResolvedSemanticReferenceFact, bool]]:
        # FeatureChainExpression MUST be before OperatorExpression: SysIDE
        # models the former as an operator subtype.
        if SysideAdapter.is_instance(expression, "FeatureChainExpression"):
            return [(feature_chain_facts(expression), plural)]
        if SysideAdapter.is_instance(expression, "FeatureReferenceExpression"):
            target = resolved_target_fact(getattr(expression, "referent", None))
            if target is None:
                return []
            return [
                (
                    ResolvedSemanticReferenceFact(
                        root=target,
                        segments=(target,),
                        leaf=target,
                        resolved_member_names=(),
                        has_index_segment=False,
                    ),
                    plural,
                )
            ]
        child_plural = plural
        if SysideAdapter.is_instance(
            expression, "InvocationExpression"
        ) and not SysideAdapter.is_instance(expression, "OperatorExpression"):
            function = getattr(expression, "function", None)
            if function is None:
                raise _UnsupportedExpressionError(
                    "invocation expression has no resolved function declaration"
                )
            function_id = declaration_id_for(function)
            if type(function).__name__ != "Function" or function_id != _SUM_FUNCTION_ID:
                raise _UnsupportedExpressionError(
                    f"unsupported invocation function {function_id.to_wire()}"
                )
            child_plural = True
        result: list[tuple[ResolvedSemanticReferenceFact, bool]] = []
        for operand in getattr(expression, "operands", None) or ():
            result.extend(self._expression_references(operand, plural=child_plural))
        return result

    def _resolve_bindings(self) -> None:
        for pending in self._pending_bindings:
            evidence = pending.evidence
            if evidence.source_form is SourceForm.AUTHORED_LITERAL:
                if pending.literal_value is None:
                    raise RuntimeError("authored literal binding has no literal value")
                pending.consumer.inputs[pending.port] = LiteralInput(pending.literal_value)
                continue
            fact = evidence.semantic_reference
            if fact is None:
                raise RuntimeError("supported reference binding has no exact semantic path")
            try:
                edges = self._resolve_semantic_reference(
                    fact,
                    pending.consumer.scope,
                    plural=False,
                )
                edge = self._follow_alias(edges[0], set())
            except _ReferenceResolutionError as error:
                self._diagnose(
                    error.code,
                    pending.consumer.node_id,
                    pending.consumer.display_path,
                    pending.consumer.input_names[pending.port],
                    error.detail,
                )
                continue
            pending.consumer.inputs[pending.port] = edge

    def _finish_readiness(self) -> None:
        self._readiness.sort(
            key=lambda finding: (
                finding.usage_qualified_name,
                finding.param_name,
                finding.code.value,
            )
        )
        if self._strict and self._readiness:
            raise ElaborationError(self._readiness)

    def _diagnose(
        self,
        code: ElaborationCode | ReadinessCode,
        consumer: NodeId | None,
        consumer_display: str,
        param_name: str | None,
        detail: str,
    ) -> None:
        diagnostic = Diagnostic(
            code=code,
            consumer=consumer,
            consumer_display=consumer_display,
            param_name=param_name,
            detail=detail,
        )
        if diagnostic not in self._graph.diagnostics:
            self._graph.diagnostics.append(diagnostic)
