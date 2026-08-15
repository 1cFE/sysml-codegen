"""Gate 4C, row L-148: registry generation across module kinds, exact route.

The responsibility this replaces is REQ-REG-02 in
``tests/conformance/test_gen_registry.py``: every import the package registry
publishes points at a file a real generation wrote to disk, and the registry
covers every module kind the graph produced. Its repointed nodes drove **v5**
snapshots of ``catf_mfe_model``, ``chain_spike_model`` and
``solar_battery_model``, all of which the exact route refuses.

Two fixtures carry it. ``source_identity_mixed_consumers`` is the widest module
mix the exact route accepts — calculation modules, constraint modules, the
constraint report aggregator, and computed-attribute modules in one package —
and ``costed_cart_d5`` adds aggregation modules, which that fixture has none of.
Between them every ``ModuleKind`` the projection emits is covered, and the test
says so by comparing against the graph rather than against a hand-written list.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

CASES = [
    ("source_identity_mixed_consumers", "mixed_consumers"),
    ("costed_cart_d5", "costed_cart"),
]


def _generate(fixture: str, package_name: str, output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURES_DIR / fixture,
            output_path=output,
            package_name=package_name,
            pipeline_name="pipeline",
        )
    ), f"the exact route must generate {fixture}"
    return output


def _module_import_lines(registry: str, package_name: str) -> list[str]:
    return [
        line
        for line in registry.splitlines()
        if line.startswith(f"from {package_name}.modules.")
    ]


@pytest.mark.parametrize("fixture,package_name", CASES, ids=[case[0] for case in CASES])
def test_every_registry_import_points_at_a_file_on_disk(
    tmp_path: Path, fixture: str, package_name: str
) -> None:
    output = _generate(fixture, package_name, tmp_path / fixture)
    registry = (output / "__init__.py").read_text()

    imports = _module_import_lines(registry, package_name)
    assert imports, f"{fixture}'s registry publishes no module imports"

    missing = []
    for line in imports:
        match = re.match(rf"from {re.escape(package_name)}\.modules\.(\S+) import \S+", line)
        if match is None:
            continue
        relative = match.group(1).replace(".", "/") + ".py"
        if not (output / "modules" / relative).exists():
            missing.append(f"{line.strip()} -> modules/{relative}")
    assert missing == [], f"{fixture} registry imports with no file on disk:\n" + "\n".join(
        missing
    )


@pytest.mark.parametrize("fixture,package_name", CASES, ids=[case[0] for case in CASES])
def test_the_registry_covers_every_module_the_graph_projected(
    tmp_path: Path, fixture: str, package_name: str
) -> None:
    """Compared against the graph, so a silently dropped module fails here."""
    output = _generate(fixture, package_name, tmp_path / f"{fixture}-cover")
    graph = build_exact_pipeline_context([FIXTURES_DIR / fixture]).computation_graph
    registry = (output / "__init__.py").read_text()

    uncovered = [
        module.name for module in graph.modules if module.module_type.split(".")[-1] not in registry
    ]
    assert uncovered == [], f"{fixture}: modules absent from the registry: {uncovered}"


def test_the_two_fixtures_together_cover_every_projected_module_kind(tmp_path: Path) -> None:
    """The claim the parametrization rests on, stated instead of assumed."""
    from sysml_codegen.resolution.models import ModuleKind

    seen: set[ModuleKind] = set()
    for fixture, _package in CASES:
        graph = build_exact_pipeline_context([FIXTURES_DIR / fixture]).computation_graph
        seen.update(module.module_kind for module in graph.modules)

    uncovered = set(ModuleKind) - seen
    assert uncovered == set(), f"module kinds with no registry coverage: {uncovered}"


@pytest.mark.parametrize("fixture,package_name", CASES, ids=[case[0] for case in CASES])
def test_every_registry_class_name_is_a_valid_identifier(
    tmp_path: Path, fixture: str, package_name: str
) -> None:
    """A quoted or spaced SysML name must never reach a class name in the registry.

    Both halves of an aliased import are checked. Aliasing is how the registry
    keeps same-named module classes from colliding (``costed_cart_d5`` has four
    such names, one per rolled cost attribute across three assemblies), so the
    alias is a generated identifier too.
    """
    output = _generate(fixture, package_name, tmp_path / f"{fixture}-names")
    registry = (output / "__init__.py").read_text()
    for line in _module_import_lines(registry, package_name):
        imported = line.split(" import ", 1)[1].strip()
        for entry in imported.split(","):
            for name in entry.split(" as "):
                assert name.strip().isidentifier(), f"{fixture}: registry imports {name!r}"
