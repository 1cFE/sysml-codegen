"""Every pipeline module type is registered once, by a class whose inputs every entry feeds.

Invariant I2 of ``.project/active/repeated-rollup-collision/design.md``, checked statically
on generated packages, so it needs no ``simkit``:

- each ``module_type`` named in ``pipelines/*.yaml`` appears exactly once in the registry's
  ``module_type_override`` in ``__init__.py``;
- the class registered for it, found through ``__init__.py``'s own import line, has input
  fields equal to the input names of every pipeline entry that uses that module type.

Run over the repeated sub-assembly fixtures, the two fixtures that hit the repeated-class
refusal before (``unresolvable_attr_probe``, ``elab_native_plural_scope``), and every
snapshot the public package oracle builds.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, REPO_ROOT, requires_license

PACKAGE = "coverage_pkg"
_ENDPOINTS = ("EntryPoint", "ExitPoint")

LIVE_MODELS = [
    *(
        f"repeated_rollup/{name}"
        for name in (
            "arity",
            "leafformula",
            "named",
            "named_total",
            "nestdiv",
            "nested",
            "onenamed",
            "specialized_renamed",
            "subname",
            "trio",
            "two",
        )
    ),
    "unresolvable_attr_probe",
    "elab_native_plural_scope",
]
SNAPSHOTS = sorted(
    path.relative_to(REPO_ROOT).as_posix()
    for path in FIXTURES_DIR.rglob("instance_graph_snapshot.json")
)


def _pipeline_inputs(package: Path) -> dict[str, list[set[str]]]:
    """Each pipeline module type, mapped to the input names of every entry using it."""
    found: dict[str, list[set[str]]] = defaultdict(list)
    for pipeline in sorted((package / "pipelines").glob("*.yaml")):
        for entry in yaml.safe_load(pipeline.read_text())["modules"].values():
            if entry["module_type"] in _ENDPOINTS:
                continue
            found[entry["module_type"]].append(set(entry.get("inputs") or {}))
    return dict(found)


def _registry(package: Path) -> tuple[dict[str, list[str]], dict[str, tuple[str, str]]]:
    """``module_type -> [registered names]`` and ``registered name -> (module, class)``."""
    tree = ast.parse((package / "__init__.py").read_text())
    imported: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
            f"{PACKAGE}.modules."
        ):
            for alias in node.names:
                imported[alias.asname or alias.name] = (node.module or "", alias.name)

    registered: dict[str, list[str]] = defaultdict(list)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "create_registry"):
            continue
        (override,) = [kw.value for kw in node.keywords if kw.arg == "module_type_override"]
        assert isinstance(override, ast.Dict)
        for key, value in zip(override.keys, override.values, strict=True):
            assert isinstance(key, ast.Name) and isinstance(value, ast.Constant)
            registered[value.value].append(key.id)
    return dict(registered), imported


def _input_fields(package: Path, module: str, class_name: str) -> set[str]:
    """The input field names of ``class_name``, read from its generated file."""
    relative = module.removeprefix(f"{PACKAGE}.").replace(".", "/") + ".py"
    tree = ast.parse((package / relative).read_text())
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    (base,) = [
        base
        for base in classes[class_name].bases
        if isinstance(base, ast.Subscript) and getattr(base.value, "id", None) == "ModuleBase"
    ]
    assert isinstance(base.slice, ast.Tuple)
    input_class = base.slice.elts[0]
    assert isinstance(input_class, ast.Name)
    return {
        node.target.id
        for node in classes[input_class.id].body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }


def _assert_registry_covers_pipeline(package: Path) -> None:
    pipeline = _pipeline_inputs(package)
    registered, imported = _registry(package)
    for module_type, entries in pipeline.items():
        names = registered.get(module_type, [])
        assert len(names) == 1, f"{module_type!r} registered {len(names)} times: {names}"
        fields = _input_fields(package, *imported[names[0]])
        for inputs in entries:
            assert inputs == fields, (module_type, inputs, fields)


def _generate(config: GenerationConfig) -> Path:
    assert run_codegen(config) is True, f"run_codegen refused {config}"
    return config.output_path


@requires_license
@pytest.mark.parametrize("model", LIVE_MODELS)
def test_live_package_registers_each_pipeline_module_type_once(model: str, tmp_path: Path):
    package = _generate(
        GenerationConfig(
            models_path=FIXTURES_DIR / model, output_path=tmp_path / "pkg", package_name=PACKAGE
        )
    )
    _assert_registry_covers_pipeline(package)


def test_the_snapshot_inventory_is_the_oracles():
    assert len(SNAPSHOTS) == 22


@pytest.mark.parametrize("snapshot", SNAPSHOTS)
def test_oracle_package_registers_each_pipeline_module_type_once(snapshot: str, tmp_path: Path):
    config = GenerationConfig(
        from_snapshot=REPO_ROOT / snapshot, output_path=tmp_path / "pkg", package_name=PACKAGE
    )
    if not run_codegen(config):
        pytest.skip(f"{snapshot} is refused by design; the oracle pins its refusal")
    _assert_registry_covers_pipeline(config.output_path)
