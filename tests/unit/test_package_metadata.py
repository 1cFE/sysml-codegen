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

    assert Version("0.1.1") not in companion.specifier
    assert Version("0.1.2") in companion.specifier


def test_lock_and_runtime_use_profile_v4_companion() -> None:
    import agentic_mbse
    from agentic_mbse.sysml.executable_profile import PROFILE_SEMANTIC_VERSION

    lock = (Path(__file__).resolve().parents[2] / "uv.lock").read_text(encoding="utf-8")
    companion = lock.split('name = "agentic-mbse"', maxsplit=1)[1].split("[[package]]", maxsplit=1)[
        0
    ]
    assert 'version = "0.1.2"' in companion
    assert agentic_mbse.__version__ == "0.1.2"
    assert PROFILE_SEMANTIC_VERSION == "executable-profile/v4"
