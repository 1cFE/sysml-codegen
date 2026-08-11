"""Gate 4C, row L-179: the v6 snapshot generation surface.

The responsibility this replaces belonged to
``tests/conformance/test_snapshot_generation.py``, whose repointed nodes drove a
**v5** extraction snapshot through the retired route. Three claims carried:

1. **License-free offline generation.** A real subprocess with every license
   variable scrubbed generates a package from a committed snapshot.
2. **No provenance leakage.** No snapshot-format or capture text reaches a
   generated artifact.
3. **Live-vs-snapshot byte identity.** Two independent processes, one live and
   one from a snapshot, write the same bytes.

Claims 1 and 2 are authored here on the shipped v6 route, against the committed
``fusion_tea`` instance-graph snapshot.

**Claim 3 does not hold on the exact route, and must not be asserted.** A v6
snapshot records its sources under the portable ``root-0/`` staging referent,
never the checkout path, so every generated file carrying a ``SysML Source:``
comment differs between the two routes by construction — that portability is the
point of the referent. What survives is that the difference is *only* the
provenance comment and that the two routes agree semantically. Both are already
pinned, so per Gate 4C's cite-don't-duplicate rule this module does not restate
them:

  * in ``test_exact_route_generated_package.py``,
    ``test_the_two_packages_differ_only_in_provenance_comments`` names the whole
    differing set and proves each difference is the source line;
  * in ``test_exact_route_fingerprint_stability.py``,
    ``test_the_semantic_fingerprint_is_identical_live_and_from_a_snapshot``
    proves the model contract's semantic fingerprint is equal across the two.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = str(Path(sys.executable).parent / "sysml-codegen")
V6_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"

_LICENSE_VARS = ("SYSIDE_LICENSE_KEY", "SYSIDE_LICENSE", "SYSIDE_LICENSE_FILE")


def _run_cli(*args: str, scrub_license: bool = False) -> subprocess.CompletedProcess:
    environment = dict(os.environ)
    if scrub_license:
        for name in _LICENSE_VARS:
            environment.pop(name, None)
    return subprocess.run(
        [CLI, *args], cwd=REPO_ROOT, capture_output=True, text=True, env=environment
    )


def test_generation_from_a_v6_snapshot_needs_no_license(tmp_path: Path) -> None:
    """A real subprocess, every license variable removed from its environment."""
    output = tmp_path / "out"
    result = _run_cli(
        "generate",
        "--from-snapshot",
        str(V6_SNAPSHOT),
        "--output",
        str(output),
        "--package-name",
        "fusion_tea",
        "--overwrite",
        scrub_license=True,
    )
    assert result.returncode == 0, result.stderr
    assert (output / "__init__.py").exists()
    assert (output / "contracts" / "package_contract.json").exists()


def test_no_snapshot_provenance_text_reaches_a_generated_artifact(tmp_path: Path) -> None:
    output = tmp_path / "out"
    result = _run_cli(
        "generate",
        "--from-snapshot",
        str(V6_SNAPSHOT),
        "--output",
        str(output),
        "--package-name",
        "fusion_tea",
        "--overwrite",
    )
    assert result.returncode == 0, result.stderr

    needles = (
        "This run did NOT use live extraction",
        "snapshot_format_version",
        "instance_graph_snapshot",
        "captured_at",
    )
    offenders = [
        f"{path.relative_to(output)}: {needle}"
        for path in output.rglob("*")
        if path.is_file()
        for needle in needles
        if needle in path.read_text(errors="ignore")
    ]
    assert offenders == []


def test_two_independent_snapshot_generations_write_the_same_bytes(tmp_path: Path) -> None:
    """The byte-identity claim the exact route *can* make: same route, two processes."""
    trees = []
    for name in ("first", "second"):
        output = tmp_path / name
        result = _run_cli(
            "generate",
            "--from-snapshot",
            str(V6_SNAPSHOT),
            "--output",
            str(output),
            "--package-name",
            "fusion_tea",
            "--overwrite",
        )
        assert result.returncode == 0, result.stderr
        trees.append(
            {
                str(path.relative_to(output)): path.read_bytes()
                for path in sorted(output.rglob("*"))
                if path.is_file()
            }
        )

    first, second = trees
    differing = sorted(
        key for key in set(first) | set(second) if first.get(key) != second.get(key)
    )
    assert differing == []


def test_the_public_surface_accepts_exactly_one_extraction_input(tmp_path: Path) -> None:
    neither = _run_cli(
        "generate", "--output", str(tmp_path / "a"), "--package-name", "x", "--overwrite"
    )
    assert neither.returncode != 0
    assert "--models" in (neither.stderr + neither.stdout)

    both = _run_cli(
        "generate",
        "--models",
        str(FIXTURES_DIR / "fusion_tea"),
        "--from-snapshot",
        str(V6_SNAPSHOT),
        "--output",
        str(tmp_path / "b"),
        "--package-name",
        "x",
        "--overwrite",
    )
    assert both.returncode != 0
    assert "not allowed with" in (both.stderr + both.stdout)


def test_a_missing_snapshot_is_a_named_refusal_not_a_traceback(tmp_path: Path) -> None:
    """In-process, so the return value is the assertion rather than an exit code."""
    assert (
        run_codegen(
            GenerationConfig(
                output_path=tmp_path / "out",
                from_snapshot=tmp_path / "absent.json",
                package_name="fusion_tea",
                overwrite=True,
            )
        )
        is False
    )
    assert not (tmp_path / "out").exists(), "a refused run must leave no output tree"


def test_the_generation_timestamp_template_variable_has_no_render_site() -> None:
    """A latent byte-identity trap: it must stay unwired from Python."""
    hits = subprocess.run(
        ["grep", "-rn", "generation_timestamp", "src/sysml_codegen"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    offenders = [
        line for line in hits.stdout.splitlines() if line.split(":", 1)[0].endswith(".py")
    ]
    assert offenders == [], f"generation_timestamp is wired from Python: {offenders}"


@pytest.mark.parametrize("directory", ["modules", "schemas", "inputs", "pipelines"])
def test_the_offline_package_carries_each_generated_directory(
    tmp_path: Path, directory: str
) -> None:
    output = tmp_path / "out"
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=V6_SNAPSHOT,
            package_name="fusion_tea",
            overwrite=True,
        )
    )
    assert (output / directory).is_dir()
