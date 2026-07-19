"""Pydantic data models for pipeline code generation.

This module defines the core data models used for building and representing
the computation graph. These models provide validation at construction
time and serve as the single source of truth for pipeline generation.

Key Design Principles:
1. Use Pydantic for validation at boundaries
2. Import existing types (BindingType) rather than redefining
3. Qualified names use __ separator per ADR-001
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Import shared types from core for re-export (backward compatibility)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.extraction.expression_compiler import Compilability


class _TransactionalAssignmentModel(BaseModel):
    """Validate a field change before mutating the live Pydantic instance.

    Pydantic's assignment validation runs model validators after setting the field. A rejected
    cross-field change therefore leaves the object invalid. These decision-carrying records need a
    stronger lifetime invariant: a failed assignment must leave the prior valid value intact.
    """

    model_config = ConfigDict(validate_assignment=True)

    def __setattr__(self, name: str, value: object) -> None:
        if name in type(self).model_fields and hasattr(self, "__pydantic_fields_set__"):
            candidate = BaseModel.model_dump(self, mode="python")
            candidate[name] = value
            type(self).model_validate(candidate)
        super().__setattr__(name, value)


class EntryPointType(str, Enum):
    """ADR-001 entry point types.

    Classification of how an entry point value is sourced:
    - LIBRARY_DEFAULT: Unbound param using calc def default value
    - DESIGN_ATTRIBUTE: Literal value defined in design part
    - USAGE_LITERAL: Literal value in calc usage binding
    """

    LIBRARY_DEFAULT = "library_default"
    DESIGN_ATTRIBUTE = "design_attribute"
    USAGE_LITERAL = "usage_literal"


class EntryPoint(BaseModel):
    """A classified entry point parameter.

    This is the DEFINITIVE representation of an entry point.
    Qualified names use __ separator per ADR-001.

    Attributes:
        qualified_name: Unique identifier with __ separator
            (e.g., "CATFMFEPhysics__catf_physics__p_fusion")
        simple_name: The parameter name alone (e.g., "p_fusion")
        entry_type: Classification per ADR-001
        default_value: Default value if available
        source_calc_usage: For LIBRARY_DEFAULT, which calc usage needs this
        param_group: Which JSON file group (e.g., "physics_params")
    """

    qualified_name: str
    simple_name: str
    entry_type: EntryPointType
    default_value: float | None = None
    source_calc_usage: str | None = None
    param_group: str | None = None
    python_type: str = "float"

    @property
    def json_field_name(self) -> str:
        """The field name in the JSON file.

        Uses qualified name for globally unique identification.
        """
        return self.qualified_name


class ParameterGroup(BaseModel):
    """A group of entry points for a single JSON file.

    Groups entry points by source file for organized parameter management.

    Attributes:
        name: Group identifier (e.g., "physics_params")
        class_name: Python class name (e.g., "PhysicsParams")
        source_file: Source SysML file
        parameters: List of entry points in this group
    """

    name: str
    class_name: str
    source_file: Path
    parameters: list[EntryPoint]

    model_config = {"arbitrary_types_allowed": True}

    @property
    def json_filename(self) -> str:
        """Filename for JSON input file."""
        return f"{self.name}.json"

    @property
    def schema_filename(self) -> str:
        """Filename for Pydantic schema file."""
        return f"{self.name}.py"


class InputSource(BaseModel):
    """Source of a module input value.

    Describes where a module input gets its value from:
    - entry_point: From a JSON input file
    - module_output: From an upstream module's output

    Attributes:
        source_type: Either "entry_point" or "module_output"
        param_group: For entry_point, which JSON file
        qualified_name: For entry_point, the qualified parameter name
        producer_channel: For module_output, the upstream channel name
    """

    source_type: str  # "entry_point" or "module_output"
    # For entry_point:
    param_group: str | None = None
    qualified_name: str | None = None
    # For module_output:
    producer_channel: str | None = None


class ConstraintFormalIdentity(BaseModel):
    """Source identity retained only for generated-constraint name validation."""

    model_config = ConfigDict(frozen=True)

    raw_name: str
    qualified_name: str | None = None


class ModuleInput(BaseModel):
    """An input to a pipeline module.

    Attributes:
        param_name: Parameter name (e.g., "p_fusion")
        python_type: Python type string (e.g., "float")
        source: Where the input value comes from
        description: Human-readable description from CalcDef input attribute
        default_value: Default value from CalcDef input attribute
    """

    param_name: str
    python_type: str
    source: InputSource
    description: str | None = None
    default_value: float | int | str | bool | None = None
    formal_identity: ConstraintFormalIdentity | None = Field(default=None, exclude=True)


class ModuleOutput(BaseModel):
    """An output from a pipeline module.

    Attributes:
        field_name: Field name ("root" for single-output, attr name for multi)
        python_type: Python type string (e.g., "float")
        channel_name: Channel name for wiring (e.g., "alphaneutronsplit_p_neutron")
        description: Human-readable description from CalcDef output attribute
        default_value: Default value from CalcDef output attribute
        unit: Physical unit from CalcDef output attribute
    """

    field_name: str
    python_type: str
    channel_name: str
    description: str | None = None
    default_value: float | int | str | bool | None = None
    unit: str | None = None


class ModuleKind(str, Enum):
    """Kind of a pipeline module — set once at construction, dispatched on at every
    generation seam. Replaces the two accreted Boolean flags PipelineModule carried
    before Item 6."""

    CALCULATION = "calculation"
    FORMULA = "formula"
    AGGREGATION = "aggregation"
    CONSTRAINT = "constraint"
    REPORT_AGGREGATOR = "report_aggregator"


class PipelineModule(BaseModel):
    """A module in the pipeline configuration.

    Represents a calculation usage that will be executed as part of the pipeline.

    Attributes:
        name: Module instance name (lowercase, e.g., "alphaneutronsplit")
        module_type: Module class name (e.g., "AlphaNeutronSplitModule")
        inputs: List of module inputs
        outputs: List of module outputs
        execution_order: Position in topological order
    """

    name: str
    module_type: str
    inputs: list[ModuleInput]
    outputs: list[ModuleOutput]
    execution_order: int
    compilability: Compilability = Compilability.UNKNOWN
    compiled_expression: str | None = None
    module_kind: ModuleKind
    output_schema_type: str | None = None
    auto_impl_context: dict | None = None
    # Metadata from CalcDef / ComputedAttributeData / AggregationExpressionData
    calc_def_name: str | None = None
    calc_def_qualified_name: str | None = None
    doc_comment: str | None = None
    calc_expressions: list[str] | None = None
    source_file: str | None = None
    source_line: int | None = None


class OutputAlias(BaseModel):
    """A modeler's EXPOSE_PURE name surfaced onto a canonical output channel.

    Item 11 (SC-7). The two EXPOSE_PURE shapes both land here, tagged by
    provenance:
    - ``part_def`` (shape A): from the ``_scoped_alias`` registry (a part-def
      derived attribute, e.g. ``total_cost = cost_calc.cost``, expanded per
      instance).
    - ``part_usage`` (shape B): from an ``expose_pure`` ``ChannelAlias`` (a
      derived attribute on a part usage).

    Attributes:
        alias_name: The modeler's sanitized ``python_name`` (Item 5 / REQ-NC-06).
        canonical_channel: The channel the value already flows on (INV-2), read
            from the registry — never re-derived.
        instance_path: The instance scope that qualifies the name so two
            siblings exposing the same name land on distinct output filenames
            (INV-4): the scope half of a ``_scoped_alias`` key (shape A) or the
            owning part's leaf (shape B).
        shape: Which source produced the entry.
    """

    alias_name: str
    canonical_channel: str
    instance_path: str
    shape: Literal["part_def", "part_usage"]

    @property
    def output_filename(self) -> str:
        """Destination filename for this alias's exit-point capture (D2).

        ``{instance_path}__{alias_name}.json`` — instance-qualified so two
        instances exposing the same name never collide (INV-4).
        """
        return f"{self.instance_path}__{self.alias_name}.json"


class ConstraintInputResolution(str, Enum):
    """How one concrete constraint's formal was resolved (Item 5 / D1 terminal switch)."""

    MODULE_OUTPUT = "module_output"
    DESIGN_ATTRIBUTE = "design_attribute"
    MODELED_DEFAULT = "modeled_default"


class ConcreteConstraintInput(BaseModel):
    """One resolved formal on a :class:`ConcreteConstraint` (Item 5 / D4).

    Only the resolution-tagged field matching ``resolution`` is populated
    (enforced by a model validator):
    - ``module_output``: ``bound_channel`` carries the producer channel the
      strict resolver actually bound — the occurrence-scoped key when it hit,
      else the shared de-indexed channel (B1-settled; recorded, never hidden,
      per INV-3). Required.
    - ``design_attribute``: ``design_attribute_qn`` carries the minted entry
      point's real qualified name (F4-safe, QN-deduped per INV-5). Required.
    - ``modeled_default``: ``default_ir`` carries the formal's own default,
      serialized the same way as ``predicate_ir`` (D5-IR). May be ``None``
      when the formal has no recorded default — graph extension then mints a
      defaultless ``LIBRARY_DEFAULT`` entry point the user must supply
      (pinned by ``test_phase4_bugfix_regressions``).
    """

    formal_name: str
    resolution: ConstraintInputResolution
    bound_channel: str | None = None
    design_attribute_qn: str | None = None
    default_ir: str | None = None
    formal_identity: ConstraintFormalIdentity | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def _resolution_field_matches_tag(self) -> "ConcreteConstraintInput":
        required_by_tag: dict[ConstraintInputResolution, str | None] = {
            ConstraintInputResolution.MODULE_OUTPUT: "bound_channel",
            ConstraintInputResolution.DESIGN_ATTRIBUTE: "design_attribute_qn",
            ConstraintInputResolution.MODELED_DEFAULT: None,  # default_ir may be absent
        }
        tag_field = required_by_tag[self.resolution]
        allowed = tag_field if tag_field is not None else "default_ir"
        for field in ("bound_channel", "design_attribute_qn", "default_ir"):
            if field != allowed and getattr(self, field) is not None:
                raise ValueError(
                    f"resolution={self.resolution.value!r} must not populate {field!r}"
                )
        if tag_field is not None and getattr(self, tag_field) is None:
            raise ValueError(f"resolution={self.resolution.value!r} requires {tag_field!r}")
        return self


class ConstraintExclusion(BaseModel):
    """Why one concrete source usage is intentionally not executable."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["non_numerical", "unassessed_form", "unsupported_owner"]
    reasons: list[str] = Field(default_factory=list)
    location: str


class ConcreteConstraint(_TransactionalAssignmentModel):
    """One concrete, expanded assertion (Item 5 / D4, D5-IR, D7).

    Attributes:
        constraint_id: Deterministic execution identity (D3/N1); catalog
            ordering is by this field (INV-4).
        usage_qualified_name: The source ``ConstraintUsageFact``'s qualified
            name (identity, not per-occurrence).
        source_local_identity: The usage's simple name when named, else its
            ``LocationFact`` rendering — the anonymous-assertion identity
            (spec `[HARD]`).
        source_form: ``ConstraintSource.form`` (``inline`` / ``definition_typed``
            / other out-of-profile forms).
        owner_kind: ``OwningDefinitionFact.kind`` (``part_def`` / ``calc_def`` /
            ``package`` / ``requirement_def``).
        owner_qualified_name: The resolved owning definition's qualified name.
        owner_instance_path: This concrete instance's own identity — an
            :class:`~sysml_codegen.analysis.part_instance_index.InstanceOccurrence`
            path for ``part_def`` owners, the calc-usage/package-usage
            qualified name otherwise.
        membership_kind: ``assert`` (nullable-guarded upstream, INV-8).
        is_negated: Polarity (nullable-guarded upstream, INV-8).
        expected_value: Derived from ``is_negated`` (``not is_negated``).
        predicate_ir: The *effective* predicate (selected per source-form),
            serialized via ``serialize_expression`` (D5-IR) — a plain string,
            no ``arbitrary_types_allowed``. ``None`` for an unassessed record.
        inputs: Resolved formals, ordered as extracted.
        evaluation_channel: This instance's own output channel (INV-3).
            ``None`` for an unassessed record (D7) — no executable node.
        eligible: ``False`` for a defensively cataloged unassessed record
            (``requirement_def`` / out-of-profile source form, D7); ``True``
            for a normally lowered, executable assertion.
        tracking_key: Optional author-controlled correlation key (D8); never
            part of ``constraint_id``.
    """

    model_config = ConfigDict(validate_assignment=True)

    constraint_id: str
    usage_qualified_name: str
    source_local_identity: str
    source_form: str
    owner_kind: str
    owner_qualified_name: str
    owner_instance_path: str
    membership_kind: str | None
    predicate_source_key: str
    is_negated: bool | None
    expected_value: bool | None
    predicate_ir: str | None = None
    inputs: list[ConcreteConstraintInput] = Field(default_factory=list)
    evaluation_channel: str | None = None
    eligible: bool = True
    exclusion: ConstraintExclusion | None = None
    tracking_key: str | None = None

    @model_validator(mode="after")
    def _eligibility_matches_executable_payload(self) -> "ConcreteConstraint":
        if self.eligible:
            if self.exclusion is not None:
                raise ValueError(
                    f"eligible constraint {self.constraint_id!r} must not carry exclusion"
                )
            if self.is_negated is None:
                raise ValueError(
                    f"eligible constraint {self.constraint_id!r} has no known polarity"
                )
            if self.predicate_source_key is None:
                raise ValueError(
                    f"eligible constraint {self.constraint_id!r} has no predicate_source_key"
                )
            if self.predicate_ir is None:
                raise ValueError(
                    f"eligible constraint {self.constraint_id!r} has no predicate_ir "
                    "(profile ADMIT guarantees an effective predicate)"
                )
            if self.evaluation_channel is None:
                raise ValueError(
                    f"eligible constraint {self.constraint_id!r} has no evaluation_channel"
                )
        else:
            payload_fields = []
            if self.predicate_ir is not None:
                payload_fields.append("predicate_ir")
            if self.inputs:
                payload_fields.append("inputs")
            if self.evaluation_channel is not None:
                payload_fields.append("evaluation_channel")
            if self.expected_value is not None:
                payload_fields.append("expected_value")
            if payload_fields:
                raise ValueError(
                    f"unassessed constraint {self.constraint_id!r} has executable payload: "
                    + ", ".join(payload_fields)
                )
            if self.exclusion is None:
                raise ValueError(f"ineligible constraint {self.constraint_id!r} requires exclusion")
        return self

    @model_validator(mode="after")
    def _expected_value_derives_from_polarity(self) -> "ConcreteConstraint":
        if not self.eligible:
            return self
        if self.is_negated is None:  # guarded by the eligibility validator
            raise ValueError(f"eligible constraint {self.constraint_id!r} has no known polarity")
        derived = not self.is_negated
        if self.expected_value != derived:
            raise ValueError(
                f"constraint {self.constraint_id!r}: expected_value={self.expected_value!r} "
                f"does not derive from is_negated={self.is_negated!r}"
            )
        return self


class ConstraintCatalogSourceRecord(BaseModel):
    """One reusable ``constraint def``'s identity and formals (Item 7 / D6).

    Assembled from ``ctx.constraint_facts.definitions`` — the source-level vocabulary a
    concrete entry's ``predicate_ir`` was compiled from. Carries no predicate IR itself
    (each concrete entry already carries its own effective ``predicate_ir``); this is the
    handoff-level record of what definitions exist, for Item 8/9 consumers.
    """

    definition_qualified_name: str
    formal_names: list[str] = Field(default_factory=list)


class ConstraintCatalogEntry(_TransactionalAssignmentModel):
    """One concrete, eligible assertion's catalog record (Item 7 / D6).

    A thin, catalog-shaped projection of :class:`ConcreteConstraint` — every field a
    generation seam or a same-IR guard reads, nothing else. ``predicate_ir`` is carried on
    every entry (not just the source record) so the same-IR guard's arm (b) (byte-agreement
    across entries sharing one definition) can run at the catalog level (INV-2).
    """

    model_config = ConfigDict(validate_assignment=True)

    constraint_id: str
    usage_qualified_name: str
    owner_instance_path: str
    membership_kind: str | None
    predicate_source_key: str
    is_negated: bool
    expected_value: bool
    predicate_ir: str
    evaluation_channel: str

    @model_validator(mode="after")
    def _expected_value_derives_from_polarity(self) -> "ConstraintCatalogEntry":
        if self.expected_value != (not self.is_negated):
            raise ValueError(
                f"catalog constraint {self.constraint_id!r}: "
                f"expected_value={self.expected_value!r} does not derive from "
                f"is_negated={self.is_negated!r}"
            )
        return self


class ConstraintCatalogExcludedRecord(BaseModel):
    """Catalog projection of one validated non-executed concrete record."""

    constraint_id: str
    usage_qualified_name: str
    source_form: str
    membership_kind: str | None
    exclusion: ConstraintExclusion


class ConstraintCatalog(BaseModel):
    """The full constraint catalog embedded on :class:`ComputationGraph` (Item 7 / D6).

    Assembled once from ``ctx.concrete_constraints`` (eligible entries) and
    ``ctx.constraint_facts`` (source records), fingerprinted once (sha256 of canonical JSON
    over ``source_records`` + ``concrete_entries`` + ``excluded_records``), and set on the graph
    before generation —
    every seam that needs catalog data reads it from here, never from ``ctx`` (Appendix A/D6:
    "generation reads only the graph").
    """

    source_records: list[ConstraintCatalogSourceRecord] = Field(default_factory=list)
    concrete_entries: list[ConstraintCatalogEntry] = Field(default_factory=list)
    excluded_records: list[ConstraintCatalogExcludedRecord] = Field(default_factory=list)
    fingerprint: str


class ComputationGraph(BaseModel):
    """The complete computation graph derived from BacktrackingResult.

    This is the SINGLE SOURCE OF TRUTH for pipeline generation.
    All downstream generation (YAML, schemas, JSON) derives from this.

    Attributes:
        modules: All pipeline modules in execution order
        entry_point_groups: Entry points grouped by source file
        execution_order: Module names in topological order
        fallback_entry_points: QNs of Step-4 fall-through entry points — bound
            bindings that matched no resolution strategy and no design attribute
            (Item 7 / D4). Carried onto the graph so ``collect_uncovered_params``
            is pure over the graph alone. In-memory analysis artifact consumed at
            the generation boundary; ``exclude=True`` keeps it out of the
            serialized graph so committed baselines do not churn.
        output_aliases: EXPOSE_PURE modeler names surfaced onto their canonical
            output channels (Item 11 / SC-7), stable-sorted by
            ``(instance_path, alias_name)``. A genuine schema field describing
            real generated output — **not** excluded (contrast
            ``fallback_entry_points``): it is serialized on every graph and
            drives the named exit-point captures in the pipeline YAML.
        constraint_catalog: The assembled :class:`ConstraintCatalog` (CONSTRAINT-EXEC
            Item 7 / D6), ``None`` when no constraint facts admitted (INV-7).
            In-memory generation-boundary artifact like ``fallback_entry_points`` —
            ``exclude=True`` keeps a constraint-free corpus's committed JSON baselines
            byte-identical; carrying catalog data into the persisted snapshot is
            Item 8's scope, not this field's.
    """

    modules: list[PipelineModule]
    entry_point_groups: list[ParameterGroup]
    execution_order: list[str]
    fallback_entry_points: set[str] = Field(default_factory=set, exclude=True)
    output_aliases: list[OutputAlias] = Field(default_factory=list)
    constraint_catalog: ConstraintCatalog | None = Field(default=None, exclude=True)


__all__ = [
    "BindingResolution",
    "BindingResolutionType",
    "ComputationGraph",
    "ConcreteConstraint",
    "ConcreteConstraintInput",
    "ConstraintCatalog",
    "ConstraintCatalogEntry",
    "ConstraintCatalogExcludedRecord",
    "ConstraintCatalogSourceRecord",
    "ConstraintExclusion",
    "ConstraintInputResolution",
    "EntryPoint",
    "EntryPointType",
    "InputSource",
    "ModuleInput",
    "ModuleKind",
    "ModuleOutput",
    "OutputAlias",
    "ParameterGroup",
    "PipelineModule",
]
