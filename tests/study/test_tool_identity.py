"""Tool identity is literal and mechanical, and old records stay valid (spec SC7, design I2, I4).

``tool.path``, ``command[0]`` and every ``TOOL_SOURCE_FILES`` entry are written as literals
rather than derived from where a file sits. These checks hold the literals to the installed
package: each one names a file under the tool home, and each tool's source list names every
study module the tool imports, directly or through another, and nothing else.

The documents the moved tools write on the station fixture carry the ``sysml_codegen/study/``
prefix, and their digests recompute from the bytes under the tool home. ``verify`` needs teax,
so its document is checked the same way in ``tests/execution/test_study_station.py``. Documents
written before the move keep their ``scripts/study/`` prefix and still validate, because the
seven schemas are fusion-tea's bytes, pinned here.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from sysml_codegen.study import roots
from tests.study.conftest import (
    DATA_DIR,
    REPO_ROOT,
    SCHEMAS,
    STATION,
    STATION_AXES,
    STATION_BASELINE,
    STATION_IDENTITY,
    STATION_MANIFEST,
    STATION_PACKAGE,
    assert_post_move_tool_identity,
    environment_with_root,
)

PREFIX = "sysml_codegen/study/"
STUDY = "sysml_codegen.study"

#: Each covered tool, and the module whose ``TOOL_SOURCE_FILES`` names its sources.
#: ``indicators`` stamps the digest ``manifest.tool_source_digest()`` computes.
TOOLS = {
    "indicators": "manifest",
    "preflight": "preflight",
    "verify": "verify",
}
COVERED = ("manifest", "indicators", "preflight", "verify")


def _source(module: str) -> Path:
    return roots.TOOL_HOME / f"{PREFIX}{module}.py"


def _study_imports(module: str) -> set[str]:
    """The study modules ``module``'s source imports, anywhere in the file."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(_source(module).read_text())):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.module == STUDY:
                found.update(alias.name for alias in node.names)
            elif node.module.startswith(STUDY + "."):
                found.add(node.module.removeprefix(STUDY + ".").split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(STUDY + "."):
                    found.add(alias.name.removeprefix(STUDY + ".").split(".")[0])
    return found


def _closure(module: str) -> set[str]:
    seen: set[str] = set()
    pending = [module]
    while pending:
        name = pending.pop()
        if name not in seen:
            seen.add(name)
            pending.extend(_study_imports(name))
    return seen


def _tool_literals(module: str) -> set[str]:
    return {
        node.value
        for node in ast.walk(ast.parse(_source(module).read_text()))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("sysml_codegen/")
    }


@pytest.mark.parametrize("module", COVERED)
def test_every_tool_path_literal_names_a_file_under_the_tool_home(module: str) -> None:
    literals = _tool_literals(module)
    assert literals, f"{module} carries no tool-path literal"
    missing = sorted(path for path in literals if not (roots.TOOL_HOME / path).is_file())
    assert missing == []


@pytest.mark.parametrize("tool", sorted(TOOLS))
def test_a_tool_names_its_own_path(tool: str) -> None:
    assert f"{PREFIX}{tool}.py" in _tool_literals(tool)


@pytest.mark.parametrize("tool", sorted(TOOLS))
def test_a_tools_sources_are_exactly_the_study_modules_it_imports(tool: str) -> None:
    listed = importlib.import_module(f"{STUDY}.{TOOLS[tool]}").TOOL_SOURCE_FILES
    python = {path for path in listed if path.endswith(".py")}
    assert python == {f"{PREFIX}{module}.py" for module in _closure(tool)}
    assert all(path.startswith(PREFIX) for path in listed)
    schemas = _source("roots").parent / "schemas"
    assert {path for path in listed if not path.endswith(".py")} <= {
        f"{PREFIX}schemas/{schema.name}" for schema in schemas.iterdir()
    }


# ------------------------------------------------- documents on the station fixture (SC7)

#: Each document a default-lane tool writes on the station, and the schema it answers to.
STATION_RUNS: dict[str, tuple[tuple[str, ...], str]] = {
    "indicators": (
        ("indicators", "--package", str(STATION_PACKAGE), "--manifest", str(STATION_MANIFEST),
         "--groups", str(STATION_AXES)),
        "indicators.v1",
    ),
    "preflight gates": (
        ("preflight", "gates", "--package", str(STATION_PACKAGE),
         "--manifest", str(STATION_MANIFEST), "--groups", str(STATION_AXES),
         "--identity", str(STATION_IDENTITY), "--baseline-result", str(STATION_BASELINE)),
        "preflight_results.v1",
    ),
    "preflight clean": (
        ("preflight", "clean", "--package", str(STATION_PACKAGE)),
        "preflight_results.v1",
    ),
}


@pytest.mark.parametrize("run", sorted(STATION_RUNS))
def test_a_moved_tools_document_carries_the_installed_identity(
    run: str, tmp_path: Path, load_schema: Callable[[str], dict[str, Any]]
) -> None:
    (tool, *argv), schema = STATION_RUNS[run]
    out = tmp_path / "document.json"
    done = subprocess.run(
        [sys.executable, "-m", f"sysml_codegen.study.{tool}", *argv, "--out", str(out)],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=environment_with_root(STATION),
    )
    assert done.returncode == 0, done.stderr
    document = json.loads(out.read_text())
    jsonschema.validate(document, load_schema(schema))
    assert_post_move_tool_identity(document)


# ------------------------------------------------------- documents from before the move

PREMOVE = DATA_DIR / "premove"
#: The bytes fusion-tea committed at ``b06585709`` (``data/premove/PROVENANCE.md``).
PREMOVE_SHA256 = {
    "indicators.json": "4f0661405df83e6fc691b4c3fd9fee979b848bda49c3f5b511321e423e166972",
    "preflight_results.json": "f74d099d3a022307a73f34ead4f03373e1ffc1d5ca912c3bc15538315c1827d8",
    "verification_summary.json": (
        "2743773729503d1f8bd3b03c8ba44ea564689414f7c58333132d25be2cc34361"
    ),
    "integration-return.json": "a34ee542cad372634810f289bfd17be435f88e6f076c009bf40b88bc97aeb926",
}
#: The schema each pre-move document answers to. The integration return has none shipped.
PREMOVE_SCHEMAS = {
    "indicators.json": "indicators.v1",
    "preflight_results.json": "preflight_results.v1",
    "verification_summary.json": "verification_summary.v1",
}


def _is_pre_move(path: str) -> bool:
    return path.startswith("scripts/study/") or path == "scripts/integrate.py"


def test_the_pre_move_documents_are_fusion_teas_bytes() -> None:
    assert {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in PREMOVE.glob("*.json")
    } == PREMOVE_SHA256


@pytest.mark.parametrize("name", sorted(PREMOVE_SCHEMAS))
def test_a_pre_move_document_validates_against_the_unchanged_schema(
    name: str, load_schema: Callable[[str], dict[str, Any]]
) -> None:
    document = json.loads((PREMOVE / name).read_text())
    jsonschema.validate(document, load_schema(PREMOVE_SCHEMAS[name]))


@pytest.mark.parametrize("name", sorted(PREMOVE_SHA256))
def test_a_pre_move_document_keeps_its_pre_move_prefix(name: str) -> None:
    """The prefix tells the eras apart; an old record is read as written, never rewritten."""
    document = json.loads((PREMOVE / name).read_text())
    tool = document["tool"]
    assert _is_pre_move(tool["path"]), tool["path"]
    assert all(_is_pre_move(entry["path"]) for entry in tool["source_digest"]["files"])
    if "command" in document:
        assert document["command"][0] == tool["path"]


# ------------------------------------------------------------------------- the schemas

#: The seven schema files, byte for byte as fusion-tea committed them at ``b06585709`` (I2).
SCHEMA_SHA256 = {
    "axis_declaration.v1.schema.json":
        "cffa3d8adc0eae833245091b529ecfb5ad784ad6fea2c3714c460c6d3061eb2b",
    "baseline_result.v1.schema.json":
        "103cf640a5c9d4a2d7b7fbe13efa887fd8471ffe79a11cc0a7fc4f71ff86e53b",
    "indicators.v1.schema.json":
        "96390664ce8eb5938bfe19eb435603e107892bd5082edf8a03514d588a081996",
    "package_identity.v1.schema.json":
        "d312ac300f1f639bccad3300e5c617658fe307594eaf9deadea66d6162008ad9",
    "preflight_results.v1.schema.json":
        "c6d25e857e533a4f92666533b31f3cd86641521c159e6cc300fb85e62dda27be",
    "study_package_manifest.v1.schema.json":
        "7e70dfa1db56e91e1e628174b7383a8ff96200c55ef7c8fd634afaef7556f1f8",
    "verification_summary.v1.schema.json":
        "7afe14d745ac7241116096f0a93af35f675d3570c96e5b0e080fac427a17fc87",
}


def test_the_seven_schemas_are_fusion_teas_bytes() -> None:
    assert {
        resource.name: hashlib.sha256(resource.read_bytes()).hexdigest()
        for resource in SCHEMAS.iterdir()
        if resource.name.endswith(".schema.json")
    } == SCHEMA_SHA256


def test_the_summary_schema_requires_the_full_digest_shape() -> None:
    """A record copies the tools' digests and its oracle digest in this shape, so the file
    list is required, not optional (fusion-tea ``test_record_template.py``)."""
    schema = json.loads((SCHEMAS / "verification_summary.v1.schema.json").read_text())
    assert '"required": ["recipe", "digest", "files"]' in json.dumps(schema)
