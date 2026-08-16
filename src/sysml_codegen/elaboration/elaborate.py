"""One exact-ID elaboration pass from the live SysIDE model to direct edges."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.constraint_extraction import (
    IdentifiedConstraintFacts,
    extract_expression_ir,
    extract_identified_constraint_facts,
)
from agentic_mbse.sysml.data_models import ResolvedSemanticReferenceFact
from agentic_mbse.sysml.executable_profile import (
    Eligibility,
    EligibilityDiagnostic,
    UsageDecision,
    evaluate_identified_profile,
)
from agentic_mbse.sysml.expression import (
    feature_chain_facts,
    is_literal_node,
    resolved_target_fact,
)
from agentic_mbse.sysml.expression_ir import serialize_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.models import AutoImplContext, AutoImplOutput, AutoImplStep
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.display import display_name, display_qualified_name
from sysml_codegen.elaboration.extraction_screen import screen_extraction_diagnostics
from sysml_codegen.elaboration.graph import (
    ASSERTED_SOURCE_FORMS,
    AttrNode,
    CalcNode,
    ConstraintNode,
    ConstraintUsageRecord,
    Diagnostic,
    ElaborationCode,
    FormalProvenance,
    Inapplicability,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    OccurrenceRecord,
    PortMetadata,
    ProducerRef,
    UsageDisposition,
    ValueSite,
    expected_severity,
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
    FeatureSlotIndex,
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction import binding_evidence
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.expression_compiler import (
    Compilability,
    CompilationError,
    ExactCalcDefCompilationResult,
    compile_calc_def_exact,
)
from sysml_codegen.extraction.expression_utils import extract_literal_value
from sysml_codegen.extraction.feature_metadata import extract_feature_unit
from sysml_codegen.extraction.modeled_defaults import resolve_modeled_default
from sysml_codegen.extraction.source_evidence import (
    ReadinessCode,
    ReadinessFinding,
    SourceForm,
    SourceReferenceEvidence,
)
from sysml_codegen.extraction.unit_annotation import annotated_ast_value

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
class _ConstraintAssociation:
    usage_id: DeclarationId
    effective_definition_id: DeclarationId | None
    decision: UsageDecision


@dataclass(frozen=True)
class _AnnotationRead:
    """What one usage's documentation said about inapplicability, defect included.

    Two fields rather than a raise, because minting must not raise (invariant 5): the
    caller needs to know *both* that the marker was unreadable and that it can still build
    a record for this usage.
    """

    inapplicability: Inapplicability | None
    #: ``None`` when the documentation is well formed; otherwise a phrase completing
    #: "constraint <qn> …", so the disposition detail and the halt read as one sentence.
    defect: str | None


#: The one spelling of the inapplicability marker. Anchored to the first line of the
#: joined documentation and parsed strictly, so a typo halts rather than doing nothing.
_INAPPLICABLE_MARKER = "@inapplicable"

#: Precedence step 3, reached only by a usage that expanded to at least one scope.
_ELIGIBILITY_DISPOSITIONS: dict[Eligibility, tuple[str, str]] = {
    Eligibility.ADMIT: ("eligible", "admitted"),
    Eligibility.NON_NUMERICAL: ("excluded", "non_numerical"),
    Eligibility.UNASSESSED: ("excluded", "unassessed_form"),
    Eligibility.BLOCK: ("excluded", "profile_blocked"),
}


@dataclass(frozen=True)
class _PendingAlias:
    node: AttrNode
    expression: Any


def _computed_expression_input_names(
    facts: Sequence[tuple[ResolvedSemanticReferenceFact, bool]],
) -> dict[int, str]:
    """Render the narrowest names that distinguish same-leaf semantic chains.

    A unique leaf keeps the established leaf-only name. Exact repeated chains
    keep it too, so projection can deduplicate repeated reads of one source.
    Only distinct resolved-ID chains with the same leaf name add resolved segment
    names, using the shortest suffix that distinguishes the chains.
    """
    names_by_ordinal: dict[int, str] = {}
    chains_by_leaf: dict[
        str,
        dict[tuple[UUID, ...], tuple[str, ...]],
    ] = defaultdict(dict)

    for reference_ordinal, (fact, _plural) in enumerate(facts):
        leaf = fact.leaf
        if leaf is None:
            continue
        leaf_name = (
            fact.resolved_member_names[-1]
            if fact.resolved_member_names
            else leaf.element_name
        )
        names_by_ordinal[reference_ordinal] = leaf_name
        chain_identity = fact.segment_element_ids or (leaf.element_id,)
        resolved_names = tuple(
            segment.element_name for segment in fact.segments if segment.element_name
        )
        chains_by_leaf[leaf_name].setdefault(chain_identity, resolved_names or (leaf_name,))

    for leaf_name, chains in chains_by_leaf.items():
        if len(chains) < 2:
            continue
        rendered_by_chain: dict[tuple[UUID, ...], str] | None = None
        for suffix_width in range(2, max(map(len, chains.values())) + 1):
            candidates = {
                identity: "_".join(resolved_names[-suffix_width:])
                for identity, resolved_names in chains.items()
            }
            rendered_by_chain = candidates
            if len(set(candidates.values())) == len(candidates):
                break
        if rendered_by_chain is None:
            continue
        for reference_ordinal, (fact, _plural) in enumerate(facts):
            if names_by_ordinal.get(reference_ordinal) != leaf_name or fact.leaf is None:
                continue
            chain_identity = fact.segment_element_ids or (fact.leaf.element_id,)
            names_by_ordinal[reference_ordinal] = rendered_by_chain[chain_identity]

    return names_by_ordinal


def elaborate(
    model: Any,
    calc_defs: Sequence[CalculationDefinitionData],
    *,
    validation_diagnostics: Sequence[Any],
    model_paths: Sequence[Path] = (),
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
        return _ExactElaborator(
            model,
            calc_defs,
            model_paths=model_paths,
            strict=strict,
        ).run()
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


def _block_reason_key(diagnostic: EligibilityDiagnostic) -> tuple[str, int, int, str, str, str]:
    """The diagnostic's normalized identity: what de-duplicates it, and what orders it.

    One key for both jobs. De-duplicating on the reason alone would collapse two *different*
    blocked chains at different lines into one entry and lose the identification the modeler
    needs; ordering on anything narrower than the full identity lets two survivors tie, and a
    tie hands the order back to the profile's walk. Because the order key *is* the de-dup
    identity, no two survivors can tie.

    Every field is normalized here rather than at the comparison, so a missing file, line, or
    column never meets an `int`. The file is basenamed in the key as well as in the rendering:
    an absolute path is checkout-dependent and would make the order machine-dependent too.
    """
    location = diagnostic.location
    return (
        Path(location.file).name if location is not None and location.file else "",
        location.line if location is not None and location.line is not None else -1,
        location.column if location is not None and location.column is not None else -1,
        diagnostic.reason,
        diagnostic.construct,
        diagnostic.message,
    )


def _render_block_reason(diagnostic: EligibilityDiagnostic) -> str:
    """One block reason as `reason: message [basename:line]`.

    The location suffix is omitted entirely when there is no usable location — no
    placeholder, because a placeholder advertises a place that does not exist. `column`
    orders and is never rendered.
    """
    file, line, _column, reason, _construct, message = _block_reason_key(diagnostic)
    suffix = f" [{file}:{line}]" if file and line >= 0 else ""
    return f"{reason}: {message}{suffix}"


def _render_block_reasons(diagnostics: Sequence[EligibilityDiagnostic]) -> str:
    """Every distinct block reason on one line, in an order the payload decides.

    A repeated reason is one entry: `LayerContinuity` blocks the same chain thirteen times
    and a modeler needs to read it once. Joined with `"; "` and never a newline — two
    consumers fold this string into a one-line regex match.
    """
    distinct = {_block_reason_key(diagnostic): diagnostic for diagnostic in diagnostics}
    return "; ".join(_render_block_reason(distinct[key]) for key in sorted(distinct))


class _EffectiveInputFormalSelector:
    """Select the exact effective input declaration from a definition's native view."""

    def __init__(self, model: Any, slots: FeatureSlotIndex) -> None:
        self._slots = slots
        self._loaded_user_inputs = {
            declaration_id_for(feature): feature
            for feature in SysideAdapter.elements_of_type(
                model, "Feature", include_subtypes=True
            )
            if getattr(feature, "qualified_name", None) is not None
            and self._is_input(feature)
        }

    def effective_input_formals(
        self, definition: Any
    ) -> dict[FeatureSlotId, DeclarationId]:
        native: dict[DeclarationId, Any] = {}
        for candidate in getattr(definition, "usages", ()) or ():
            if not SysideAdapter.is_instance(candidate, "Feature"):
                continue
            if getattr(candidate, "qualified_name", None) is None:
                continue
            candidate_id = declaration_id_for(candidate)
            if candidate_id not in self._loaded_user_inputs:
                continue
            if not self._is_input(candidate):
                continue
            existing = native.get(candidate_id)
            if existing is not None and existing is not candidate:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_REDEFINITION_INVALID,
                    f"native input view repeats declaration {candidate_id.to_wire()}",
                )
            native[candidate_id] = candidate

        by_slot: dict[FeatureSlotId, set[DeclarationId]] = defaultdict(set)
        for candidate_id in native:
            by_slot[self._slots.slot_of(candidate_id)].add(candidate_id)
        return {
            slot: self._slots.effective_declaration(candidates)
            for slot, candidates in by_slot.items()
        }

    @staticmethod
    def _is_input(member: Any) -> bool:
        direction = getattr(member, "direction", None)
        return direction is not None and direction is getattr(type(direction), "In", None)


class _ExactElaborator:
    def __init__(
        self,
        model: Any,
        calc_defs: Sequence[CalculationDefinitionData],
        *,
        strict: bool,
        model_paths: Sequence[Path] = (),
    ) -> None:
        self._model = model
        self._model_paths = tuple(model_paths)
        self._strict = strict
        self._calc_defs = self._index_calculation_payloads(calc_defs)
        self._compilation_results = self._compile_calculation_payloads()
        # The one read of the identified constraint facts. Screening the extraction
        # diagnostics here — before any node is built — is what puts the blocking
        # halt ahead of lowering and serialization on both the live and the capture
        # route (REQ-DIAG-02/03; docs/architecture/reference/30-diagnostic-severity.md).
        identified = extract_identified_constraint_facts(model)
        screen_extraction_diagnostics(identified.facts)
        self._constraint_associations = self._index_constraint_associations(model, identified)
        self._slots = build_feature_slot_index(model)
        self._formal_selector = _EffectiveInputFormalSelector(model, self._slots)
        self._effective_formals_by_definition: dict[
            DeclarationId, dict[FeatureSlotId, DeclarationId]
        ] = {}
        self._occurrences = build_occurrence_index(model, self._slots)
        self._graph = InstanceGraph(
            occurrences={
                occurrence.occurrence_id: OccurrenceRecord(
                    occurrence_id=occurrence.occurrence_id,
                    parent_id=occurrence.parent_id,
                    containment_slot=(
                        occurrence.occurrence_id.steps[-1].containment_slot
                    ),
                    occurrence_index=(
                        occurrence.occurrence_id.steps[-1].occurrence_index
                    ),
                    effective_usage_id=occurrence.effective_usage_id,
                    effective_type_ids=tuple(
                        sorted(occurrence.type_closure, key=lambda item: item.to_wire())
                    ),
                    display_segment=occurrence.display_segment,
                    package_display=occurrence.package_display,
                )
                for occurrence in self._occurrences.occurrences()
            }
        )
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

    @staticmethod
    def _index_constraint_associations(
        model: Any, identified: IdentifiedConstraintFacts
    ) -> dict[UUID, _ConstraintAssociation]:
        stable_usage_ids: dict[UUID, DeclarationId] = {}
        for usage in SysideAdapter.elements_of_type(
            model, "ConstraintUsage", include_subtypes=True
        ):
            raw_id = SysideAdapter.element_id(usage)
            if raw_id in stable_usage_ids:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"duplicate live constraint usage UUID {raw_id}",
                )
            stable_usage_ids[raw_id] = declaration_id_for(usage)

        stable_definition_ids: dict[UUID, DeclarationId] = {}
        for definition in SysideAdapter.elements_of_type(
            model, "ConstraintDefinition", include_subtypes=True
        ):
            raw_id = SysideAdapter.element_id(definition)
            if raw_id in stable_definition_ids:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"duplicate live constraint definition UUID {raw_id}",
                )
            stable_definition_ids[raw_id] = declaration_id_for(definition)

        profile = evaluate_identified_profile(identified)
        try:
            missing_profile_ids = profile.missing_usage_ids
            decisions_by_id = profile.by_usage_id
        except ValueError as error:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"constraint profile decision inventory is invalid: {error}",
            ) from error
        if missing_profile_ids:
            missing_ids = ", ".join(
                str(item) for item in sorted(missing_profile_ids, key=str)
            )
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"constraint profile omitted usage UUIDs: {missing_ids}",
            )

        unknown = set(decisions_by_id) - set(stable_usage_ids)
        missing = set(stable_usage_ids) - set(decisions_by_id)
        if unknown or missing:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                "constraint profile/live usage UUID inventory disagrees: "
                f"unknown={sorted(str(item) for item in unknown)}, "
                f"missing={sorted(str(item) for item in missing)}",
            )

        result: dict[UUID, _ConstraintAssociation] = {}
        for raw_usage_id, item in decisions_by_id.items():
            effective_definition_id = None
            if item.effective_definition_id is not None:
                effective_definition_id = stable_definition_ids.get(item.effective_definition_id)
                if effective_definition_id is None:
                    raise ElaborationInvariantError(
                        ElaborationCode.SI_EDGE_DANGLING,
                        "constraint profile selected an unrecognized definition UUID "
                        f"{item.effective_definition_id}",
                    )
            result[raw_usage_id] = _ConstraintAssociation(
                usage_id=stable_usage_ids[raw_usage_id],
                effective_definition_id=effective_definition_id,
                decision=item.decision,
            )
        return result

    def _constraint_association(self, usage: Any) -> _ConstraintAssociation:
        raw_id = SysideAdapter.element_id(usage)
        association = self._constraint_associations.get(raw_id)
        if association is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"constraint usage UUID {raw_id} has no exact profile decision",
            )
        return association

    @staticmethod
    def _index_calculation_payloads(
        calc_defs: Sequence[CalculationDefinitionData],
    ) -> dict[DeclarationId, CalculationDefinitionData]:
        result: dict[DeclarationId, CalculationDefinitionData] = {}
        for calc_def in calc_defs:
            if not isinstance(calc_def.element_id, UUID):
                raise ElaborationInvariantError(
                    ElaborationCode.SI_ID_MISSING,
                    f"calculation payload {calc_def.qualified_name!r} has no definition UUID",
                )
            definition_id = DeclarationId(calc_def.element_id)
            if definition_id in result:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"duplicate calculation payload for definition {definition_id.to_wire()}",
                )
            for role, attributes in (
                ("input", calc_def.input_attributes),
                ("output", calc_def.output_attributes),
            ):
                for attribute in attributes:
                    if not isinstance(attribute.element_id, UUID):
                        raise ElaborationInvariantError(
                            ElaborationCode.SI_ID_MISSING,
                            f"calculation {definition_id.to_wire()} {role} "
                            f"{attribute.name!r} has no declaration UUID",
                        )
            result[definition_id] = calc_def
        return result

    def _compile_calculation_payloads(
        self,
    ) -> dict[DeclarationId, ExactCalcDefCompilationResult]:
        result: dict[DeclarationId, ExactCalcDefCompilationResult] = {}
        for definition_id, calc_def in self._calc_defs.items():
            try:
                compilation = compile_calc_def_exact(calc_def)
            except (CompilationError, ValueError) as error:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"calculation {definition_id.to_wire()} exact compilation failed: {error}",
                ) from error
            if DeclarationId(compilation.definition_id) != definition_id:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"calculation {definition_id.to_wire()} compilation identity disagrees",
                )
            result[definition_id] = compilation
        return result

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

    def _attachment(self, owner: Any) -> tuple[tuple[ScopeId, ...], str | None]:
        """The scopes an owner attaches its members to, and why there are none.

        An empty result has three structurally different causes, and the severity of a
        non-reaching constraint keys on which one it is: the element has no semantic
        owner at all, the owner's kind has no attachment capability (a ``calc def``), or
        the owner could attach but nothing of it was ever instantiated. Returning the
        cause beside the scopes is what lets a caller grade the three differently instead
        of reading one bare empty tuple three ways.
        """
        if owner is None:
            return (), "owner_absent"
        if SysideAdapter.is_instance(owner, "PartDefinition"):
            owner_id = declaration_id_for(owner)
            scopes: tuple[ScopeId, ...] = tuple(
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_type(owner_id)
            )
            return scopes, None if scopes else "owner_has_no_occurrences"
        if SysideAdapter.is_instance(owner, "PartUsage"):
            owner_id = declaration_id_for(owner)
            scopes = tuple(
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_declaration(owner_id)
            )
            return scopes, None if scopes else "owner_has_no_occurrences"
        if SysideAdapter.is_instance(owner, "Package"):
            return (self._package_scope(owner),), None
        return (), "owner_kind_unattachable"

    def _scopes_for_owner(self, owner: Any) -> tuple[ScopeId, ...]:
        """The attachment scopes alone, for the callers that cannot act on the cause."""
        return self._attachment(owner)[0]

    @staticmethod
    def _owner_kind(owner: Any) -> str:
        """The graded kind of a constraint usage's semantic owner, from a closed map.

        The map used to end in a ``.get(..., type(owner).__name__.lower())`` fallback,
        which let an owner kind nobody had considered be graded by accident — and the
        disposition severity now keys on this value, so an accidental grade would decide
        whether a model halts. An unmapped kind fails by name instead.
        """
        kinds = {
            "NoneType": "absent",
            "PartDefinition": "part_def",
            "PartUsage": "part_usage",
            "CalculationDefinition": "calc_def",
            "Package": "package",
            "RequirementDefinition": "requirement_def",
        }
        kind = kinds.get(type(owner).__name__)
        if kind is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_CONSTRAINT_UNATTACHED,
                f"constraint owner kind {type(owner).__name__!r} "
                f"({getattr(owner, 'qualified_name', None)!r}) is not in the closed owner-kind map",
            )
        return kind

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

        attributes_by_slot: dict[FeatureSlotId, list[Any]] = defaultdict(list)
        for attribute in SysideAdapter.elements_of_type(self._model, "AttributeUsage"):
            if getattr(attribute, "qualified_name", None) is None:
                continue
            attribute_id = declaration_id_for(attribute)
            if not feature_scopes[attribute_id]:
                continue
            slot = self._slots.slot_of(attribute_id)
            attributes_by_slot[slot].append(attribute)

        for slot, attributes in sorted(
            attributes_by_slot.items(), key=lambda item: item[0].root_declaration.to_wire()
        ):
            roots = [
                attribute
                for attribute in attributes
                if declaration_id_for(attribute) == slot.root_declaration
            ]
            if len(roots) != 1:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_REDEFINITION_INVALID,
                    f"attribute slot {slot!r} has {len(roots)} exact root declarations",
                )
            base = roots[0]
            scopes = {
                scope
                for attribute in attributes
                for scope in feature_scopes[declaration_id_for(attribute)]
            }
            for scope in sorted(scopes, key=repr):
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
        expression = self._without_unit_annotation(
            getattr(writer, "feature_value_expression", None)
        )
        value_site = self._value_site(base, writer, scope)
        # An enumeration value reference names a value, not another feature:
        # `:>> scope = 'CAS Scope'::shared;` has no occurrence to resolve against.
        # Reading it as a reference sends it down the alias walk, which then fails
        # with SI_OCCURRENCE_MISSING against a leaf slot that is an enum member.
        enumeration_literal = self._enumeration_literal(expression)
        literal: float | int | str | None
        if enumeration_literal is not None:
            literal = enumeration_literal
        elif expression is not None:
            literal = extract_literal_value(expression)
        else:
            literal = None
        source_file, source_line = self._source_location(writer)

        if (
            expression is not None
            and enumeration_literal is None
            and not is_literal_node(expression)
        ):
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
                    owner_qualified_name=str(
                        getattr(self._semantic_owner(base), "qualified_name", None) or ""
                    ),
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
                expression_ir=neutral_expression,
                compilability=Compilability.FULLY_COMPILABLE,
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
            owner_qualified_name=str(
                getattr(self._semantic_owner(base), "qualified_name", None) or ""
            ),
        )
        self._register_attr(attr_node)

    @staticmethod
    def _without_unit_annotation(expression: Any) -> Any:
        """Apply the unit-annotation rule to a syside AST, refusing typed if it is malformed.

        The rule and both of its spellings live in ``extraction/unit_annotation``; this is
        the elaborator saying how it refuses. Unwrapping here rather than at each downstream
        test is what keeps it one rule instead of a second special case beside
        ``_enumeration_literal``.
        """
        try:
            return annotated_ast_value(expression)
        except ValueError as error:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                str(error),
            ) from error

    @staticmethod
    def _enumeration_literal(expression: Any) -> str | None:
        """The qualified name of the enumeration value a reference names, if it names one."""
        if expression is None or not SysideAdapter.is_instance(
            expression, "FeatureReferenceExpression"
        ):
            return None
        referent = getattr(expression, "referent", None)
        if referent is None or not SysideAdapter.is_instance(
            getattr(referent, "owner", None), "EnumerationDefinition"
        ):
            return None
        # Identity gate, not a value read: an enumeration member without a
        # reload-stable declaration identity cannot enter the graph, and
        # declaration_id_for raises rather than inventing one.
        declaration_id_for(referent)
        return str(referent.qualified_name)

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
            roots = [
                usage
                for usage in alternatives
                if declaration_id_for(usage) == slot.root_declaration
            ]
            if len(roots) != 1:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_REDEFINITION_INVALID,
                    f"calculation slot {slot!r} has {len(roots)} exact root declarations",
                )
            base = roots[0]
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
            definition_id = declaration_id_for(definition)
            node_id = NodeId(NodeKind.CALCULATION, scope, usage_id)
            calc_data = self._calc_defs.get(definition_id)
            compilation = self._compilation_results.get(definition_id)
            if calc_data is None or compilation is None:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"calculation definition {definition_id.to_wire()} has no exact payload",
                )
            outputs, output_names, output_metadata = self._output_ports(
                node_id, definition, calc_data
            )
            name = str(getattr(usage, "name", None) or "calculation")
            definition_qn = str(getattr(definition, "qualified_name", None) or "")
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
                compilability=compilation.overall_compilability,
                auto_impl_context=self._calculation_auto_impl_context(compilation),
                doc_comment=calc_data.doc_comment,
                calc_expressions=tuple(calc_data.calc_expressions),
                calculation_definition_id=definition_id,
                compilation_definition_id=DeclarationId(compilation.definition_id),
                compiled_output_ids=tuple(
                    DeclarationId(item) for item in compilation.declared_output_ids
                ),
                source_file=str(calc_data.source_file),
                source_line=calc_data.source_line,
            )
            self._graph.calcs[node_id] = node
            for declaration in applicable:
                self._calcs[(scope, declaration_id_for(declaration))] = node
            self._collect_bound_members(usage, definition, node)
            self._collect_unbound_calculation_formals(definition, node)

    def _build_constraint_nodes(self) -> None:
        for usage in SysideAdapter.elements_of_type(
            self._model, "ConstraintUsage", include_subtypes=True
        ):
            association = self._constraint_association(usage)
            usage_id = association.usage_id
            definition = self._typed_definition(usage, "ConstraintDefinition", required=False)
            scopes, cause = self._attachment(self._semantic_owner(usage))
            record = self._mint_constraint_usage_record(
                usage, definition, association, cause, len(scopes)
            )
            self._graph.constraint_usages[usage_id] = record
            for scope in scopes:
                node_id = NodeId(NodeKind.CONSTRAINT, scope, usage_id)
                name = str(getattr(usage, "name", None) or "constraint")
                metadata = self._constraint_metadata(usage, definition, association)
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
                if association.decision.eligibility is Eligibility.BLOCK:
                    reasons = _render_block_reasons(association.decision.diagnostics)
                    self._diagnose(
                        ElaborationCode.SI_CONSTRAINT_BLOCKED,
                        node.node_id,
                        node.display_path,
                        None,
                        f"constraint profile blocked execution: {reasons}",
                    )
                self._collect_bound_members(usage, definition, node)
                if definition is not None and node.source_form == "definition_typed":
                    self._collect_unbound_constraint_formals(definition, node)
                if node.source_form in ("inline", "requirement_constraint"):
                    predicate_expression = getattr(usage, "result_expression", None)
                    if predicate_expression is not None:
                        self._pending_expressions.append(
                            _PendingExpression(node, predicate_expression)
                        )
        self._assert_minting_totality()
        self._halt_on_error_dispositions()

    # ---- the usage tier ---------------------------------------------------

    def _mint_constraint_usage_record(
        self,
        usage: Any,
        definition: Any | None,
        association: _ConstraintAssociation,
        cause: str | None,
        occurrence_count: int,
    ) -> ConstraintUsageRecord:
        """One domain member for one authored usage, minted before expansion.

        The form gate runs first and the record is built from identity metadata alone,
        so a usage that reaches no instance still gets a visible carrier however its
        predicate would behave if walked. Only an *asserted* non-reaching usage is
        classified any further, because an asserted gate that cannot be understood is a
        real failure — and even then the failure arrives as this record's disposition
        rather than as a bare error that leaves every other usage without a carrier.

        The same rule governs an unreadable ``@inapplicable:`` marker: it is reported, not
        raised, and becomes this record's error-grade disposition. Invariant 5 admits no
        exception, so nothing on this path may take the model's whole domain down.
        """
        source_form = self._constraint_source_form(usage)
        owner = self._semantic_owner(usage)
        owner_kind = self._owner_kind(owner)
        source_file, source_line = self._source_location(usage)
        name = str(getattr(usage, "name", None) or "constraint")
        usage_qn = str(getattr(usage, "qualified_name", None) or "<anonymous>")
        annotation = self._read_annotation(usage)
        if annotation.defect is not None:
            # A marker the author wrote but this cannot read. The usage's coverage role is
            # unknowable until the annotation is fixed, so it gets the error-grade
            # disposition the design built for exactly that, and the completeness gate
            # converts it into a named halt.
            disposition = self._disposition(
                "non_reaching",
                "classification_incomplete",
                source_form,
                f"{usage_qn} {annotation.defect}",
            )
        else:
            disposition = self._usage_disposition(
                usage, definition, association, source_form, owner_kind, cause
            )
        return ConstraintUsageRecord(
            declaration_id=association.usage_id,
            usage_qualified_name=str(getattr(usage, "qualified_name", None) or "<anonymous>"),
            display_name=display_name(name),
            source_form=source_form,
            owner_kind=owner_kind,
            owner_qualified_name=str(getattr(owner, "qualified_name", None) or ""),
            membership_kind=self._membership_kind(usage),
            is_negated=bool(getattr(usage, "is_negated", False)),
            source_file=source_file,
            source_line=source_line,
            disposition=disposition,
            occurrence_count=occurrence_count,
            definition_qualified_name=(
                str(getattr(definition, "qualified_name", None) or "")
                if source_form == "definition_typed"
                else None
            ),
            inapplicability=annotation.inapplicability,
        )

    @staticmethod
    def _read_annotation(usage: Any) -> _AnnotationRead:
        """Read an ``@inapplicable: <reason>`` decision off the usage's documentation.

        Read once, here, and recorded on the record — so it travels in the graph and the
        snapshot and no downstream route re-reads the source.

        **It reports a malformed marker; it never raises.** Invariant 5 says minting never
        raises for any form, because a raise during minting leaves *no* usage in the model
        with a disposition — the absence-not-disposition failure this whole item exists to
        end, reached by an authoring typo in one doc comment. The strictness the design
        asks for is preserved and is stronger for being per-usage: the caller turns a
        defect into an error-grade disposition on this record, and the completeness gate
        turns that into a named halt while every other carrier survives.

        The seam is the joined documentation, not "the doc comment": the extractor
        collects every ``Comment`` owned member, trims each body, and joins the survivors
        with newlines (``extraction/extractor.py:803-814``). ``strip("*")`` means a
        ``doc /* … */`` body arrives already trimmed, so "first line" means the first line
        of the join.
        """
        bodies = [
            trimmed
            for member in (getattr(usage, "owned_members", None) or ())
            if SysideAdapter.is_instance(member, "Comment")
            and (raw := getattr(member, "body", None))
            and (trimmed := str(raw).strip().strip("*").strip())
        ]
        if not bodies:
            return _AnnotationRead(None, None)
        lines = "\n".join(bodies).split("\n")
        for later in lines[1:]:
            if later.strip().startswith(_INAPPLICABLE_MARKER):
                return _AnnotationRead(
                    None,
                    f"carries {_INAPPLICABLE_MARKER!r} on a later documentation line; it is "
                    "only read on the first line of the joined documentation",
                )
        first = lines[0].strip()
        if not first.startswith(_INAPPLICABLE_MARKER):
            return _AnnotationRead(None, None)
        reason = first[len(_INAPPLICABLE_MARKER) :]
        if not reason.startswith(":") or not reason[1:].strip():
            return _AnnotationRead(
                None,
                f"has a malformed inapplicability annotation {first!r}; the shape is "
                f"'{_INAPPLICABLE_MARKER}: <reason>'",
            )
        return _AnnotationRead(Inapplicability(reason=reason[1:].strip()), None)

    def _usage_disposition(
        self,
        usage: Any,
        definition: Any | None,
        association: _ConstraintAssociation,
        source_form: str,
        owner_kind: str,
        cause: str | None,
    ) -> UsageDisposition:
        """The ordered precedence rule: form gate, then expansion cause, then profile.

        The causes co-fire — a ``satisfy`` owned by a ``calc def`` matches both the form
        gate and the unattachable-owner rule — so this evaluates in a fixed order and
        stops at the first match. Exactly one disposition comes out, every run.
        """
        usage_qn = str(getattr(usage, "qualified_name", None) or "<anonymous>")
        if source_form == "satisfy_reference":
            return self._disposition(
                "excluded",
                "out_of_scope_satisfy",
                source_form,
                f"{usage_qn} is a satisfy reference, outside the executable scope",
            )
        if owner_kind == "requirement_def":
            return self._disposition(
                "excluded",
                "out_of_profile_owner",
                source_form,
                f"{usage_qn} is owned by the requirement definition "
                f"{self._semantic_owner(usage).qualified_name}, outside the executable profile",
            )
        if cause is not None:
            reason = self._non_reaching_reason(usage, definition, association, source_form, cause)
            return self._disposition(
                "non_reaching",
                reason,
                source_form,
                f"{usage_qn} reaches no instance: {reason}",
            )
        eligibility = association.decision.eligibility
        kind, reason = _ELIGIBILITY_DISPOSITIONS[eligibility]
        return self._disposition(
            kind, reason, source_form, f"{usage_qn} profile eligibility {eligibility.value}"
        )

    def _non_reaching_reason(
        self,
        usage: Any,
        definition: Any | None,
        association: _ConstraintAssociation,
        source_form: str,
        cause: str,
    ) -> str:
        """The expansion cause, unless an asserted usage cannot be classified at all.

        Classification is attempted only for asserted forms. For every other form the
        mint stops at the gate, which is what makes minting non-raising: the predicate
        walk and the definition cross-check are the only two paths that can fail here, and
        neither runs. (The other way a usage can fail to classify is an unreadable
        ``@inapplicable:`` marker; the mint site handles that one before this is reached,
        and by the same rule — a disposition, never a raise.)
        """
        if source_form not in ASSERTED_SOURCE_FORMS:
            return cause
        try:
            self._constraint_metadata(usage, definition, association)
        except ElaborationInvariantError:
            return "classification_incomplete"
        return cause

    @staticmethod
    def _disposition(kind: str, reason: str, source_form: str, detail: str) -> UsageDisposition:
        return UsageDisposition(
            kind=kind,
            reason=reason,
            severity=expected_severity(reason, source_form),
            detail=detail,
        )

    def _assert_minting_totality(self) -> None:
        """Invariant 1: the domain is the pre-expansion sweep, member for member.

        Asserted here because this is the one place both are in scope. The sweep behind
        ``_constraint_associations`` is already proven equal to the profile's decision
        inventory in both directions (``_index_constraint_associations``), so a member
        missing here is a minting defect and nothing else.
        """
        swept = {association.usage_id for association in self._constraint_associations.values()}
        minted = set(self._graph.constraint_usages)
        if swept != minted:
            missing = sorted(item.to_wire() for item in swept - minted)
            unknown = sorted(item.to_wire() for item in minted - swept)
            raise ElaborationInvariantError(
                ElaborationCode.SI_CONSTRAINT_INCOMPLETE,
                "constraint usage domain incomplete: the minted domain disagrees with the "
                f"pre-expansion sweep: unminted={missing}, unswept={unknown}",
            )

    def _halt_on_error_dispositions(self) -> None:
        """Every error-grade disposition becomes a named halt, one diagnostic per usage.

        Raised as graph diagnostics rather than as an immediate exception so that every
        *other* usage in the model still carries a visible record when one fires — the
        whole point of moving the mint upstream. Strict elaboration turns the diagnostics
        into the halt.

        Two causes reach error grade and they get different codes, because a reader acts on
        them differently. An unattachable owner is invariant 9's structural authoring error:
        nothing could ever run this gate, so the diagnostic names the usage *and* the
        missing attachment. A classification that could not complete is a defect in what
        the author wrote about the usage rather than in where they put it, so it reports
        what it could not read.
        """
        for record in self._graph.constraint_usages.values():
            if record.disposition.severity != "error":
                continue
            where = (
                f"{record.declaration_id.to_wire()}) at "
                f"{record.source_file}:{record.source_line}"
            )
            if record.disposition.reason == "classification_incomplete":
                self._diagnose(
                    ElaborationCode.SI_CONSTRAINT_INCOMPLETE,
                    None,
                    record.usage_qualified_name,
                    None,
                    f"constraint usage domain incomplete: {record.usage_qualified_name} "
                    f"({where} cannot be classified: {record.disposition.detail}",
                )
                continue
            self._diagnose(
                ElaborationCode.SI_CONSTRAINT_UNATTACHED,
                None,
                record.usage_qualified_name,
                None,
                f"constraint {record.usage_qualified_name} "
                f"({where} is asserted "
                f"({record.source_form}) but its owner "
                f"{record.owner_qualified_name or '<none>'} ({record.owner_kind}) provides no "
                f"attachment: {record.disposition.reason}",
            )

    @staticmethod
    def _constraint_source_form(usage: Any) -> str:
        """Which of the six authored shapes this usage is, from membership and type alone.

        Total and non-raising by construction — every branch is a type or membership
        test — which is what lets it run over usages that never reached an instance.
        """
        membership = getattr(usage, "owning_feature_membership", None)
        if SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
            return "requirement_constraint"
        if SysideAdapter.is_instance(usage, "AssertConstraintUsage"):
            asserted = getattr(usage, "asserted_constraint", None)
            if asserted is not usage:
                return "named_usage_reference"
            if getattr(usage, "result_expression", None) is None:
                return "definition_typed"
            return "inline"
        if SysideAdapter.is_instance(usage, "SatisfyRequirementUsage"):
            return "satisfy_reference"
        return "plain_usage"

    @staticmethod
    def _membership_kind(usage: Any) -> str | None:
        membership = getattr(usage, "owning_feature_membership", None)
        if not SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
            return None
        raw_kind = getattr(membership, "kind", None)
        return str(getattr(raw_kind, "name", raw_kind)).lower()

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
    def _calculation_auto_impl_context(compilation: Any) -> AutoImplContext | None:
        """Render the stencil's assignment steps and return values in exact order.

        A compiled member becomes an assignment step when something else consumes
        it: every undeclared intermediate, plus any declared output another
        declared output depends on. Stepped members are then returned by name, so
        the rendered function never forward-references or recomputes a value.

        Return values follow declaration-UUID order because that is the order
        projection renders the module's outputs in (``_Projection._outputs``
        sorts on ``DeclarationId.to_wire()``); the returned tuple has to line up
        with that schema positionally, and rendered member names never decide it.
        """
        if compilation.overall_compilability is not Compilability.FULLY_COMPILABLE:
            return None
        results = {result.output_id: result for result in compilation.output_results}
        consumed_ids = {
            dependency
            for result in compilation.output_results
            for dependency in result.dependency_ids
        }
        execution_steps: list[AutoImplStep] = []
        stepped_ids: set[UUID] = set()
        for member_id in compilation.execution_order:
            result = results.get(member_id)
            if result is None or result.python_expression is None:
                continue
            if not result.is_undeclared_intermediate and member_id not in consumed_ids:
                continue
            execution_steps.append(
                AutoImplStep(name=result.output_name, expression=result.python_expression)
            )
            stepped_ids.add(member_id)

        output_expressions: list[AutoImplOutput] = []
        for output_id in sorted(compilation.declared_output_ids):
            result = results.get(output_id)
            if result is None or result.python_expression is None:
                continue
            output_expressions.append(
                AutoImplOutput(
                    name=result.output_name,
                    expression=(
                        result.output_name
                        if output_id in stepped_ids
                        else result.python_expression
                    ),
                )
            )
        return AutoImplContext(
            execution_steps=execution_steps,
            output_expressions=output_expressions,
            output_count=len(output_expressions),
            single_output_expression=(
                output_expressions[0].expression if len(output_expressions) == 1 else None
            ),
        )

    def _constraint_metadata(
        self,
        usage: Any,
        definition: Any | None,
        association: _ConstraintAssociation,
    ) -> dict[str, Any]:
        source_form = self._constraint_source_form(usage)

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
        if source_form == "definition_typed":
            live_definition_id = (
                SysideAdapter.element_id(definition) if definition is not None else None
            )
            selected_definition_id = (
                association.effective_definition_id.value
                if association.effective_definition_id is not None
                else None
            )
            if live_definition_id != selected_definition_id:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"constraint {usage_qn!r} exact definition association disagrees: "
                    f"live={live_definition_id}, profile={selected_definition_id}",
                )
        decision = association.decision
        predicate_ir = decision.effective_predicate
        if predicate_ir is None:
            predicate_expression = getattr(predicate_source, "result_expression", None)
            if predicate_expression is not None:
                neutral_predicate = extract_expression_ir(predicate_expression)
                if neutral_predicate is None:
                    raise ElaborationInvariantError(
                        ElaborationCode.SI_REDEFINITION_INVALID,
                        f"constraint {usage_qn!r} has no representable predicate IR",
                    )
                predicate_ir = neutral_predicate
        owner = self._semantic_owner(usage)
        owner_kind = self._owner_kind(owner)
        source_file, source_line = self._source_location(usage)
        exclusion_reasons = (
            tuple(diagnostic.reason for diagnostic in decision.diagnostics)
            if decision.eligibility is Eligibility.NON_NUMERICAL
            else ()
        )
        membership_kind = self._membership_kind(usage)
        definition_qn = (
            str(getattr(definition, "qualified_name", None) or "")
            if source_form == "definition_typed"
            else None
        )
        predicate_qn = str(getattr(predicate_source, "qualified_name", None) or "")
        # Exact definition identity stays typed in the graph. Projection owns the
        # model-derived public source key and renders it from definition metadata.
        source_key = (
            ""
            if source_form == "definition_typed"
            else f"inline:{predicate_qn}"
            if source_form in ("inline", "requirement_constraint") and predicate_qn
            else association.usage_id.to_wire()
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
            "eligibility": decision.eligibility,
            "effective_definition_id": association.effective_definition_id,
            "exclusion_reasons": exclusion_reasons,
            "exclusion_location": (f"{source_file}:{source_line}" if exclusion_reasons else None),
            "source_file": source_file,
            "source_line": source_line,
        }

    def _output_ports(
        self,
        node_id: NodeId,
        definition: Any,
        calc_data: CalculationDefinitionData,
    ) -> tuple[
        dict[DeclarationId, OutputPortId],
        dict[DeclarationId, str],
        dict[DeclarationId, PortMetadata],
    ]:
        outputs: dict[DeclarationId, OutputPortId] = {}
        names: dict[DeclarationId, str] = {}
        metadata: dict[DeclarationId, PortMetadata] = {}
        output_data = {
            DeclarationId(item.element_id): item
            for item in calc_data.output_attributes
            if item.element_id is not None
        }
        for member in getattr(definition, "owned_members", None) or ():
            if self._direction(member) not in ("out", "return"):
                continue
            output_id = declaration_id_for(member)
            outputs[output_id] = OutputPortId(node_id, output_id)
            raw_name = str(getattr(member, "name", None) or "result")
            names[output_id] = display_name(raw_name)
            extracted = output_data.get(output_id)
            if extracted is None:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"calculation output {output_id.to_wire()} has no exact metadata",
                )
            metadata[output_id] = PortMetadata(
                python_type=extracted.python_type,
                description=extracted.description,
                default_value=extracted.default_value,
                unit=extracted.unit,
                qualified_name=str(getattr(member, "qualified_name", None) or ""),
            )
        if set(output_data) != set(outputs):
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                "extracted output metadata does not match the live output declarations",
            )
        return outputs, names, metadata

    def _collect_bound_members(
        self,
        usage: Any,
        definition: Any | None,
        consumer: CalcNode | ConstraintNode,
    ) -> None:
        unbound: list[DeclarationId] = []
        for member in getattr(usage, "owned_members", None) or ():
            if self._direction(member) != "in":
                continue
            member_id = declaration_id_for(member)
            if definition is None:
                raise ElaborationInvariantError(
                    ElaborationCode.SI_EDGE_DANGLING,
                    f"bound input {member_id.to_wire()} has no selected definition",
                )
            effective_formal_id = self._unit_source_for_formal(definition, member_id)
            structural_formal_id = (
                effective_formal_id if isinstance(consumer, ConstraintNode) else member_id
            )
            port = ConsumerPortId(consumer.node_id, structural_formal_id)
            name = str(getattr(member, "name", None) or "input")
            consumer.input_names[port] = display_name(name)
            extracted = None
            if isinstance(consumer, CalcNode):
                extracted = self._calculation_input_attribute(
                    consumer, effective_formal_id
                )
            consumer.input_metadata[port] = PortMetadata(
                python_type=(
                    extracted.python_type
                    if extracted is not None
                    else self._feature_python_type(effective_formal_id)
                ),
                description=(extracted.description if extracted is not None else None),
                default_value=(extracted.default_value if extracted is not None else None),
                unit=(
                    extracted.unit
                    if extracted is not None
                    else self._unit_for_declaration(effective_formal_id)
                ),
                qualified_name=str(getattr(member, "qualified_name", None) or ""),
                formal_provenance=(
                    self._formal_provenance(effective_formal_id)
                    if isinstance(consumer, ConstraintNode)
                    else None
                ),
            )
            # The same rule, in the binding lane: `in tol = 0.05 [m];` binds the number.
            # Unwrapped once here rather than inside `_binding_evidence`, because the
            # literal read below wants the same expression the classifier saw — and
            # because a second application site is a second place the rule could drift.
            expression = self._without_unit_annotation(
                getattr(member, "feature_value_expression", None)
            )
            if expression is None:
                unbound.append(structural_formal_id)
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
        for slot, formal_id in self._effective_input_formals(definition).items():
            if slot in occupied_slots:
                continue
            formal = self._feature(formal_id)
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
                python_type=self._feature_python_type(formal_id),
                default_value=resolved_default.value,
                unit=resolved_default.unit_text or self._unit_for_declaration(formal_id),
                qualified_name=str(getattr(formal, "qualified_name", None) or ""),
                unresolved_default_kind=resolved_default.unresolved_node_kind,
                formal_provenance=self._formal_provenance(formal_id),
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
        unbound = list(consumer.unbound_formals)
        for slot, formal_id in self._effective_input_formals(definition).items():
            if slot in occupied_slots:
                continue
            formal = self._feature(formal_id)
            port = ConsumerPortId(consumer.node_id, formal_id)
            name = str(getattr(formal, "name", None) or "input")
            extracted = self._calculation_input_attribute(consumer, formal_id)
            expression = getattr(formal, "feature_value_expression", None)
            serialized_default = None
            if expression is not None:
                default_ir = extract_expression_ir(expression)
                if default_ir is not None:
                    serialized_default = serialize_expression(default_ir)
            resolved_default = resolve_modeled_default(serialized_default)
            consumer.input_names[port] = display_name(name)
            consumer.input_metadata[port] = PortMetadata(
                python_type=extracted.python_type,
                description=extracted.description,
                default_value=(
                    resolved_default.value
                    if expression is not None
                    else extracted.default_value
                ),
                unit=resolved_default.unit_text
                or extracted.unit
                or self._unit_for_declaration(formal_id),
                qualified_name=str(getattr(formal, "qualified_name", None) or ""),
                unresolved_default_kind=resolved_default.unresolved_node_kind,
            )
            unbound.append(formal_id)
            occupied_slots.add(slot)
        consumer.unbound_formals = tuple(unbound)

    def _calculation_input_attribute(
        self,
        consumer: CalcNode,
        formal_id: DeclarationId,
    ) -> Any:
        definition_id = consumer.calculation_definition_id
        if definition_id is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"calculation {consumer.display_path!r} has no definition identity",
            )
        calc_data = self._calc_defs.get(definition_id)
        if calc_data is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"calculation definition {definition_id.to_wire()} has no exact payload",
            )
        matches = [
            item
            for item in calc_data.input_attributes
            if item.element_id is not None and DeclarationId(item.element_id) == formal_id
        ]
        if len(matches) != 1:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"formal {formal_id.to_wire()} maps to {len(matches)} exact metadata records",
            )
        return matches[0]

    def _feature_python_type(self, declaration_id: DeclarationId) -> str:
        """Render a public scalar type from one exact feature-typing relationship."""
        root_id = self._slots.slot_of(declaration_id).root_declaration
        feature = self._elements.get(root_id)
        if feature is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"feature {root_id.to_wire()} has no exact live declaration",
            )
        type_targets = [
            target
            for relationship, target in (getattr(feature, "heritage", None) or ())
            if SysideAdapter.is_instance(relationship, "FeatureTyping")
        ]
        if len(type_targets) != 1:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"feature {root_id.to_wire()} has {len(type_targets)} exact typings",
            )
        type_name = str(getattr(type_targets[0], "qualified_name", None) or "")
        python_type = {
            "ScalarValues::Boolean": "bool",
            "ScalarValues::Integer": "int",
            "ScalarValues::Real": "float",
            "ScalarValues::String": "str",
        }.get(type_name)
        if python_type is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"feature {root_id.to_wire()} has unsupported exact type {type_name!r}",
            )
        return python_type

    def _effective_input_formals(
        self, definition: Any
    ) -> dict[FeatureSlotId, DeclarationId]:
        definition_id = declaration_id_for(definition)
        selected = self._effective_formals_by_definition.get(definition_id)
        if selected is None:
            selected = self._formal_selector.effective_input_formals(definition)
            self._effective_formals_by_definition[definition_id] = selected
        return selected

    def _unit_source_for_formal(
        self, definition: Any, declaration_id: DeclarationId
    ) -> DeclarationId:
        slot = self._slots.slot_of(declaration_id)
        selected = self._effective_input_formals(definition).get(slot)
        if selected is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"input slot {slot!r} has no effective formal on selected definition "
                f"{declaration_id_for(definition).to_wire()}",
            )
        return selected

    def _feature(self, declaration_id: DeclarationId) -> Any:
        feature = self._elements.get(declaration_id)
        if feature is None or not SysideAdapter.is_instance(feature, "Feature"):
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"feature {declaration_id.to_wire()} has no exact live declaration",
            )
        return feature

    def _unit_for_declaration(self, declaration_id: DeclarationId) -> str | None:
        return extract_feature_unit(
            self._feature(declaration_id),
            model_paths=self._model_paths,
        )

    def _formal_provenance(self, declaration_id: DeclarationId) -> FormalProvenance:
        formal = self._elements.get(declaration_id)
        if formal is None:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"constraint formal {declaration_id.to_wire()} has no exact live declaration",
            )
        raw_name = str(getattr(formal, "name", None) or "")
        qualified_name = str(getattr(formal, "qualified_name", None) or "")
        if not raw_name or not qualified_name:
            raise ElaborationInvariantError(
                ElaborationCode.SI_EDGE_DANGLING,
                f"constraint formal {declaration_id.to_wire()} lacks display metadata",
            )
        return FormalProvenance(
            declaration_id=declaration_id,
            raw_name=raw_name,
            qualified_name=qualified_name,
        )

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
            return [self._resolve_direct_reference(reference.leaf_id, consumer_scope)]
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
                *self._select_calc_nodes(
                    calc_candidates,
                    consumer_scope,
                    plural=plural,
                )
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
            permitted = [
                candidate
                for candidate in candidates
                if self._occurrences.occurrence(candidate).parent_id is None
            ]
            if not permitted:
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_MISSING,
                    "package context has no top-level occurrence for the exact declaration",
                )
            if not plural and len(permitted) != 1:
                raise _ReferenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    f"package context contains {len(permitted)} candidate occurrences",
                )
            return permitted
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
        permitted = [
            candidate
            for candidate in candidates
            if self._occurrences.occurrence(candidate).parent_id is None
        ]
        if not permitted:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                "consumer context has no permitted occurrence for the exact declaration",
            )
        if not plural and len(permitted) != 1:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"permitted scope contains {len(permitted)} candidate occurrences",
            )
        return permitted

    def _select_calc_nodes(
        self,
        candidates: list[CalcNode],
        consumer_scope: ScopeId,
        *,
        plural: bool,
    ) -> list[CalcNode]:
        if not candidates:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                "exact calculation declaration has no concrete node",
            )
        by_scope = {node.scope: node for node in candidates}
        exact = by_scope.get(consumer_scope)
        if exact is not None:
            return [exact]
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
                if under and plural:
                    return under
                if len(under) == 1:
                    return under
                if len(under) > 1:
                    raise _ReferenceResolutionError(
                        ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                        f"consumer context contains {len(under)} calculation nodes",
                    )
        permitted = [
            node
            for node in candidates
            if isinstance(node.scope, PackageScopeId)
            or (
                isinstance(node.scope, OccurrenceId)
                and self._occurrences.occurrence(node.scope).parent_id is None
            )
        ]
        if not permitted:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                "consumer context has no permitted calculation node",
            )
        if not plural and len(permitted) != 1:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"permitted scope contains {len(permitted)} calculation nodes",
            )
        return permitted

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

    def _resolve_direct_reference(
        self,
        leaf_id: DeclarationId,
        consumer_scope: ScopeId,
    ) -> NodeRef | ProducerRef:
        """Resolve a one-segment reference, anchored on its leaf's exact owner.

        SysIDE has already resolved the written text to one exact leaf declaration, and
        when a ``PartUsage`` owns that declaration the owner *is* the occurrence the
        author named. Feature slots are shared across a whole redefinition family, so
        re-finding the slot from the consumer's own lineage — what ``_resolve_leaf``
        does — can land on a sibling occurrence that merely carries the same slot. This
        route keeps the author's occurrence by running the sequence in the order the
        model states it: owner declaration, then owner occurrence, then leaf slot at
        that occurrence.

        Only a ``PartUsage`` owner names an occurrence. A leaf owned by a definition,
        package, enumeration, or calculation has none of its own, so it keeps the
        existing leaf route unchanged.

        A leaf the element index does not know is refused rather than routed. The index
        holds every declaration that carries a reload-stable qualified name, which is
        every declaration an author can write a reference to; a leaf missing from it
        means the resolved fact and the index disagree about what the model contains.
        Owner classification is then unanswerable, and the definition-owned route would
        answer from the consumer's own lineage — a positional guess dressed as the
        deliberate exemption above. This site therefore refuses by name.
        """
        leaf = self._elements.get(leaf_id)
        if leaf is None:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"leaf declaration {leaf_id.to_wire()} is absent from the element index, "
                "so its owner cannot be classified",
            )

        owner = self._semantic_owner(leaf)
        if not SysideAdapter.is_instance(owner, "PartUsage"):
            return self._resolve_leaf(leaf_id, consumer_scope)

        owner_id = declaration_id_for(owner)
        # Scalar regardless of the caller's ``plural``: that flag describes the
        # aggregation the caller is expanding, not this reference. A direct term names
        # one owner, so honoring the flag here would fan the term out across sibling
        # occurrences and invent a cardinality the model never authored.
        [owner_occurrence] = self._select_occurrences(
            [
                occurrence.occurrence_id
                for occurrence in self._occurrences.occurrences_for_declaration(owner_id)
            ],
            consumer_scope,
            plural=False,
        )
        # An owner that cannot be selected, or that carries no target for the leaf, is
        # final. Consumer position decided the wrong occurrence in the first place; it is
        # not a recovery authority, so there is no retry of the leaf route from here.
        edge = self._target_at(owner_occurrence, leaf_id)
        if edge is None:
            raise _ReferenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"exact owner {owner_id.to_wire()} has no target for leaf "
                f"{leaf_id.to_wire()} at its selected occurrence",
            )
        return edge

    def _resolve_leaf(
        self,
        declaration_id: DeclarationId,
        consumer_scope: ScopeId,
    ) -> NodeRef | ProducerRef:
        producing_calcs = [
            node for node in self._graph.calcs.values() if declaration_id in node.outputs
        ]
        if producing_calcs:
            [producer] = self._select_calc_nodes(
                producing_calcs,
                consumer_scope,
                plural=False,
            )
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
            input_names = (
                _computed_expression_input_names(facts)
                if isinstance(pending.consumer, CalcNode)
                else {}
            )
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
                    input_name = input_names.get(
                        reference_ordinal,
                        (
                            fact.resolved_member_names[-1]
                            if fact.resolved_member_names
                            else leaf_fact.element_name
                        ),
                    )
                    pending.consumer.input_names[port] = input_name
                    pending.consumer.input_metadata[port] = PortMetadata(
                        python_type=self._feature_python_type(leaf),
                        unit=self._unit_for_declaration(leaf),
                        qualified_name=leaf_fact.qualified_name,
                        formal_provenance=(
                            self._formal_provenance(leaf)
                            if isinstance(pending.consumer, ConstraintNode)
                            else None
                        ),
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
        # A unit annotation contributes its value and never a reference, and the walk is
        # where the predicate lane learns that. It has to be the head, before any
        # structural dispatch, and it has to be here rather than at the predicate entry:
        # `gap_width [m] >= 0.25 [m]` nests both annotations under the comparison, so an
        # entry-level unwrap is a no-op on the actual defect. Safe against the dispatch
        # below because `annotated_ast_value` returns the expression unchanged unless its
        # operator is `[`, and a FeatureChainExpression's is not.
        expression = self._without_unit_annotation(expression)
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
