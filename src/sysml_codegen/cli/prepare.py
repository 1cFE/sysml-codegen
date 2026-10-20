"""The read-only half of ``generate``: everything before the first write (Item 2b D1).

The template environment, the path helpers both halves use, and the preflights that refuse a
model before anything under the destination is cleared, created or written. Nothing here
takes a destination; ``cli/emit.py`` may import from this module, never the reverse.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from sysml_codegen.core.identifier_types import PythonModulePath
    from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConstraintCatalogEntry,
        ConstraintCatalogExcludedRecord,
        ConstraintCatalogUsageRecord,
        PipelineModule,
    )


def _get_template_env() -> jinja2.Environment:
    """Set up Jinja2 environment with package templates."""
    # Use __file__ to find templates relative to package
    template_dir = Path(__file__).parent.parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _get_python_path(module: PipelineModule) -> PythonModulePath:
    """Get PythonModulePath from PipelineModule (all module types)."""
    from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
        # module_type is already a Python-dotted path (D9 naming), not a SysML "::"
        # qualified name — derive directly rather than routing through from_sysml.
        # D9: "file stem lowercased" — the whole final segment, lowercased as-is.
        parts = module.module_type.split(".")
        return PythonModulePath(directory="/".join(parts[:-1]), filename=parts[-1].lower())
    if module.module_kind == ModuleKind.FORMULA:
        sysml_qn = f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.module_kind == ModuleKind.AGGREGATION:
        sysml_qn = module.name.replace("__", "::")
    elif module.module_kind == ModuleKind.CALCULATION:
        assert module.calc_def_qualified_name is not None
        sysml_qn = module.calc_def_qualified_name
    else:
        raise unrenderable_module_kind_error(module, "python-path")
    sqn = SysMLQualifiedName(sysml_qn)
    return PythonModulePath.from_sysml(sqn)


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
      `{filename}_impl.py` from the same _get_python_path output), so one path
      check covers both.
    - Schemas are keyed on `calc_def_name.lower()` (only multi-output modules
      reach the schema pass), a *different* key space: two calc defs whose names
      lower to one identifier collide on `x_output.py` even when module paths
      differ.

    Only a collision between *different* raw sources is an error -- multiple
    usages of one calc def legitimately derive the same path.
    """
    from sysml_codegen.core.errors import GenerationCode
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.generation import CodeGenerationError

    module_paths: dict[str, str] = {}
    for module in modules:
        path = _get_python_path(module).full_path
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
            ModuleKind.CALCULATION, ModuleKind.FORMULA, ModuleKind.AGGREGATION
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
    from sysml_codegen.generation.registry import residual_class_name_collisions

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

