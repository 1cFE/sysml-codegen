"""One diagnostic vocabulary for exact-ID elaboration failures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["ElaborationCode", "ElaborationInvariantError", "ManualStubNotice", "SiteReason"]


class ElaborationCode(StrEnum):
    SI_EVIDENCE_INCOMPLETE = "SI_EVIDENCE_INCOMPLETE"
    SI_TYPE_INVALID = "SI_TYPE_INVALID"
    SYSML_NAMESPACE_NOT_DISTINGUISHABLE = "SYSML_NAMESPACE_NOT_DISTINGUISHABLE"
    SI_OCCURRENCE_MISSING = "SI_OCCURRENCE_MISSING"
    SI_OCCURRENCE_AMBIGUOUS = "SI_OCCURRENCE_AMBIGUOUS"
    OVERRIDE_TARGET_MISSING = "OVERRIDE_TARGET_MISSING"
    SI_ID_MISSING = "SI_ID_MISSING"
    SI_ID_UNSTABLE = "SI_ID_UNSTABLE"
    SI_REDEFINITION_INVALID = "SI_REDEFINITION_INVALID"
    SI_MULTIPLICITY_UNRESOLVED = "SI_MULTIPLICITY_UNRESOLVED"
    SI_MULTIPLICITY_UNSUPPORTED = "SI_MULTIPLICITY_UNSUPPORTED"
    SI_MULTIPLICITY_INVALID = "SI_MULTIPLICITY_INVALID"
    SI_INDEXED_SOURCE_UNSUPPORTED = "SI_INDEXED_SOURCE_UNSUPPORTED"
    SI_EXPRESSION_SOURCE_UNSUPPORTED = "SI_EXPRESSION_SOURCE_UNSUPPORTED"
    SI_CONTAINMENT_RECURSIVE = "SI_CONTAINMENT_RECURSIVE"
    SI_ALIAS_CYCLE = "SI_ALIAS_CYCLE"
    SI_EDGE_DANGLING = "SI_EDGE_DANGLING"
    SI_CONSTRAINT_BLOCKED = "SI_CONSTRAINT_BLOCKED"
    SI_CONSTRAINT_UNATTACHED = "SI_CONSTRAINT_UNATTACHED"
    SI_CONSTRAINT_INCOMPLETE = "SI_CONSTRAINT_INCOMPLETE"
    SI_RENDERING_COLLISION = "SI_RENDERING_COLLISION"
    SI_SNAPSHOT_INVALID = "SI_SNAPSHOT_INVALID"
    EXTRACTION_DIAGNOSTIC_BLOCKING = "EXTRACTION_DIAGNOSTIC_BLOCKING"
    #: Not a statement about the model. This one names a defect in the
    #: generator itself, so a user can tell "your model" from "our bug".
    SI_INTERNAL_DEFECT = "SI_INTERNAL_DEFECT"


class SiteReason(StrEnum):
    """Which refusal site fired, finer than its code (EXEC-SUBSET-CONTRACT Item 2a D8).

    Many sites share one ``ElaborationCode``, and a later check can refuse with the same
    code as an earlier one it shadows. The reason names the site, so a conformance case
    can tell which one refused. Members are ``<stage>_<condition>`` and stay distinct from
    the shared contract's ``SUBSET_REASON_CODES``, which name modelled shapes, not sites.

    A reason is carried live only. It is not part of the v6 snapshot encoding, and a
    sealed graph holds no diagnostics to carry one.
    """

    OCCURRENCE_MULTIPLICITY_ORDERED = "occurrence_multiplicity_ordered"
    OCCURRENCE_MULTIPLICITY_NONUNIQUE = "occurrence_multiplicity_nonunique"
    OCCURRENCE_MULTIPLICITY_UPPER_UNRESOLVED = "occurrence_multiplicity_upper_unresolved"
    OCCURRENCE_MULTIPLICITY_NEGATIVE = "occurrence_multiplicity_negative"
    OCCURRENCE_MULTIPLICITY_LOWER_UNRESOLVED = "occurrence_multiplicity_lower_unresolved"
    OCCURRENCE_MULTIPLICITY_RANGE = "occurrence_multiplicity_range"
    ELABORATION_CONSTRAINT_OWNER_UNMAPPED = "elaboration_constraint_owner_unmapped"
    ELABORATION_ASSERTED_CONSTRAINT_UNATTACHED = "elaboration_asserted_constraint_unattached"
    CONSTRAINT_PROFILE_BLOCKED = "constraint_profile_blocked"
    BINDING_SOURCE_FORM_UNSUPPORTED = "binding_source_form_unsupported"
    EXTRACTION_TYPING_TARGET_UNSUPPORTED = "extraction_typing_target_unsupported"
    ELABORATION_NO_EXECUTABLE_CONTENT = "elaboration_no_executable_content"
    GENERATION_CONSTRAINT_NAME_UNSAFE = "generation_constraint_name_unsafe"
    INTERNAL_FAILURE_UNCLASSIFIED = "internal_failure_unclassified"
    # Sites an R3 row of the subset contract names: the generator refuses there and no shared
    # rule describes the shape, so the reason is how a conformance case tells them apart.
    OCCURRENCE_CONTAINMENT_UNANCHORED = "occurrence_containment_unanchored"
    OCCURRENCE_CONTAINMENT_STEP_MISSING = "occurrence_containment_step_missing"
    ELABORATION_VALUE_WRITERS_INCOMPARABLE = "elaboration_value_writers_incomparable"
    ELABORATION_OWNER_ADDRESS_TARGET_MISSING = "elaboration_owner_address_target_missing"
    ELABORATION_CALCULATION_OUTPUT_UNPRODUCED = "elaboration_calculation_output_unproduced"
    ELABORATION_FEATURE_DECLARATION_UNINDEXED = "elaboration_feature_declaration_unindexed"
    PROJECTION_DEFAULT_NON_NUMERIC = "projection_default_non_numeric"
    PROJECTION_SUM_ARGUMENT_COUNT = "projection_sum_argument_count"
    EXTRACTION_CALC_DEF_NO_OUTPUT = "extraction_calc_def_no_output"
    # Codegen-only refusals of a valid model: no shared rule or R3 row names the shape, so the
    # contract is silent and the reason is what a conformance case pins (Item 2a P6).
    EXTRACTION_CALC_DEF_RETURN_UNNAMED = "extraction_calc_def_return_unnamed"
    EXTRACTION_PARAMETER_TYPING_COUNT = "extraction_parameter_typing_count"
    IDENTITY_QUALIFIED_NAME_MISSING = "identity_qualified_name_missing"
    OCCURRENCE_REDEFINITION_ROOTS_UNRELATED = "occurrence_redefinition_roots_unrelated"
    OCCURRENCE_ANCHOR_SCOPE_MISSING = "occurrence_anchor_scope_missing"
    OCCURRENCE_ANCHOR_DEFINITION_AMBIGUOUS = "occurrence_anchor_definition_ambiguous"
    OCCURRENCE_CONTAINMENT_STEP_AMBIGUOUS = "occurrence_containment_step_ambiguous"
    OCCURRENCE_PART_TYPING_AMBIGUOUS = "occurrence_part_typing_ambiguous"
    ELABORATION_CALC_DEF_ID_MISSING = "elaboration_calc_def_id_missing"
    ELABORATION_CALC_PARAMETER_ID_MISSING = "elaboration_calc_parameter_id_missing"
    ELABORATION_DEEP_OVERRIDE_TARGET_MISSING = "elaboration_deep_override_target_missing"
    ELABORATION_DEEP_OVERRIDE_TARGET_COMPUTED = "elaboration_deep_override_target_computed"
    ELABORATION_CALC_DEF_PAYLOAD_MISSING = "elaboration_calc_def_payload_missing"
    ELABORATION_USAGE_DEFINITION_TYPING_COUNT = "elaboration_usage_definition_typing_count"
    ELABORATION_CONSTRAINT_DEFINITION_DISAGREES = "elaboration_constraint_definition_disagrees"
    ELABORATION_CALC_OUTPUT_METADATA_MISSING = "elaboration_calc_output_metadata_missing"
    ELABORATION_BOUND_INPUT_DEFINITION_MISSING = "elaboration_bound_input_definition_missing"
    ELABORATION_FEATURE_TYPING_COUNT = "elaboration_feature_typing_count"
    ELABORATION_FEATURE_TYPE_UNSUPPORTED = "elaboration_feature_type_unsupported"
    ELABORATION_BOUND_INPUT_FORMAL_MISSING = "elaboration_bound_input_formal_missing"
    ELABORATION_REFERENCE_LEAF_UNINDEXED = "elaboration_reference_leaf_unindexed"
    ELABORATION_BARE_REFERENCE_PREFIX_REQUIRED = "elaboration_bare_reference_prefix_required"
    ELABORATION_CALCULATION_OUTPUT_AMBIGUOUS = "elaboration_calculation_output_ambiguous"
    ELABORATION_LITERAL_BINDING_EMPTY = "elaboration_literal_binding_empty"
    GRAPH_COMPUTED_IR_UNSUPPORTED = "graph_computed_ir_unsupported"
    PROJECTION_MODULE_NAME_COLLISION = "projection_module_name_collision"
    PROJECTION_CHANNEL_NAME_COLLISION = "projection_channel_name_collision"
    PROJECTION_GROUP_PACKAGE_UNNAMED = "projection_group_package_unnamed"
    PROJECTION_ENTRY_POINT_NAME_COLLISION = "projection_entry_point_name_collision"
    PROJECTION_ENTRY_POINT_METADATA_CONFLICT = "projection_entry_point_metadata_conflict"
    PROJECTION_PARAMETER_NAME_COLLISION = "projection_parameter_name_collision"
    PROJECTION_EXPRESSION_PARAMETER_COLLISION = "projection_expression_parameter_collision"
    PROJECTION_OUTPUT_ALIAS_COLLISION = "projection_output_alias_collision"
    COMPILE_REFERENCE_OUTSIDE_CALC_DEF = "compile_reference_outside_calc_def"
    GENERATION_MODULE_PATH_COLLISION = "generation_module_path_collision"
    GENERATION_SCHEMA_PATH_COLLISION = "generation_schema_path_collision"
    GENERATION_REGISTRY_CLASS_NAME_COLLISION = "generation_registry_class_name_collision"
    GENERATION_PARAM_FIELD_COLLISION = "generation_param_field_collision"
    GENERATION_PREDICATE_FUNCTION_NAME_COLLISION = "generation_predicate_function_name_collision"
    # Two sites the corpus reaches that Item 2a first recorded as reached by no model (final
    # audit, Blocker 1). The second refuses a valid model: a suspected defect, RG1-12.
    ELABORATION_CONSTRAINT_DEFINITION_UNINDEXED = "elaboration_constraint_definition_unindexed"
    GRAPH_ROOT_OCCURRENCE_PACKAGE_MISSING = "graph_root_occurrence_package_missing"
    # Re-checks behind a preflight that already refused the same condition: no valid model
    # reaches them, but each factory caller still names its own site.
    GENERATION_REGISTRY_RENDER_CLASS_NAME_COLLISION = (
        "generation_registry_render_class_name_collision"
    )
    GENERATION_PREDICATE_BINDING_NAME_UNSAFE = "generation_predicate_binding_name_unsafe"
    # Stub causes: a calc def output the compiler cannot render becomes a ``MANUAL_REQUIRED``
    # stub on a successful run. One per renderer site (``extraction/calc_compat_renderer.py``)
    # and per compiler path that stubs without raising (``extraction/expression_compiler.py``).
    COMPILE_OUTPUT_NOT_PYTHON = "compile_output_not_python"
    COMPILE_INVOCATION = "compile_invocation"
    COMPILE_IR_NODE_UNSUPPORTED = "compile_ir_node_unsupported"
    COMPILE_IR_NODE_UNKNOWN = "compile_ir_node_unknown"
    COMPILE_LITERAL_KIND = "compile_literal_kind"
    COMPILE_FEATURE_CHAIN = "compile_feature_chain"
    COMPILE_REFERENCE_UNRESOLVED = "compile_reference_unresolved"
    COMPILE_OPERATOR_UNSUPPORTED = "compile_operator_unsupported"
    COMPILE_OPERATOR_WITHOUT_OPERANDS = "compile_operator_without_operands"
    COMPILE_UNARY_OPERATOR_UNSUPPORTED = "compile_unary_operator_unsupported"
    COMPILE_DEPENDENCY_CYCLE = "compile_dependency_cycle"
    COMPILE_NO_EXPRESSION = "compile_no_expression"
    # Relayed from agentic-mbse: one per ``SemanticEvidenceCode``, set where the live
    # route converts a ``SemanticEvidenceError`` (``orchestration/elaborated_pipeline.py``).
    EVIDENCE_METATYPE_CHECK_FAILED = "evidence_metatype_check_failed"
    EVIDENCE_EXPRESSION_KIND_UNSUPPORTED = "evidence_expression_kind_unsupported"
    EVIDENCE_OPERAND_ITERATION_FAILED = "evidence_operand_iteration_failed"
    EVIDENCE_EXPRESSION_DEPTH_EXHAUSTED = "evidence_expression_depth_exhausted"
    EVIDENCE_RESOLVED_TARGET_MISSING = "evidence_resolved_target_missing"
    EVIDENCE_DOCUMENT_TIER_MISSING = "evidence_document_tier_missing"
    EVIDENCE_DOCUMENT_TIER_UNKNOWN = "evidence_document_tier_unknown"
    EVIDENCE_RESOLVED_LEAF_MISSING = "evidence_resolved_leaf_missing"
    EVIDENCE_INDEXED_REFERENCE_UNSUPPORTED = "evidence_indexed_reference_unsupported"


@dataclass(frozen=True)
class ManualStubNotice:
    """One calc def output that compiles to a ``MANUAL_REQUIRED`` stub, and why (Item 2a D9).

    Generation succeeds with a handwritten stub in its place, so the run itself says nothing.
    Elaboration logs one notice per (calc def, output) as a warning carrying this object, so
    the cause is visible on the live route. A from-snapshot run compiles nothing and logs none.
    """

    calculation: str
    output: str
    reason: SiteReason
    detail: str
    #: The stubbed member is an undeclared intermediate another output reads, not an output.
    intermediate: bool


class ElaborationInvariantError(ValueError):
    """An exact-ID invariant failed before a usable graph could be built."""

    def __init__(
        self,
        code: ElaborationCode,
        detail: str,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
        reason: SiteReason | None = None,
    ) -> None:
        self.code = code
        self.detail = detail
        self.reference = reference
        self.location = location
        self.reason = reason
        super().__init__(f"{code.value}: {detail}")
