"""Minimal in-repo pipeline executor (SC-3 deliverable, reusable by Item 3).

Executes a generated package by importing its modules, wiring them per the pipeline
YAML, feeding the emitted JSON inputs, and running them in dependency order. Returns
every module output channel's computed value — proving the generated package produces
the right number *by execution*, not by graph inspection.

`simkit` (the TEAx runtime) is not importable in-repo, so this is the fixture-local
driver form (the design's plan-time open): a tiny `simkit` stub supplies the
`ModuleBase`/`ModuleResult` surface the generated wrappers import, and the wrappers'
auto-generated implementations do the arithmetic. The signature is pinned; Item 3
consumes it sight-unseen.
"""

from __future__ import annotations

import importlib
import json
import sys
import types
from pathlib import Path
from typing import Any

import yaml


def _install_simkit_stub() -> None:
    """Provide the minimal `simkit` surface the generated module wrappers import.

    A generated wrapper does `from simkit.core.base import ModuleBase, ModuleResult`
    and subclasses `ModuleBase[Input, Output]`. The stub gives a subscriptable base and
    a result holder; the wrapper's own `run` method and auto-impl do the work.

    A multi-output calc additionally does `from simkit.config.schema import MultiOutput`
    and subclasses it with one float field per output channel. The real `MultiOutput` is
    a pydantic container; the stub aliases it to `BaseModel`, which is all the runner needs
    (it reads each output via `getattr(result.data, field_name)`).
    """
    if "simkit" in sys.modules:
        return

    from pydantic import BaseModel

    class _Subscriptable:
        def __class_getitem__(cls, _item: Any) -> type:
            return cls

    class ModuleResult(_Subscriptable):
        def __init__(self, data: Any = None, **_: Any) -> None:
            self.data = data

    class ModuleBase(_Subscriptable):
        def __init__(self, **_: Any) -> None:
            pass

    class PipelineModuleRegistry:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass

    def create_registry(*_: Any, **__: Any) -> PipelineModuleRegistry:
        return PipelineModuleRegistry()

    # Proper packages (with __path__) so `simkit.core.<sub>` submodule imports resolve.
    simkit = types.ModuleType("simkit")
    simkit.__path__ = []  # type: ignore[attr-defined]
    core = types.ModuleType("simkit.core")
    core.__path__ = []  # type: ignore[attr-defined]
    base = types.ModuleType("simkit.core.base")
    registry = types.ModuleType("simkit.core.pipeline_registry")
    registry_builder = types.ModuleType("simkit.core.registry_builder")
    base.ModuleBase = ModuleBase
    base.ModuleResult = ModuleResult
    registry.PipelineModuleRegistry = PipelineModuleRegistry
    registry_builder.create_registry = create_registry
    core.base = base
    core.pipeline_registry = registry
    core.registry_builder = registry_builder
    simkit.core = core

    # Multi-output surface: `simkit.config.schema.MultiOutput`, a pydantic container base.
    config = types.ModuleType("simkit.config")
    config.__path__ = []  # type: ignore[attr-defined]
    config_schema = types.ModuleType("simkit.config.schema")
    config_schema.MultiOutput = BaseModel
    config.schema = config_schema
    simkit.config = config

    sys.modules.update(
        {
            "simkit": simkit,
            "simkit.core": core,
            "simkit.core.base": base,
            "simkit.core.pipeline_registry": registry,
            "simkit.core.registry_builder": registry_builder,
            "simkit.config": config,
            "simkit.config.schema": config_schema,
        }
    )


def _load_entry_values(package_dir: Path) -> dict[str, float]:
    """Merge every emitted entry-point JSON file into one {QN: value} map."""
    values: dict[str, float] = {}
    inputs_dir = package_dir / "inputs"
    if inputs_dir.is_dir():
        for jf in sorted(inputs_dir.glob("*.json")):
            data = json.loads(jf.read_text())
            values.update({k: v for k, v in data.items() if isinstance(v, (int, float))})
    return values


def _module_import_path(package: str, module_type: str) -> tuple[str, str]:
    """Map a YAML module_type (`namespace.ClassNameModule`) to (import_path, class)."""
    namespace, class_name = module_type.rsplit(".", 1)
    file_stem = class_name[:-6].lower() if class_name.endswith("Module") else class_name.lower()
    return f"{package}.modules.{namespace}.{file_stem}", class_name


def _resolve_source(
    source: str, entry_values: dict[str, float], channels: dict[str, float]
) -> float:
    """Resolve one input source token to a value.

    Three source forms appear in the pipeline YAML:
      - ``<channel>.root``   single-output upstream channel (RootModel wrapper)
      - ``<channel>``        multi-output upstream channel (bare channel name, ``__``-keyed)
      - ``<group>.<QN>``     entry point (value from the emitted JSON)

    Upstream channels resolve first: modules run in dependency order, so a producer's
    channel is registered before any consumer reads it. Anything left is an entry point,
    keyed by its QN (the leading group segment is stripped).
    """
    if source.endswith(".root"):
        channel = source[: -len(".root")]
        if channel not in channels:
            raise KeyError(f"unresolved upstream channel '{channel}'")
        return channels[channel]
    if source in channels:  # multi-output channel: a bare channel name, no `.root` wrapper
        return channels[source]
    # Entry point: strip the leading group segment to get the JSON key (the QN).
    qn = source.split(".", 1)[1] if "." in source else source
    if qn not in entry_values:
        raise KeyError(f"no input value for entry point '{qn}'")
    return entry_values[qn]


def run_pipeline(
    package_dir: Path,
    inputs: dict[str, float] | None = None,
) -> dict[str, float]:
    """Execute a generated package and return every module output channel's value.

    Args:
        package_dir: A generated package (modules/, pipelines/*.yaml, inputs/*.json).
        inputs: Optional entry-point overrides keyed by QN; else the emitted JSON.

    Returns:
        channel_name -> computed value, for every module output.
    """
    package_dir = Path(package_dir)
    _install_simkit_stub()

    entry_values = _load_entry_values(package_dir)
    if inputs:
        entry_values.update(inputs)

    pipeline_yaml = next((package_dir / "pipelines").glob("*.yaml"))
    spec = yaml.safe_load(pipeline_yaml.read_text())

    package = package_dir.name
    parent = str(package_dir.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    channels: dict[str, float] = {}
    for name, mod in spec.get("modules", {}).items():
        module_type = mod.get("module_type")
        # Skip the EntryPoint / ExitPoint sentinels — only real calc modules run.
        if not module_type or module_type in ("EntryPoint", "ExitPoint"):
            continue

        import_path, class_name = _module_import_path(package, module_type)
        module_cls = getattr(importlib.import_module(import_path), class_name)

        kwargs: dict[str, float] = {}
        for param_name, decl in (mod.get("inputs") or {}).items():
            source = decl.split()[-1]  # "float <source>"
            kwargs[param_name] = _resolve_source(source, entry_values, channels)

        result = module_cls().run(**kwargs)

        for field_name, decl in (mod.get("outputs") or {}).items():
            channel = decl.split()[-1]  # "RootModel[float] <channel>"
            data = result.data
            value = data.root if field_name == "root" and hasattr(data, "root") else getattr(
                data, field_name
            )
            channels[channel] = value

    return channels
