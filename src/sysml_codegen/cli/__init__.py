"""CLI entry point for sysml-codegen.

CRITICAL CHANGES:
- Parameterized all hardcoded values
- Removed CATF-specific references
- Package name is now a CLI argument
- install-commands installs the study layer and the TEAx completion helper
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from sysml_codegen.cli import emit, prepare
from sysml_codegen.cli.study import STUDY_TOOLS, cmd_study

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ComputationGraph

# Note: Heavy imports moved inside run_codegen to avoid loading generation
# module at CLI import time. This keeps CLI startup fast.

logger = logging.getLogger(__name__)


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
        unexpected_public_failure,
    )
    from sysml_codegen.generation import SysMLParsingError
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
    from sysml_codegen.snapshot.envelope import (
        InstanceGraphSnapshotError,
        SnapshotCertifiabilityError,
    )

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
    except InstanceGraphSnapshotError as error:
        if isinstance(error, SnapshotCertifiabilityError):
            rendered: list[str] = []
            for diagnostic in error.diagnostics:
                reference = (
                    f": reference={diagnostic.reference!r}"
                    if diagnostic.reference is not None
                    else ""
                )
                location = (
                    f" [{diagnostic.source_file}:{diagnostic.source_line}]"
                    if diagnostic.source_file is not None and diagnostic.source_line is not None
                    else ""
                )
                rendered.append(
                    f"{diagnostic.code.value}: {diagnostic.detail}{reference}{location}"
                )
            detail = "; ".join(rendered)
            logger.error(f"Snapshot refused: {detail}")
        else:
            logger.error(f"Snapshot refused: {error}")
        return 1
    except OSError as error:
        logger.error(f"Snapshot could not be written: {error}")
        return 1
    except Exception as error:
        diagnostic = unexpected_public_failure(error)
        logger.error(f"Snapshot failed exact-route validation: {diagnostic}")
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
    """Install the study layer: the run-study skill, the teax-completion command and the policy."""
    # Imported here so that only this subcommand needs agentic-mbse's installer API.
    from sysml_codegen.cli import install

    install.require_installer_api()
    if args.list:
        print("\n".join(install.list_assets()))
        return 0
    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        return 1
    actions = install.install_commands(target, assistant=args.assistant, force=args.force)
    print("\n".join(install.summarize(target, actions)))
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
        help="Path to a sealed v6 instance-graph snapshot (license-free generation)",
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
        "snapshot", help="Capture a sealed v6 instance-graph snapshot from live models"
    )
    snap_parser.add_argument(
        "--models", "-m", type=Path, required=True, help="Path to SysML model directory or file"
    )
    snap_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Snapshot output path (default: <models>/instance_graph_snapshot.json)",
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

    # Install-commands subcommand — the study layer and the teax-completion helper
    install_parser = subparsers.add_parser(
        "install-commands",
        help="Install the run-study skill, the teax-completion command and the study policy",
    )
    install_parser.add_argument(
        "directory", nargs="?", default=".", help="Target directory (default: current directory)"
    )
    install_parser.add_argument(
        "--assistant",
        choices=("claude", "codex", "both"),
        default="both",
        help="Assistants to install for (default: both); teax-completion is Claude's",
    )
    install_parser.add_argument(
        "--list", action="store_true", help="List what would be installed, without installing"
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace edited skill files and the project's STUDY_POLICY.md",
    )
    install_parser.set_defaults(func=cmd_install_commands)

    # Study subcommand — run one installed study tool; everything after the tool name is its own
    study_parser = subparsers.add_parser(
        "study", help="Run a study tool: indicators, preflight, verify or integrate"
    )
    study_parser.add_argument("tool", choices=STUDY_TOOLS, help="The study tool to run")
    study_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments passed unchanged to the tool"
    )
    study_parser.set_defaults(func=cmd_study)

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
    from sysml_codegen.cli.refusal import (
        Refusal,
        RefusalKind,
        diagnostic_refusal,
        generation_refusal,
        readiness_refusal,
    )
    from sysml_codegen.elaboration.elaborate import (
        ElaborationDiagnosticError,
        ElaborationError,
        unexpected_public_failure,
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
        logger.error(
            f"Snapshot refused: {error}", extra={"refusal": Refusal(RefusalKind.SNAPSHOT)}
        )
        return False
    # The two elaboration refusal classes stay distinct in the log the way the
    # corpus driver keeps them distinct: readiness findings and validation
    # diagnostics are different answers, and collapsing them loses which gate
    # refused. Neither is a CodeGenerationError, so neither is caught below.
    except ElaborationError as error:
        logger.error(
            f"Model is not ready for the exact route: {error}",
            extra={"refusal": readiness_refusal(error)},
        )
        return False
    except ElaborationDiagnosticError as error:
        logger.error(
            f"Model failed exact-route validation: {error}",
            extra={"refusal": diagnostic_refusal(error)},
        )
        return False
    except SysMLParsingError as error:
        logger.error(
            f"SysML parsing failed: {error}", extra={"refusal": Refusal(RefusalKind.PARSING)}
        )
        return False
    except CodeGenerationError as error:
        logger.error(
            f"Code generation failed: {error}",
            extra={
                "constraint_name_safety": error.name_safety_violation,
                "refusal": generation_refusal(error),
            },
        )
        return False
    except Exception as error:
        diagnostic = unexpected_public_failure(error)
        logger.error(
            f"Model failed exact-route validation: {diagnostic}",
            extra={"refusal": diagnostic_refusal(diagnostic)},
        )
        return False

    logger.info(f"Built computation graph with {len(graph.modules)} modules")
    try:
        return _generate_package_from_graph(graph, config)
    # A refusal generation already formed keeps its own code and vocabulary; only
    # a failure nobody classified becomes an internal defect.
    except CodeGenerationError as error:
        logger.error(
            f"Code generation failed: {error}",
            extra={
                "constraint_name_safety": error.name_safety_violation,
                "refusal": generation_refusal(error),
            },
        )
        return False
    except Exception as error:
        diagnostic = unexpected_public_failure(error)
        logger.error(
            f"Code generation failed: {diagnostic}",
            extra={"refusal": diagnostic_refusal(diagnostic)},
        )
        return False


def _generate_package_from_graph(graph: ComputationGraph, config: GenerationConfig) -> bool:
    """Write and seal one package from an already-constructed computation graph.

    Authority-neutral by construction: it takes a graph and chooses nothing. The
    caller has already decided which authority produced it, which is why
    ``run_codegen`` is the only thing that decides. Private on purpose — the
    recovery's legacy-specimen tests drive it directly while their fixtures are
    retired, and Phase 4 removes those callers with the legacy owners.
    """
    from sysml_codegen.cli.refusal import Refusal, RefusalKind, generation_refusal
    from sysml_codegen.contracts import PackageSealError, ensure_package_tree_is_link_free
    from sysml_codegen.generation import (
        CodeGenerationError,
        SysMLParsingError,
    )
    from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan

    try:
        # Unsupported root-output wrappers are a public model refusal, before
        # link inspection, plan rendering, output clearing, directory creation,
        # or any write. Registry collection shares the same total validator.
        prepare._preflight_generation_metadata(graph)
        prepare._preflight_exit_point_types(graph)

        # Validate both generated constraint scopes before overwrite clearing or output creation.
        prepare._preflight_constraint_names(graph)

        # Step 1.5: Fail fast on a sanitize-collision BEFORE clearing output, so a
        # duplicate path never wipes or silently overwrites existing files.
        prepare._check_duplicate_output_paths(graph.modules)

        # Step 1.7: registry class-name collisions the aliasing cannot resolve.
        # The check itself lives at the registry pass, which runs after the tree
        # is cleared; running it here is what makes the refusal fail-before-mutate.
        prepare._preflight_registry_class_names(graph)

        # Step 1.8: the constraint catalog accounts for every authored usage, and
        # every occurrence row joins one of them by identity. Before output clear,
        # like the preceding checks: a package that shipped a catalog missing a carrier would
        # claim coverage it does not have.
        prepare._preflight_constraint_totality(graph)

        try:
            ensure_package_tree_is_link_free(config.output_path)
        except (PackageSealError, OSError) as error:
            logger.error(
                f"Package sealing failed: {error}",
                extra={"refusal": Refusal(RefusalKind.PACKAGE_WRITE)},
            )
            return False

        # Build every constraint body and wrapper while the target tree is still untouched.
        template_env = prepare._get_template_env()
        constraint_plan = build_constraint_generation_plan(graph, template_env, config.package_name)

        # Step 1.9: the coverage account the package is about to bake agrees with the catalog
        # it claims to summarize, and the aggregator's existence agrees with the same
        # population. Still before the clear, so a disagreement refuses without touching the
        # tree.
        prepare._preflight_coverage_account(graph, constraint_plan)

        # Step 2: Clear and setup output directories
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            emit._clear_output_directory(config)

        logger.info("Creating output directory structure...")
        emit._setup_output_directories(config)

        # Step 3: Generate primitives.py (required for module imports)
        emit._generate_primitives(config)

        # Step 5: Generate schemas
        logger.info("Generating schemas...")
        emit._generate_schemas(graph, config, template_env)

        # Step 6: Generate modules and stencils (all types unified via graph)
        logger.info("Generating TEAx module wrappers...")
        emit._generate_modules(graph, config, template_env, constraint_plan)

        logger.info("Generating implementation stencils...")
        emit._generate_stencils(graph, config, template_env)

        # Step 7: Generate pipeline and registry
        logger.info("Generating pipeline configuration...")
        emit._generate_pipeline(graph, config, template_env)

        logger.info("Generating module registry...")
        emit._generate_registry(graph, config, template_env)

        # Step 8: Generate entry points and extras
        logger.info("Generating entry point schemas and JSON templates...")
        emit._generate_entry_points(graph, config, template_env)

        logger.info("Generating implementation backlog...")
        emit._generate_backlog(graph, config)

        logger.info("Generating runnable tests...")
        emit._generate_tests(graph, config, template_env)

        # Step 9: Seal the package (D1) — over final on-disk state, both live and
        # from-snapshot paths alike (D8).
        logger.info("Sealing package...")
        try:
            emit._seal_package(graph, config)
        except (PackageSealError, OSError) as error:
            logger.error(
                f"Package sealing failed: {error}",
                extra={"refusal": Refusal(RefusalKind.PACKAGE_WRITE)},
            )
            return False

        logger.info("Code generation complete")
        return True

    except SysMLParsingError as e:
        logger.error(f"SysML parsing failed: {e}", extra={"refusal": Refusal(RefusalKind.PARSING)})
        return False
    except CodeGenerationError as e:
        logger.error(
            f"Code generation failed: {e}",
            extra={
                "constraint_name_safety": e.name_safety_violation,
                "refusal": generation_refusal(e),
            },
        )
        return False
    except OSError as e:
        # The only unnamed failure this half can operationally hit is the
        # filesystem: the output tree is created and written from step 2 onward.
        # Everything else reaching here is converted by ``run_codegen`` into the
        # same caused, located public diagnostic as construction failures. The
        # private writer keeps the original exception intact for that boundary.
        #
        # Measured, and deliberately not changed here: any failure after step 2
        # leaves the partially written output tree on disk. That is true of the
        # named refusals above as well, and has been since before this narrowing.
        logger.error(
            f"Writing the generated package failed: {e}",
            extra={"refusal": Refusal(RefusalKind.PACKAGE_WRITE)},
        )
        return False


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "cmd_study",
]
