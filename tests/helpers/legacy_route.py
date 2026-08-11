"""Drive package generation from the LEGACY authority, for retired specimens.

**Read this before using it.** Slice 3E switched every public caller onto the
exact instance-graph route. A hundred test nodes could not follow, because their
*specimens* are exactly what the cutover retires:

- Forty-four generate from a committed **v5 extraction snapshot**. The public
  ``--from-snapshot`` is v6-only now, and for most of these fixtures no v6
  snapshot can ever exist, because the exact route refuses the model.
- Fifty-six generate live from a fixture the exact route **refuses**
  (``SI_SELF_BINDING`` on ``solar_battery_model``, ``catf_mfe_model``,
  ``chain_spike_model``). Those refusals are the owner-ratified corpus outcome
  (`.project/completed/20260809_elaborator-breadth/diff-ledger.md`), not damage.

Their *responsibilities* survive and are recorded one row per module in the
recovery plan's Slice 3E test dispositions, each naming the Gate 4C owner that
must author an exact-route specimen. Gate 4B may not delete a legacy production
owner while any of those rows lacks its replacement.

So this helper is deliberately not a second product route. It is a test-only
adapter that keeps retired specimens running against the implementation that
still understands them, until Gate 4C replaces them and Phase 4 deletes both.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.cli import GenerationConfig, _generate_package_from_graph

__all__ = ["generate_via_legacy_route"]


def generate_via_legacy_route(config: GenerationConfig) -> bool:
    """Build a legacy ``PipelineContext`` for ``config`` and generate from its graph.

    Mirrors what ``run_codegen`` did before the Slice 3E switch, so a repointed
    test measures the same behaviour it always did. Raises rather than guessing
    if the caller supplies neither a model path nor a snapshot.
    """
    import logging

    from sysml_codegen.generation import CodeGenerationError, SysMLParsingError
    from sysml_codegen.snapshot import GrandfatheredSnapshotError

    logger = logging.getLogger("sysml_codegen.cli")
    try:
        if config.from_snapshot is not None:
            from sysml_codegen.orchestration.snapshot_context import (
                build_pipeline_context_from_snapshot,
            )
            from sysml_codegen.snapshot import assert_snapshot_certifiable

            context = build_pipeline_context_from_snapshot(config.from_snapshot)
            assert_snapshot_certifiable(context.constraint_lowering_mode, config.from_snapshot)
        elif config.models_path is not None:
            from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

            # The legacy deriver still takes a design-path filter and defaults it
            # to accept-all. The public config lost that field with the flag
            # (Gate 4B-G0) and no repointed specimen ever set it, so the default
            # is what every specimen already measured.
            context = build_pipeline_context([config.models_path])
        else:
            raise ValueError("generate_via_legacy_route needs either models_path or from_snapshot")
        graph = context.computation_graph
    # The three construction-time refusals ``run_codegen`` reported as False
    # before the switch. Mirrored here so a repointed test sees what it saw.
    except GrandfatheredSnapshotError as error:
        logger.error(str(error))
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

    return _generate_package_from_graph(graph, config)


def _main(argv: list[str] | None = None) -> int:
    """A ``generate``-shaped command line over the legacy authority.

    Some retired specimens prove things a subprocess is required for — that
    generation from a v5 snapshot needs no licence, and that two independent
    processes emit byte-identical trees. Those subjects survive the switch only
    if they keep running in a real subprocess, so this mirrors the flags the
    shipped ``generate`` used to accept and routes them at the legacy builders.

    Run as ``python -m tests.helpers.legacy_route generate ...``.
    """
    import argparse
    import logging
    import sys

    parser = argparse.ArgumentParser(prog="legacy-generate")
    parser.add_argument("command", choices=["generate", "snapshot"])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--models", "-m", type=Path)
    source.add_argument("--from-snapshot", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--package-name", default="generated_code")
    parser.add_argument("--pipeline-name", default="pipeline")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--preserve-handwritten", action="store_true")
    parser.add_argument("--smart-regen", action="store_true")
    parser.add_argument("--design-path-filter", default="")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if args.command == "snapshot":
        # The v5 capture the shipped `snapshot` subcommand no longer performs.
        from sysml_codegen.snapshot import capture_snapshot

        capture_snapshot([args.models], args.output, design_path_filter=args.design_path_filter)
        return 0

    config = GenerationConfig(
        models_path=args.models,
        from_snapshot=args.from_snapshot,
        output_path=args.output,
        package_name=args.package_name,
        pipeline_name=args.pipeline_name,
        overwrite=args.overwrite,
        preserve_handwritten=args.preserve_handwritten,
        smart_regen=args.smart_regen,
    )
    return 0 if generate_via_legacy_route(config) else 1


if __name__ == "__main__":
    raise SystemExit(_main())
