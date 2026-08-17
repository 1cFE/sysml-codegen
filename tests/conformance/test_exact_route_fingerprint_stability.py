"""Gate 4C, row L-140: fingerprint stability on the exact route.

The responsibility this replaces belonged to
``tests/conformance/test_fingerprint_stability.py``, whose specimen was a **v5**
extraction snapshot. Three claims carried, and all three are re-authored here on
the shipped v6 route:

1. two independent generations of the same snapshot produce the same
   fingerprints, and the executable fingerprint is the documented digest of the
   artifact hashes;
2. a verifier-policy change moves the verifier hash and the derived executable
   fingerprint, and nothing else;
3. the model's own fingerprint survives the round trip through a snapshot.

Claim 3 was re-stated when the exact route landed — the live route then wrote
checkout-absolute ``SysML Source:`` comments, so only the **semantic**
fingerprint was route-independent and the executable fingerprints' divergence
was pinned by value. Step 5 of the Item-7 correction (audit-F4) removed that
divergence: both routes render the portable ``root-0/`` referent, so the
original claim holds again and both fingerprints are asserted equal.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import agentic_mbse
import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

REPO_ROOT = Path(__file__).resolve().parents[2]
V6_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"
PACKAGE = "fusion_tea"
AGENTIC_SOURCE_ROOT = Path(agentic_mbse.__file__).resolve().parents[1]

# The revision supplying the previous verifier policy. Carried unchanged from
# tests/conformance/test_fingerprint_stability.py: the policy last changed at
# e217119 and this revision precedes it.
REVIEWED_REVISION = "512786c7dfab44fba7a0185d09e845b7494c702d"
REVIEWED_VERIFY_SHA256 = "24eb3565b0a7a682cf8a2510c871d7af9baa938fdaac6b5e826f88045a400276"


def _seal(package: Path) -> dict:
    return json.loads((package / "contracts" / "package_contract.json").read_text())


def _executable_fingerprint(package: Path) -> str:
    return _seal(package)["executable_fingerprint"]


def _semantic_fingerprint(package: Path) -> str:
    contract = json.loads((package / "contracts" / "model_contract.json").read_text())
    return contract["semantic_fingerprint"]


def _generate_from_snapshot(output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=V6_SNAPSHOT,
            package_name=PACKAGE,
            overwrite=True,
        )
    )
    return output


def test_fingerprints_are_stable_across_two_independent_generations(tmp_path: Path) -> None:
    first = _generate_from_snapshot(tmp_path / "a")
    second = _generate_from_snapshot(tmp_path / "b")

    assert _executable_fingerprint(first) == _executable_fingerprint(second)
    assert _semantic_fingerprint(first) == _semantic_fingerprint(second)

    seal = _seal(first)
    assert seal["artifact_hashes"] == _seal(second)["artifact_hashes"]
    digest_input = "\n".join(
        f"{path}:{digest}" for path, digest in sorted(seal["artifact_hashes"].items())
    ).encode()
    assert seal["executable_fingerprint"] == hashlib.sha256(digest_input).hexdigest()


def _generate_with_source_tree(source_root: Path, output: Path) -> None:
    """Generate in a subprocess whose ``sysml_codegen`` comes from ``source_root``."""
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        "from sysml_codegen.cli import GenerationConfig, run_codegen\n"
        "output, snapshot = Path(sys.argv[1]), Path(sys.argv[2])\n"
        "config = GenerationConfig(\n"
        "    output_path=output, from_snapshot=snapshot,\n"
        f"    package_name={PACKAGE!r}, overwrite=True,\n"
        ")\n"
        "raise SystemExit(0 if run_codegen(config) else 1)\n"
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join(
                [str(source_root / "src"), str(AGENTIC_SOURCE_ROOT), str(REPO_ROOT)]
            ),
        }
    )
    subprocess.run(
        [sys.executable, "-c", script, str(output), str(V6_SNAPSHOT)],
        check=True,
        cwd=REPO_ROOT,
        env=environment,
    )


def test_a_verifier_policy_change_moves_only_its_hash_and_the_derived_fingerprint(
    tmp_path: Path,
) -> None:
    """One variable is isolated: both sides are the working tree, one verifier apart."""
    reviewed_verify = subprocess.run(
        ["git", "show", f"{REVIEWED_REVISION}:src/sysml_codegen/contracts/verify.py"],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
    ).stdout
    canonical = (REPO_ROOT / "src/sysml_codegen/contracts/verify.py").read_bytes()
    assert reviewed_verify != canonical, (
        "REVIEWED_REVISION must carry a different verifier policy, or this asserts nothing"
    )

    reviewed_source = tmp_path / "reviewed"
    (reviewed_source / "src").mkdir(parents=True)
    for entry in (REPO_ROOT / "src").iterdir():
        if entry.name != "sysml_codegen":
            (reviewed_source / "src" / entry.name).symlink_to(entry)
    shutil.copytree(
        REPO_ROOT / "src/sysml_codegen", reviewed_source / "src/sysml_codegen", symlinks=True
    )
    (reviewed_source / "src/sysml_codegen/contracts/verify.py").write_bytes(reviewed_verify)

    reviewed_output = tmp_path / "reviewed-output"
    candidate_output = tmp_path / "candidate-output"
    _generate_with_source_tree(reviewed_source, reviewed_output)
    _generate_with_source_tree(REPO_ROOT, candidate_output)

    reviewed_seal = _seal(reviewed_output)
    candidate_seal = _seal(candidate_output)
    reviewed_hashes = dict(reviewed_seal["artifact_hashes"])
    candidate_hashes = dict(candidate_seal["artifact_hashes"])
    reviewed_verifier_hash = reviewed_hashes.pop("contracts/verify.py")
    candidate_verifier_hash = candidate_hashes.pop("contracts/verify.py")

    assert reviewed_hashes == candidate_hashes
    assert reviewed_verifier_hash == REVIEWED_VERIFY_SHA256
    assert (candidate_output / "contracts/verify.py").read_bytes() == canonical
    assert candidate_verifier_hash == hashlib.sha256(canonical).hexdigest()
    assert candidate_verifier_hash != reviewed_verifier_hash

    for seal in (reviewed_seal, candidate_seal):
        digest_input = "\n".join(
            f"{path}:{digest}" for path, digest in sorted(seal["artifact_hashes"].items())
        ).encode()
        assert seal["executable_fingerprint"] == hashlib.sha256(digest_input).hexdigest()
    assert reviewed_seal["executable_fingerprint"] != candidate_seal["executable_fingerprint"]


@requires_license
@pytest.mark.parametrize("fixture", ["wi014_toy", "constraint_multi_instance"])
def test_the_semantic_fingerprint_is_identical_live_and_from_a_snapshot(
    fixture: str, tmp_path: Path
) -> None:
    """Both fingerprints survive capture and replay.

    The semantic fingerprint always did. The executable fingerprint follows
    since step 5 (audit-F4): the live route renders the same portable
    ``root-0/`` referent a snapshot records, so every artifact hash agrees.
    The provenance comments must still be present — equality via two packages
    that dropped their ``SysML Source:`` lines would prove nothing.
    """
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

    models = FIXTURES_DIR / fixture
    live = tmp_path / "live"
    assert run_codegen(
        GenerationConfig(
            models_path=models, output_path=live, package_name=fixture, overwrite=True
        )
    )

    snapshot = capture_instance_graph_snapshot([models], tmp_path / "snapshot.json")
    replayed = tmp_path / "snap"
    assert run_codegen(
        GenerationConfig(
            output_path=replayed,
            from_snapshot=snapshot,
            package_name=fixture,
            overwrite=True,
        )
    )

    assert _semantic_fingerprint(live) == _semantic_fingerprint(replayed)
    assert _executable_fingerprint(live) == _executable_fingerprint(replayed)

    live_hashes = _seal(live)["artifact_hashes"]
    replay_hashes = _seal(replayed)["artifact_hashes"]
    assert live_hashes == replay_hashes

    commented = [
        path for path in live_hashes if "SysML Source: root-0/" in (live / path).read_text()
    ]
    assert commented, "no artifact carries a portable provenance comment"
