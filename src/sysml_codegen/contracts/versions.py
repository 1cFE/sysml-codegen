"""Pinned version constants for the contracts package (CONSTRAINT-EXEC Item 9 / P4).

Both are generator constants, never read from an installed runtime — a package's seal
records the generator that produced it, not whatever happens to be on the loading
machine (D5: coupling generation to an installed teax would break license-free
snapshot determinism).
"""

from __future__ import annotations

RUNTIME_CONTRACT_VERSION = "2.0.0"
"""The runtime API surface the emitted code targets.

Bump the major version on any breaking change to that surface; minor/patch for
compatible additions. Owner-overridable; ``1.0.0`` was the initial token (P4).

Bumped to ``2.0.0`` at CONSTRAINT-SEMANTICS Item 3, where three things broke at once for a
runtime reading a ``ConstraintReport``:

- ``assessed_count`` is renamed ``assessed_entry_count``, because a second, coarser count now
  exists beside it and a reader must not have to guess which tier a field means;
- ``coverage`` is a new **required** block carrying the ``CoverageAccount``;
- the ``headline`` vocabulary is replaced, not extended — ``all_satisfied`` becomes
  ``full_satisfaction`` and the new ``partial_coverage`` state joins it. The rename is
  deliberate: state 3's meaning strengthens from "nothing failed" to "everything was checked
  and passed", and a token whose meaning changes under a reader is a silent misread. Renaming
  turns every stale reader into a named refusal instead.

TEAx **replaces** its vendored ``ACCEPTED_RUNTIME_CONTRACT_VERSIONS`` rather than extending
it, so a package built before this item fails at seal verification before any report is read.
``TRUSTED_VERIFIER_SHA256`` does not move: ``contracts/verify.py`` reads the version out of
the seal data and contains no version literal, so its bytes are unchanged by the bump.
"""

CATALOG_SCHEMA_VERSION = "3.0.0"
"""The embedded constraint-catalog schema shape a ``model_contract.json`` carries (Item 8).

Bumped from the implicit ``1.x`` (pre-Item-8, no version token) to ``2.0.0`` when the
admitted-usage tier and the five projected entry fields landed — a breaking schema addition.
Bumped to ``3.0.0`` at CONSTRAINT-SEMANTICS Item 2, where two things broke at once for a
consumer reading ``usage_records``: the **population** widened from admitted-only to every
authored constraint usage, and the **identity** moved from the
``(usage_qualified_name, source_local_identity)`` string pair to ``declaration_id``, which
every catalog row now carries. A consumer that wanted the old, narrower set recovers it
exactly by filtering ``disposition_kind == "eligible"``.
A consumer (TEAx) vendors an accepted set by copy (B3 forbids importing this repo) and fails
closed on a version it does not accept, before reading any catalog field (INV-4). It sits
*inside* the fingerprinted model-contract payload, so a schema bump is also an identity change
(``semantic_fingerprint`` moves). Bumping it is a deliberate act; a new drift test
(``tests/conformance/test_catalog_schema_version.py``) pins it against the vendored TEAx set.
"""

TRUSTED_VERIFIER_SHA256 = "ad0a855af17d18af5f3e8c36b1a6c500f492d88ec777b40f307c646306c67284"
"""The sha256 of the canonical stdlib-only verifier (``contracts/verify.py``), published as
the trust anchor a runtime (TEAx) vendors to authenticate a package-local verifier's bytes
*before* executing it (Item 7, D1/INV-B). It is a literal, not computed from the file, so a
drift test can catch a verify.py edit that was not accompanied by re-publishing here and
re-vendoring in the runtime.

One image per ``RUNTIME_CONTRACT_VERSION`` (D3): a deliberate verify.py byte change requires a
version bump and this constant updated in lockstep. The current bytes *are* the single 1.0.0
image. Cross-repo agreement rests on this constant plus manual re-vendoring — B3 forbids the
runtime importing sysml-codegen, so no automated cross-repo check is possible.
"""


def generator_version() -> str:
    """The sysml-codegen version that produced a seal."""
    from sysml_codegen import __version__

    return __version__


__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "RUNTIME_CONTRACT_VERSION",
    "TRUSTED_VERIFIER_SHA256",
    "generator_version",
]
