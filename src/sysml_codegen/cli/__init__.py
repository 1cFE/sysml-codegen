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

from sysml_codegen.cli import emit, prepare
from sysml_codegen.cli.study import STUDY_TOOLS, cmd_study

# Note: the generate route imports its heavy modules inside the functions that use
# them, so loading the CLI stays fast.

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

    The route is ``load_source``, then ``prepare`` (read-only), then the destination
    check, then ``emit_package`` (the only step that writes). A refusal at any step is
    logged once, as one record carrying its ``Refusal``.

    Args:
        config: Generation configuration with paths and options.

    Returns:
        True if generation succeeded, False otherwise.
    """
    source: prepare.ModelSource
    if config.from_snapshot is not None:
        source = prepare.SnapshotFile(config.from_snapshot)
        logger.info(f"Generating code from {config.from_snapshot}")
    else:
        assert config.models_path is not None  # guaranteed by the CLI group
        source = prepare.LiveModels((config.models_path,))
        logger.info(f"Generating code from {config.models_path}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    logger.info("Building pipeline context...")
    prepared = prepare.prepare(prepare.load_source(source), config.package_name)
    if isinstance(prepared, prepare.Refused):
        prepare.log_refused(prepared)
        return False
    # Only a model that builds has its destination inspected, so a refused run logs one
    # record, the model's.
    problem = emit.inspect_destination(config.output_path)
    if problem is not None:
        prepare.log_refused(emit.destination_refused(problem))
        return False
    return emit.emit_package(prepared, config) is None


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "cmd_study",
]
