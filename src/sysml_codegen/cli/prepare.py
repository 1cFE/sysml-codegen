"""The read-only half of ``generate``: everything before the first write (Item 2b D1).

``load_source`` opens the model source once; ``prepare`` constructs the computation graph from
it and runs the preflights that refuse a model before anything under the destination is
cleared, created or written. Each refusal comes back as a ``Refused`` value carrying the record
``generate`` logs for it, and ``log_refused`` logs that record. Nothing here takes a
destination; ``cli/emit.py`` may import from this module, never the reverse.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

from sysml_codegen.cli.refusal import (
    Refusal,
    RefusalKind,
    diagnostic_refusal,
    generation_refusal,
    readiness_refusal,
)

if TYPE_CHECKING:
    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation
    from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan
    from sysml_codegen.orchestration.elaborated_pipeline import FailedLoad, LiveLoad
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConstraintCatalogEntry,
        ConstraintCatalogExcludedRecord,
        ConstraintCatalogUsageRecord,
        PipelineModule,
    )

#: The CLI's logger, so a record keeps the name it had before the route was split.
logger = logging.getLogger("sysml_codegen.cli")


@dataclass(frozen=True)
class LiveModels:
    """Model files to load with SysIDE."""

    paths: tuple[Path, ...]


@dataclass(frozen=True)
class SnapshotFile:
    """A sealed v6 instance-graph snapshot. Loading it needs no SysIDE."""

    path: Path


type ModelSource = LiveModels | SnapshotFile
#: What ``load_source`` returns: a live load, a live load that failed, or the snapshot.
type LoadedSource = LiveLoad | FailedLoad | SnapshotFile


def load_source(source: ModelSource) -> LoadedSource:
    """Open the model source once. Never raises: a failed live load is a ``FailedLoad``."""
    from sysml_codegen.orchestration import elaborated_pipeline

    if isinstance(source, SnapshotFile):
        return source
    return elaborated_pipeline.load_live_models(source.paths)


class PreparationStep(Enum):
    """The steps of the generator's route, in the order they run.

    ``prepare`` runs construction through the parameter-field check. ``emit_package`` runs the
    destination check, then writes.
    """

    CONSTRUCTION = auto()
    GENERATION_METADATA = auto()
    EXIT_POINT_TYPES = auto()
    CONSTRAINT_NAMES = auto()
    OUTPUT_PATHS = auto()
    REGISTRY_CLASS_NAMES = auto()
    CONSTRAINT_TOTALITY = auto()
    CONSTRAINT_PLAN = auto()
    COVERAGE_ACCOUNT = auto()
    PARAMETER_FIELD_NAMES = auto()
    DESTINATION = auto()
    EMIT = auto()


@dataclass(frozen=True)
class Prepared:
    """A model the generator's route builds, ready for ``emit_package``."""

    graph: ComputationGraph
    template_env: jinja2.Environment
    constraint_plan: ConstraintGenerationPlan
    package_name: str


@dataclass(frozen=True)
class Refused:
    """A refusal, the step that refused, and the record ``generate`` logs for it."""

    step: PreparationStep
    refusal: Refusal
    message: str
    #: Set exactly when ``refusal.kind`` is ``GENERATION``; may itself be ``None``.
    constraint_name_safety: ConstraintNameViolation | None = None


def log_refused(refused: Refused) -> None:
    """Log the one refusal record for a refused run, as ``generate`` has always logged it."""
    extra: dict[str, object] = {"refusal": refused.refusal}
    if refused.refusal.kind is RefusalKind.GENERATION:
        extra["constraint_name_safety"] = refused.constraint_name_safety
    logger.error(refused.message, extra=extra)


def log_generator_answer(generator: Prepared | Refused) -> None:
    """The generator's answer: a refusal's one record, or that the model builds.

    ``generate`` prints it before it writes (design D16); ``check`` prints it instead of writing.
    """
    if isinstance(generator, Refused):
        log_refused(generator)
    else:
        logger.info(f"Generator: builds ({len(generator.graph.modules)} modules)")


def refused_at_construction(error: Exception) -> Refused:
    """Convert a failure to load, elaborate or project into its refusal.

    The two elaboration refusal classes stay distinct the way the corpus driver keeps them
    distinct: readiness findings and validation diagnostics are different answers, and
    collapsing them loses which gate refused. A failure nobody classified becomes the
    internal-defect diagnostic.
    """
    from sysml_codegen.elaboration.elaborate import (
        ElaborationDiagnosticError,
        ElaborationError,
        unexpected_public_failure,
    )
    from sysml_codegen.generation import CodeGenerationError, SysMLParsingError
    from sysml_codegen.snapshot.envelope import InstanceGraphSnapshotError

    step = PreparationStep.CONSTRUCTION
    if isinstance(error, InstanceGraphSnapshotError):
        return Refused(step, Refusal(RefusalKind.SNAPSHOT), f"Snapshot refused: {error}")
    if isinstance(error, ElaborationError):
        return Refused(
            step,
            readiness_refusal(error),
            f"Model is not ready for the exact route: {error}",
        )
    if isinstance(error, ElaborationDiagnosticError):
        return Refused(
            step, diagnostic_refusal(error), f"Model failed exact-route validation: {error}"
        )
    if isinstance(error, SysMLParsingError):
        return Refused(step, Refusal(RefusalKind.PARSING), f"SysML parsing failed: {error}")
    if isinstance(error, CodeGenerationError):
        return _generation_refused(step, error)
    diagnostic = unexpected_public_failure(error)
    return Refused(
        step,
        diagnostic_refusal(diagnostic),
        f"Model failed exact-route validation: {diagnostic}",
    )


def refused_at_generation(step: PreparationStep, error: Exception) -> Refused:
    """Convert a failure after construction into its refusal.

    A refusal generation already formed keeps its own code and vocabulary. The only unnamed
    failure the writing steps can operationally hit is the filesystem; any other failure
    nobody classified becomes the internal-defect diagnostic.
    """
    from sysml_codegen.elaboration.elaborate import unexpected_public_failure
    from sysml_codegen.generation import CodeGenerationError, SysMLParsingError

    if isinstance(error, SysMLParsingError):
        return Refused(step, Refusal(RefusalKind.PARSING), f"SysML parsing failed: {error}")
    if isinstance(error, CodeGenerationError):
        return _generation_refused(step, error)
    if isinstance(error, OSError):
        return Refused(
            step,
            Refusal(RefusalKind.PACKAGE_WRITE),
            f"Writing the generated package failed: {error}",
        )
    diagnostic = unexpected_public_failure(error)
    return Refused(step, diagnostic_refusal(diagnostic), f"Code generation failed: {diagnostic}")


def _generation_refused(step: PreparationStep, error: CodeGenerationError) -> Refused:
    return Refused(
        step,
        generation_refusal(error),
        f"Code generation failed: {error}",
        error.name_safety_violation,
    )


def prepare(loaded: LoadedSource, package_name: str) -> Prepared | Refused:
    """Run the generator's route up to, not including, the first write.

    One read, one projection: every later step works from the graph read here, so a package
    is never assembled out of several separately derived graphs.
    """
    from sysml_codegen.orchestration import exact_pipeline_context
    from sysml_codegen.orchestration.elaborated_pipeline import FailedLoad

    if isinstance(loaded, FailedLoad):
        return refused_at_construction(loaded.error)
    try:
        if isinstance(loaded, SnapshotFile):
            context = exact_pipeline_context.build_exact_pipeline_context_from_snapshot(loaded.path)
        else:
            context = exact_pipeline_context.build_exact_pipeline_context_from_live_load(loaded)
        graph = context.computation_graph
    except Exception as error:
        return refused_at_construction(error)

    logger.info(f"Built computation graph with {len(graph.modules)} modules")
    return prepare_graph(graph, package_name)


def prepare_graph(graph: ComputationGraph, package_name: str) -> Prepared | Refused:
    """Run every check after construction, in order, on a constructed graph.

    Each one refuses before the destination is inspected, cleared, created or written.
    """
    from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan
    from sysml_codegen.generation.entry_point import refuse_param_field_collisions
    from sysml_codegen.generation.registry import class_owners

    step = PreparationStep.GENERATION_METADATA
    try:
        # Unsupported root-output wrappers are a public model refusal. Registry collection
        # shares the same total validator.
        _preflight_generation_metadata(graph)
        step = PreparationStep.EXIT_POINT_TYPES
        _preflight_exit_point_types(graph)

        # Both generated constraint scopes.
        step = PreparationStep.CONSTRAINT_NAMES
        _preflight_constraint_names(graph)

        # A sanitize-collision, so a duplicate path never wipes or silently overwrites
        # existing files.
        step = PreparationStep.OUTPUT_PATHS
        _check_duplicate_output_paths(class_owners(graph.modules))

        # Registry class-name collisions the aliasing cannot resolve. The check itself lives
        # at the registry pass, which runs after the tree is cleared; running it here is what
        # makes the refusal fail-before-mutate.
        step = PreparationStep.REGISTRY_CLASS_NAMES
        _preflight_registry_class_names(graph)

        # The constraint catalog accounts for every authored usage, and every occurrence row
        # joins one of them by identity: a package that shipped a catalog missing a carrier
        # would claim coverage it does not have.
        step = PreparationStep.CONSTRAINT_TOTALITY
        _preflight_constraint_totality(graph)

        # Every constraint body and wrapper, rendered in memory.
        step = PreparationStep.CONSTRAINT_PLAN
        template_env = _get_template_env()
        constraint_plan = build_constraint_generation_plan(graph, template_env, package_name)

        # The coverage account the package is about to bake agrees with the catalog it claims
        # to summarize, and the aggregator's existence agrees with the same population.
        step = PreparationStep.COVERAGE_ACCOUNT
        _preflight_coverage_account(graph, constraint_plan)

        # Two parameter keys that render as one schema field. Last, so every check that ran
        # before it at the base still reports first for a model with several faults.
        step = PreparationStep.PARAMETER_FIELD_NAMES
        refuse_param_field_collisions(graph.entry_point_groups)
    except Exception as error:
        return refused_at_generation(step, error)
    return Prepared(graph, template_env, constraint_plan, package_name)


def _get_template_env() -> jinja2.Environment:
    """Set up Jinja2 environment with package templates."""
    # Use __file__ to find templates relative to package
    template_dir = Path(__file__).parent.parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _raw_source_name(module: PipelineModule) -> str:
    """Raw SysML spelling of a module, for duplicate-path provenance.

    After sanitize the colliding modules share a derived identifier, so the
    error must recover each raw name. For a FORMULA module that is the owner QN
    plus the raw attribute name; for a calc-usage module the raw calc-def QN.
    Both are raw (never sanitized) on every module type that can collide.
    """
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind == ModuleKind.FORMULA:
        return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    if module.module_kind in (ModuleKind.AGGREGATION, ModuleKind.CALCULATION):
        return module.calc_def_qualified_name or module.name
    if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
        return module.name
    raise unrenderable_module_kind_error(module, "raw-source-name")


def _module_source(module: PipelineModule) -> str:
    """Cite the module's authored source, or say plainly that none was recorded.

    The graph carries ``source_file``/``source_line`` only when elaboration read
    them off the model; this never substitutes a stand-in for the ones it did not.
    """
    if module.source_file is None or module.source_line is None:
        return ""
    return f" source='{module.source_file}:{module.source_line}'"


def _check_duplicate_output_paths(modules: list[PipelineModule]) -> None:
    """Fail fast when two distinct SysML names sanitize to one output file.

    Run BEFORE _clear_output_directory so a collision never wipes or silently
    overwrites existing output. Covers the two write key spaces a
    sanitize-collision spans (D2):

    - Modules + stencils share the derived python path (stencils are
      `{filename}_impl.py` from the same module_python_path output), so one path
      check covers both.
    - Schemas are keyed on `calc_def_name.lower()` (only multi-output modules
      reach the schema pass), a *different* key space: two calc defs whose names
      lower to one identifier collide on `x_output.py` even when module paths
      differ.

    Only a collision between *different* raw sources is an error -- multiple
    usages of one calc def legitimately derive the same path. The caller passes the
    modules whose files are written (``registry.class_owners``): the other copies of a
    formula or rollup class write no file of their own.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.generation.module_paths import module_python_path

    module_paths: dict[str, str] = {}
    for module in modules:
        path = module_python_path(module).full_path
        raw = _raw_source_name(module)
        prior = module_paths.get(path)
        if prior is not None and prior != raw:
            raise CodeGenerationError(
                f"DUPLICATE_OUTPUT_PATH: SysML names {prior!r} and {raw!r} both "
                f"derive modules/{path}. Rename one, or this would silently "
                f"overwrite.{_module_source(module)}",
                code=GenerationCode.DUPLICATE_OUTPUT_PATH,
                reason=SiteReason.GENERATION_MODULE_PATH_COLLISION,
            )
        module_paths[path] = raw

    schema_sources: dict[str, str] = {}
    for module in modules:
        if len(module.outputs) < 2 or not module.calc_def_name:
            continue
        schema_file = f"{module.calc_def_name.lower()}_output.py"
        raw = _raw_source_name(module)
        prior = schema_sources.get(schema_file)
        if prior is not None and prior != raw:
            raise CodeGenerationError(
                f"DUPLICATE_OUTPUT_PATH: SysML names {prior!r} and {raw!r} both "
                f"derive schemas/{schema_file}. Rename one, or this would silently "
                f"overwrite.{_module_source(module)}",
                code=GenerationCode.DUPLICATE_OUTPUT_PATH,
                reason=SiteReason.GENERATION_SCHEMA_PATH_COLLISION,
            )
        schema_sources[schema_file] = raw


def _preflight_generation_metadata(graph: ComputationGraph) -> None:
    """Validate renderer-required optional metadata before mutating output."""
    from sysml_codegen.core.errors import CodeGenerationError, GenerationCode
    from sysml_codegen.generation.pipeline import _input_to_context
    from sysml_codegen.resolution.models import ModuleKind

    for module in graph.modules:
        if module.module_kind in (
            ModuleKind.CALCULATION,
            ModuleKind.FORMULA,
            ModuleKind.AGGREGATION,
        ):
            if module.calc_def_name is None:
                raise CodeGenerationError(
                    f"GENERATION_METADATA_MISSING: module {module.name!r} lacks calc_def_name",
                    code=GenerationCode.GENERATION_METADATA_MISSING,
                )
        if module.module_kind in (ModuleKind.CALCULATION, ModuleKind.FORMULA):
            if module.calc_def_qualified_name is None:
                raise CodeGenerationError(
                    f"GENERATION_METADATA_MISSING: module {module.name!r} "
                    "lacks calc_def_qualified_name",
                    code=GenerationCode.GENERATION_METADATA_MISSING,
                )
        for module_input in module.inputs:
            _input_to_context(module_input, {})


def _preflight_registry_class_names(graph: ComputationGraph) -> None:
    """Refuse a graph whose registry class names collide beyond aliasing (REQ-REG-08).

    The check belonged to the registry pass alone, which runs after
    ``_clear_output_directory``: a model that trips it left a half-written
    package behind and reported "Unexpected error", because the raise was an
    untyped ``ValueError``. Running the same pure detector here — beside
    ``_check_duplicate_output_paths``, before
    anything is written — is what makes it fail-before-mutate, and the error is
    the package's own so the operator reads a refusal rather than a traceback.
    """
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.generation.errors import residual_class_name_collision_error
    from sysml_codegen.generation.registry import (
        require_one_class_per_module_type,
        residual_class_name_collisions,
    )

    # Projection settled one class body per computed module type; a breach is the
    # generator's defect, raised plainly so it is reported as one (design D7).
    require_one_class_per_module_type(graph.modules)
    residual = residual_class_name_collisions(graph)
    if residual:
        raise residual_class_name_collision_error(
            residual, reason=SiteReason.GENERATION_REGISTRY_CLASS_NAME_COLLISION
        )


def _preflight_exit_point_types(graph: ComputationGraph) -> None:
    """Refuse an unsupported root-output wrapper before touching the output tree."""
    from sysml_codegen.generation.registry import required_exit_point_wrapper_types

    required_exit_point_wrapper_types(graph)


def _preflight_constraint_totality(graph: ComputationGraph) -> None:
    """Refuse a catalog whose usage rows and occurrence rows do not account for each other.

    The domain is complete by construction upstream — that is where the records are born —
    and ``InstanceGraph.validate()`` already gates the domain against the occurrence nodes
    on every route. What this owns is the *catalog* end of the same join, at the
    fail-before-mutate boundary, because the catalog is what ships: a package whose
    catalog lost a carrier would claim coverage it does not have, and nothing downstream
    would notice.

    It joins by ``declaration_id`` only, never by qualified name, and it refuses rather
    than repairs.

    **Two kinds of check, and the second is why removal of a non-reaching row is caught.**
    The joins below are catalog-internal: they compare the row lists against each other,
    which catches a duplicate, an orphaned occurrence row, and a disagreeing count. They
    cannot catch a *removed* row whose ``occurrence_count`` is zero, because such a row has
    no occurrence to orphan and no count to contradict — its removal leaves the catalog
    perfectly self-consistent. That is 56 of ``catf_mfe_d5``'s 65 members, which is the
    whole population this item exists to make visible. The seal check is the guard for
    those: ``fingerprint`` was minted at projection from the domain, so it still knows the
    removed row existed.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.elaboration.graph import DISPOSITION_REASONS
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.resolution.models import ModuleKind

    catalog = graph.constraint_catalog
    if catalog is None:
        if any(module.module_kind is ModuleKind.CONSTRAINT for module in graph.modules):
            raise CodeGenerationError(
                "CONSTRAINT_DOMAIN_INCOMPLETE: the graph generates constraint modules "
                "but carries no catalog",
                code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
            )
        return

    if catalog.recomputed_fingerprint() != catalog.fingerprint:
        raise CodeGenerationError(
            "CONSTRAINT_DOMAIN_INCOMPLETE: the catalog's "
            f"{len(catalog.usage_records)} usage rows no longer match the fingerprint "
            "sealed at projection, so a row was added, removed, or altered after the "
            "domain was rendered",
            code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
        )

    rows_by_id: dict[str, ConstraintCatalogUsageRecord] = {}
    for row in catalog.usage_records:
        if row.declaration_id in rows_by_id:
            raise CodeGenerationError(
                "CONSTRAINT_DOMAIN_INCOMPLETE: duplicate usage record for "
                f"{row.usage_qualified_name} ({row.declaration_id})",
                code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
            )
        reasons = DISPOSITION_REASONS.get(row.disposition_kind)
        if reasons is None or row.disposition_reason not in reasons:
            raise CodeGenerationError(
                "CONSTRAINT_DOMAIN_INCOMPLETE: no disposition for "
                f"{row.usage_qualified_name} ({row.declaration_id})",
                code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
            )
        rows_by_id[row.declaration_id] = row

    occurrence_rows: list[ConstraintCatalogEntry | ConstraintCatalogExcludedRecord] = [
        *catalog.concrete_entries,
        *catalog.excluded_records,
    ]
    occurrences: dict[str, int] = {}
    for occurrence in occurrence_rows:
        if occurrence.declaration_id not in rows_by_id:
            raise CodeGenerationError(
                "CONSTRAINT_DOMAIN_INCOMPLETE: catalog row joins no domain member for "
                f"{occurrence.usage_qualified_name} ({occurrence.declaration_id})",
                code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
            )
        occurrences[occurrence.declaration_id] = occurrences.get(occurrence.declaration_id, 0) + 1

    for declaration_id, row in rows_by_id.items():
        counted = occurrences.get(declaration_id, 0)
        if row.occurrence_count != counted:
            raise CodeGenerationError(
                f"CONSTRAINT_DOMAIN_INCOMPLETE: occurrence_count {row.occurrence_count} "
                f"disagrees with {counted} nodes for {row.usage_qualified_name} "
                f"({declaration_id})",
                code=GenerationCode.CONSTRAINT_DOMAIN_INCOMPLETE,
            )


def _preflight_coverage_account(
    graph: ComputationGraph, constraint_plan: ConstraintGenerationPlan
) -> None:
    """Refuse a coverage account that disagrees with the catalog it summarizes (Item 3 / D3).

    Four refusals, one function: they share the catalog read and the same failure class, and
    each carries its own message because each has its own cure.

    1. **Recomputation.** The account is derived once, at plan build, and rendered into the
       aggregator as baked constants. Recomputing it here from the graph's catalog and
       comparing is what makes "the numbers in the package describe this package's catalog" a
       check rather than a convention (invariant 5).
    2. **Aggregator iff usage rows.** D5's rule is read in two places — the instance graph's
       ``constraint_usages`` when the module is minted, the catalog's ``usage_records`` at the
       three generation seams. Two readings of one rule is the drift Item 2's A4 cure exists to
       stop, so the disagreement is refused by name in both directions.
    3. **The reason vocabulary** and 4. **D9's contradiction** raise from inside
       :func:`coverage_account`, which the recomputation calls. They fire at plan build too —
       earlier still — and are re-asserted here so this function is total over the four.

    Runs after the plan is built and before ``_clear_output_directory``, so it is
    fail-before-mutate. The only thing between the earlier preflight block and this call is
    ``ensure_package_tree_is_link_free``, which inspects and raises and writes nothing.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.generation.coverage import coverage_account
    from sysml_codegen.resolution.models import ModuleKind, ships_constraint_machinery

    catalog = graph.constraint_catalog
    has_aggregator = any(
        module.module_kind is ModuleKind.REPORT_AGGREGATOR for module in graph.modules
    )

    if catalog is None:
        if has_aggregator:
            raise CodeGenerationError(
                "COVERAGE_ACCOUNT_INVALID: the graph carries a REPORT_AGGREGATOR "
                "module but no constraint catalog, so the report it would ship could not "
                "state its coverage",
                code=GenerationCode.COVERAGE_ACCOUNT_INVALID,
            )
        return

    if has_aggregator != ships_constraint_machinery(graph):
        expected = "a REPORT_AGGREGATOR module" if not has_aggregator else "no aggregator"
        raise CodeGenerationError(
            "COVERAGE_ACCOUNT_INVALID: the account disagrees with the report-required rule: "
            "the catalog has "
            f"{len(catalog.usage_records)} usage row(s), which requires {expected}. "
            "A report is required iff the model authored at least one constraint usage; the "
            "aggregator mint and the generation seams must read that one population.",
            code=GenerationCode.COVERAGE_ACCOUNT_INVALID,
        )

    recomputed = coverage_account(catalog)
    if constraint_plan.coverage != recomputed:
        raise CodeGenerationError(
            "COVERAGE_ACCOUNT_INVALID: the account disagrees with its catalog: the plan holds "
            f"{constraint_plan.coverage}, and the sealed catalog implies {recomputed}. The "
            "account is a summary of that catalog and nothing else, so it was altered after "
            "it was derived.",
            code=GenerationCode.COVERAGE_ACCOUNT_INVALID,
        )


def _preflight_constraint_names(graph: ComputationGraph) -> None:
    """Validate both generated constraint scopes before a graph-aware boundary acts."""
    from sysml_codegen.generation.errors import validate_constraint_graph_or_raise
    from sysml_codegen.resolution.models import ships_constraint_machinery

    validate_constraint_graph_or_raise(graph)
    if ships_constraint_machinery(graph):
        from sysml_codegen.generation.modules import assert_unique_predicate_function_names

        catalog = graph.constraint_catalog
        assert catalog is not None  # ships_constraint_machinery implies it; narrows the type
        assert_unique_predicate_function_names(catalog)
