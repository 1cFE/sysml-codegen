"""CLI entry point for sysml-codegen.

CRITICAL CHANGES:
- Parameterized all hardcoded values
- Removed CATF-specific references
- Package name is now a CLI argument
- Added install-commands subcommand for TEAx completion helper
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        ConstraintCatalogEntry,
        ConstraintCatalogExcludedRecord,
        ConstraintCatalogUsageRecord,
        PipelineModule,
    )

# Note: Heavy imports moved inside run_codegen to avoid loading generation
# module at CLI import time. This keeps CLI startup fast.

logger = logging.getLogger(__name__)


def _ensure_package_init_files(
    base_dir: Path, relative_path: str, docstring: str = '"""Namespace package."""\n'
) -> None:
    """Ensure __init__.py exists in all directories along relative_path."""
    parts = Path(relative_path).parts
    current = base_dir
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists():
            init_file.write_text(docstring)


# Commands available for installation
CODEGEN_COMMANDS = [
    "teax-completion.md",
]


def get_commands_dir() -> Path:
    """Get path to bundled commands directory.

    Path calculation:
    - __file__ = sysml-codegen/src/sysml_codegen/cli/__init__.py
    - parent.parent.parent.parent = sysml-codegen/
    - result = sysml-codegen/claude/commands/
    """
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "commands"


@dataclass
class GenerationConfig:
    """Configuration for code generation."""

    output_path: Path
    models_path: Path | None = None  # None when generating from a snapshot
    from_snapshot: Path | None = None  # snapshot to generate from (else live)
    package_name: str = "generated_code"  # Parameterized, was: fusion_simkit
    schema_class_name: str = "Params"  # Parameterized, was: FusionParams
    pipeline_name: str = "pipeline"  # Parameterized, was: catf_fusion
    overwrite: bool = False
    preserve_handwritten: bool = False
    smart_regen: bool = False


def _clear_output_directory(config: GenerationConfig) -> None:
    """Clear existing output directory before regeneration.

    Respects preserve_handwritten flag to keep handwritten/ directory intact.
    """
    if not config.output_path.exists():
        return

    for item in config.output_path.iterdir():
        # Skip handwritten directory if preserve flag is set
        if config.preserve_handwritten and item.name == "handwritten":
            logger.debug("Preserving handwritten/ directory")
            continue

        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    logger.debug(f"Cleared output directory: {config.output_path}")


def _setup_output_directories(config: GenerationConfig) -> None:
    """Create output directory structure."""
    dirs = [
        config.output_path,
        config.output_path / "schemas",
        config.output_path / "modules",
        config.output_path / "handwritten",
        config.output_path / "pipelines",
        config.output_path / "inputs",
        config.output_path / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Bug 7 broader scope: ensure all subdirectories are proper Python packages.
    # Excludes output_path itself — its __init__.py is generated later by _generate_registry().
    for d in dirs:
        init_file = d / "__init__.py"
        if d != config.output_path and not init_file.exists():
            init_file.write_text('"""Generated package."""\n')


def _generate_primitives(config: GenerationConfig) -> None:
    """Generate primitives.py with RootModel wrappers."""
    content = '''"""Pydantic RootModel wrappers for primitive types."""
from pydantic import RootModel

Float = RootModel[float]
Int = RootModel[int]
String = RootModel[str]
Bool = RootModel[bool]

__all__ = ["Float", "Int", "String", "Bool"]
'''
    output_path = config.output_path / "primitives.py"
    output_path.write_text(content)
    logger.debug(f"Generated primitives: {output_path}")


def _get_template_env() -> jinja2.Environment:
    """Set up Jinja2 environment with package templates."""
    # Use __file__ to find templates relative to package
    template_dir = Path(__file__).parent.parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _get_python_path(module):
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
    from sysml_codegen.generation import CodeGenerationError

    module_paths: dict[str, str] = {}
    for module in modules:
        path = _get_python_path(module).full_path
        raw = _raw_source_name(module)
        prior = module_paths.get(path)
        if prior is not None and prior != raw:
            raise CodeGenerationError(
                f"Duplicate output path: SysML names {prior!r} and {raw!r} both "
                f"derive modules/{path}. Rename one, or this would silently overwrite."
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
                f"Duplicate output path: SysML names {prior!r} and {raw!r} both "
                f"derive schemas/{schema_file}. Rename one, or this would silently "
                f"overwrite."
            )
        schema_sources[schema_file] = raw


def _reconcile_params_coverage(graph: ComputationGraph) -> None:
    """Reconcile the fell-through-valueless entry points (Item 7 / D4, M1).

    Runs at the generation boundary, BEFORE output is cleared, beside
    ``_check_duplicate_output_paths``. Partitions the fell-through, valueless
    entry points by whether pipeline wiring references them:

    - **unwired** remainder → one WARNING reconciliation summary (tracked
      residue; no runtime ``KeyError``). Logged FIRST so the digest reaches the
      operator even when generation aborts.
    - **wired** half → V11 hard error, generation aborts. The JSON never mints
      the key but the pipeline references it → guaranteed runtime ``KeyError``.

    Always strict (no escape-hatch flag). Raises ``CodeGenerationError`` on any
    wired violation, matching the ``_check_duplicate_output_paths`` fail-fast
    idiom (caught by ``run_codegen``, aborts the run).
    """
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.resolution.uncovered_params import (
        collect_uncovered_params,
        collect_unwired_fallthrough,
    )

    # Reconciliation summary first (unwired remainder), so the operator sees the
    # digest even if the V11 raise below aborts the run.
    unwired = collect_unwired_fallthrough(graph)
    if unwired:
        logger.warning(
            "Unresolved after assembly: %d entry point(s) fell through and still "
            "lack a value (unwired): %s",
            len(unwired),
            unwired,
        )

    uncovered = collect_uncovered_params(graph)
    if uncovered:
        details = "; ".join(
            f"module '{u.module}' input '{u.input}' -> params key '{u.missing_key}'"
            for u in uncovered
        )
        raise CodeGenerationError(
            f"V11: {len(uncovered)} module input(s) reference a params key that no "
            f"parameter group provides — the JSON never mints the key, so the "
            f"pipeline will KeyError at load. Cause: an unresolved cross-part "
            f"reference not yet wired (Items 9-11) or a resolution bug. "
            f"Offenders: {details}"
        )


def _preflight_registry_class_names(graph: ComputationGraph) -> None:
    """Refuse a graph whose registry class names collide beyond aliasing (REQ-REG-08).

    The check belonged to the registry pass alone, which runs after
    ``_clear_output_directory``: a model that trips it left a half-written
    package behind and reported "Unexpected error", because the raise was an
    untyped ``ValueError``. Running the same pure detector here — beside
    ``_check_duplicate_output_paths`` and ``_reconcile_params_coverage``, before
    anything is written — is what makes it fail-before-mutate, and the error is
    the package's own so the operator reads a refusal rather than a traceback.
    """
    from sysml_codegen.generation.errors import residual_class_name_collision_error
    from sysml_codegen.generation.registry import residual_class_name_collisions

    residual = residual_class_name_collisions(graph)
    if residual:
        raise residual_class_name_collision_error(residual)


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
    from sysml_codegen.elaboration.graph import DISPOSITION_REASONS
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.resolution.models import ModuleKind

    catalog = graph.constraint_catalog
    if catalog is None:
        if any(module.module_kind is ModuleKind.CONSTRAINT for module in graph.modules):
            raise CodeGenerationError(
                "constraint usage domain incomplete: the graph generates constraint modules "
                "but carries no catalog"
            )
        return

    if catalog.recomputed_fingerprint() != catalog.fingerprint:
        raise CodeGenerationError(
            "constraint usage domain incomplete: the catalog's "
            f"{len(catalog.usage_records)} usage rows no longer match the fingerprint "
            "sealed at projection, so a row was added, removed, or altered after the "
            "domain was rendered"
        )

    rows_by_id: dict[str, ConstraintCatalogUsageRecord] = {}
    for row in catalog.usage_records:
        if row.declaration_id in rows_by_id:
            raise CodeGenerationError(
                "constraint usage domain incomplete: duplicate usage record for "
                f"{row.usage_qualified_name} ({row.declaration_id})"
            )
        reasons = DISPOSITION_REASONS.get(row.disposition_kind)
        if reasons is None or row.disposition_reason not in reasons:
            raise CodeGenerationError(
                "constraint usage domain incomplete: no disposition for "
                f"{row.usage_qualified_name} ({row.declaration_id})"
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
                "constraint usage domain incomplete: catalog row joins no domain member for "
                f"{occurrence.usage_qualified_name} ({occurrence.declaration_id})"
            )
        occurrences[occurrence.declaration_id] = (
            occurrences.get(occurrence.declaration_id, 0) + 1
        )

    for declaration_id, row in rows_by_id.items():
        counted = occurrences.get(declaration_id, 0)
        if row.occurrence_count != counted:
            raise CodeGenerationError(
                f"constraint usage domain incomplete: occurrence_count {row.occurrence_count} "
                f"disagrees with {counted} nodes for {row.usage_qualified_name} "
                f"({declaration_id})"
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
                "coverage account cannot be built: the graph carries a REPORT_AGGREGATOR "
                "module but no constraint catalog, so the report it would ship could not "
                "state its coverage"
            )
        return

    if has_aggregator != ships_constraint_machinery(graph):
        expected = "a REPORT_AGGREGATOR module" if not has_aggregator else "no aggregator"
        raise CodeGenerationError(
            "coverage account disagrees with the report-required rule: the catalog has "
            f"{len(catalog.usage_records)} usage row(s), which requires {expected}. "
            "A report is required iff the model authored at least one constraint usage; the "
            "aggregator mint and the generation seams must read that one population."
        )

    recomputed = coverage_account(catalog)
    if constraint_plan.coverage != recomputed:
        raise CodeGenerationError(
            "coverage account disagrees with its catalog: the plan holds "
            f"{constraint_plan.coverage}, and the sealed catalog implies {recomputed}. The "
            "account is a summary of that catalog and nothing else, so it was altered after "
            "it was derived."
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


def _generate_schemas(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate Pydantic schemas for multi-output modules."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_multioutput_model
    from sysml_codegen.resolution.models import ModuleKind

    schemas_dir = config.output_path / "schemas"

    multioutput_count = 0
    for module in graph.modules:
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            continue
        if len(module.outputs) < 2:
            continue
        output_path = schemas_dir / f"{module.calc_def_name.lower()}_output.py"
        code = generate_multioutput_model(
            module,
            template_env,
            output_path,
            package_name=config.package_name,
        )
        if code:
            output_path.write_text(code)
            multioutput_count += 1
            logger.debug(f"Generated schema: {output_path.name}")

    logger.info(f"Generated {multioutput_count} multi-output schemas")

    # Item 7 / D4: per-package evidence schemas, gated on the package actually having
    # constraint machinery that could run — one concrete entry. A corpus that declares no
    # constraint writes nothing here (INV-7), and so does one that declares constraints
    # none of which reach an instance: there would be nothing to populate the evidence
    # with. See `ships_constraint_machinery` for why the catalog's existence stopped being
    # the right question, and which item supersedes this rule.
    from sysml_codegen.resolution.models import ships_constraint_machinery

    if ships_constraint_machinery(graph):
        template = template_env.get_template("constraint_types.py.jinja2")
        code = template.render()
        if not code.endswith("\n"):
            code += "\n"
        (schemas_dir / "constraint_types.py").write_text(code)
        logger.info("Generated constraint evidence schemas: constraint_types.py")


def _generate_modules(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
    constraint_plan: ConstraintGenerationPlan,
) -> None:
    """Generate TEAx module wrappers for all module types (ADR-003 namespacing)."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_teax_module
    from sysml_codegen.resolution.models import ModuleKind

    modules_dir = config.output_path / "modules"
    catalog = graph.constraint_catalog
    staged: list[tuple[Path, str]] = []

    if constraint_plan.predicates_code is not None:
        staged.append(
            (modules_dir / "constraints" / "predicates.py", constraint_plan.predicates_code)
        )

    for module in graph.modules:
        python_path = _get_python_path(module)
        output_path = modules_dir / python_path.full_path
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            code = constraint_plan.rendered_modules[module.name]
        else:
            code = generate_teax_module(
                module,
                template_env,
                output_path,
                config.package_name,
            )
        if code:
            staged.append((output_path, code))

    # Rendering and semantic scope checks are complete. Only now may this writer mutate.
    initialized_namespaces: set[str] = set()
    for output_path, code in staged:
        relative_parent = output_path.parent.relative_to(modules_dir)
        namespace = relative_parent.as_posix()
        if namespace != "." and namespace not in initialized_namespaces:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                modules_dir,
                namespace,
                '"""Namespace package for generated modules."""\n',
            )
            initialized_namespaces.add(namespace)
        output_path.write_text(code)
        logger.debug(f"Generated module: {output_path}")

    module_count = len(staged) - (1 if catalog is not None else 0)
    logger.info(f"Generated {module_count} TEAx module wrappers")


def _generate_stencils(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate implementation stencils for all module types (ADR-003 namespacing)."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import (
        backup_implementation,
        generate_implementation,
        should_regenerate_stencil,
    )
    from sysml_codegen.resolution.models import ModuleKind

    handwritten_dir = config.output_path / "handwritten"
    backup_dir = handwritten_dir / "backup"

    stats = {"new": 0, "preserved": 0, "regenerated": 0}

    for module in graph.modules:
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            # D8: fully generated, no handwritten implementation to stencil.
            continue
        python_path = _get_python_path(module)

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                handwritten_dir,
                python_path.directory,
                '"""Handwritten implementations."""\n',
            )
            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        # Smart regeneration logic
        if config.smart_regen and output_path.exists():
            should_regen, reason = should_regenerate_stencil(module, output_path)
            if should_regen:
                backup_implementation(output_path, backup_dir)
                code = generate_implementation(
                    module,
                    template_env,
                    output_path,
                    config.package_name,
                )
                if code:
                    output_path.write_text(code)
                stats["regenerated"] += 1
                logger.debug(f"Regenerated stencil ({reason}): {output_path.name}")
            else:
                # Smart-regen: signature unchanged. Check if stub can be upgraded.
                existing_content = output_path.read_text()
                is_stub = "raise NotImplementedError" in existing_content
                has_auto_impl = module.auto_impl_context is not None
                if is_stub and has_auto_impl:
                    backup_implementation(output_path, backup_dir)
                    code = generate_implementation(
                        module,
                        template_env,
                        output_path,
                        config.package_name,
                    )
                    if code:
                        output_path.write_text(code)
                    stats["regenerated"] += 1
                    logger.debug(f"Upgraded stub to auto-impl: {output_path.name}")
                else:
                    stats["preserved"] += 1
                    logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
        elif config.preserve_handwritten and output_path.exists():
            stats["preserved"] += 1
            logger.debug(f"Preserved existing stencil: {output_path.name}")
        else:
            code = generate_implementation(
                module,
                template_env,
                output_path,
                config.package_name,
            )
            if code:
                output_path.write_text(code)
            stats["new"] += 1

    if config.smart_regen:
        logger.info(
            f"Stencils - New: {stats['new']}, "
            f"Preserved: {stats['preserved']}, "
            f"Regenerated: {stats['regenerated']}"
        )
    else:
        logger.info(f"Generated {stats['new']} implementation stencils")


def _generate_pipeline(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate pipeline YAML from computation graph."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_pipeline_yaml

    pipelines_dir = config.output_path / "pipelines"
    output_path = pipelines_dir / f"{config.pipeline_name}.yaml"

    yaml_content = generate_pipeline_yaml(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
    )
    if yaml_content:
        output_path.write_text(yaml_content)
        logger.debug(f"Generated pipeline: {output_path}")

    logger.info(f"Generated pipeline configuration: {config.pipeline_name}.yaml")


def _generate_registry(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate registry function in __init__.py."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_registry
    from sysml_codegen.generation.registry import _collect_exit_point_primitive_types

    output_path = config.output_path / "__init__.py"

    exit_point_types = _collect_exit_point_primitive_types(graph.modules)

    code = generate_registry(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
        exit_point_primitive_types=exit_point_types,
    )
    if code:
        output_path.write_text(code)
        logger.debug(f"Generated registry: {output_path}")

    logger.info(f"Generated module registry with {len(graph.modules)} modules")


def _generate_entry_points(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate entry point parameter group schemas and JSON templates."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import (
        generate_all_derived_jsons_from_graph,
        generate_all_derived_schemas_from_graph,
    )

    entry_point_groups = graph.entry_point_groups

    if entry_point_groups:
        schema_files = generate_all_derived_schemas_from_graph(
            entry_point_groups,
            template_env,
            config.output_path,
        )
        logger.info(f"Generated {len(schema_files)} parameter group schemas")

        json_files = generate_all_derived_jsons_from_graph(
            entry_point_groups,
            config.output_path,
        )
        logger.info(f"Generated {len(json_files)} JSON input templates")
    else:
        logger.info("No entry point groups to generate")


def _generate_backlog(
    graph: ComputationGraph,
    config: GenerationConfig,
) -> None:
    """Generate implementation backlog report."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_backlog_report

    output_path = config.output_path / "IMPLEMENTATION_BACKLOG.md"

    markdown = generate_backlog_report(
        graph,
        output_path,
        config.package_name,
    )
    if markdown:
        output_path.write_text(markdown)
        logger.info(f"Generated implementation backlog: {output_path.name}")


def _generate_tests(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate runnable test file for implementations."""
    _preflight_constraint_names(graph)
    from sysml_codegen.generation import generate_test_implementations

    tests_dir = config.output_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    output_path = tests_dir / "test_implementations_runnable.py"

    content = generate_test_implementations(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    output_path.write_text(content)
    logger.info(f"Generated runnable tests: {output_path.name}")


def _seal_package(
    graph: ComputationGraph,
    config: GenerationConfig,
) -> None:
    """Step 9: seal the generated package (D1).

    Order is the seal-well-formedness invariant (INV-3): every covered artifact must be
    final on disk before ``seal_package`` runs, and ``package_contract.json`` is written
    last, never in its own coverage.
    """
    _preflight_constraint_names(graph)
    from sysml_codegen.contracts import (
        DEFAULT_COVERAGE_POLICY,
        build_generation_manifest,
        build_model_contract,
        ensure_package_tree_is_link_free,
        seal_package,
    )
    from sysml_codegen.contracts.serialize import write_contract_json

    ensure_package_tree_is_link_free(config.output_path)
    contracts_dir = config.output_path / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    # (1) ModelContract — pure graph projection, written first.
    model_contract = build_model_contract(graph)
    write_contract_json(contracts_dir / "model_contract.json", model_contract)

    # (2) The canonical verifier, copied verbatim (INV-8 drift guard).
    verify_source = Path(__file__).resolve().parent.parent / "contracts" / "verify.py"
    shutil.copy(verify_source, contracts_dir / "verify.py")

    # (3) The generation manifest (Item 7): provenance the re-seal gate consults so a foreign
    # file cannot be laundered as codegen-produced. Built from the tree as it stands now —
    # ModelContract and verify.py present, manifest and seal not yet — so `codegen_produced`
    # is the covered tree minus handwritten/runtime plus the manifest's own path. Written
    # before the seal so it is itself a covered (hashed, frozen) artifact.
    manifest_entries = ensure_package_tree_is_link_free(config.output_path)
    manifest = build_generation_manifest(manifest_entries, DEFAULT_COVERAGE_POLICY)
    write_contract_json(contracts_dir / "generation_manifest.json", manifest)

    # (4)+(5) Seal everything now on disk (including the three files above) and write the
    # seal last — it is the only thing excluded from its own coverage.
    package_contract = seal_package(
        config.output_path, config.package_name, DEFAULT_COVERAGE_POLICY
    )
    write_contract_json(contracts_dir / "package_contract.json", package_contract)


def cmd_generate(args: argparse.Namespace) -> int:
    """Run the code generation command."""
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Validate agentic-mbse is installed
    try:
        import agentic_mbse

        logger.debug(f"agentic-mbse version: {agentic_mbse.__version__}")
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        return 1

    config = GenerationConfig(
        models_path=args.models,
        from_snapshot=args.from_snapshot,
        output_path=args.output,
        package_name=args.package_name,
        schema_class_name=args.schema_class,
        pipeline_name=args.pipeline_name,
        overwrite=args.overwrite,
        preserve_handwritten=args.preserve_handwritten,
        smart_regen=args.smart_regen,
    )

    success = run_codegen(config)
    return 0 if success else 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Capture one v6 instance-graph snapshot from live models.

    This subcommand emits what this CLI's ``generate --from-snapshot`` accepts.
    It is the only snapshot this tool writes: the v5 extraction snapshot retired
    with the v5 family.
    """
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    try:
        import agentic_mbse  # noqa: F401
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        return 1

    from sysml_codegen.elaboration.elaborate import (
        ElaborationDiagnosticError,
        ElaborationError,
    )
    from sysml_codegen.generation import SysMLParsingError
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

    models_path: Path = args.models
    output_path: Path = args.output or (models_path / "instance_graph_snapshot.json")
    # The same distinct refusal classes run_codegen keeps distinct: a model the
    # exact route declines gets its typed message and exit 1, never a traceback.
    try:
        out = capture_instance_graph_snapshot([models_path], output_path)
    except ElaborationError as error:
        logger.error(f"Model is not ready for the exact route: {error}")
        return 1
    except ElaborationDiagnosticError as error:
        logger.error(f"Model failed exact-route validation: {error}")
        return 1
    except SysMLParsingError as error:
        logger.error(f"SysML parsing failed: {error}")
        return 1
    except OSError as error:
        logger.error(f"Snapshot could not be written: {error}")
        return 1
    logger.info(f"Wrote snapshot to {out}")
    return 0


def cmd_seal(args: argparse.Namespace) -> int:
    """Re-seal an existing generated package (D2).

    Recomputes the ``PackageContract`` only — graph-free, license-free — over a package
    directory that has already been sealed once by ``generate``. Use this after editing a
    handwritten stencil to make the seal match the edited bytes again.
    """
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    from sysml_codegen.contracts import (
        DEFAULT_COVERAGE_POLICY,
        PackageSealError,
        ProvenanceError,
        check_reseal_provenance,
        ensure_package_tree_is_link_free,
        seal_package,
    )
    from sysml_codegen.contracts.serialize import write_contract_json

    package_dir: Path = args.package_dir
    try:
        entries = ensure_package_tree_is_link_free(package_dir)
    except (PackageSealError, OSError) as error:
        logger.error(f"Package sealing failed: {error}")
        return 1

    model_contract_path = package_dir / "contracts" / "model_contract.json"
    if not model_contract_path.is_file():
        logger.error(
            f"{model_contract_path} not found. `seal` re-seals a package `generate` has "
            "already sealed once (D2) — it does not build a ModelContract from scratch."
        )
        return 1

    # Provenance gate (Item 7): consult the generation manifest against the prior seal so a
    # re-seal cannot launder a foreign file as codegen-produced, nor record an edited
    # generated file. Runs before `seal_package`, which stays a pure directory→seal function.
    prior_seal_path = package_dir / "contracts" / "package_contract.json"
    if not prior_seal_path.is_file():
        logger.error(
            f"{prior_seal_path} not found. `seal` re-seals a package `generate` has already "
            "sealed once (D2); there is no prior seal to re-seal against."
        )
        return 1
    try:
        prior_seal = json.loads(prior_seal_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        logger.error(f"Package sealing failed: prior seal is unreadable: {error}")
        return 1
    try:
        check_reseal_provenance(package_dir, entries, prior_seal, DEFAULT_COVERAGE_POLICY)
    except ProvenanceError as error:
        logger.error(f"Re-seal refused (provenance): {error}")
        return 1

    try:
        package_contract = seal_package(package_dir, args.package_name, DEFAULT_COVERAGE_POLICY)
    except (PackageSealError, OSError) as error:
        logger.error(f"Package sealing failed: {error}")
        return 1
    write_contract_json(package_dir / "contracts" / "package_contract.json", package_contract)
    logger.info(f"Re-sealed {package_dir} as {args.package_name!r}")
    return 0


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install teax-completion helper command to a project."""
    if args.list:
        print("Available codegen helper commands:")
        for cmd in CODEGEN_COMMANDS:
            print(f"  - {cmd}")
        return 0

    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a directory", file=sys.stderr)
        return 1

    commands_dir = target_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    source_dir = get_commands_dir()
    copied = 0
    for cmd in CODEGEN_COMMANDS:
        src = source_dir / cmd
        dst = commands_dir / cmd
        if dst.exists() and not args.force:
            print(f"Skipping {cmd} (exists, use --force to overwrite)")
            continue
        if src.exists():
            shutil.copy(src, dst)
            print(f"Installed {cmd}")
            copied += 1
        else:
            print(f"Warning: {cmd} not found in package", file=sys.stderr)

    print(f"Installed {copied} command(s) to {commands_dir}")
    return 0


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="SysML v2 code generation tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate Python code from SysML v2 models")
    # Exactly one extraction input: live --models or a captured --from-snapshot
    # (both-forbidden / neither-forbidden come free from a required group — INV-7).
    gen_input = gen_parser.add_mutually_exclusive_group(required=True)
    gen_input.add_argument(
        "--models", "-m", type=Path, help="Path to SysML model directory or file (live extraction)"
    )
    gen_input.add_argument(
        "--from-snapshot",
        type=Path,
        help="Path to a captured extraction snapshot (license-free generation)",
    )
    gen_parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Output directory for generated code"
    )
    gen_parser.add_argument(
        "--package-name",
        type=str,
        default="generated_code",
        help="Python package name for generated code (default: generated_code)",
    )
    gen_parser.add_argument(
        "--schema-class",
        type=str,
        default="Params",
        help="Name for the main schema class (default: Params)",
    )
    gen_parser.add_argument(
        "--pipeline-name",
        type=str,
        default="pipeline",
        help="Name for the pipeline configuration (default: pipeline)",
    )
    gen_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    gen_parser.add_argument(
        "--preserve-handwritten",
        action="store_true",
        help="Preserve handwritten implementations during regeneration",
    )
    gen_parser.add_argument(
        "--smart-regen", action="store_true", help="Smart regeneration with signature comparison"
    )
    gen_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    gen_parser.set_defaults(func=cmd_generate)

    # Snapshot subcommand — capture a versioned snapshot from live models (D5)
    snap_parser = subparsers.add_parser(
        "snapshot", help="Capture a versioned extraction snapshot from live models"
    )
    snap_parser.add_argument(
        "--models", "-m", type=Path, required=True, help="Path to SysML model directory or file"
    )
    snap_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Snapshot output path (default: <models>/extraction_snapshot.json)",
    )
    snap_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    snap_parser.set_defaults(func=cmd_snapshot)

    # Seal subcommand — re-seal a generated package in place (D1/D2)
    seal_parser = subparsers.add_parser(
        "seal", help="Re-seal a generated package (recomputes the PackageContract only)"
    )
    seal_parser.add_argument(
        "package_dir", type=Path, help="Path to the generated package directory"
    )
    seal_parser.add_argument(
        "--package-name", type=str, required=True, help="Package name to record in the seal"
    )
    seal_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    seal_parser.set_defaults(func=cmd_seal)

    # Install-commands subcommand
    install_parser = subparsers.add_parser(
        "install-commands", help="Install teax-completion helper command"
    )
    install_parser.add_argument(
        "directory", nargs="?", default=".", help="Target directory (default: current directory)"
    )
    install_parser.add_argument(
        "--list", action="store_true", help="List available commands without installing"
    )
    install_parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    install_parser.set_defaults(func=cmd_install_commands)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


def run_codegen(config: GenerationConfig) -> bool:
    """Generate one package from the exact instance-graph authority.

    This is the single public generation entry point, and it constructs exactly
    one way. ``--models`` and ``--from-snapshot`` are two *sources* for the same
    authority, not two implementations: both seal into an ``ExactPipelineContext``
    whose receipt binds the instance graph to what it projects to. There is no
    flag, environment variable, or config field that selects an implementation.

    The legacy builders are gone from the tree entirely (retirement steps 1-4);
    there is no other construction authority left to be reachable from here.

    Args:
        config: Generation configuration with paths and options.

    Returns:
        True if generation succeeded, False otherwise.
    """
    from sysml_codegen.elaboration.elaborate import (
        ElaborationDiagnosticError,
        ElaborationError,
    )
    from sysml_codegen.generation import CodeGenerationError, SysMLParsingError
    from sysml_codegen.orchestration.exact_pipeline_context import (
        build_exact_pipeline_context,
        build_exact_pipeline_context_from_snapshot,
    )
    from sysml_codegen.snapshot.envelope import InstanceGraphSnapshotError

    source = config.from_snapshot if config.from_snapshot is not None else config.models_path
    logger.info(f"Generating code from {source}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    logger.info("Building pipeline context...")
    try:
        if config.from_snapshot is not None:
            context = build_exact_pipeline_context_from_snapshot(config.from_snapshot)
        else:
            assert config.models_path is not None  # guaranteed by the CLI group
            context = build_exact_pipeline_context([config.models_path])
        # One read, one projection. Every later step works from this object, so a
        # package is never assembled out of several separately derived graphs.
        graph = context.computation_graph
    except InstanceGraphSnapshotError as error:
        logger.error(f"Snapshot refused: {error}")
        return False
    # The two elaboration refusal classes stay distinct in the log the way the
    # corpus driver keeps them distinct: readiness findings and validation
    # diagnostics are different answers, and collapsing them loses which gate
    # refused. Neither is a CodeGenerationError, so neither is caught below.
    except ElaborationError as error:
        logger.error(f"Model is not ready for the exact route: {error}")
        return False
    except ElaborationDiagnosticError as error:
        logger.error(f"Model failed exact-route validation: {error}")
        return False
    except SysMLParsingError as error:
        logger.error(f"SysML parsing failed: {error}")
        return False
    except CodeGenerationError as error:
        logger.error(
            f"Code generation failed: {error}",
            extra={"constraint_name_safety": error.name_safety_violation},
        )
        return False

    logger.info(f"Built computation graph with {len(graph.modules)} modules")
    return _generate_package_from_graph(graph, config)


def _generate_package_from_graph(graph: ComputationGraph, config: GenerationConfig) -> bool:
    """Write and seal one package from an already-constructed computation graph.

    Authority-neutral by construction: it takes a graph and chooses nothing. The
    caller has already decided which authority produced it, which is why
    ``run_codegen`` is the only thing that decides. Private on purpose — the
    recovery's legacy-specimen tests drive it directly while their fixtures are
    retired, and Phase 4 removes those callers with the legacy owners.
    """
    from sysml_codegen.contracts import PackageSealError, ensure_package_tree_is_link_free
    from sysml_codegen.generation import (
        CodeGenerationError,
        SysMLParsingError,
    )
    from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan

    try:
        # Validate both generated constraint scopes before overwrite clearing or output creation.
        _preflight_constraint_names(graph)

        # Step 1.5: Fail fast on a sanitize-collision BEFORE clearing output, so a
        # duplicate path never wipes or silently overwrites existing files.
        _check_duplicate_output_paths(graph.modules)

        # Step 1.6: Params-coverage reconciliation (Item 7 / D4, M1). Always
        # strict — logs the unwired-remainder summary, then raises V11 on any
        # wired fell-through-valueless input. Before output clear, like 1.5.
        _reconcile_params_coverage(graph)

        # Step 1.7: registry class-name collisions the aliasing cannot resolve.
        # The check itself lives at the registry pass, which runs after the tree
        # is cleared; running it here is what makes the refusal fail-before-mutate.
        _preflight_registry_class_names(graph)

        # Step 1.8: the constraint catalog accounts for every authored usage, and
        # every occurrence row joins one of them by identity. Before output clear,
        # like 1.5-1.7: a package that shipped a catalog missing a carrier would
        # claim coverage it does not have.
        _preflight_constraint_totality(graph)

        try:
            ensure_package_tree_is_link_free(config.output_path)
        except (PackageSealError, OSError) as error:
            logger.error(f"Package sealing failed: {error}")
            return False

        # Build every constraint body and wrapper while the target tree is still untouched.
        template_env = _get_template_env()
        constraint_plan = build_constraint_generation_plan(
            graph, template_env, config.package_name
        )

        # Step 1.9: the coverage account the package is about to bake agrees with the catalog
        # it claims to summarize, and the aggregator's existence agrees with the same
        # population. Still before the clear, so a disagreement refuses without touching the
        # tree.
        _preflight_coverage_account(graph, constraint_plan)

        # Step 2: Clear and setup output directories
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            _clear_output_directory(config)

        logger.info("Creating output directory structure...")
        _setup_output_directories(config)

        # Step 3: Generate primitives.py (required for module imports)
        _generate_primitives(config)

        # Step 5: Generate schemas
        logger.info("Generating schemas...")
        _generate_schemas(graph, config, template_env)

        # Step 6: Generate modules and stencils (all types unified via graph)
        logger.info("Generating TEAx module wrappers...")
        _generate_modules(graph, config, template_env, constraint_plan)

        logger.info("Generating implementation stencils...")
        _generate_stencils(graph, config, template_env)

        # Step 7: Generate pipeline and registry
        logger.info("Generating pipeline configuration...")
        _generate_pipeline(graph, config, template_env)

        logger.info("Generating module registry...")
        _generate_registry(graph, config, template_env)

        # Step 8: Generate entry points and extras
        logger.info("Generating entry point schemas and JSON templates...")
        _generate_entry_points(graph, config, template_env)

        logger.info("Generating implementation backlog...")
        _generate_backlog(graph, config)

        logger.info("Generating runnable tests...")
        _generate_tests(graph, config, template_env)

        # Step 9: Seal the package (D1) — over final on-disk state, both live and
        # from-snapshot paths alike (D8).
        logger.info("Sealing package...")
        try:
            _seal_package(graph, config)
        except (PackageSealError, OSError) as error:
            logger.error(f"Package sealing failed: {error}")
            return False

        logger.info("Code generation complete")
        return True

    except SysMLParsingError as e:
        logger.error(f"SysML parsing failed: {e}")
        return False
    except CodeGenerationError as e:
        logger.error(
            f"Code generation failed: {e}",
            extra={"constraint_name_safety": e.name_safety_violation},
        )
        return False
    except OSError as e:
        # The only unnamed failure this half can operationally hit is the
        # filesystem: the output tree is created and written from step 2 onward.
        # Everything else reaching here — a template defect, a graph field the
        # renderer did not expect — is a programming defect, and it now propagates
        # to the CLI boundary with its traceback instead of becoming a bare
        # "generation failed" and exit 1.
        #
        # Measured, and deliberately not changed here: any failure after step 2
        # leaves the partially written output tree on disk. That is true of the
        # named refusals above as well, and has been since before this narrowing.
        logger.error(f"Writing the generated package failed: {e}")
        return False


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "CODEGEN_COMMANDS",
]
