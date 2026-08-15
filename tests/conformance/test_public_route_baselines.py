"""The public route carries what the two v5 baseline-capture scripts used to.

`scripts/capture_baseline_yaml.py` (ledger L-039) and
`scripts/capture_pipeline_baselines.py` (L-040) captured committed baselines — pipeline YAML,
ComputationGraph JSON, registry `__init__.py` — by driving `build_full_graph_from_snapshot`
over v5 extraction snapshots. Both halves of that input retire with the v5 family, so neither
script can be repointed; a v6 capture driver beside the public route is the second capture
path ruling 1 declined. The replacement is the public route itself: `run_codegen` reading a
committed v6 `instance_graph_snapshot.json`, license-free, regenerating those artifacts on
demand instead of storing them.

`tests/conftest.py` (L-289) is the third row here. Its v5 helper `snapshot_fixture()` retires;
its v6 replacements `instance_graph_fixture()` and `exact_graph_from_fixture()` are what the
repointed tests read, and what this file proves read the same thing the product does.

All three rows' previous proof nodes lived in `tests/conformance/test_gen_registry.py`, which
retires on its own recorded disposition (L-148). These nodes are their replacement.

License-free by construction: every input is a committed v6 snapshot.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import exact_graph_from_fixture, instance_graph_fixture

#: A committed fixture with a sealed v6 graph and a wide package: 79 pipeline entries across
#: two declaring files, arrayed occurrences, and five module-class collisions that exercise
#: the registry's aliasing. A narrower fixture would prove less about the same code.
FIXTURE = "solar_battery_d5"
PACKAGE = "sb"

_MODULE_IMPORT = re.compile(rf"^from {PACKAGE}\.modules\.(\S+) import ", re.MULTILINE)


def _generate(output: Path) -> Path:
    generated = run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=instance_graph_fixture(FIXTURE),
            package_name=PACKAGE,
            overwrite=True,
        )
    )
    assert generated is True, f"generation failed for {FIXTURE}"
    return output


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    return _generate(tmp_path_factory.mktemp("baseline") / "pkg")


def test_the_public_route_writes_the_pipeline_yaml_the_capture_script_used_to(
    package: Path,
) -> None:
    """L-039's responsibility: a pipeline YAML whose every reference resolves on disk.

    A captured baseline was worth keeping only because the YAML is not self-describing —
    its module types and its entry-point block point at other files, and a capture froze a
    known-good set of those pointers. Regenerating instead of freezing is only an
    improvement if the pointers are checked, so they are checked here, in both directions
    and against the filesystem rather than against the YAML's own text.
    """
    document = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    assert set(document) == {"metadata", "modules"}
    modules = document["modules"]

    # The entry block names every generated inputs JSON, and only those. Read the expected
    # set off the inputs directory, not out of the graph that also wrote the YAML.
    entry_inputs = modules["entry_fusion"]["inputs"]
    on_disk = {path.stem for path in (package / "inputs").glob("*.json")}
    assert set(entry_inputs) == on_disk
    for group, declaration in entry_inputs.items():
        schema_class, json_path = declaration.split()
        assert (package / "pipelines" / json_path).resolve().is_file()
        assert (package / "schemas" / f"{group}.py").is_file()
        assert f"class {schema_class}" in (package / "schemas" / f"{group}.py").read_text()

    # Every exit line writes its own file. Two channels sharing an output filename is the
    # collision the alias machinery exists to prevent, and it is invisible in a frozen
    # baseline that happened not to contain one.
    exit_files = [
        declaration.split()[-1] for declaration in modules["exit_point"]["outputs"].values()
    ]
    assert len(exit_files) == len(set(exit_files))

    # Every calculation module's `module_type` is `<subpackage>.<Name>`, and the subpackage
    # has to be a real directory under modules/. (The name half is the registry's to
    # resolve, and aliases collided class names, so it is checked there and not here.)
    calculations = {
        name: body
        for name, body in modules.items()
        if name not in {"entry_fusion", "exit_point"}
    }
    assert len(calculations) == 77
    for name, body in calculations.items():
        subpackage = body["module_type"].rsplit(".", 1)[0]
        directory = package / "modules" / subpackage.replace(".", "/")
        assert directory.is_dir(), f"{name}: no modules/{subpackage}"


def test_the_registry_and_the_module_tree_agree_in_both_directions(package: Path) -> None:
    """L-040's first half: the registry `__init__.py` names the module tree exactly.

    One direction alone is half a check. An import with no file is a package that fails to
    load; a file with no import is a module the pipeline can never reach, and the captured
    baseline could not see either, because it froze the registry and the tree together.
    """
    imported = set(_MODULE_IMPORT.findall((package / "__init__.py").read_text()))
    written = {
        str(source.relative_to(package / "modules").with_suffix("")).replace("/", ".")
        for source in (package / "modules").rglob("*.py")
        if source.name != "__init__.py"
    }
    assert imported == written


def test_regenerating_from_the_same_v6_snapshot_is_byte_identical(tmp_path: Path) -> None:
    """L-040's second half, and the premise the whole replacement rests on.

    A stored baseline is a claim that generation is reproducible; deleting the store and
    regenerating on demand is only safe if that claim is true. So it is asserted directly:
    two runs from the same sealed graph produce the same bytes, for every file, not just the
    two the scripts happened to capture.
    """
    first = _generate(tmp_path / "first")
    second = _generate(tmp_path / "second")

    def tree(root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    left, right = tree(first), tree(second)
    assert set(left) == set(right)
    differing = sorted(name for name in left if left[name] != right[name])
    assert differing == [], differing


def test_the_v6_fixture_helper_reads_what_the_product_reads(package: Path) -> None:
    """L-289's responsibility: the helper and the CLI resolve to one graph.

    `exact_graph_from_fixture` exists so a repointed test can read a fixture's graph without
    a licence. That is only sound while it is the *same* graph the shipped route generates
    from — otherwise every test repointed onto it is measuring a private copy. The pipeline
    YAML is the CLI's own rendering of its graph, so comparing module sets compares the two
    readers, not one reader with itself. `entry_fusion` and `exit_point` are the renderer's
    own two pseudo-modules and have no graph counterpart.
    """
    from_helper = {module.name for module in exact_graph_from_fixture(FIXTURE).modules}
    from_product = set(
        yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())["modules"]
    ) - {"entry_fusion", "exit_point"}
    assert from_helper == from_product
