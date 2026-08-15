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

import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType

from sysml_codegen.cli import GenerationConfig, run_codegen

FUSION_TEA = Path(__file__).resolve().parents[1] / "fixtures" / "fusion_tea"
LCOE_CHANNEL = "hif_plant_pkg__hif_plant__lcoe_calc__lcoe"

#: Where a relocated read is staged: the directory the checkouts themselves sit
#: in, not ``/tmp``. The relocated route's claim is that a snapshot generates the
#: same package from a *different checkout root*, and ``/tmp`` is not one.
SCRATCH_PARENT = Path(__file__).resolve().parents[2].parent


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


@contextmanager
def relocated_snapshot(models: Path, prefix: str) -> Iterator[Path]:
    """Yield a v6 snapshot captured from a copy of ``models`` at a foreign root.

    Three things make the read relocated rather than merely indirect: the model
    is copied to a scratch root beside the checkouts, the snapshot is then moved
    away from where it was captured, and the copied model tree is deleted before
    the caller generates. A generator that reached back to the source files
    would fail rather than quietly succeed.

    The scratch root is removed on exit, so the caller must generate inside the
    ``with`` block and write its package somewhere else.
    """
    SCRATCH_PARENT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=prefix, dir=SCRATCH_PARENT))
    try:
        from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

        model_copy = root / "model-tree" / models.name
        shutil.copytree(models, model_copy)
        captured = capture_instance_graph_snapshot(
            [model_copy], root / "capture" / "snapshot.json"
        )

        moved = root / "elsewhere" / "snapshot.json"
        moved.parent.mkdir(parents=True)
        shutil.copyfile(captured, moved)
        shutil.rmtree(root / "model-tree")
        assert not model_copy.exists()
        yield moved
    finally:
        shutil.rmtree(root, ignore_errors=True)


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


def execute_sealed_package(package: Path, name: str, root: Path) -> dict[str, object]:
    """Seal-load a generated package and run its pipeline through real TEAx.

    ``root`` is scratch space: the loader's link tree and the run directory are
    created under it.
    """
    from simkit.core.pipeline import execute_pipeline
    from simkit.core.registry_builder import create_registry

    module, fingerprint = load_sealed_package(package, name, root / "link")

    factory = getattr(module, f"create_{name}_registry")
    registry = factory()
    result = execute_pipeline(
        package / "pipelines/pipeline.yaml",
        root / "run",
        registry=registry,
        custom_schema_types=module.CUSTOM_SCHEMA_TYPES,
    )
    return {
        "package": package,
        "name": name,
        "module": module,
        "fingerprint": fingerprint,
        "registry_backing": factory.__globals__.get("create_registry"),
        "public_create_registry": create_registry,
        "registry": registry,
        "result": result,
    }


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
