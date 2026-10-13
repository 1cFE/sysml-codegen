"""``integrate`` judges any target from what that target declares (spec SC8; B4–B7, B10, B12).

Design DD8, DD10, I7, I11 and I12. Every run is a subprocess against the station copied into
a fresh git repository. teax is replaced by a stub ``simkit`` package in a git repository of
its own, and the licence by a dummy value: gate 0 checks only that the licence variable is
exported, and no default-lane run reaches a gate that uses it. The one license-lane test, at
the end, reaches gate 5 and needs the real licence for regeneration and the snapshot.
"""

from __future__ import annotations

import ast
import json
import os
import re
from importlib import metadata
from pathlib import Path

import pytest

from sysml_codegen.study import integrate, roots
from tests.conftest import requires_license
from tests.study.conftest import (
    IntegrateRun,
    commit_stub_simkit,
    git_head,
    integration_request,
    run_integrate,
    seam_environment,
)

DUMMY_LICENSE = "dummy-licence-gate-zero-only-checks-presence"
#: The station's own declaration (``tests/fixtures/study_station/pyproject.toml``).
STATION_GATES = {
    "pinned-packages": ("gates/check_pins.py", "the fixture's toolchain imports"),
    "model-family-spine": (
        "gates/check_census.py", "the tracked entry-point census against the committed package"
    ),
}
FIXED_TOOLCHAIN = ["agentic_mbse", "sysml_codegen", "teax_revision", "teax_module_path"]


@pytest.fixture
def stub_teax(tmp_path: Path) -> Path:
    return commit_stub_simkit(tmp_path / "stub-teax")


def declare(
    repo: Path,
    *,
    gates: dict[str, tuple[str, str]],
    environment: tuple[str, ...] = (),
    distributions: dict[str, str] | None = None,
) -> None:
    """Replace the repository's declaration. The package tree, which gate 0 checks, is untouched."""
    lines = ["[tool.sysml-codegen.integrate]", f"environment = {json.dumps(list(environment))}"]
    if distributions:
        pairs = ", ".join(f'{key} = "{value}"' for key, value in distributions.items())
        lines.append(f"record-distributions = {{ {pairs} }}")
    for name, (target, checked) in gates.items():
        lines += [f"[tool.sysml-codegen.integrate.gates.{name}]",
                  f'target = "{target}"', f'checked = "{checked}"']
    (repo / "pyproject.toml").write_text("\n".join(lines) + "\n")


def run(
    repo: Path, tmp_path: Path, *, teax: Path | None, pythonpath: Path | None = None,
    license_key: str | None = DUMMY_LICENSE, exported: dict[str, str] | None = None,
    **overrides: str | None,
) -> IntegrateRun:
    extra = dict(exported or {})
    if pythonpath is not None:
        extra["PYTHONPATH"] = str(pythonpath)
    env = seam_environment(teax=teax, license_key=license_key, tmpdir=tmp_path / "tmp", **extra)
    return run_integrate(repo, integration_request(repo, tmp_path / "out", **overrides), env)


def assert_blocker(result: IntegrateRun, *, gate: str, mode: str, condition: str) -> dict:
    assert result.returncode == 1, result.stderr
    assert result.document["class"] == "BLOCKER"
    blocker: dict = result.document["blocker"]
    assert (blocker["gate"], blocker["mode"], blocker["condition"]) == (gate, mode, condition), (
        blocker
    )
    return blocker


# ------------------------------------------------------------- repo-scope gates (B5, B12)


def test_an_undeclared_pinned_packages_gate_blocks_as_unasked(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    """Spec D8: an undeclared repo gate could not run; it did not pass. Nothing ran it."""
    declare(station_repo, gates={"model-family-spine": STATION_GATES["model-family-spine"]})
    result = run(station_repo, tmp_path, teax=stub_teax)
    blocker = assert_blocker(
        result, gate="pinned-packages", mode="could_not_run", condition="input-missing"
    )
    assert "[tool.sysml-codegen.integrate.gates.pinned-packages]" in blocker["detail"]
    row = result.row("pinned-packages")
    assert row["producer"] == row["checked"] == "not declared"
    assert row["status"] == "did not run"
    assert not (tmp_path / "out" / "junit").exists(), "an undeclared gate ran a producer"


def test_a_declared_pinned_packages_gate_runs_its_target_and_passes(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    result = run(station_repo, tmp_path, teax=stub_teax)
    row = result.row("pinned-packages")
    assert row["status"] == "pass"
    assert (row["producer"], row["checked"]) == STATION_GATES["pinned-packages"]
    assert row["detail"] == "gates/check_pins.py passed"
    assert row["evidence"] == ["../out/junit/pinned-packages.xml"]
    assert_blocker(result, gate="teax-revision", mode="could_not_run", condition="input-missing")


def test_a_declared_pinned_packages_gate_that_fails_refuses(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    (station_repo / "gates" / "check_refuses.py").write_text(
        "def test_a_pin_has_drifted():\n    assert False, 'pinned revision moved'\n"
    )
    declare(station_repo, gates={
        "pinned-packages": ("gates/check_refuses.py", "a pin that has drifted"),
        "model-family-spine": STATION_GATES["model-family-spine"],
    })
    result = run(station_repo, tmp_path, teax=stub_teax)
    blocker = assert_blocker(
        result, gate="pinned-packages", mode="refused", condition="toolchain-drift"
    )
    assert blocker["producer"] == "gates/check_refuses.py"
    assert blocker["evidence"] == ["../out/junit/pinned-packages.xml"]
    row = result.row("pinned-packages")
    assert (row["status"], row["checked"]) == ("fail", "a pin that has drifted")


def test_rows_1a_and_5_state_only_what_the_station_declared(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    """B12: what a return says a repo gate examined is the target's own declared text,
    whether or not the sequence reached the gate."""
    result = run(station_repo, tmp_path, teax=stub_teax)
    for gate, (target, checked) in STATION_GATES.items():
        row = result.row(gate)
        assert (row["producer"], row["checked"]) == (target, checked)
    assert result.row("model-family-spine")["status"] == "not reached"


def test_the_ten_gates_keep_their_order_and_scope_under_a_declaration(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    result = run(station_repo, tmp_path, teax=stub_teax)
    assert [(row["gate"], row["scope"]) for row in result.document["gates"]] == [
        (gate.name, gate.scope) for gate in integrate.GATES
    ]


# ----------------------------------------------------------------- gate 1b (B7, DD10)


def test_gate_1b_refuses_a_teax_revision_the_request_did_not_name(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    result = run(station_repo, tmp_path, teax=stub_teax, expected_teax_revision="0" * 40)
    blocker = assert_blocker(
        result, gate="teax-revision", mode="refused", condition="toolchain-drift"
    )
    assert (blocker["expected"], blocker["actual"]) == ("0" * 40, git_head(stub_teax))


def test_gate_1b_cannot_run_without_teax_simkit_path(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    """DD10: simkit still imports, from ``PYTHONPATH``, so gate 0 passes; but the revision
    comes only from ``TEAX_SIMKIT_PATH``, so gate 1b compares nothing and does not pass."""
    result = run(
        station_repo, tmp_path, teax=None, pythonpath=stub_teax,
        expected_teax_revision=git_head(stub_teax),
    )
    blocker = assert_blocker(
        result, gate="teax-revision", mode="could_not_run", condition="env-missing"
    )
    assert "TEAX_SIMKIT_PATH is not set" in blocker["detail"]
    assert result.row("pinned-packages")["status"] == "pass"


# --------------------------------------------------------- the environment sweep (B4)


def test_a_declared_variable_left_unexported_blocks_at_gate_zero(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    declare(station_repo, gates=STATION_GATES, environment=("STATION_GAUGE_FEED",))
    result = run(station_repo, tmp_path, teax=stub_teax)
    blocker = assert_blocker(
        result, gate="preconditions", mode="could_not_run", condition="env-missing"
    )
    assert blocker["detail"] == "the environment does not export: STATION_GAUGE_FEED"
    assert {row["status"] for row in result.document["gates"]} == {"not reached"}


def test_a_declared_variable_that_is_exported_passes_the_sweep(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    declare(station_repo, gates=STATION_GATES, environment=("STATION_GAUGE_FEED",))
    result = run(
        station_repo, tmp_path, teax=stub_teax, exported={"STATION_GAUGE_FEED": "gauge.csv"}
    )
    assert result.document["blocker"]["gate"] != "preconditions"


def test_a_fixed_variable_declared_again_is_swept_once(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    declare(station_repo, gates=STATION_GATES, environment=("SYSIDE_LICENSE_KEY",))
    result = run(station_repo, tmp_path, teax=stub_teax, license_key=None)
    blocker = assert_blocker(
        result, gate="preconditions", mode="could_not_run", condition="env-missing"
    )
    assert blocker["detail"] == "the environment does not export: SYSIDE_LICENSE_KEY"


# ------------------------------------------------------ a malformed declaration (B5, B12)


@pytest.mark.parametrize(
    ("gate_body", "reason"),
    [
        ('target = "gates/check_pins.py"', "has no checked"),
        ('target = "/etc/check_pins.py"\nchecked = "pins"', "is absolute"),
        ('target = "../check_pins.py"\nchecked = "pins"', "resolves outside the project root"),
    ],
    ids=["no checked", "absolute target", "parent target"],
)
def test_a_malformed_declaration_blocks_at_gate_zero_as_input_invalid(
    station_repo: Path, stub_teax: Path, tmp_path: Path, gate_body: str, reason: str
) -> None:
    (station_repo / "pyproject.toml").write_text(
        f"[tool.sysml-codegen.integrate.gates.pinned-packages]\n{gate_body}\n"
    )
    result = run(station_repo, tmp_path, teax=stub_teax)
    blocker = assert_blocker(
        result, gate="preconditions", mode="could_not_run", condition="input-invalid"
    )
    assert reason in blocker["detail"]
    for gate in STATION_GATES:
        assert result.row(gate)["producer"] == result.row(gate)["checked"] == "not declared"
    assert not (tmp_path / "out").exists(), "the seam acted on a declaration it refused"


# ------------------------------------------------------------ the toolchain block (B6)


def test_the_toolchain_records_the_fixed_keys_and_nothing_undeclared(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    toolchain = run(station_repo, tmp_path, teax=stub_teax).document["toolchain"]
    assert list(toolchain) == FIXED_TOOLCHAIN
    assert toolchain["teax_revision"] == git_head(stub_teax)
    assert toolchain["teax_module_path"] == str(stub_teax / "simkit")


def test_a_declared_distribution_is_recorded_beside_the_fixed_keys(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    declare(station_repo, gates=STATION_GATES, distributions={"templating": "jinja2"})
    toolchain = run(station_repo, tmp_path, teax=stub_teax).document["toolchain"]
    assert list(toolchain) == [*FIXED_TOOLCHAIN[:2], "templating", *FIXED_TOOLCHAIN[2:]]
    assert toolchain["templating"] == metadata.version("jinja2")


def test_without_teax_simkit_path_the_recorded_teax_revision_is_null(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    """I12: a recorded teax revision comes from ``TEAX_SIMKIT_PATH`` or is not recorded."""
    toolchain = run(station_repo, tmp_path, teax=None, pythonpath=stub_teax).document["toolchain"]
    assert toolchain["teax_revision"] is None
    assert toolchain["teax_module_path"] == str(stub_teax / "simkit")


# ------------------------------------------------------------------ without teax (B9, I9)


def test_without_teax_the_seam_blocks_at_gate_zero_naming_teax_and_runs_no_producer(
    station_repo: Path, tmp_path: Path
) -> None:
    result = run(station_repo, tmp_path, teax=None)
    blocker = assert_blocker(
        result, gate="preconditions", mode="could_not_run", condition="env-missing"
    )
    assert "teax" in blocker["detail"]
    assert "TEAX_SIMKIT_PATH is not set" in blocker["detail"]
    out = tmp_path / "out"
    assert sorted(path.name for path in out.iterdir()) == ["integration_return.json"], (
        "a producer ran past a gate-0 refusal"
    )


def test_a_teax_simkit_path_that_holds_no_simkit_blocks_at_gate_zero(
    station_repo: Path, tmp_path: Path
) -> None:
    empty = tmp_path / "not-simkit"
    empty.mkdir()
    result = run(station_repo, tmp_path, teax=empty)
    blocker = assert_blocker(
        result, gate="preconditions", mode="could_not_run", condition="env-missing"
    )
    assert blocker["detail"] == (
        f"TEAX_SIMKIT_PATH={empty} has no simkit/__init__.py, so it names no teax simkit root"
    )


# ------------------------------------------------------------------ backup prefix (B10)


@pytest.mark.parametrize(
    ("declared", "prefix"),
    [(True, "station-integration-backup-"), (False, "sysml-codegen-integration-backup-")],
    ids=["declared", "default"],
)
def test_the_package_is_backed_up_under_the_declared_prefix(
    station_repo: Path, stub_teax: Path, tmp_path: Path, declared: bool, prefix: str
) -> None:
    if not declared:
        (station_repo / "pyproject.toml").unlink()
    run(station_repo, tmp_path, teax=stub_teax)
    location = json.loads((tmp_path / "out" / "backup-location.json").read_text())
    backup = Path(location["backup"])
    assert backup.parent.parent == tmp_path / "tmp"
    assert backup.parent.name.startswith(prefix)
    assert (backup / "contracts" / "model_contract.json").is_file()


# ------------------------------------------- integrate names nothing of any target (SC8)

SOURCE = roots.TOOL_HOME / "sysml_codegen" / "study" / "integrate.py"
#: A Python file named inside a string: a path or a bare file name ending ``.py``.
PYTHON_FILE = re.compile(r"[\w./-]*\w\.py\b")


def _code_strings() -> list[str]:
    """Every string integrate's code holds, f-string parts included; docstrings excluded."""
    tree = ast.parse(SOURCE.read_text())
    docstrings = {
        id(node.value) for node in ast.walk(tree)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
    }
    return [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def test_integrate_names_no_target_test_file() -> None:
    """Every Python file integrate names is one of its own study modules, or the one file gate
    0 requires under ``TEAX_SIMKIT_PATH`` (DD10). It names no test path at all."""
    strings = _code_strings()
    named = {token for text in strings for token in PYTHON_FILE.findall(text)}
    own = {path.name for path in SOURCE.parent.glob("*.py")} | {"simkit/__init__.py"}
    foreign = sorted(
        token for token in named
        if not (token in own or (token.startswith("sysml_codegen/study/")
                                 and (roots.TOOL_HOME / token).is_file()))
    )
    assert named and foreign == []
    assert not any("tests/" in text or "test_" in text for text in strings)


def test_integrate_reads_no_target_environment_variable() -> None:
    """The variables integrate reads or sets itself are its own; a target's are declared."""
    assert integrate.REQUIRED_ENV == ("SYSIDE_LICENSE_KEY",)
    keys: set[str] = set()
    for node in ast.walk(ast.parse(SOURCE.read_text())):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            if isinstance(node.value, ast.Name) and node.value.id.endswith("env"):
                keys.add(node.slice.value)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if (node.func.attr == "get" and isinstance(owner, ast.Name)
                    and owner.id.endswith("env") and isinstance(node.args[0], ast.Constant)):
                keys.add(node.args[0].value)
        elif isinstance(node, ast.Dict) and any(
            key is None and isinstance(value, ast.Name) and value.id.endswith("env")
            for key, value in zip(node.keys, node.values, strict=True)
        ):
            keys.update(key.value for key in node.keys if isinstance(key, ast.Constant))
    assert keys == {"PYTHONPATH", "STUDY_REQUIRE_TEAX", "TMPDIR"}


def test_integrate_records_no_target_only_distribution() -> None:
    """Only the two toolchain distributions every target has are fixed; the rest are declared."""
    recorded = {
        node.args[0].value for node in ast.walk(ast.parse(SOURCE.read_text()))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "installed_version" and isinstance(node.args[0], ast.Constant)
    }
    assert recorded == {"agentic-mbse", "sysml-codegen"}


# ------------------------------------------------------------- license lane: gate 5 (SC8)


@requires_license
def test_an_undeclared_model_family_spine_gate_blocks_as_unasked_after_gates_1a_to_4_pass(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    """Gates 2 and 4 regenerate the package and recapture the snapshot, so they need the
    licence; everything else here is the station and a stub teax."""
    declare(station_repo, gates={"pinned-packages": STATION_GATES["pinned-packages"]})
    result = run(
        station_repo, tmp_path, teax=stub_teax, license_key=os.environ["SYSIDE_LICENSE_KEY"],
        expected_teax_revision=git_head(stub_teax),
    )
    assert [row["status"] for row in result.document["gates"][:5]] == ["pass"] * 5, (
        result.stderr
    )
    blocker = assert_blocker(
        result, gate="model-family-spine", mode="could_not_run", condition="input-missing"
    )
    assert blocker["producer"] == "not declared"
    row = result.row("model-family-spine")
    assert (row["producer"], row["checked"], row["status"]) == (
        "not declared", "not declared", "did not run"
    )
