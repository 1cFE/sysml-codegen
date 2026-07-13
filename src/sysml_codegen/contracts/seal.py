"""``seal_package`` — the pure directory-to-``PackageContract`` seal (Item 9 / D1-D5).

Sealing is a pure function of a directory plus a declared coverage policy, independent of
the pipeline that produced the directory (Core Concept). That is what makes this the same
function generation runs at Step 9 and the ``seal`` subcommand runs again after a human
edits a stencil (D1/D2).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from sysml_codegen.contracts.models import CoveragePolicy, PackageContract
from sysml_codegen.contracts.versions import RUNTIME_CONTRACT_VERSION, generator_version

DEFAULT_COVERAGE_POLICY = CoveragePolicy(
    exclude_globs=["contracts/package_contract.json", "**/__pycache__/**"],
    runtime_output_globs=[],
)


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a ``/``-separated glob (``*``, ``?``, ``**``) to an anchored regex.

    ``**`` adjoining a slash consumes zero or more whole path segments (including the
    slash); a bare ``*``/``?`` never crosses a ``/``. Kept identical in ``verify.py``
    (duplicated, not imported — D7 stdlib-only) so producer and consumer agree.
    """
    out = []
    i, n = 0, len(pattern)
    while i < n:
        if pattern[i : i + 3] == "**/":
            out.append("(?:.*/)?")
            i += 3
        elif pattern[i : i + 3] == "/**" and i + 3 == n:
            out.append("(?:/.*)?")
            i += 3
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _is_covered(rel_path: str, policy: CoveragePolicy) -> bool:
    patterns = [*policy.exclude_globs, *policy.runtime_output_globs]
    return not any(_glob_to_regex(pattern).match(rel_path) for pattern in patterns)


def seal_package(
    package_dir: Path,
    package_name: str,
    policy: CoveragePolicy = DEFAULT_COVERAGE_POLICY,
) -> PackageContract:
    """Hash every policy-covered file under ``package_dir`` into a ``PackageContract``.

    Pure over the directory: walks and hashes whatever is on disk *now* (stubs or
    preserved handwritten code alike), so the identical call re-seals after an edit.
    """
    artifact_hashes: dict[str, str] = {}
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(package_dir).as_posix()
        if _is_covered(rel_path, policy):
            artifact_hashes[rel_path] = hashlib.sha256(path.read_bytes()).hexdigest()

    executable_fingerprint = hashlib.sha256(
        "\n".join(f"{k}:{v}" for k, v in sorted(artifact_hashes.items())).encode("utf-8")
    ).hexdigest()

    return PackageContract(
        package_name=package_name,
        coverage_policy=policy,
        artifact_hashes=artifact_hashes,
        executable_fingerprint=executable_fingerprint,
        generator_version=generator_version(),
        runtime_contract_version=RUNTIME_CONTRACT_VERSION,
    )


__all__ = ["DEFAULT_COVERAGE_POLICY", "seal_package"]
