"""Tool identity is literal and mechanical (design D7, I4).

``tool.path``, ``command[0]`` and every ``TOOL_SOURCE_FILES`` entry are written as literals
rather than derived from where a file sits. These checks hold the literals to the installed
package: each one names a file under the tool home, and each tool's source list names every
study module the tool imports, directly or through another, and nothing else.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from sysml_codegen.study import roots

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
