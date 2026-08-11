"""Generation and loading helpers for the Slice 3D real-TEAx lane.

Two jobs, both mechanical:

- ``generate_package_from_models`` and ``generate_package_from_snapshot`` call
  the shipped public ``run_codegen`` — since the Slice 3E authority switch that
  *is* the exact route, so this lane's evidence now comes from the surface a
  user has. Slice 3D had to drive the generation steps directly because the
  exact route had no public entry point yet; it does now.
- ``load_sealed_package`` hands the sealed directory to TEAx's own
  ``ProvisionalPackageLoader``, which authenticates the package-local verifier
  against its trusted hash, runs the seal check, and imports the package. This
  module never verifies the seal itself.

Nothing here installs a stub, patches an import, or reimplements a runner. The
in-repo ``tests/runtime/pipeline_runner.py`` does install a fake ``simkit``
(``_install_simkit_stub``); it must not appear anywhere on this lane.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

from sysml_codegen.cli import GenerationConfig, run_codegen

FUSION_TEA = Path(__file__).resolve().parents[1] / "fixtures" / "fusion_tea"
LCOE_CHANNEL = "hif_plant_pkg__hif_plant__lcoe_calc__lcoe"


def generate_package_from_models(models: Path, output_path: Path, package_name: str) -> Path:
    """Generate and seal a package live, through the shipped public route."""
    return _generate(
        GenerationConfig(
            models_path=models,
            output_path=output_path,
            package_name=package_name,
            overwrite=True,
        )
    )


def generate_package_from_snapshot(snapshot: Path, output_path: Path, package_name: str) -> Path:
    """Generate and seal a package from a v6 snapshot, through the same public route."""
    return _generate(
        GenerationConfig(
            from_snapshot=snapshot,
            output_path=output_path,
            package_name=package_name,
            overwrite=True,
        )
    )


def _generate(config: GenerationConfig) -> Path:
    assert run_codegen(config) is True, f"run_codegen refused {config}"
    return config.output_path


def load_sealed_package(
    package_dir: Path, package_name: str, link_root: Path
) -> tuple[ModuleType, str]:
    """Seal-verify and import a package through TEAx's own loader."""
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    loader = ProvisionalPackageLoader(
        package_dir=package_dir, package_name=package_name, link_root=link_root
    )
    return loader.load()


def package_loader(package_dir: Path, package_name: str, link_root: Path):
    """The loader object itself, for callers that hand it to ``PreparedEvaluator``."""
    from simkit.evaluation.package_load import ProvisionalPackageLoader

    return ProvisionalPackageLoader(
        package_dir=package_dir, package_name=package_name, link_root=link_root
    )


def consumer_ports(graph, entry_point_qualified_name: str) -> set[tuple[str, str]]:
    """Every ``(module, formal)`` port fed by one entry point, over the whole graph."""
    return {
        (module.name, module_input.param_name)
        for module in graph.modules
        for module_input in module.inputs
        if module_input.source.qualified_name == entry_point_qualified_name
    }


def all_ports(graph) -> set[tuple[str, str]]:
    """Every ``(module, formal)`` input port in the graph, entry-fed or not."""
    return {
        (module.name, module_input.param_name)
        for module in graph.modules
        for module_input in module.inputs
    }
