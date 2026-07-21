"""Generation-provenance manifest and the re-seal provenance gate (Item 7, D4/D5).

Codegen-side only — never emitted into a package, so it may import pydantic and the seal
helpers. It **reuses** the seal walker's coverage helpers (does not duplicate them) and adds
no walker of its own, so the deliberately-distinct seal and verify walkers stay untouched
(INV-D). The pure ``seal_package`` function is likewise unchanged: this gate lives one layer
up, at the ``seal`` CLI, exactly where re-seal already runs.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from sysml_codegen.contracts.models import CoveragePolicy, GenerationManifest
from sysml_codegen.contracts.seal import _glob_to_regex, _is_covered

HANDWRITTEN_GLOBS = ["handwritten/**"]
MANIFEST_REL_PATH = "contracts/generation_manifest.json"
SEAL_REL_PATH = "contracts/package_contract.json"


class ProvenanceError(ValueError):
    """A re-seal would admit a file the generation manifest does not account for."""


def _matches_any(rel_path: str, globs: list[str]) -> bool:
    return any(_glob_to_regex(pattern).match(rel_path) for pattern in globs)


def build_generation_manifest(
    entries: list[tuple[str, Path]], policy: CoveragePolicy
) -> GenerationManifest:
    """Classify the covered tree into provenance classes at first seal.

    ``codegen_produced`` = covered files minus the handwritten region minus runtime globs,
    plus the manifest's own path (not yet on disk when this runs). Completeness by
    construction (Major 4): every covered non-handwritten file is enumerated, so a legitimate
    re-seal never false-fails on a generated file.
    """
    runtime_globs = list(policy.runtime_output_globs)
    covered = [rel for rel, path in entries if path.is_file() and _is_covered(rel, policy)]
    codegen = {
        rel
        for rel in covered
        if not _matches_any(rel, HANDWRITTEN_GLOBS) and not _matches_any(rel, runtime_globs)
    }
    codegen.add(MANIFEST_REL_PATH)
    return GenerationManifest(
        codegen_produced=sorted(codegen),
        handwritten_globs=list(HANDWRITTEN_GLOBS),
        runtime_globs=runtime_globs,
    )


def check_reseal_provenance(
    package_dir: Path,
    entries: list[tuple[str, Path]],
    prior_seal: dict,
    policy: CoveragePolicy,
) -> None:
    """Reject a re-seal that would launder a foreign file or an edited generated file.

    The gate authenticates the on-disk manifest against the *prior* seal (its trust anchor),
    then requires every covered file to be either a frozen codegen-produced artifact (hash
    unchanged since the prior seal) or a file under a non-codegen glob. This defeats a
    non-collusive drop-a-file injection (attack b); it is defense-in-depth, not proof against a
    same-privilege adversary who also rewrites the manifest and the prior seal (design
    Non-Goals: seal signing).

    Raises:
        ProvenanceError: on a missing/tampered manifest, an edited codegen file, a foreign
            file, or a manifest-recorded codegen file missing on disk.
    """
    manifest_path = package_dir / "contracts" / "generation_manifest.json"
    if not manifest_path.is_file():
        raise ProvenanceError(
            f"{MANIFEST_REL_PATH} is missing — this package predates the generation manifest; "
            "regenerate it before re-sealing"
        )
    prior_hashes: dict = prior_seal.get("artifact_hashes", {})
    manifest_bytes = manifest_path.read_bytes()
    on_disk_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if prior_hashes.get(MANIFEST_REL_PATH) != on_disk_hash:
        raise ProvenanceError(
            "generation manifest does not match the prior seal — it was tampered with, or the "
            "prior seal predates it"
        )

    manifest = GenerationManifest.model_validate_json(manifest_bytes)
    codegen = set(manifest.codegen_produced)
    non_codegen = manifest.handwritten_globs + manifest.runtime_globs

    covered_on_disk: set[str] = set()
    for rel, path in entries:
        if not path.is_file() or not _is_covered(rel, policy) or rel == SEAL_REL_PATH:
            continue
        covered_on_disk.add(rel)
        if rel in codegen:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if prior_hashes.get(rel) != actual:
                raise ProvenanceError(
                    "codegen-produced file changed since the seal (only handwritten files may "
                    f"change across a re-seal): {rel}"
                )
        elif not _matches_any(rel, non_codegen):
            raise ProvenanceError(
                "foreign file not accounted for by the generation manifest (cannot be "
                f"laundered as codegen-produced): {rel}"
            )

    missing = codegen - covered_on_disk
    if missing:
        raise ProvenanceError(
            "codegen-produced files recorded in the manifest are missing on disk: "
            + ", ".join(sorted(missing))
        )


__all__ = [
    "HANDWRITTEN_GLOBS",
    "MANIFEST_REL_PATH",
    "ProvenanceError",
    "build_generation_manifest",
    "check_reseal_provenance",
]
