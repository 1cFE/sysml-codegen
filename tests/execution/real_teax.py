"""Generation and loading helpers for the Slice 3D real-TEAx lane.

Two jobs, both mechanical:

- ``generate_exact_package`` runs the shipped generation steps over an
  ``ExactPipelineContext`` and seals the result. It is the same step sequence
  ``cmd_generate`` runs (``cli/__init__.py``), in the same order, ending at
  ``_seal_package`` — the exact route has no public ``generate`` entry point of
  its own until the Slice 3E authority switch, and adding a second public flag
  before then is the dual authority the recovery plan bans.
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

from sysml_codegen.cli import (
    GenerationConfig,
    _generate_backlog,
    _generate_entry_points,
    _generate_modules,
    _generate_pipeline,
    _generate_primitives,
    _generate_registry,
    _generate_schemas,
    _generate_stencils,
    _generate_tests,
    _get_template_env,
    _seal_package,
    _setup_output_directories,
)
from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan

FUSION_TEA = Path(__file__).resolve().parents[1] / "fixtures" / "fusion_tea"
LCOE_CHANNEL = "hif_plant_pkg__hif_plant__lcoe_calc__lcoe"


def generate_exact_package(context, output_path: Path, package_name: str) -> Path:
    """Generate and seal a package from a receipt-bound exact context."""
    config = GenerationConfig(
        output_path=output_path, package_name=package_name, overwrite=True
    )
    template_env = _get_template_env()
    plan = build_constraint_generation_plan(
        context.computation_graph, template_env, package_name
    )
    _setup_output_directories(config)
    _generate_primitives(config)
    _generate_schemas(context, config, template_env)
    _generate_modules(context, config, template_env, plan)
    _generate_stencils(context, config, template_env)
    _generate_pipeline(context, config, template_env)
    _generate_registry(context, config, template_env)
    _generate_entry_points(context, config, template_env)
    _generate_backlog(context, config)
    _generate_tests(context, config, template_env)
    _seal_package(context, config)
    return output_path


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
