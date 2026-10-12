"""The operator guide is walked by strangers, so what it must contain is a test.

A guide missing a condition slug, an environment variable, an exit code or a declaration key
cannot possibly be followed, and it should fail here first rather than in a project that met
the gap. These tests check the guide is complete against ``integrate``'s own surface, not that
it is good.

Moved from fusion-tea's ``tests/study/test_integrate_guide_contract.py`` at ``b06585709`` and
rewritten for the guide that ships in the ``run-study`` bundle (design DD17, Appendix F). The
checks for one project's sealed-wheel home and decision record stay with that project's own
guide supplement.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from sysml_codegen.study import declarations, integrate, roots

RUN_STUDY = roots.TOOL_HOME / "sysml_codegen" / "assets" / "skills" / "run-study"
GUIDE = RUN_STUDY / "integration-guide.md"


@pytest.fixture(scope="module")
def guide() -> str:
    return GUIDE.read_text()


def test_guide_enumerates_every_condition_slug(guide: str) -> None:
    missing = [slug for slug in integrate.CONDITIONS if f"`{slug}`" not in guide]
    assert missing == [], "a caller reading these slugs has nowhere to look them up"
    assert len(integrate.CONDITIONS) == 15
    assert "fifteen" in guide


def test_guide_lists_every_environment_variable_the_seam_requires(guide: str) -> None:
    assert [name for name in integrate.REQUIRED_ENV if name not in guide] == []


def test_guide_states_every_exit_code(guide: str) -> None:
    for code in ("exit 0", "exit 1", "exit 2"):
        assert code in guide


def test_guide_states_the_two_exits_that_write_no_document(guide: str) -> None:
    """Exit 2 also covers an invocation that never started; the guide must say no file appears."""
    row = next(line for line in guide.splitlines() if line.startswith("| **exit 2**"))
    assert "argparse usage error" in row and "no project root" in row
    assert "no document was written" in row


def test_guide_names_every_flag_the_seam_accepts(guide: str) -> None:
    """An input with no stated source is an input the walker has to guess at."""
    flags = [
        action.option_strings[0]
        for action in integrate.build_parser()._actions
        if action.option_strings and action.option_strings[0] != "-h"
    ]
    assert [flag for flag in flags if flag not in guide] == []


def test_guide_names_every_gate_and_its_scope(guide: str) -> None:
    assert [gate.name for gate in integrate.GATES if f"`{gate.name}`" not in guide] == []
    assert "scope" in guide and "repo" in guide and "request" in guide


def test_guide_states_the_repo_scoped_gates_and_the_census_scope(guide: str) -> None:
    assert "--census-file" in guide and "gate 4" in guide
    assert "judge the repository" in guide


def test_guide_states_the_prove_do_not_perform_boundary(guide: str) -> None:
    """The counter-intuitive consequence, in the operator's words, not the designer's."""
    assert "regenerated and committed" in guide
    assert "modeling item" in guide


def test_guide_states_what_the_seam_does_not_check(guide: str) -> None:
    assert "assert_read_set_covered" in guide
    assert "unrecorded" in guide, "verify's teax.revision limit is not stated"


def _example_table(guide: str) -> str:
    blocks = re.findall(r"```toml\n(.*?)```", guide, flags=re.S)
    assert len(blocks) == 1, "the guide carries exactly one example declaration"
    return blocks[0]


def test_guide_documents_every_declaration_key(guide: str) -> None:
    """The declaration is the project's whole say over ``integrate``; every key needs a home.

    The example uses every key, and each key has its own bullet, so a key added to the
    declaration fails here until the guide says what it is for.
    """
    table = tomllib.loads(_example_table(guide))["tool"]["sysml-codegen"]["integrate"]
    assert set(table) == set(declarations._TABLE_KEYS)
    assert set(table["gates"]) == set(declarations.REPO_GATES)
    for gate in table["gates"].values():
        assert set(gate) == set(declarations._GATE_KEYS)
    bullets = [line for line in guide.splitlines() if line.startswith("- **`")]
    for key in (*(f"gates.{gate}" for gate in declarations.REPO_GATES),
                *(key for key in declarations._TABLE_KEYS if key != "gates")):
        assert any(line.startswith(f"- **`{key}`**") for line in bullets), key
    for key in declarations._GATE_KEYS:
        assert f"`{key}` is the" in guide or f"**`{key}` has no default**" in guide, key
    for key in declarations.FIXED_TOOLCHAIN_KEYS:
        assert f"`{key}`" in guide, key
    assert declarations.DEFAULT_BACKUP_PREFIX in guide


def test_guide_says_checked_has_no_default_and_why(guide: str) -> None:
    assert "**`checked` has no default**" in guide
    assert "would claim a check nobody declared" in guide


def test_guide_states_the_undeclared_gate_outcome(guide: str) -> None:
    assert f"`{integrate.NOT_DECLARED}`" in guide
    assert "`could_not_run`, `input-missing`" in guide


def test_the_guides_example_declaration_is_a_valid_declaration(guide: str, tmp_path: Path) -> None:
    """The one declaration a reader will copy must load, or the guide teaches a refusal."""
    (tmp_path / "pyproject.toml").write_text(_example_table(guide))
    declared = declarations.load_declaration(tmp_path)
    assert set(declared.gates) == set(declarations.REPO_GATES)
    assert all(gate.checked for gate in declared.gates.values())


def test_guide_names_teax_and_the_project_root_variables(guide: str) -> None:
    assert roots.TEAX_SIMKIT_PATH in guide
    assert roots.PROJECT_ROOT_ENV in guide
    assert "STUDY_REQUIRE_TEAX=1" in guide


def test_guide_states_gate_1b_needs_the_teax_variable(guide: str) -> None:
    row = next(line for line in guide.splitlines() if line.startswith("| 1b | `teax-revision`"))
    assert roots.TEAX_SIMKIT_PATH in row and "could not run" in row


def test_guide_states_the_snapshot_rule(guide: str) -> None:
    """Gate 4 globs ``*.snapshot.json``; this repository's usual snapshot name does not match."""
    assert "exactly one `*.snapshot.json` beside `--models-root`" in guide
    assert "`instance_graph_snapshot.json`, does not match" in guide


def test_guide_states_the_project_root_and_monorepo_rule(guide: str) -> None:
    section = guide.split("## Where the project root is", 1)[1].split("\n## ", 1)[0]
    assert "git work tree that contains `--package`" in section
    assert "exit 2" in section
    assert "monorepo" in section and roots.PROJECT_ROOT_ENV in section
