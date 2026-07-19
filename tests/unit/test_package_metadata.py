"""Package metadata must prevent an incompatible companion pairing."""

import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version


def test_declared_metadata_requires_compatible_companion() -> None:
    project_file = Path(__file__).resolve().parents[2] / "pyproject.toml"
    project = tomllib.loads(project_file.read_text(encoding="utf-8"))
    requirements = (Requirement(value) for value in project["project"]["dependencies"])
    companion = next(
        requirement for requirement in requirements if requirement.name == "agentic-mbse"
    )

    assert Version("0.1.0") not in companion.specifier
    assert Version("0.1.1") in companion.specifier
