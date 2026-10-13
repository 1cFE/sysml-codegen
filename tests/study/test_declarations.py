"""A target's integrate declaration loads exactly, or is refused as malformed (B5, B6, B10, B12).

``integrate`` reports a :class:`DeclarationError` at gate 0 as ``input-invalid``, so every
shape refused here is a request the seam refuses before it judges anything.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.study.declarations import (
    DEFAULT_BACKUP_PREFIX,
    UNDECLARED,
    DeclarationError,
    GateDeclaration,
    IntegrateDeclaration,
    load_declaration,
)

TABLE = "[tool.sysml-codegen.integrate]\n"
#: Design Appendix D's fusion-tea declaration, verbatim.
FUSION_TEA = """\
[tool.sysml-codegen.integrate]
environment = ["STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL", \
"STOP_PARSER_CODEGEN_WHEEL", "STOP_PARSER_COSTINGFE_WHEEL", "STOP_PARSER_TEAX_ROOT"]
backup-prefix = "fusion-tea-integration-backup-"
record-distributions = { costingfe = "1costingfe" }
[tool.sysml-codegen.integrate.gates.pinned-packages]
target = "tests/test_dependency_provenance.py"
checked = "the pinned package revisions and installed wheel artifacts"
[tool.sysml-codegen.integrate.gates.model-family-spine]
target = "tests/models/test_model_family_spines.py"
checked = "the canonical tree, the family twins and the tracked census"
"""


def _project(root: Path, pyproject: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(pyproject)
    return root


def _gate(name: str, body: str) -> str:
    return f"[tool.sysml-codegen.integrate.gates.{name}]\n{body}"


# ------------------------------------------------------------------- what loads


def test_no_pyproject_is_undeclared(tmp_path: Path) -> None:
    assert load_declaration(tmp_path) == UNDECLARED


@pytest.mark.parametrize(
    "pyproject",
    ['[project]\nname = "x"\n', '[tool.other]\nx = 1\n', '[tool.sysml-codegen]\nother = 1\n'],
)
def test_a_pyproject_without_the_table_is_undeclared(tmp_path: Path, pyproject: str) -> None:
    assert load_declaration(_project(tmp_path, pyproject)) == UNDECLARED


def test_undeclared_declares_nothing() -> None:
    assert dict(UNDECLARED.gates) == {}
    assert UNDECLARED.environment == ()
    assert UNDECLARED.record_distributions == ()
    assert UNDECLARED.backup_prefix == DEFAULT_BACKUP_PREFIX == "sysml-codegen-integration-backup-"


def test_an_empty_table_is_undeclared(tmp_path: Path) -> None:
    assert load_declaration(_project(tmp_path, TABLE)) == UNDECLARED


def test_fusion_teas_declaration_loads_to_its_own_values(tmp_path: Path) -> None:
    declaration = load_declaration(_project(tmp_path, FUSION_TEA))
    assert declaration == IntegrateDeclaration(
        gates={
            "pinned-packages": GateDeclaration(
                target="tests/test_dependency_provenance.py",
                checked="the pinned package revisions and installed wheel artifacts",
            ),
            "model-family-spine": GateDeclaration(
                target="tests/models/test_model_family_spines.py",
                checked="the canonical tree, the family twins and the tracked census",
            ),
        },
        environment=(
            "STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL", "STOP_PARSER_CODEGEN_WHEEL",
            "STOP_PARSER_COSTINGFE_WHEEL", "STOP_PARSER_TEAX_ROOT",
        ),
        record_distributions=(("costingfe", "1costingfe"),),
        backup_prefix="fusion-tea-integration-backup-",
    )


def test_a_target_may_name_a_node_inside_its_file(tmp_path: Path) -> None:
    pyproject = TABLE + _gate(
        "pinned-packages", 'target = "tests/pins.py::test_pins"\nchecked = "the pins"\n'
    )
    declaration = load_declaration(_project(tmp_path, pyproject))
    assert declaration.gates["pinned-packages"].target == "tests/pins.py::test_pins"


def test_one_declared_gate_leaves_the_other_undeclared(tmp_path: Path) -> None:
    pyproject = TABLE + _gate("model-family-spine", 'target = "t.py"\nchecked = "the tree"\n')
    assert set(load_declaration(_project(tmp_path, pyproject)).gates) == {"model-family-spine"}


def test_the_loaded_gates_cannot_be_edited(tmp_path: Path) -> None:
    gates = load_declaration(_project(tmp_path, FUSION_TEA)).gates
    with pytest.raises(TypeError):
        gates["pinned-packages"] = GateDeclaration(target="x.py", checked="x")  # type: ignore[index]


# ---------------------------------------------------------------- what is refused

MALFORMED = {
    "not TOML": ("[tool.sysml-codegen.integrate\n", "not valid TOML"),
    "integrate is not a table": ("[tool.sysml-codegen]\nintegrate = 1\n", "must be a table"),
    "sysml-codegen is not a table": ('[tool]\nsysml-codegen = "x"\n', "must be a table"),
    "an unknown key": (TABLE + "gate = 1\n", "unknown key gate"),
    "gates is not a table": (TABLE + 'gates = "x"\n', "gates must be a table"),
    "an unknown gate": (
        TABLE + _gate("lint", 'target = "t.py"\nchecked = "x"\n'), "lint is not a repo-scope gate"
    ),
    "a gate that is not a table": (TABLE + "gates = { pinned-packages = 1 }\n", "must be a table"),
    "a gate without checked": (
        TABLE + _gate("pinned-packages", 'target = "tests/t.py"\n'), "has no checked"
    ),
    "a gate without target": (
        TABLE + _gate("pinned-packages", 'checked = "the pins"\n'), "has no target"
    ),
    "a gate with a third key": (
        TABLE + _gate("pinned-packages", 'target = "t.py"\nchecked = "x"\nscope = "repo"\n'),
        "unknown key scope",
    ),
    "an empty checked": (
        TABLE + _gate("pinned-packages", 'target = "t.py"\nchecked = ""\n'),
        "checked must be a non-empty string",
    ),
    "a blank checked": (
        TABLE + _gate("pinned-packages", 'target = "t.py"\nchecked = "  "\n'),
        "checked must be a non-empty string",
    ),
    "a checked that is not a string": (
        TABLE + _gate("pinned-packages", 'target = "t.py"\nchecked = true\n'),
        "checked must be a non-empty string",
    ),
    "an empty target": (
        TABLE + _gate("pinned-packages", 'target = ""\nchecked = "x"\n'),
        "target must be a non-empty string",
    ),
    "a target that is not a string": (
        TABLE + _gate("pinned-packages", 'target = ["t.py"]\nchecked = "x"\n'),
        "target must be a non-empty string",
    ),
    "an absolute target": (
        TABLE + _gate("pinned-packages", 'target = "/etc/t.py"\nchecked = "x"\n'), "is absolute"
    ),
    "a ../ target": (
        TABLE + _gate("model-family-spine", 'target = "../t.py"\nchecked = "x"\n'),
        "resolves outside the project root",
    ),
    "a target that normalizes outside": (
        TABLE + _gate("model-family-spine", 'target = "tests/../../t.py::n"\nchecked = "x"\n'),
        "resolves outside the project root",
    ),
    "a target with no file": (
        TABLE + _gate("pinned-packages", 'target = "::test_x"\nchecked = "x"\n'), "names no file"
    ),
    "environment is not an array": (TABLE + 'environment = "A"\n', "must be an array"),
    "an environment entry that is not a name": (
        TABLE + 'environment = ["A-B"]\n', "'A-B' is not a variable name"
    ),
    "an environment entry starting with a digit": (
        TABLE + 'environment = ["1A"]\n', "'1A' is not a variable name"
    ),
    "an environment entry that is not a string": (
        TABLE + "environment = [1]\n", "1 is not a variable name"
    ),
    "a duplicated environment name": (TABLE + 'environment = ["A", "A"]\n', "names A twice"),
    "record-distributions is not a table": (
        TABLE + 'record-distributions = "x"\n', "record-distributions must be a table"
    ),
    "a distribution key that is not an identifier": (
        TABLE + 'record-distributions = { "cost-fe" = "1costingfe" }\n',
        "'cost-fe' is not an identifier",
    ),
    "a distribution key that is a fixed key": (
        TABLE + 'record-distributions = { teax_revision = "teax" }\n',
        "teax_revision is a fixed toolchain key",
    ),
    "an empty distribution": (
        TABLE + 'record-distributions = { costingfe = "" }\n',
        "record-distributions.costingfe must be a non-empty string",
    ),
    "an empty backup prefix": (
        TABLE + 'backup-prefix = ""\n', "backup-prefix must be a non-empty string"
    ),
    "a backup prefix with a slash": (TABLE + 'backup-prefix = "a/b-"\n', "contains '/'"),
    "a backup prefix that is not a string": (
        TABLE + "backup-prefix = 3\n", "backup-prefix must be a non-empty string"
    ),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_a_malformed_declaration_is_refused(tmp_path: Path, case: str) -> None:
    pyproject, reason = MALFORMED[case]
    with pytest.raises(DeclarationError, match=reason):
        load_declaration(_project(tmp_path / "project", pyproject))


def test_a_target_through_a_symlink_out_of_the_project_is_refused(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    root = _project(
        tmp_path / "project",
        TABLE + _gate("pinned-packages", 'target = "escape/t.py"\nchecked = "x"\n'),
    )
    (root / "escape").symlink_to(outside)
    with pytest.raises(DeclarationError, match="resolves outside the project root"):
        load_declaration(root)


def test_a_refusal_cites_the_file_relative_to_the_project(tmp_path: Path) -> None:
    """The message lands in a return document, whose paths never depend on where it ran."""
    root = _project(tmp_path, TABLE + _gate("pinned-packages", 'target = "t.py"\n'))
    with pytest.raises(DeclarationError) as caught:
        load_declaration(root)
    assert str(tmp_path) not in str(caught.value)
    assert str(caught.value).startswith(
        "pyproject.toml [tool.sysml-codegen.integrate.gates.pinned-packages]"
    )
